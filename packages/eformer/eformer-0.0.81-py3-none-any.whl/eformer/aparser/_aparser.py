# Copyright 2025 The EasyDeL/eFormer Author @erfanzar (Erfan Zare Chavoshi).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import dataclasses
import json
import os
import sys
import types
import typing as tp
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, ArgumentTypeError
from copy import copy
from enum import Enum
from inspect import isclass
from pathlib import Path

import yaml

from eformer.paths import ePath

DataClass = tp.NewType("DataClass", tp.Any)
DataClassType = tp.NewType("DataClassType", tp.Any)


def string_to_bool(v: str | bool) -> bool:
    """
    Convert a string to a boolean.

    Accepts various string representations for truthy and falsy values.
    """
    if isinstance(v, bool):
        return v
    lower_v = v.lower()
    if lower_v in ("yes", "true", "t", "y", "1"):
        return True
    elif lower_v in ("no", "false", "f", "n", "0"):
        return False
    raise ArgumentTypeError(
        f"Truthy value expected: got {v} but expected one of yes/no, true/false, t/f, y/n, 1/0 (case insensitive)."
    )


def make_choice_type_function(choices: list[tp.Any]) -> tp.Callable[[str], tp.Any]:
    """
    Create a function that maps a string representation to an actual value from choices.
    """
    str_to_choice = {str(choice): choice for choice in choices}
    return lambda arg: str_to_choice.get(arg, arg)


def Argu(
    *,
    aliases: str | list[str] | None = None,
    help: str | None = None,  # noqa
    default: tp.Any = dataclasses.MISSING,
    default_factory: tp.Callable[[], tp.Any] = dataclasses.MISSING,
    metadata: dict | None = None,
    **kwargs,
) -> dataclasses.Field:
    if metadata is None:
        metadata = {}
    if aliases is not None:
        metadata["aliases"] = aliases
    if help is not None:
        metadata["help"] = help

    return dataclasses.field(metadata=metadata, default=default, default_factory=default_factory, **kwargs)


