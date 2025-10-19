import json
import io
import pandas as pd
import numpy as np
from typing import Union
from hed.models import Sidecar
from hed.schema import HedSchema, HedSchemaGroup
from pynwb.core import VectorData
from ndx_events import MeaningsTable, EventsTable, TimestampVectorData, DurationVectorData, CategoricalVectorData
from ndx_hed import HedTags, HedValueVector


def extract_definitions(sidecar_data: dict, hed_schema: Union[HedSchema, HedSchemaGroup]) -> tuple:
    """
    Extracts definitions from a HED sidecar JSON data using the provided HED schema.

    Args:
        sidecar_data (dict): A dictionary representing the loaded HED Sidecar JSON data.
        hed_schema (HedSchema or HedSchemaGroup): The HED schema object for validation and processing.

    Returns:
        tuple: A tuple containing:
            - DefinitionDict: A dictionary of definitions extracted from the sidecar.
            - list: A list of validation issues found during extraction.
    """
    sidecar = Sidecar(io.StringIO(json.dumps(sidecar_data)))
    definitions = sidecar.get_def_dict(hed_schema)
    issues = sidecar._extract_definition_issues
    return definitions, issues


def extract_meanings(sidecar_data: dict) -> dict:
    """
    Converts a HED sidecar JSON data to a meanings dictionary.

    Args:
        sidecar_data (dict): A dictionary representing the loaded HED Sidecar JSON data.

    Returns:
        dict: A meanings dictionary with keys "categorical" and "value"
              - "categorical": dict mapping column names to a dict of {category: (description, HED string)}
              - "value": dict mapping column names to HED strings
    """

    meanings = {"categorical": {}, "value": {}}

    for column_name, column_info in sidecar_data.items():
        if "Levels" in column_info or ("HED" in column_info and isinstance(column_info.get("HED", None), dict)):
            meanings["categorical"][column_name] = get_categorical_meanings(column_name, column_info)
        elif "HED" in column_info:
            meanings["value"][column_name] = column_info["HED"]
    return meanings


def get_categorical_meanings(column_name: str, column_info: dict) -> "MeaningsTable":
    """
    Converts a categorical column info dict to a MeaningsTable.

    Args:
        column_name (str): The name of the column.
        column_info (dict): The column info dictionary from the sidecar.

    Returns:
        MeaningsTable: The constructed MeaningsTable object.
    """
    description = column_info.get("Description", f"Meanings for {column_name}")
    meanings_tab = MeaningsTable(name=column_name + "_meanings", description=description)
    levels = column_info.get("Levels", {})  # Default to empty dict
    hed_info = column_info.get("HED", None)
    hed_data = []

    for value in list(levels.keys()):
        meanings_tab.add_row(value=value, meaning=levels.get(value, f"Description for {value}"))
        if hed_info is not None:
            hed_data.append(hed_info.get(value, "n/a"))
    if hed_info is not None:
        meanings_tab.add_column(
            name="HED", description=f"HED tags for {column_name} categories", col_cls=HedTags, data=hed_data
        )
    return meanings_tab


def get_events_table(name: str, description: str, df: pd.DataFrame, meanings: dict) -> "EventsTable":
    """
    Converts a pandas DataFrame and meanings dictionary to an EventsTable.

    Parameters:
        name (str): The name of the EventsTable.
        description (str): The description of the EventsTable.
        df (pd.DataFrame): The DataFrame containing event data.
        meanings (dict): The meanings dictionary with keys "categorical" and "value".

    Returns:
        EventsTable: The constructed EventsTable object.
    """

    columns = []

    # Replace "n/a" with NaN in onset and duration columns directly in DataFrame
    if "onset" in df.columns:
        df["onset"] = df["onset"].replace(["n/a", "N/A", "na", "NA"], np.nan).infer_objects(copy=False)
    if "duration" in df.columns:
        df["duration"] = df["duration"].replace(["n/a", "N/A", "na", "NA"], np.nan).infer_objects(copy=False)

    # Add columns from the DataFrame
    for col_name in df.columns:
        col_data = df[col_name].tolist()
        if col_name == "onset":
            columns.append(TimestampVectorData(name="timestamp", description="Onset times of events", data=col_data))
        elif col_name == "duration":
            columns.append(DurationVectorData(name="duration", description="Duration of events", data=col_data))
        elif col_name in meanings["categorical"]:
            columns.append(
                CategoricalVectorData(
                    name=col_name,
                    description=f"Categorical column {col_name}",
                    data=col_data,
                    meanings=meanings["categorical"][col_name],
                )
            )
        elif col_name in meanings["value"]:
            columns.append(
                HedValueVector(
                    name=col_name,
                    description=f"Value column {col_name}",
                    data=col_data,
                    hed=meanings["value"][col_name],
                )
            )
        elif col_name == "HED":
            columns.append(HedTags(name="HED", description="HED tags for events", data=col_data))
        else:
            columns.append(VectorData(name=col_name, description=f"Value column {col_name}", data=col_data))
    events_tab = EventsTable(name=name, description=description, columns=columns)
    return events_tab


def get_bids_events(events_table: EventsTable) -> tuple:
    """
    Converts an EventsTable back to BIDS format (DataFrame and JSON sidecar).

    Parameters:
        events_table (EventsTable): The EventsTable to convert.

    Returns:
        tuple: A tuple containing:
            - pd.DataFrame: The events data with proper column names (onset, duration, etc.)
            - dict: The JSON sidecar data with column metadata, levels, and HED annotations
    """

    # Get DataFrame from EventsTable
    df = events_table.to_dataframe()

    # Initialize JSON sidecar structure
    json_data = {}

    # Process each column to build JSON metadata
    for col_name in events_table.colnames:
        column = events_table[col_name]
        column_info = {}

        # Add description if available
        if hasattr(column, "description") and column.description:
            column_info["Description"] = column.description

        # Handle different column types
        if isinstance(column, TimestampVectorData):
            # Rename timestamp back to onset in DataFrame
            if "timestamp" in df.columns:
                df = df.rename(columns={"timestamp": "onset"})
            # TimestampVectorData doesn't typically have HED metadata in BIDS

        elif isinstance(column, DurationVectorData):
            # Duration column - no special HED metadata typically
            # TODO: Might need to extend this to include a HED field if needed.
            pass

        elif isinstance(column, CategoricalVectorData):
            # Extract levels and HED from MeaningsTable
            if hasattr(column, "meanings") and column.meanings is not None:
                meanings_table = column.meanings
                meanings_df = meanings_table.to_dataframe()

                # Build Levels dictionary
                levels = {}
                hed_dict = {}

                for _, row in meanings_df.iterrows():
                    value = row["value"]
                    meaning = row.get("meaning", "")
                    levels[value] = meaning

                    # Check for HED column
                    if "HED" in row and pd.notna(row["HED"]) and row["HED"] != "":
                        hed_dict[value] = row["HED"]

                if levels:
                    column_info["Levels"] = levels
                if hed_dict:
                    column_info["HED"] = hed_dict

        elif isinstance(column, HedValueVector) and column.hed != "" and column.hed != "n/a":
            column_info["HED"] = column.hed

        elif isinstance(column, HedTags):
            # The HED tags are stored as data in the column itself - no additional metadata
            pass

        # Add column info to JSON if it has any metadata
        if column_info:
            json_data[col_name] = column_info

    return df, json_data
