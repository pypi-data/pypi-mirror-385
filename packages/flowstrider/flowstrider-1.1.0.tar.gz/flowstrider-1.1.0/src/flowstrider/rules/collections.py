# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

from .builtin.bsi_rules import BSIRuleCollection
from .builtin.linddun_rules import LINDDUNRuleCollection
from .builtin.stride_rules import GenericSTRIDERuleCollection

all_collections = [
    BSIRuleCollection,
    GenericSTRIDERuleCollection,
    LINDDUNRuleCollection,
]

__all__ = ["all_collections"]
