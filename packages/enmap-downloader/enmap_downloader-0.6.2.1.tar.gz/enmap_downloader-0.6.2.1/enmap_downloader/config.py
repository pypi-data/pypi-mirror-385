# SPDX-FileCopyrightText: 2025 GFZ Helmholtz Centre for Geosciences
# SPDX-FileCopyrightText: 2025 Felix Dombrowski
# SPDX-License-Identifier: EUPL-1.2

import json
import os

from datetime import datetime
from json import JSONDecodeError
from typing import List
from pydantic import BaseModel, Field, field_validator, TypeAdapter, ValidationError, HttpUrl

class AoiSettings(BaseModel, extra="forbid"):

    geojson: str = Field(
        title="geojson",
        description="Path to a geojson file or directory containing geojson files",
        default="",
    )

    start_date: str = Field(
        title="Start Date",
        description="Format: YYYY-MM-DDTHH:MM:SS",
        default="",
    )

    end_date: str = Field(
        title="End Date",
        description="Format: YYYY-MM-DDTHH:MM:SS",
        default="",
    )

    @field_validator("geojson")
    def check_geojson(cls, v: str) -> str:
        """
        Validate that the geojson is a valid geojson file or directory.

        Parameters
        ----------
        v : str
            The path to the geojson.

        Returns
        -------
        str
            The validated path to the geojson.

        Raises
        ------
        ValueError
            If the path is not a valid geojson file or directory.
        """

        # Check if the path exists
        if not os.path.exists(v):
            raise ValueError(f"The path {v} does not exist.")

        # If it's a directory, check if it contains .geojson files
        if os.path.isdir(v):
            geojson_files = [f for f in os.listdir(v) if f.endswith(".geojson")]
            if not geojson_files:
                raise ValueError(f"The directory {v} does not contain any GeoJSON files.")

        # If it's a file, ensure it's a valid GeoJSON file
        elif os.path.isfile(v):
            if not v.endswith(".geojson"):
                raise ValueError(f"The file {v} is not a valid GeoJSON file (must end with .geojson).")

            try:
                # Try to load the file to check if it's a valid GeoJSON
                with open(v, 'r') as f:
                    json.load(f)  # If loading succeeds, it's a valid GeoJSON
            except json.JSONDecodeError:
                raise ValueError(f"The file {v} is not a valid GeoJSON file.")

        else:
            raise ValueError(f"The path {v} is neither a valid file nor directory.")

        # Return the validated path
        return v

    @field_validator("start_date")
    def validate_start_date(cls, v: str) -> str:
        """
        Validate that the start time is in a valid format.
        Supported formats:
        - YYYY-MM-DDTHH:MM:SS
        - YYYY-MM
        - Any other common date or time format.

        Parameters
        ----------
        v : str
            The start time string to be validated.

        Returns
        -------
        str
            The validated start time string.

        Raises
        ------
        ValueError
            If the start time is not in one of the accepted formats.
        """

        # If the string is empty, it's considered valid
        if v == "":
            return v

        date_formats = [
            "%Y-%m-%dT%H:%M:%S",  # Format: YYYY-MM-DDTHH:MM:SS
            "%Y-%m",  # Format: YYYY-MM
            "%Y-%m-%d",  # Format: YYYY-MM-DD
            "%Y",  # Format: YYYY (only year)
            "%Y-%m-%dT%H:%M",  # Format: YYYY-MM-DDTHH:MM
        ]

        for date_format in date_formats:
            try:
                # Try to parse the string with each format
                datetime.strptime(v, date_format)
                return v  # Return the valid string if successful
            except ValueError:
                continue  # Try the next format if the current one fails

        # If no format matches, raise a ValueError
        raise ValueError(
            f"The start date {v} is not in a valid format. Supported formats include: YYYY-MM-DDTHH:MM:SS, YYYY-MM, YYYY-MM-DD, YYYY.")

    @field_validator("end_date")
    def validate_end_date(cls, v: str) -> str:
        """
        Validate that the start time is in a valid format.
        Supported formats:
        - YYYY-MM-DDTHH:MM:SS
        - YYYY-MM
        - Any other common date or time format.

        Parameters
        ----------
        v : str
            The start time string to be validated.

        Returns
        -------
        str
            The validated start time string.

        Raises
        ------
        ValueError
            If the start time is not in one of the accepted formats.
        """

        # If the string is empty, it's considered valid
        if v == "":
            return v

        date_formats = [
            "%Y-%m-%dT%H:%M:%S",  # Format: YYYY-MM-DDTHH:MM:SS
            "%Y-%m",  # Format: YYYY-MM
            "%Y-%m-%d",  # Format: YYYY-MM-DD
            "%Y",  # Format: YYYY (only year)
            "%Y-%m-%dT%H:%M",  # Format: YYYY-MM-DDTHH:MM
        ]

        for date_format in date_formats:
            try:
                # Try to parse the string with each format
                datetime.strptime(v, date_format)
                return v  # Return the valid string if successful
            except ValueError:
                continue  # Try the next format if the current one fails

        # If no format matches, raise a ValueError
        raise ValueError(
            f"The start date {v} is not in a valid format. Supported formats include: YYYY-MM-DDTHH:MM:SS, YYYY-MM, YYYY-MM-DD, YYYY.")