class DataClassArgumentParser(ArgumentParser):
    """
    A subclass of argparse.ArgumentParser that automatically generates arguments based on dataclass type hints.

    It supports additional argparse features (like sub-groups) and can also load configuration
    from dictionaries, JSON files, or YAML files.
    """

    dataclass_types: tp.Iterable[DataClassType]

    def __init__(
        self,
        dataclass_types: DataClassType | tp.Iterable[DataClassType],
        **kwargs: tp.Any,
    ) -> None:
        if "formatter_class" not in kwargs:
            kwargs["formatter_class"] = ArgumentDefaultsHelpFormatter
        super().__init__(**kwargs)
        if dataclasses.is_dataclass(dataclass_types):
            dataclass_types = [dataclass_types]
        self.dataclass_types = list(dataclass_types)
        for dtype in self.dataclass_types:
            self._add_dataclass_arguments(dtype)

    @staticmethod
    def _parse_dataclass_field(parser: ArgumentParser, field: dataclasses.Field) -> None:
        """
        Convert a dataclass field into a corresponding argparse argument.
        """

        long_options = [f"--{field.name}"]
        if "_" in field.name:
            long_options.append(f"--{field.name.replace('_', '-')}")

        kwargs = field.metadata.copy()

        if isinstance(field.type, str):
            raise RuntimeError(
                f"Unresolved type detected for field '{field.name}'. Ensure that type annotations are fully resolved."
            )

        aliases = kwargs.pop("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]

        origin_type = getattr(field.type, "__origin__", None)
        if origin_type in (tp.Union, getattr(types, "UnionType", None)):
            union_args = field.type.__args__
            if len(union_args) == 2 and type(None) in union_args:
                field.type = next(arg for arg in union_args if arg is not type(None))
                origin_type = getattr(field.type, "__origin__", None)
            else:
                raise ValueError(
                    f"Only tp.Optional types (tp.Union[T, None]) are supported for "
                    f"field '{field.name}', got {field.type}."
                )

        bool_kwargs: dict[str, tp.Any] = {}
        if field.type is bool:
            bool_kwargs = copy(kwargs)
            kwargs["type"] = string_to_bool
            default_val = False if field.default is dataclasses.MISSING else field.default
            kwargs["default"] = default_val
            kwargs["nargs"] = "?"
            kwargs["const"] = True

        elif origin_type is tp.Literal or (isinstance(field.type, type) and issubclass(field.type, Enum)):
            if origin_type is tp.Literal:
                kwargs["choices"] = field.type.__args__
            else:
                kwargs["choices"] = [member.value for member in field.type]
            kwargs["type"] = make_choice_type_function(kwargs["choices"])
            if field.default is not dataclasses.MISSING:
                kwargs["default"] = field.default
            else:
                kwargs["required"] = True

        elif isclass(field.type) and issubclass(field.type, list):
            kwargs["type"] = field.type.__args__[0]
            kwargs["nargs"] = "+"
            if field.default_factory is not dataclasses.MISSING:
                kwargs["default"] = field.default_factory()
            elif field.default is dataclasses.MISSING:
                kwargs["required"] = True
        else:
            kwargs["type"] = field.type
            if field.default is not dataclasses.MISSING:
                kwargs["default"] = field.default
            elif field.default_factory is not dataclasses.MISSING:
                kwargs["default"] = field.default_factory()
            else:
                kwargs["required"] = True

        current_type = kwargs["type"]
        type_args = tp.get_args(current_type)

        if type_args and type(None) in type_args:
            non_none_args = [arg for arg in type_args if arg is not type(None)]

            if len(non_none_args) == 1:
                kwargs["type"] = non_none_args[0]
            elif len(non_none_args) > 1:
                kwargs["type"] = tp.Union[tuple(non_none_args)]  # noqa:UP007

        parser.add_argument(*long_options, *aliases, **kwargs)

        if field.type is bool and field.default is True:
            bool_kwargs["default"] = False
            parser.add_argument(
                f"--no_{field.name}",
                f"--no-{field.name.replace('_', '-')}",
                action="store_false",
                dest=field.name,
                **bool_kwargs,
            )

    def _add_dataclass_arguments(self, dtype: DataClassType) -> None:
        """
        Add arguments for all 'init'-enabled fields of a dataclass.
        """
        group_name = getattr(dtype, "_argument_group_name", None)
        parser = self.add_argument_group(group_name) if group_name else self

        try:
            type_hints: dict[str, type] = tp.get_type_hints(dtype)
        except NameError as e:
            raise RuntimeError(
                f"Type resolution failed for {dtype}. Consider declaring the class in global scope or disabling "
                "PEP 563 (postponed evaluation of annotations)."
            ) from e
        except TypeError as ex:
            if sys.version_info < (3, 10) and "unsupported operand type(s) for |" in str(ex):
                python_version = ".".join(map(str, sys.version_info[:3]))
                raise RuntimeError(
                    f"Type resolution failed for {dtype} on Python {python_version}. "
                    "Please use typing.tp.Union and typing.tp.Optional instead of the | syntax for union types."
                ) from ex
            raise

        for field in dataclasses.fields(dtype):
            if not field.init:
                continue
            field.type = type_hints[field.name]
            self._parse_dataclass_field(parser, field)

    def parse_args_into_dataclasses(
        self,
        args: list[str] | None = None,
        return_remaining_strings: bool = False,
        look_for_args_file: bool = True,
        args_filename: str | None = None,
        args_file_flag: str | None = None,
    ) -> tuple[tp.Any, ...]:
        """
        Parse command-line arguments into instances of the specified dataclass types.

        Optionally, this method can also look for an external ".args" file or a command-line flag that points
        to one, and prepend its content to the command-line arguments.

        Raises:
            ValueError: If there are any unknown arguments (and return_remaining_strings is False).
        """
        if args_file_flag or args_filename or (look_for_args_file and sys.argv):
            args_files: list[Path] = []
            if args_filename:
                args_files.append(Path(args_filename))
            elif look_for_args_file and sys.argv:
                args_files.append(Path(sys.argv[0]).with_suffix(".args"))

            if args_file_flag:
                args_file_parser = ArgumentParser(add_help=False)
                args_file_parser.add_argument(args_file_flag, type=str, action="append")
                cfg, args = args_file_parser.parse_known_args(args=args)
                cmd_args_file_paths = getattr(cfg, args_file_flag.lstrip("-"), None)
                if cmd_args_file_paths:
                    args_files.extend(Path(p) for p in cmd_args_file_paths)

            file_args: list[str] = []
            for args_file in args_files:
                if args_file.exists():
                    file_args.extend(args_file.read_text(encoding="utf-8").split())

            if args is None:
                args = sys.argv[1:]

            args = file_args + args

        namespace, remaining_args = self.parse_known_args(args=args)
        outputs = []
        for dtype in self.dataclass_types:
            field_names = {f.name for f in dataclasses.fields(dtype) if f.init}
            init_args = {k: v for k, v in vars(namespace).items() if k in field_names}

            for key in init_args:
                delattr(namespace, key)
            outputs.append(dtype(**init_args))
        if namespace.__dict__:
            outputs.append(namespace)

        if return_remaining_strings:
            return (*outputs, remaining_args)
        elif remaining_args:
            raise ValueError(f"Some arguments were not used by DataClassArgumentParser: {remaining_args}")
        return tuple(outputs)

    def parse_dict(self, args: dict[str, tp.Any], allow_extra_keys: bool = False) -> tuple[tp.Any, ...]:
        """
        Parse a dictionary of configuration values into dataclass instances.

        Args:
            args: Dictionary containing configuration values.
            allow_extra_keys: If False, raises an exception if unknown keys are present.
        """
        unused_keys = set(args.keys())
        outputs = []
        for dtype in self.dataclass_types:
            field_names = {f.name for f in dataclasses.fields(dtype) if f.init}
            init_args = {k: v for k, v in args.items() if k in field_names}
            unused_keys -= init_args.keys()
            outputs.append(dtype(**init_args))
        if not allow_extra_keys and unused_keys:
            raise ValueError(f"Unused keys in configuration: {sorted(unused_keys)}")
        return tuple(outputs)

    def parse_json_file(
        self,
        json_file: str | os.PathLike,
        allow_extra_keys: bool = False,
    ) -> tuple[tp.Any, ...]:
        """
        Load a JSON file and parse it into dataclass instances.
        """
        data = json.loads(ePath(json_file).read_text())
        return self.parse_dict(data, allow_extra_keys=allow_extra_keys)

    def parse_yaml_file(
        self,
        yaml_file: str | os.PathLike,
        allow_extra_keys: bool = False,
    ) -> tuple[tp.Any, ...]:
        """
        Load a YAML file and parse it into dataclass instances.
        """
        yaml_text = Path(yaml_file).read_text(encoding="utf-8")
        data = yaml.safe_load(yaml_text)
        return self.parse_dict(data, allow_extra_keys=allow_extra_keys)
