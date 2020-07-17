# Value errors
class UnknownID(ValueError):

    def __init__(self, *args, missing_ids=None, type_=None, value=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.missing_ids = missing_ids
        self.type_ = type_
        self.value = value


class UnknownMetric(ValueError):
    pass


# Key errors
class DisjointError(KeyError):
    pass


# Type errors
class ConfigurationError(TypeError):
    pass
