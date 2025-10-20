"""
Main maml object.
"""

import os
import warnings

import yaml
from yaml import SafeDumper

import pandas as pd
from yaml_to_markdown.md_converter import MDConverter

from .read import read_maml
from .parse import MODELS, _assert_version, check_order


def _remove_nones(obj):
    if isinstance(obj, dict):
        return {k: _remove_nones(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_remove_nones(v) for v in obj if v is not None]
    return obj


class MAML:
    """
    Main MAML class
    """

    def __init__(self, data: dict, version):
        """
        Initializaing and checking that the version is supported
        """
        _assert_version(version)
        self.version = version
        self.meta = MODELS[version](**data)

    @classmethod
    def from_file(cls, file_name: str, version: str) -> "MAML":
        """
        Creates a new maml object from file. Checks that order of keys is in the correct order.
        """
        _assert_version(version)
        data = read_maml(file_name)
        if not check_order(data, version):
            warnings.warn(
                "Ordering is not correct. See (https://github.com/asgr/MAML-Format)"
            )
        return cls(data, version)

    def to_dict(self, include_none: bool = True) -> dict:
        """
        Returns dictionary represenation of the model base class.
        """
        raw = self.meta.model_dump(mode="json")
        if not include_none:
            return _remove_nones(raw)
        return raw

    def to_file(self, file_name: str) -> dict:
        """
        Creates a dictionary representation of the base model.
        """
        SafeDumper.add_representer(
            type(None),
            lambda dumper, _: dumper.represent_scalar("tag:yaml.org,2002:null", ""),
        )
        root, ext = os.path.splitext(file_name)
        if ext != ".maml":
            raise ValueError(f"Extension '{ext}' is not a valid maml extension.")
        with open(f"{root}.maml", "w", encoding="utf8") as file:
            yaml.safe_dump(
                self.to_dict(), file, sort_keys=False, default_flow_style=False
            )

    def to_markdown(self, outfile: str) -> None:
        """
        Dumps the maml as a markdown file.
        """
        data = self.to_dict()
        converter = MDConverter()
        with open(outfile, "w", encoding="utf8") as f:
            converter.convert(data, f)

    def __str__(self) -> str:
        data = self.meta.model_dump(mode="json")
        return f"MAML(version = {self.version}, metadata = {data})"


class MAMLBuilder:
    """
    Builder pattern for constructing the MAML format based on whatever version is decided.
    """

    def __init__(self, version: str, defaults: bool = False):
        """
        Initializing and checking version is valid.
        """
        _assert_version(version)
        self.version: str = version
        self._model_cls = MODELS[version]
        if defaults:
            self._data = self._model_cls.with_defaults().model_dump(mode="json")
        elif not defaults:
            self._data: dict = {}
        else:
            raise ValueError("defaults must be True or False")

    def set(self, field: str, value):
        """
        For setting scalar values
        """
        self._data[field] = value
        return self

    def add(self, field: str, value):
        """
        For adding vector values
        """
        try:
            self._data.setdefault(field, []).append(value)
        except AttributeError:
            self._data[field] = [value]
        return self

    def build(self):
        """
        Attempts to build the class for the current version
        """
        return MAML(self._data, self.version)

    def __str__(self) -> str:
        """
        String represenation showing the current state of the dictionary
        """
        return f"Builder(version = {self.version}, current_build = {self._data})"

    def possible_metadata(self) -> list[str]:
        """
        Lists all the values that can be added in this schema.
        """
        all_values = self._model_cls.with_defaults().model_dump(mode="json").keys()
        return list(all_values)

    def fields_from_pandas(self, pandas_dataframe: pd.DataFrame):
        """
        Fills in the fields from a pandas dataframe using the column names and types.
        """
        field_names = list(pandas_dataframe.columns)
        data_types = [str(dtype) for dtype in list(pandas_dataframe.dtypes)]
        for field_name, dtype in zip(field_names, data_types):
            self.add("fields", {"name": field_name, "data_type": dtype})
        return self
