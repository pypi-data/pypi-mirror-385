# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

from flowstrider.rules import attributes_dict, collections

accepted_types = [
    "Node: Interactor",
    "Node: DataStore",
    "Node: Process",
    "Edge: Dataflow",
    "TrustBoundary",
    "DataflowDiagram",
]

correct_rule_set_tags = []
for rule_set in collections.all_collections:
    correct_rule_set_tags.extend(rule_set.tags)


def test_attributes_correct_types():
    for key, value in attributes_dict.attributes.items():
        for type in value.applicable_entities:
            assert type in accepted_types

        assert len(value.corresponding_rule_sets) > 0
        for rule_set in value.corresponding_rule_sets:
            assert rule_set in correct_rule_set_tags
