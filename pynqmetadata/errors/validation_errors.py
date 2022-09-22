# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

class NotValidPmdError(Exception):
    """ Raise an exception when we do not have valid metadata """
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors

class ImmutableClassModifiedError(Exception):
    """ Raise an exception when we have edited an immutable class """
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors

