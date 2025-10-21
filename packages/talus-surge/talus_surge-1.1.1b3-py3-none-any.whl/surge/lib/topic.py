# -*- coding: utf-8 -*-
import asyncio
from uuid import UUID
from collections import deque
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi.websockets import WebSocket
from starlette.datastructures import State
from sqlalchemy.ext.asyncio import AsyncSession as Session
from eastwind.lib.util import Result
from eastwind.lib.database import commit
from modules.task.api import (
    Task,
    TaskStatus,
    query_by_uid as query_task_by_uid,
    query_pending as query_task_pending,
)


class WorkerState:
    IDLE = 0
    BUSY = 1


class TaskMissing(Exception):
    pass


@asynccontextmanager
async def update_task(state: State, task_uid: UUID) -> AsyncGenerator[tuple[Session, Task], None]:
    async with state.Session() as sess:
        # Avoid ORM caching dirty read.
        await commit(sess)
        # Fetch the task with update lock.
        result_task: Result[Task] = await query_task_by_uid(sess, task_uid, for_update=True)
        if result_task.is_error():
            # No target task found.
            raise TaskMissing(result_task.error["error"])
        # Call the task.
        yield sess, result_task.value
        await commit(sess)


class TopicWorker:
    def __init__(self, socket: WebSocket, worker_uid: UUID):
        self.socket: WebSocket = socket
        self.status: int = WorkerState.IDLE
        self.worker_uid: UUID = worker_uid
        self.task_uid: UUID | None = None


class TopicManager:
    def __init__(self, topic: str):
        self.__topic: str = topic
        # Create a lock for idle and busy state change.
        self.__lock = asyncio.Lock()
        # Prepare the idle queue and busy set.
        self.__idle = deque()
        self.__busy = []

    async def dispatch(self, state: State) -> bool:
        async with self.__lock:
            # Check whether any worker is free.
            num_idle_workers: int = len(self.__idle)
            if num_idle_workers == 0:
                return False
            # Fetch the PENDING tasks from database.
            worker_to_notify: list[TopicWorker] = []
            async with state.Session() as sess:
                # Avoid ORM caching dirty read.
                await commit(sess)
                # Fetch the tasks.
                result_tasks: list[Task] = await query_task_pending(sess, self.__topic, num_idle_workers, for_update=True)
                # Check the number of the tasks.
                if len(result_tasks) == 0:
                    # No task to be dispatched.
                    return False
                # Assign the tasks to different worker.
                for task in result_tasks:
                    # Extract the worker.
                    worker: TopicWorker = self.__idle.popleft()
                    # Update the worker information.
                    worker.task_uid = task.uid
                    worker.status = WorkerState.BUSY
                    # Update the task information.
                    task.status = TaskStatus.RUNNING
                    task.runner = worker.worker_uid
                    # Save the task status update.
                    await commit(sess)
                    # Save to the worker tasks.
                    worker_to_notify.append(worker)
                    self.__busy.append(worker)
            # Notify the worker, ignore any error occurs during the worker.
            for worker in worker_to_notify:
                try:
                    await worker.socket.send_json({"uid": worker.task_uid.hex})
                except Exception:
                    pass
            return True

    async def on_connect(self, socket: WebSocket, worker_uid: UUID) -> TopicWorker:
        # Accept and create a worker object.
        worker = TopicWorker(socket, worker_uid)
        await socket.accept()
        # Save the worker to idle queue.
        async with self.__lock:
            self.__idle.append(worker)
        # Dispatch the current task.
        asyncio.create_task(self.dispatch(socket.state))
        # Give back the worker.
        return worker

    async def on_completed(self, state: State, worker: TopicWorker, task_status: int, task_log: str) -> None:
        # Update the task status into DONE or error.
        async with update_task(state, worker.task_uid) as (sess, task):
            task.status = task_status
            task.pipeline_log = task_log
            task.runner = None
        # Update with worker.
        worker.status = WorkerState.IDLE
        worker.task_uid = None
        # Reset the worker to IDLE.
        async with self.__lock:
            self.__busy.remove(worker)
            self.__idle.append(worker)
        # Dispatch a new task.
        asyncio.create_task(self.dispatch(state))

    async def on_disconnect(self, worker: TopicWorker) -> None:
        # Save the worker to idle queue.
        async with self.__lock:
            # Check whether the worker is busy.
            if worker.status == WorkerState.BUSY:
                # Reset the task back to PENDING.
                async with update_task(worker.socket.state, worker.task_uid) as (sess, result_task):
                    task: Task = result_task.value
                    if task.status == TaskStatus.RUNNING:
                        # Reset the task status back to PENDING.
                        task.status = TaskStatus.PENDING
                        task.runner = None
                # Remove the worker from the set.
                self.__busy.remove(worker)
            else:
                # Remove the worker from the waiting queue.
                self.__idle.remove(worker)


TOPICS: dict[str, TopicManager] = {}
