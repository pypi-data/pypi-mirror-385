# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest

from flowstrider.rules import collections


class TestRules(unittest.TestCase):
    def setUp(self):
        self.all_rules = []
        for collection in collections.all_collections:
            self.all_rules.extend(collection.node_rules)
            self.all_rules.extend(collection.edge_rules)
            self.all_rules.extend(collection.dfd_rules)
            self.all_rules.extend(collection.graph_rules)

    def test_rules_severity_range(self):
        for rule in self.all_rules:
            assert not rule.severity < 0
