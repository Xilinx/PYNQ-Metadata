# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

class DFXInterfaceMismatch(Exception):
    """ An error that is thrown when a BDC being loaded into a DFX region does not have the same interface """
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors

class DFXLoadbleBDCParameterMissing(Exception):
    """ An error that is thrown when we cannot find the parameter that contains the list of loadble BDCs that we can load """
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors

