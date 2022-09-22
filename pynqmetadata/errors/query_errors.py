# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

## Errors related to querying the Pmd Objects


class MetadataObjectNotFound(Exception):
    """Error for when an object cannot be found in the metadata"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class CoreNotFound(Exception):
    """Raise an exception that a core cannot be found within a Pmd Object"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ParameterNotFound(Exception):
    """Raise an exception that a paramter could not be found"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class PortNotFound(Exception):
    """Raise an exception that a port cannot be found within a Pmd Object"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ExternalPortNotFound(Exception):
    """Raise an exception that an external port cannot be found within a Pmd Object"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class BlockNotFound(Exception):
    """Raise an exception that a block cannot be found within a Pmd Object"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class PortSignalNotFound(Exception):
    """Raise an exception that a portsignal cannot be found within a Pmd Object"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ConnectionNotFound(Exception):
    """Raise an exception that a connection cannot be found within a Pmd Object"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class RegisterNotFound(Exception):
    """Raise an exception that a register cannot be found within a Pmd Object"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class BitNotFound(Exception):
    """Raise an exception that a bit cannot be found within a Pmd Object"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class AddrMapNotFound(Exception):
    """Raise an exception that an address cannot be found within a ManagerPort"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors
