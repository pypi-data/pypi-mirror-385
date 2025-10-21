# -*- coding: utf-8 -*-
import json
import asyncio
from uuid import UUID
from typing import AsyncGenerator
from argparse import ArgumentParser
from multiprocessing import cpu_count
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession as Session
from starlette.datastructures import State
from eastwind.lib.util import Result
from eastwind.lib.database import commit
from eastwind.core.project import (
    Project,
    start_project,
    stop_project,
)
from sdk.node import (
    NodeStatus,
    Variable,
)
from sdk.node.environment import (
    create as create_environment,
    clean as clean_environment,
)
from sdk.pipeline import Pipeline
from sdk.tool import ToolPipeline, ToolBase
from sdk.workflow import WorkflowPipeline
from modules.pipeline.api import (
    extract_from_indicator,
)
from modules.task.api import (
    Task,
    TaskStatus,
    query_by_uid as query_task_by_uid,
)


class TaskResetException(Exception):
    pass


@asynccontextmanager
async def update_task(state: State, task_uid: UUID, runner_uid: UUID) -> AsyncGenerator[tuple[Session, Task], None]:
    async with state.Session() as sess:
        # Avoid ORM caching dirty read.
        await commit(sess)
        # Fetch the task with update lock.
        result_task: Result[Task] = await query_task_by_uid(sess, task_uid, for_update=True)
        if result_task.is_error():
            # No target task found.
            raise ValueError(result_task.error["error"])
        # Check whether the task status is reset to PENDING.
        task: Task = result_task.value
        # Check whether the task status is reset to PENDING.
        # Or the runner is no-longer be responsible for this task.
        if task.status != TaskStatus.RUNNING or task.runner != runner_uid:
            raise TaskResetException()
        # Call the task.
        yield sess, task
        # Apply the changes.
        await commit(sess)


def get_pipeline(pipeline_type: str, pipeline_uid: str) -> Pipeline:
    # Construct the tool pipeline.
    result_pipeline_type: Result[type] = extract_from_indicator(pipeline_uid)
    if result_pipeline_type.is_error():
        raise Exception(result_pipeline_type.error["error"])
    # Check the pipeline type.
    if pipeline_type == "tool":
        if not issubclass(result_pipeline_type.value, ToolBase):
            raise Exception(f"Invalid tool type {pipeline_uid}")
        return ToolPipeline(result_pipeline_type.value)
    if pipeline_type == "workflow":
        # Extract the workflow pipeline.
        if not issubclass(result_pipeline_type.value, WorkflowPipeline):
            raise Exception(f"Invalid workflow type {pipeline_uid}")
        return result_pipeline_type.value()
    raise ValueError(f"Invalid pipeline type: {pipeline_type}")


async def run_pipeline(state: State, task_uid: UUID, runner_uid: UUID, pipeline: Pipeline) -> None:
    async def __save_task(target: Task):
        # Update the task data JSON.
        target.pipeline_data = json.dumps(pipeline.data)

    # Run each node stored in the pipeline.
    for node_instance in pipeline.nodes:
        # # Skip the COMPLETED node.
        # if node_instance.status() == NodeStatus.DONE:
        #     continue
        # Prepare the node for execution.
        async with update_task(state, task_uid, runner_uid) as (db, task):
            # Mark the node is running.
            node_instance.set_status(NodeStatus.RUNNING)
            # Update the input variable pack from the connections.
            if node_instance in pipeline.links:
                for var_name, (src_node, src_var_name) in pipeline.links[node_instance].items():
                    src_var: Variable = src_node.output.get(src_var_name)
                    await node_instance.input.get(var_name).assign(db, src_var.value())
                # Update the task information.
                await __save_task(task)
            # Save the node information.
            await __save_task(task)
        # Run the node exec code.
        try:
            # Launch the exec status.
            await node_instance.exec()
            # Mark the node status to complete.
            node_instance.set_status(NodeStatus.DONE)
            async with update_task(state, task_uid, runner_uid) as (_, task):
                await __save_task(task)
        except Exception:
            # Mark the node status to error.
            node_instance.set_status(NodeStatus.ERROR)
            async with update_task(state, task_uid, runner_uid) as (_, task):
                await __save_task(task)
            raise


async def run_task(state: State, task_uid: UUID, runner_uid: UUID) -> None:
    # Reset the task running log.
    async with update_task(state, task_uid, runner_uid) as (_, task):
        task.pipeline_log = ""
    # Prepare the environment variables.
    environments: dict = create_environment(runner_uid, task_uid, cpu_count())
    # Add state to environments.
    environments["state"] = state
    try:
        # Prepare the pipeline, load from the task.
        pipeline: Pipeline = get_pipeline(task.pipeline_type, task.pipeline_uid)
        pipeline.load_from_data(json.loads(task.pipeline_data))
        # Before actual launch, clean the work directory, it might exist before.
        clean_environment(environments)
        # Update the pipeline.
        pipeline.set_environments(environments)
        # Launch the pipeline instance.
        await run_pipeline(state, task_uid, runner_uid, pipeline)
    finally:
        # Clean the environments after the task execution.
        clean_environment(environments)


async def lifespan(task_uid: UUID, runner_uid: UUID) -> None:
    # Initialize the project for database access.
    project: Project = start_project()
    # Load all the endpoints from each module referenced in the config file.
    state: State = State(project)
    # Fetch the project.
    await run_task(state, task_uid, runner_uid)
    # Close the project.
    await stop_project(project)


def main() -> None:
    parser = ArgumentParser(
        description='Run a specific task stored in the database',
    )
    parser.add_argument('uid', type=UUID, help='The target task uid')
    parser.add_argument('runner_uid', type=UUID, help='The pipeline runner uid')
    args = parser.parse_args()
    # Run the target mission.
    asyncio.run(lifespan(args.uid, args.runner_uid))


if __name__ == "__main__":
    main()
