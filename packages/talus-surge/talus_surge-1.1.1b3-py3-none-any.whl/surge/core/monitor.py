# -*- coding: utf-8 -*-
from uuid import UUID
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import (
    WebSocket,
    WebSocketDisconnect
)
from eastwind.lib.util import response
from eastwind.lib.database import commit
from eastwind.lib.sql import fetch_iterate
from eastwind.core.project import (
    start_project,
    stop_project,
    Project,
)
from modules.task.sql import (
    select_valid_running_task,
)
from modules.task.model import (
    TaskStatus,
)
from surge.__version__ import VERSION
from surge.lib.util import DEBUG_MODE
from surge.lib.path import DIR_SURGE_STATIC
from surge.lib.topic import (
    TOPICS,
    TopicManager,
    TopicWorker,
)
from .docs import (
    URL_OPENAPI,
    URL_SWAGGER_OAUTH2_REDIRECT,
    APP_TITLE,
    PREFIX_STATIC,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[Project]:
    # Initialize the project.
    project: Project = start_project()
    # Reset all RUNNING tasks into PENDING.
    async with project["Session"]() as sess:
        # Avoid ORM caching dirty read.
        await commit(sess)
        # Fetch the RUNNING tasks, reset them into PENDING.
        counter = 0
        async for task in await fetch_iterate(sess, select_valid_running_task(), for_update=True):
            counter += 1
            # Change the status, reset the runner.
            task.status = TaskStatus.PENDING
            task.runner = None
        print(f"Processed {counter} tasks")
        await commit(sess)
    # Start the application.
    yield project
    # Close the project correctly.
    await stop_project(project)


app = FastAPI(lifespan=lifespan,
              title=APP_TITLE,
              version=VERSION,
              openapi_url=URL_OPENAPI,
              docs_url=None, redoc_url=None,
              swagger_ui_oauth2_redirect_url=URL_SWAGGER_OAUTH2_REDIRECT,)
# Mount the library used offline static files.
app.mount(PREFIX_STATIC, StaticFiles(directory=DIR_SURGE_STATIC), name="static")
# Only loaded docs in DEBUG_MODE.
if DEBUG_MODE:
    from .docs import router as docs_router
    app.include_router(docs_router)


@app.post("/{topic}", response_class=JSONResponse)
async def notify_topic_workers(request: Request, topic: str):
    # Extract the topic manager.
    if topic not in TOPICS:
        return response(code=202)
    # Extract the topic and topic manager.
    if await TOPICS[topic].dispatch(request.state):
        # Some task is dispatched.
        return response(code=200)
    # All the workers are busy, task is queued.
    return response(code=202)


@app.websocket("/{topic}/{worker_uid}")
async def on_worker(socket: WebSocket, topic: str, worker_uid: UUID):
    # Check topic validation.
    if topic not in TOPICS:
        TOPICS[topic] = TopicManager(topic)
    # Insert the socket into the manager.
    topic_manager: TopicManager = TOPICS[topic]
    worker: TopicWorker = await topic_manager.on_connect(socket, worker_uid)
    # Await for worker status change.
    try:
        async for task_result in socket.iter_json():
            # Read the task running result.
            # If any response received, reset the worker to complete.
            await topic_manager.on_completed(socket.state, worker, task_result["status"], task_result["log"])
    except WebSocketDisconnect:
        pass
    finally:
        await TOPICS[topic].on_disconnect(worker)
