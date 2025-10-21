# -*- coding: utf-8 -*-
import os
import sys
import json
import asyncio
import logging
from uuid import UUID
from logging.handlers import TimedRotatingFileHandler
from uuid6 import uuid7
from argparse import ArgumentParser
from starlette.datastructures import State
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
from eastwind.lib.util import (
    launch_python,
)
from eastwind.core.config import (
    SurgeMonitorConfig,
    SurgeWorkerConfig,
)
from eastwind.core.project import (
    Project,
    start_project,
    stop_project,
)

from modules.task.model import TaskStatus
# Websocket log only shown WARNING and above.
logging.getLogger("websockets").setLevel(logging.WARNING)
# Task execution log and system running logs are separated.
logger = logging.getLogger("surge_core")
PATH_RUNNER: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline_runner.py")


class Worker:
    def __init__(self, uid: UUID, topic: str):
        self.__uid: str = uid.hex
        self.__topic: str = topic
        self.__worker_proc: asyncio.subprocess.Process | None = None

    def terminate_worker(self):
        if self.__worker_proc is not None:
            self.__worker_proc.terminate()
            self.__worker_proc = None

    async def run_task(self, task_uid: str) -> tuple[int, str]:
        # Run the python script in async process.
        self.__worker_proc = await launch_python(
            PATH_RUNNER, task_uid, self.__uid,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        # Hold and wait the process.
        _, error_output = await self.__worker_proc.communicate()
        # Get the task status
        task_status: int = TaskStatus.COMPLETE if self.__worker_proc.returncode == 0 else TaskStatus.ERROR
        task_log: str = error_output.decode("utf-8")
        # After the worker is complete, reset to None.
        self.__worker_proc = None
        return task_status, task_log

    async def exec(self, state: State) -> None:
        monitor_config: SurgeMonitorConfig = state.config.surge_monitor
        worker_config: SurgeWorkerConfig = state.config.surge_worker
        ws_url: str = f"ws://{monitor_config.address}:{monitor_config.port}"
        logger.info(f"Worker UID: {self.__uid}")
        logger.info(f"Connecting to {ws_url} (Press CTRL+C to quit)")
        # Keep connect to server.
        async for socket in connect(f"{ws_url}/{self.__topic}/{self.__uid}",
                                    ping_interval=worker_config.heartbeat_interval,
                                    ping_timeout=worker_config.heartbeat_max_timeout):
            try:
                logger.info(f"Monitor connected.")
                async for message in socket:
                    try:
                        # Wait for incoming request.
                        payload: dict = json.loads(message)
                    except json.decoder.JSONDecodeError:
                        break
                    # Check out the task UID.
                    if "uid" not in payload:
                        break
                    logger.info(f"Running task {payload["uid"]}")
                    task_status, task_log = await self.run_task(payload["uid"])
                    # Send the completed response information.
                    await socket.send(json.dumps({
                        "status": task_status,
                        "log": task_log,
                    }))
                    logger.info(f"Complete task {payload["uid"]}")
            except ConnectionClosed:
                # If the worker process is running, force to stop it.
                self.terminate_worker()
                # Reconnect in another 5 seconds.
                logger.info(f"Monitor disconnected, retry connecting...")
                await asyncio.sleep(5)


LOG_LEVEL_MAP: dict[str, int] = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}


async def lifespan(topic: str, log_level: int, log_file_path: str, no_console: bool) -> None:
    # Setup logger level.
    logger_format = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    logger.setLevel(log_level)
    if len(log_file_path) > 0:
        file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=30, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logger_format)
        logger.addHandler(file_handler)
    if not no_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logger_format)
        logger.addHandler(console_handler)

    # Start logging.
    logger.info(f"Started surge worker process [{os.getpid()}]")
    # Generate a UUID for the current worker.
    worker_uid: UUID = uuid7()
    # Start the project.
    project: Project = start_project()
    logger.info(f"Task topic: {topic}")
    # Convert the project to state.
    worker = Worker(worker_uid, topic)
    # Connect to the monitor.
    try:
        await worker.exec(State(project))
    except (KeyboardInterrupt, asyncio.CancelledError):
        # Shutting down the system.
        logger.info(f"Shutting down")
        # If the worker process is running, force to stop it.
        worker.terminate_worker()
    # Stop the project.
    await stop_project(project)
    logger.info(f"Finished surge worker process [{os.getpid()}]")


def main(command_args: list[str]) -> None:
    parser = ArgumentParser(
        prog="surge worker",
        description='Run a specific task stored in the database',
    )
    parser.add_argument('topic', type=str, help='Task topic to subscribe')
    parser.add_argument("--log-level", type=str, default="info", help="Set the log level (critical, error, warning, info, debug), default: info")
    parser.add_argument("--log-file", type=str, default="", help="Set the log file path, default: ''")
    parser.add_argument("--no-console", action="store_true", help="Disable console output")
    parser.add_argument("--uvloop", action="store_true", help="Use uvloop instead of asyncio")
    args = parser.parse_args(command_args)
    # Check uvloop enabling.
    if args.uvloop:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # Run the target mission.
    asyncio.run(lifespan(args.topic, LOG_LEVEL_MAP[args.log_level], args.log_file, args.no_console))


if __name__ == '__main__':
    main(sys.argv[1:])
