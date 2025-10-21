#
# Copyright 2025 Tabs Data Inc.
#

import os
import tempfile
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Annotated, Any, List

import polars as pl
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool

from tabsdata_agent._core.constants import registry_status_content
from tabsdata_agent._core.utils import get_client


class ReadWriteMode(Enum):
    READ = auto()
    READWRITE = auto()


class TabsdataToolsFactory:
    def __init__(self, mode: ReadWriteMode = ReadWriteMode.READWRITE):
        self.mode = mode

    def get_tools(self) -> List[BaseTool]:
        read_tools = [
            collections_list,
            collection_read,
            functions_list,
            function_read,
            tables_list,
            table_read,
            table_sample,
            table_schema,
            data_versions_list,
            execution_plan_read,
            status_registry,
            convert_timestamp,
        ]

        write_tools = [
            function_execute,
            function_register,
            function_update,
            execution_plan_cancel,
            execution_plan_recover,
        ]

        if self.mode == ReadWriteMode.READ:
            return read_tools
        elif self.mode == ReadWriteMode.READWRITE:
            return read_tools + write_tools
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")


# Tools definitions
# Note that we cannot return complex objects like Collection,
# Function, Table, etc. directly to the LLM, as they may not
# be serializable. Instead, we return their string representations
# or specific attributes that are useful for the user.


# Collection
@tool
def collections_list(
    config: RunnableConfig,
    filter: Annotated[List[str] | str | None, "Filter to apply."] = None,
) -> dict[str, Any]:
    """List all collections in the TabsData instance."""
    collections = get_client(config).list_collections(filter=filter)
    collections = {collection.name: collection._data for collection in collections}
    return {"collections": collections}


@tool
def collection_read(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
) -> dict[str, Any]:
    """Get metadata for a collection."""
    collection = get_client(config).get_collection(collection_name)
    return collection._data


# Function
@tool
def functions_list(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    filter: Annotated[List[str] | str | None, "Filter to apply."] = None,
) -> dict[str, Any]:
    """List all functions in a collection."""
    functions = get_client(config).list_functions(collection_name, filter=filter)
    functions = {function.name: function._data for function in functions}
    return {"functions": functions}


@tool
def function_read(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    function_name: Annotated[str, "Name of the function."],
) -> dict[str, Any]:
    """Get metadata for a function in a collection."""
    function = get_client(config).get_function(collection_name, function_name)
    return function._data


@tool
def function_execute(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    function_name: Annotated[str, "Name of the function."],
) -> dict[str, Any]:
    """Execute a function and return the execution plan metadata."""
    function = get_client(config).get_function(collection_name, function_name)
    response = function.trigger()
    return response._data


@tool
def function_register(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    function_name: Annotated[str, "Name for the new function."],
    function_description: Annotated[
        str | None, "Description of the function (optional)."
    ],
    function_content: Annotated[str, "Python code for the function."],
) -> dict[str, Any]:
    """Register a new function in a collection."""
    try:
        compile(function_content, "<string>", "exec")
    except SyntaxError as e:
        raise RuntimeError(f"Error registering function: {e}")
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "function.py")
        with open(file_path, "w") as f:
            f.write(function_content)
        try:
            function = get_client(config).register_function(
                collection_name=collection_name,
                description=function_description or "",
                function_path=f"{file_path}::{function_name}",
            )
            return function._data
        except Exception as e:
            raise RuntimeError(f"Error registering function: {e}")


@tool
def function_update(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    current_function_name: Annotated[str, "Current function name."],
    new_function_name: Annotated[str, "New function name."],
    function_description: Annotated[str | None, "New description (optional)."],
    function_content: Annotated[str, "Updated Python code."],
) -> dict[str, Any]:
    """Update an existing function in a collection."""
    try:
        compile(function_content, "<string>", "exec")
    except SyntaxError as e:
        raise RuntimeError(f"Error updating function: {e}")
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "function.py")
        with open(file_path, "w") as f:
            f.write(function_content)
        try:
            kwargs = {
                "collection_name": collection_name,
                "function_name": current_function_name,
                "function_path": f"{file_path}::{new_function_name}",
            }
            if function_description is not None:
                kwargs["description"] = function_description
            function = get_client(config).update_function(**kwargs)
            return function._data
        except Exception as e:
            raise RuntimeError(f"Error updating function: {e}")


# Table
@tool
def tables_list(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    filter: Annotated[List[str] | str | None, "Filter to apply."] = None,
) -> dict[str, Any]:
    """List all tables in a collection."""
    tables = get_client(config).list_tables(collection_name, filter=filter)
    tables = {table.name: table._data for table in tables}
    return {"tables": tables}


@tool
def table_read(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    table_name: Annotated[str, "Name of the table."],
) -> dict[str, Any]:
    """Get metadata for a table in a collection."""
    collection = get_client(config).get_collection(collection_name)
    table = collection.get_table(table_name)
    return table._data


@tool
def table_sample(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    table_name: Annotated[str, "Name of the table."],
) -> pl.DataFrame:
    """Get a sample of rows from a table."""
    collection = get_client(config).get_collection(collection_name)
    table = collection.get_table(table_name)
    sample = table.sample()
    return sample


@tool
def table_schema(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    table_name: Annotated[str, "Name of the table."],
) -> list[dict]:
    """Get the schema of a table."""
    collection = get_client(config).get_collection(collection_name)
    table = collection.get_table(table_name)
    schema = table.get_schema()
    return schema


# Data version
@tool
def data_versions_list(
    config: RunnableConfig,
    collection_name: Annotated[str, "Name of the collection."],
    table_name: Annotated[str, "Name of the table."],
    filter: Annotated[List[str] | str | None, "Filter to apply."] = None,
) -> dict[str, Any]:
    """List all data versions for a table."""
    collection = get_client(config).get_collection(collection_name)
    table = collection.get_table(table_name)
    data_versions = table.list_dataversions(filter=filter)
    data_versions = {
        data_version.id: data_version._data for data_version in data_versions
    }
    return {"data_versions": data_versions}


# Execution plan
@tool
def execution_plan_read(
    config: RunnableConfig,
    execution_plan_id: Annotated[str, "Execution plan ID."],
) -> dict[str, Any]:
    """Get details for an execution plan by ID."""
    execution_plan = get_client(config).get_execution(execution_plan_id)
    return execution_plan._data


@tool
def execution_plan_cancel(
    config: RunnableConfig,
    execution_plan_id: Annotated[str, "Execution plan ID."],
) -> str:
    """Cancel an execution plan by ID."""
    execution_plan = get_client(config).get_execution(execution_plan_id)
    execution_plan.cancel()
    return (
        f"The execution plan with ID {execution_plan_id} has been set for cancellation."
    )


@tool
def execution_plan_recover(
    config: RunnableConfig,
    execution_plan_id: Annotated[str, "Execution plan ID."],
) -> str:
    """Recover an execution plan by ID."""
    execution_plan = get_client(config).get_execution(execution_plan_id)
    execution_plan.recover()
    return (
        f"The execution plan with ID {execution_plan_id} has been set for recovering."
    )


# Utils
@tool
def status_registry() -> dict[str, Any]:
    """Get the status registry to convert status codes to actual status."""
    return registry_status_content


@tool
def convert_timestamp(
    epoch_millis: Annotated[int, "Epoch time in milliseconds."],
) -> str:
    """Convert epoch milliseconds to a UTC timestamp string (ISO 8601 format)."""
    return (
        datetime.fromtimestamp(epoch_millis / 1000, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        )[:-3]
        + " Z"
    )