class SearchSettings(BaseModel, extra="forbid"):

    collections: List[str] = Field(
        title="Collections",
        description="Define which collections should be used to acquire products",
        default=["ENMAP_HSI_L2A"],
    )

    catalog_link: str = Field(
        title="Catalog Link",
        description="Link of the catalog that should be used to acquire products",
        default="https://geoservice.dlr.de/eoc/ogc/stac/v1/",
    )

    aoi_settings: AoiSettings = Field(title="AoI settings", description="")

    @field_validator("catalog_link")
    def check_stac_catalog_url(cls, v: str) -> str:
        """
        Validate that the URL is a valid HTTP/HTTPS URL.

        Parameters
        ----------
        v : str
            The URL to validate.

        Returns
        -------
        str
            The validated URL.

        Raises
        ------
        ValueError
            If the URL is not a valid HTTP/HTTPS URL.
        """
        ta = TypeAdapter(HttpUrl)
        try:
            ta.validate_strings(v, strict=True)
        except ValidationError as err:
            raise ValueError(f"The catalog_link is invalid:{err}.") from err
        return v

class ResultSettings(BaseModel, extra="forbid"):

    crop_value: str = Field(
        title="Crop Data",
        description="",
        default="",
    )

    results_dir: str = Field(
        title="Result Directory",
        description="",
        default="",
    )

    result_format: str = Field(
        title="Result Format",
        description="",
        default="",
    )

    download_data: bool = Field(
        title="Download Data",
        description="",
        default="",
    )

    download_metadata: bool = Field(
        title="Download Metadata",
        description="",
        default="",
    )

    logging_level: str = Field(
        title="Logging Level",
        description="",
        default="",
    )

    logging_dir: str = Field(
        title="Logging Directory",
        description="",
        default="",
    )

    @field_validator("results_dir")
    def validate_results_dir(cls, v: str) -> str:
        """
        Validate that the directory is not empty and is a valid directory path.

        Parameters
        ----------
        v : str
            The directory path to be validated.

        Returns
        -------
        str
            The validated directory path.
        Raises
        ------
        ValueError
            If the folder path is an empty string.
        """
        if v == "":
            raise ValueError("Empty string is not allowed.")

        return v

    @field_validator("logging_dir")
    def validate_logging_dir(cls, v: str) -> str:
        """
        Validate that the directory is not empty and is a valid directory path.

        Parameters
        ----------
        v : str
            The directory path to be validated.

        Returns
        -------
        str
            The validated directory path.
        Raises
        ------
        ValueError
            If the folder path is an empty string.
        """
        if v == "":
            raise ValueError("Empty string is not allowed.")
        return v

    @field_validator("result_format")
    def validate_result_format(cls, v: str) -> str:
        """
        Validate that the result format is 'npy'.

        Parameters
        ----------
        v : str
            The result format to be validated.

        Returns
        -------
        str
            The validated result format.

        Raises
        ------
        ValueError
            If the result format is not 'npy'.
        """
        # Ensure the result format is not empty
        if not v:
            raise ValueError("The result format cannot be empty.")

        # Check if the result format is 'npy'
        if v != "npy" and v != "tif":
            raise ValueError(f"The result format must be 'npy' or 'tif', but got '{v}'.")

        return v

    @field_validator("download_data", "download_metadata")
    def validate_bool(cls, v: bool) -> bool:
        """
        Validate that the value is a boolean.

        Parameters
        ----------
        v : bool
            The boolean value to be validated.

        Returns
        -------
        bool
            The validated boolean value.

        Raises
        ------
        ValueError
            If the value is not a boolean.
        """
        if not isinstance(v, bool):
            raise ValueError(f"The value must be a boolean, but got {type(v).__name__}.")
        return v

    @field_validator("crop_value")
    def validate_crop_value(cls, v: str) -> str:
        """
        Validate that the value is a one of the expected parameters.

        Parameters
        ----------
        v : str
            The str to be validated.

        Returns
        -------
        str
            The validated str.

        Raises
        ------
        ValueError
            If the value is not a validated str.
        """

        accepted_values = ["default", "bbox", "precise"]
        if v not in accepted_values:
            raise ValueError(f"crop_value must be one of {accepted_values}, but got '{v}'.")
        return v

    @field_validator("logging_level")
    def checkLogLevel(cls, v: str) -> str:  # noqa: N805
        """
        Validate that the logging level is correct.

        The logging level must be one of the following:
        - "DEBUG"
        - "INFO"
        - "WARN"
        - "ERROR"

        Parameters
        ----------
        v : str
            The logging level to validate.

        Returns
        -------
        str
            The validated logging level.

        Raises
        ------
        ValueError
            If the logging level is not one of the allowed values.
        """
        if v not in ["DEBUG", "INFO", "WARN", "ERROR"]:
            raise ValueError("Logging level, it should be one of: DEBUG, INFO, WARN, or ERROR.")
        return v

class Config(BaseModel):
    """Template for the EnMap configuration file."""

    search_settings : SearchSettings = Field(title="Search Settings", description="")
    result_settings : ResultSettings = Field(title="Result Settings", description="")

def loadConfiguration(*, path: str) -> dict:
    """
    Load configuration json file.

    Parameters
    ----------
    path : str
        Path to the configuration json file.

    Returns
    -------
    : dict
        A dictionary containing configurations.

    Raises
    ------
    OSError
        Failed to load the configuration json file.
    """
    try:
        with open(path) as config_fp:
            config = json.load(config_fp)
            config = Config(**config).model_dump(by_alias=True)
    except JSONDecodeError as e:
        raise OSError(f"Failed to load the configuration json file => {e}") from e
    return config
