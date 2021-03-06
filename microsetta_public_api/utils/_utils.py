from collections import namedtuple
from flask import jsonify as flask_jsonify
from microsetta_public_api.exceptions import UnknownResource, UnknownID


def jsonify(*args, **kwargs):
    return flask_jsonify(*args, **kwargs)


def stepwise_resource_getter(resources, dataset, keyword, type_):
    try:
        dataset_resource = resources.gets('datasets', dataset)
    except KeyError:
        raise UnknownResource(f"Unknown dataset: '{dataset}'")
    try:
        resource = dataset_resource.gets(keyword)
    except KeyError:
        raise UnknownResource(f"No {type_} data (kw: '{keyword}') for "
                              f"dataset='{dataset}'.")
    return resource


def validate_resource_alt(available, name, type_):
    if name not in available:
        raise UnknownResource(
            f"Requested {type_}: '{name}' "
            f"is unavailable. Available {type_}(s): "
            f"{available}")


def validate_resource(available, name, type_):
    if name not in available:
        return jsonify(error=404,
                       text=f"Requested {type_}: '{name}' "
                            f"is unavailable. Available {type_}(s): "
                            f"{available}"), 404


def check_missing_ids_alt(missing_ids, alpha_metric, type_):
    if len(missing_ids) > 0:
        raise UnknownID(f"Sample ID(s) not found for {type_}: {alpha_metric}. "
                        f"Unknown IDs: {missing_ids}")


def check_missing_ids(missing_ids, alpha_metric, type_):
    if len(missing_ids) > 0:
        return jsonify(missing_ids=missing_ids,
                       error=404, text=f"Sample ID(s) not found for "
                                       f"{type_}: {alpha_metric}"), \
               404


_data_table = namedtuple('DataTable', ['data', 'columns'])


class DataTable(_data_table):
    """A convenience class for constructing jQuery a DataTable in python
    that is JSON serializable.

    A DataTable should have data entries and a list of columns that are in
    the entries.

    Attributes
    ----------

    data : list of DataEntry
        The entries that comprise the DataTable
    columns : list of str
        The names of the columns in the DataTable

    """
    def to_dict(self):
        dict_ = self._asdict()
        dict_['data'] = [entry.to_dict() for entry in self.data]
        return dict_

    @classmethod
    def from_dataframe(cls, df):
        """

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to create a DataTable from.

        Returns
        -------
        DataTable
            A DataTable corresponding to DataFrame

        """
        DataEntry = create_data_entry(df.columns)
        data = df.apply(lambda x: DataEntry(*x), axis=1).values.tolist()
        columns = [{"data": col} for col in df.columns]
        return cls(data, columns)


def create_data_entry(columns):
    _data_entry_class = namedtuple('DataEntry', columns)

    class DataEntry(_data_entry_class):

        def to_dict(self):
            return self._asdict()

    return DataEntry
