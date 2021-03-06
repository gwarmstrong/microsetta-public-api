# Value errors
class UnknownID(ValueError):
    pass


class UnknownMetric(ValueError):
    pass


class UnknownLevel(ValueError):
    pass


class UnknownResource(ValueError):
    pass


class InvalidParameter(ValueError):
    pass


class UnknownCategory(ValueError):
    pass


class IncompatibleOptions(ValueError):
    pass


# Key errors
class DisjointError(KeyError):
    pass


class SubsetError(KeyError):
    pass


# Type errors
class ConfigurationError(TypeError):
    pass
