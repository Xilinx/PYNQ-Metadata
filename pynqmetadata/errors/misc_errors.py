# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

class FeatureNotYetImplemented(Exception):
    """ Raise an exception when we are trying to use a feature that is not yet implemented """
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


class ItemNotFound(Exception):
    """ An item was not found when searching the Pmd """
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors


