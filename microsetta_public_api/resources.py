import os
import pandas as pd
from copy import deepcopy
from microsetta_public_api.exceptions import ConfigurationError
from qiime2 import Artifact
from q2_types.sample_data import AlphaDiversity, SampleData
from typing import Dict, Any, NewType

_AlphaSampleData = NewType('SampleData[AlphaDiversity]', Any)


def _str_str_to_str_alpha(dict_of_qza_paths, resource_name):
    _validate_dict_of_qza_paths(dict_of_qza_paths,
                                resource_name)
    new_resource = _replace_paths_with_qza(dict_of_qza_paths,
                                           resource_name,
                                           SampleData[AlphaDiversity])
    return new_resource


def _parse_q2_data(filepath, semantic_type):
    try:
        data = Artifact.load(filepath)
    except ValueError as e:
        raise ConfigurationError(*e.args)

    if data.type != semantic_type:
        raise ConfigurationError(f"Expected QZA '{filepath}' to have type "
                                 f"'{semantic_type}'. "
                                 f"Received '{data.type}'.")

    return data.view(pd.Series)


def _validate_dict_of_qza_paths(dict_of_qza_paths, name):
    if not isinstance(dict_of_qza_paths, dict):
        raise ValueError(f"Expected '{name}' field to contain a dict. "
                         f"Got {type(dict_of_qza_paths).__name__}")
    for key, value in dict_of_qza_paths.items():
        value_is_existing_qza_path = isinstance(value, str) and \
                                     (value[-4:] == '.qza') and \
                                     os.path.exists(value)

        if not value_is_existing_qza_path:
            raise ValueError(f'Expected existing path with .qza '
                             f'extension. Got: {value}')


def _replace_paths_with_qza(dict_of_qza_paths, name, semantic_type):
    new_resource = {name: dict()}
    for key, value in dict_of_qza_paths.items():
        new_resource[name][key] = _parse_q2_data(value,
                                                 semantic_type)
    return new_resource


class ResourceManager(dict):

    dict_of_qza_resources = {'alpha_resources': SampleData[AlphaDiversity]}

    resource_formats = {
        'alpha_resources': ({
            'from': Dict[str, str],
            'to': Dict[str, _AlphaSampleData],
        }),
    }

    transformers = {
        (Dict[str, str],
         Dict[str, _AlphaSampleData]): _str_str_to_str_alpha,
    }

    def update(self, *args, **kwargs):
        """
        Updates the managers resources.

        Parameters
        ----------
        other : optional dict
            Resource identifier to resource mapping. 'alpha_resources' is
            reserved for a dictionary. The values in 'alpha_resources' must be
            existing file paths with a .qza extension, they will be read
            into a python QZA.
        kwargs : dict
            kwargs for dict.update. Similar to `other`, but can be passed as
            keywords.

        Returns
        -------
        NoneType

        Examples
        --------
        >>> resources = ResourceManager(alpha_resources={
        ...     {'faith_pd': '/path/to/some.qza',
        ...      'chao1': '/another/path/to/a.qza',
        ...     }}, some_other_resource='here is a string resource')


        """
        if len(args) == 1 and isinstance(args[0], dict):
            other = args[0]
        elif len(args) == 0:
            other = dict()
        else:
            raise TypeError(f'update expected at most 1 positional argument '
                            f'that is a dict. Got {args}')

        for resource_name, type_ in self.dict_of_qza_resources.items():
            if resource_name in other:
                new_resource = _str_str_to_str_alpha(other[resource_name],
                                                     resource_name)
                other.update(new_resource)
            if resource_name in kwargs:
                new_resource = _str_str_to_str_alpha(kwargs[resource_name],
                                                     resource_name)
                kwargs.update(new_resource)

        return super().update(other, **kwargs)


resources = ResourceManager()
