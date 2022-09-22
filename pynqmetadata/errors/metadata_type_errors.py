# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

class ExpectedStreamTypeError(Exception):
    """An error that is thrown when we were expecting a stream type but did not get one"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ExpectedManagerTypeError(Exception):
    """An error that is thrown when we were expecting a manager type but did not get one"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class UnexpectedMetadataObjectType(Exception):
    """An error that occurs when we have an unexpected metadata object type"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ExpectedStreamDriverTypeError(Exception):
    """An error that is thrown when we were expecting a stream type that is a driver"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ExpectedSignalType(Exception):
    """An error that is thrown when a signal was expected"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ExpectedClkRstPortType(Exception):
    """An error that is thrown when we were expecting a clk rst port type"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ExpectedScalarPortType(Exception):
    """An error that is thrown when we were expecting a scalar port type"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ExpectedExternalPort(Exception):
    """An error that is thrown when we were expecting an external port"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class InterruptSensitivityWidthMismatch(Exception):
    """An error that is thrown when we are trying to create an interrupt portsignal
    but the sensitivity list does not match the length"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class UnexpectedCoreTypeError(Exception):
    """An error that gets raised when we have a core type that we do not expect"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class UnexpectedPortTypeError(Exception):
    """An error that gets raised when we have a port type that we do not expect"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors
