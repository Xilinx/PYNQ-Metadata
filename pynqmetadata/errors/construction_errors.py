# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

class PortAlreadyExists(Exception):
    """Raise an exception that a port already exists in a core or Pmd object"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class PortNotFound(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class MergeConflict(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class CoreAlreadyExists(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class HierarchyAlreadyExists(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ExternalPortAlreadyExists(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class BlockAlreadyExists(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ConnectionAlreadyExists(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class PortSignalAlreadyExists(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class RegisterAlreadyExists(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class BitAlreadyExists(Exception):
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class AlreadyAChild(Exception):
    """Error for when we are trying to add a child to an object where it is already a child"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ReferenceError(Exception):
    """Error for when the reference of a MetadataObject is unexpected"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class TooManySignals(Exception):
    """Error when too many signals are attempted to be assigned to a port"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class UnexpectedExternalPort(Exception):
    """Error when we a port has been marked as external but it is not external from the root"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class WrongPolarityConnection(Exception):
    """Error when two ports are connected with a polarity mismatch"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class DestinationAlreadyExists(Exception):
    """Error when a destination has been assigned to a portmap twice"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class UnexpectedPmdObject(Exception):
    """Error that occurs when we expected a different PmdObject to be added"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class InterruptSensitivityListError(Exception):
    """Error for when we have an interrupt but the wrong number of sensitivity elements is specified"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class IncompleteHierarchyError(Exception):
    """An error when we have not got a fully connected up module"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class AddressMapAlreadyExists(Exception):
    """Error for when the Address map already exists for a manager port"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ParentIsNone(Exception):
    """Error when the parent of an object is None when we are expecting something to be there"""

    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors
