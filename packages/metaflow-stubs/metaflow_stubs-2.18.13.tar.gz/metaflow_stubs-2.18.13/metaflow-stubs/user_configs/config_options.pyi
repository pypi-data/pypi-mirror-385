######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13                                                                                #
# Generated on 2025-10-20T17:35:52.563005                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow._vendor.click.types
    import typing

from .._vendor import click as click
from .config_parameters import ConfigValue as ConfigValue
from ..exception import MetaflowException as MetaflowException
from ..exception import MetaflowInternalError as MetaflowInternalError
from ..packaging_sys import MetaflowCodeContent as MetaflowCodeContent
from ..parameters import DeployTimeField as DeployTimeField
from ..parameters import ParameterContext as ParameterContext

class ConvertPath(metaflow._vendor.click.types.Path, metaclass=type):
    def convert(self, value, param, ctx):
        ...
    @staticmethod
    def mark_as_default(value):
        ...
    @staticmethod
    def convert_value(value, is_default):
        ...
    ...

class ConvertDictOrStr(metaflow._vendor.click.types.ParamType, metaclass=type):
    def convert(self, value, param, ctx):
        ...
    @staticmethod
    def convert_value(value, is_default):
        ...
    @staticmethod
    def mark_as_default(value):
        ...
    ...

class MultipleTuple(metaflow._vendor.click.types.Tuple, metaclass=type):
    def split_envvar_value(self, rv):
        ...
    ...

class ConfigInput(object, metaclass=type):
    def __init__(self, req_configs: typing.List[str], defaults: typing.Dict[str, typing.Tuple[typing.Union[str, typing.Dict[typing.Any, typing.Any]], bool]], parsers: typing.Dict[str, typing.Union[str, typing.Callable[[str], typing.Dict[typing.Any, typing.Any]]]]):
        ...
    @staticmethod
    def make_key_name(name: str) -> str:
        ...
    @classmethod
    def set_config_file(cls, config_file: str):
        ...
    @classmethod
    def get_config(cls, config_name: str) -> typing.Optional[typing.Dict[typing.Any, typing.Any]]:
        ...
    def process_configs(self, flow_name: str, param_name: str, param_value: typing.Dict[str, typing.Optional[str]], quiet: bool, datastore: str, click_obj: typing.Optional[typing.Any] = None):
        ...
    def process_configs_click(self, ctx, param, value):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

class LocalFileInput(metaflow._vendor.click.types.Path, metaclass=type):
    def convert(self, value, param, ctx):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

def config_options_with_config_input(cmd):
    ...

def config_options(cmd):
    ...

