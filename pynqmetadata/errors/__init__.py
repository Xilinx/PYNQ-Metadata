# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from .construction_errors import (
    AddressMapAlreadyExists,
    AlreadyAChild,
    BitAlreadyExists,
    BlockAlreadyExists,
    ConnectionAlreadyExists,
    CoreAlreadyExists,
    DestinationAlreadyExists,
    ExternalPortAlreadyExists,
    HierarchyAlreadyExists,
    IncompleteHierarchyError,
    InterruptSensitivityListError,
    MergeConflict,
    ParentIsNone,
    PortAlreadyExists,
    PortSignalAlreadyExists,
    ReferenceError,
    RegisterAlreadyExists,
    TooManySignals,
    UnexpectedExternalPort,
    UnexpectedPmdObject,
    WrongPolarityConnection,
)
from .dfx_errors import DFXInterfaceMismatch, DFXLoadbleBDCParameterMissing
from .metadata_type_errors import (
    ExpectedClkRstPortType,
    ExpectedExternalPort,
    ExpectedManagerTypeError,
    ExpectedScalarPortType,
    ExpectedSignalType,
    ExpectedStreamDriverTypeError,
    ExpectedStreamTypeError,
    UnexpectedCoreTypeError,
    UnexpectedMetadataObjectType,
    UnexpectedPortTypeError,
)
from .misc_errors import FeatureNotYetImplemented, ItemNotFound
from .parsing_errors import (
    UnableToParseInputIntoMetadataError,
    XsaParsingCannotFindBlockDesignName,
)
from .query_errors import (
    AddrMapNotFound,
    BitNotFound,
    BlockNotFound,
    ConnectionNotFound,
    CoreNotFound,
    ExternalPortNotFound,
    MetadataObjectNotFound,
    ParameterNotFound,
    PortNotFound,
    PortSignalNotFound,
    RegisterNotFound,
)
from .validation_errors import ImmutableClassModifiedError, NotValidPmdError
