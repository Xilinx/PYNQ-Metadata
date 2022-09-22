# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

class UnableToParseInputIntoMetadataError(Exception):
    """ Raise an exception when we cannot parse the input into any sort of metadata """
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors

class XsaParsingCannotFindBlockDesignName(Exception):
    """ Raise an exception when we cannot find the name of the block design when parsing the XSA """
    def __init__(self, message=None, errors=None):
        super().__init__(message)
        self.errors = errors

