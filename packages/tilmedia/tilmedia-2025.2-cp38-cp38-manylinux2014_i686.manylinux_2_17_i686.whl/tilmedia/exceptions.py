"""
TILMedia Exception Classes
"""


class TILMediaError(Exception):
    """
    TILMedia Error without further specification.
    """

    def __init__(self, message, index=None):
        Exception.__init__(self, message)
        self.message = message
        self.index = index

    def __str__(self):
        return self.message


class TILMediaErrorInvalidMedium(TILMediaError):
    """
    An invalid medium name was given. Either the name is invalid in general, the medium could not
    be found, or the license does not allow it. Consult the message provided.
    """


class TILMediaErrorInvalidLicense(TILMediaError):
    """
    The TILMedia license is not available.
    """


class TILMediaErrorInvalidParameter(TILMediaError):
    """
    Invalid parameters were given by the user.
    """


class TILMediaErrorIncompatibleVectorLength(TILMediaError):
    """
    The lengths of the input data vectors are incompatible. E.g. different lengths for pressure
    and enthalpy arrays.
    """


class TILMediaErrorReuseOfSession(TILMediaError):
    """
    The TILMediaSession instance was connect to more than one medium instance.
    """


class TILMediaErrorInconsistentLoggers(TILMediaError):
    """
    The logger of the session is not the same as the logger of the medium
    """
