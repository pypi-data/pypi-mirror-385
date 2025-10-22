# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

import math
import os
import pathlib
import typing
import unittest
from unittest.mock import patch

from flowstrider import rules, storage
from flowstrider.models.common_models import Cluster, Edge, Node
from flowstrider.models.dataflowdiagram import DataflowDiagram
from flowstrider.models.threat import Threat

__location__ = os.path.dirname(__file__)


# Test Rules:
class TestNodeRule1(rules.common_rules.NodeRule):
    severity = 1.0
    short_description = ""

    @classmethod
    def _test(cls, node, dfd):
        return True


class TestNodeRule2(rules.common_rules.NodeRule):
    severity = 2.5
    short_description = ""

    @classmethod
    def _test(cls, node, dfd):
        return True


class TestEdgeRule1(rules.common_rules.EdgeRule):
    severity = 1.0
    short_description = ""

    @classmethod
    def _test(cls, node, dfd):
        return True


class TestEdgeRule2(rules.common_rules.EdgeRule):
    severity = 2.5
    short_description = ""

    @classmethod
    def _test(cls, node, dfd):
        return True


class TestRuleCollection(rules.common_rules.DataflowDiagramRuleCollection):
    tags = {"test_rules"}

    node_rules = [
        TestNodeRule1,
        TestNodeRule2,
    ]
    edge_rules = [
        TestEdgeRule1,
        TestEdgeRule2,
    ]


class TestElicitSeverityOrder(unittest.TestCase):
    def modified_elicit(cls, dfd: DataflowDiagram) -> typing.List[Threat]:
        with patch(
            "flowstrider.tool.locale.getlocale",
            return_value="en",
        ):
            with patch(
                "flowstrider.rules.collections.all_collections", [TestRuleCollection]
            ):
                threats = rules.elicit(dfd)
                return threats

    def test_elicit_severity_order(cls):
        example_2_path: pathlib.Path = (
            pathlib.Path(__location__) / "../resources/dfd_example-2.json"
        )

        with open(example_2_path) as dfd_file:
            serialized_dfd = dfd_file.read()

        dfd = storage.deserialize_dfd(serialized_dfd)
        dfd.tags = ["test_rules"]

        threats = cls.modified_elicit(dfd)

        # All threats should be in order of severity (descending) and in order of source
        # ...for same severity
        for i in range(len(threats) - 1):
            assert threats[i].severity >= threats[i + 1].severity
            if threats[i].severity == threats[i + 1].severity:
                assert threats[i].source <= threats[i + 1].source

        # Test severity for two specific threats
        found = [False, False]
        for threat in threats:
            if threat.uid() == "TestNodeRule2@Node3":
                found[0] = True
                assert threat.severity == 2.5

            if threat.uid() == "TestNodeRule1@Node4":
                found[1] = True
                assert threat.severity == 1.0

        assert all(found)

    def test_elicit_severity_multiplier_nodes(cls):
        # Normal severity
        node1 = Node(id="n1", severity_multiplier=1.0, name="ProcessA")
        node2 = Node(id="n2", severity_multiplier=0.0, name="ProcessB")
        # Negative severity should be clamped to 0.0 with a warning that the
        # ...severity_multiplier can't be negative
        node3 = Node(id="n3", severity_multiplier=-1.5, name="ProcessC")
        node4 = Node(id="n4", severity_multiplier=7.8, name="ProcessD")
        node5 = Node(id="n5", severity_multiplier=-100.0, name="ProcessE")
        node6 = Node(id="n6", severity_multiplier=1000.0, name="ProcessF")

        edge1 = Edge(id="e1", source_id=node1.id, sink_id=node2.id)

        # Diagram setup
        dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": node1,
                "node2": node2,
                "node3": node3,
                "node4": node4,
                "node5": node5,
                "node6": node6,
            },
            edges={
                "edge1": edge1,
            },
            clusters={},
            tags={"test_rules"},
        )

        threats = cls.modified_elicit(dfd)

        # Test severity for the threats and assert that all were found
        found = [False for i in range(12)]
        for threat in threats:
            print("> " + threat.uid())
            match threat.uid():
                case "TestNodeRule1@n1":
                    found[0] = True
                    assert math.isclose(threat.severity, 1.0)
                    assert not math.isclose(threat.severity, 1.1)
                case "TestNodeRule2@n1":
                    found[1] = True
                    assert math.isclose(threat.severity, 2.5)
                case "TestNodeRule1@n2":
                    found[2] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestNodeRule2@n2":
                    found[3] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestNodeRule1@n3":
                    found[4] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestNodeRule2@n3":
                    found[5] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestNodeRule1@n4":
                    found[6] = True
                    assert math.isclose(threat.severity, 7.8)
                case "TestNodeRule2@n4":
                    found[7] = True
                    assert math.isclose(threat.severity, 19.5)
                case "TestNodeRule1@n5":
                    found[8] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestNodeRule2@n5":
                    found[9] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestNodeRule1@n6":
                    found[10] = True
                    assert math.isclose(threat.severity, 1000.0)
                case "TestNodeRule2@n6":
                    found[11] = True
                    assert math.isclose(threat.severity, 2500.0)

        assert all(found)

    def test_elicit_severity_multiplier_clusters(cls):
        # Node not in clusters should be unaffected and keep its multiplier
        node1 = Node(id="n1", severity_multiplier=1.2, name="ProcessA")
        # Node in cluster with multiplier 1.0 should keep its multiplier
        node2 = Node(id="n2", severity_multiplier=1.2, name="ProcessB")
        # Node in cluster with small multiplier should lessen its multiplier
        node3 = Node(id="n3", severity_multiplier=1.4, name="ProcessC")
        # Node in cluster with big multiplier should increase its multiplier
        node4 = Node(id="n4", severity_multiplier=1.2, name="ProcessD")
        # Nodes in two clusters should be affected by both multipliers
        node5 = Node(id="n5", severity_multiplier=1.0, name="ProcessE")
        node6 = Node(id="n6", severity_multiplier=1.5, name="ProcessF")
        node7 = Node(id="n7", severity_multiplier=1.8, name="ProcessG")
        # Node in cluster with multiplier 0.0 should become 0.0
        node8 = Node(id="n8", severity_multiplier=1.2, name="ProcessH")
        # Node in cluster with negative multiplier should be clamped to 0.0 + warning
        node9 = Node(id="n9", severity_multiplier=1.2, name="ProcessI")

        edge1 = Edge(id="e1", source_id=node1.id, sink_id=node2.id, name="Edge1")

        cluster1 = Cluster(
            id="c1", node_ids=[node2.id], severity_multiplier=1.0, name="ClusterA"
        )
        cluster2 = Cluster(
            id="c2",
            node_ids=[node3.id, node6.id],
            severity_multiplier=0.1,
            name="ClusterB",
        )
        cluster3 = Cluster(
            id="c3",
            node_ids=[node4.id, node5.id, node7.id],
            severity_multiplier=2.0,
            name="ClusterC",
        )
        cluster4 = Cluster(
            id="c4",
            node_ids=[node5.id, node7.id],
            severity_multiplier=2.0,
            name="ClusterD",
        )
        cluster5 = Cluster(
            id="c5", node_ids=[node6.id], severity_multiplier=0.8, name="ClusterE"
        )
        cluster6 = Cluster(
            id="c6", node_ids=[node8.id], severity_multiplier=0.0, name="ClusterF"
        )
        cluster7 = Cluster(
            id="c7", node_ids=[node9.id], severity_multiplier=-1.5, name="ClusterG"
        )
        cluster8 = Cluster(
            id="c8", node_ids=[node7.id], severity_multiplier=1.1, name="ClusterH"
        )

        # Diagram setup
        dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": node1,
                "node2": node2,
                "node3": node3,
                "node4": node4,
                "node5": node5,
                "node6": node6,
                "node7": node7,
                "node8": node8,
                "node9": node9,
            },
            edges={
                "edge1": edge1,
            },
            clusters={
                "cluster1": cluster1,
                "cluster2": cluster2,
                "cluster3": cluster3,
                "cluster4": cluster4,
                "cluster5": cluster5,
                "cluster6": cluster6,
                "cluster7": cluster7,
                "cluster8": cluster8,
            },
            tags={"test_rules"},
        )

        threats = cls.modified_elicit(dfd)

        found = [False for i in range(18)]
        for threat in threats:
            match threat.uid():
                case "TestNodeRule1@n1":
                    found[0] = True
                    assert math.isclose(threat.severity, 1.2)
                    assert not math.isclose(threat.severity, 1.1)
                case "TestNodeRule2@n1":
                    found[1] = True
                    assert math.isclose(threat.severity, 3.0)
                case "TestNodeRule1@n2":
                    found[2] = True
                    assert math.isclose(threat.severity, 1.2)
                case "TestNodeRule2@n2":
                    found[3] = True
                    assert math.isclose(threat.severity, 3.0)
                case "TestNodeRule1@n3":
                    found[4] = True
                    assert math.isclose(threat.severity, 0.14)
                case "TestNodeRule2@n3":
                    found[5] = True
                    assert math.isclose(threat.severity, 0.35)
                case "TestNodeRule1@n4":
                    found[6] = True
                    assert math.isclose(threat.severity, 2.4)
                case "TestNodeRule2@n4":
                    found[7] = True
                    assert math.isclose(threat.severity, 6.0)
                case "TestNodeRule1@n5":
                    found[8] = True
                    assert math.isclose(threat.severity, 4.0)
                case "TestNodeRule2@n5":
                    found[9] = True
                    assert math.isclose(threat.severity, 10.0)
                case "TestNodeRule1@n6":
                    found[10] = True
                    assert math.isclose(threat.severity, 0.12)
                case "TestNodeRule2@n6":
                    found[11] = True
                    assert math.isclose(threat.severity, 0.30)
                case "TestNodeRule1@n7":
                    found[12] = True
                    assert math.isclose(threat.severity, 7.92)
                case "TestNodeRule2@n7":
                    found[13] = True
                    assert math.isclose(threat.severity, 19.8)
                case "TestNodeRule1@n8":
                    found[14] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestNodeRule2@n8":
                    found[15] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestNodeRule1@n9":
                    found[16] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestNodeRule2@n9":
                    found[17] = True
                    assert math.isclose(threat.severity, 0.0)

        assert all(found)

    def test_elicit_severity_multiplier_edges(cls):
        node1 = Node(id="n1", severity_multiplier=1.1, name="ProcessA")
        node2 = Node(id="n2", severity_multiplier=1.1, name="ProcessB")
        node3 = Node(id="n3", severity_multiplier=1.2, name="ProcessC")
        node4 = Node(id="n4", severity_multiplier=1.5, name="ProcessD")
        node5 = Node(id="n5", severity_multiplier=1.3, name="ProcessE")
        node6 = Node(id="n6", severity_multiplier=2.0, name="ProcessF")
        node7 = Node(id="n7", severity_multiplier=0.0, name="ProcessG")
        node8 = Node(id="n8", severity_multiplier=-0.5, name="ProcessH")
        node9 = Node(id="n9", severity_multiplier=-0.8, name="ProcessI")

        # Edge between nodes with same severity_multp should take that multp
        edge1 = Edge(id="e1", source_id=node1.id, sink_id=node2.id, name="Edge1")
        # Edges between nodes with different severity should take the highest multp
        edge2 = Edge(id="e2", source_id=node2.id, sink_id=node3.id, name="Edge2")
        edge3 = Edge(id="e3", source_id=node4.id, sink_id=node3.id, name="Edge3")
        # Edges between nodes in clusters should take the cluster modifiers into account
        edge4 = Edge(id="e4", source_id=node5.id, sink_id=node4.id, name="Edge4")
        edge5 = Edge(id="e5", source_id=node5.id, sink_id=node6.id, name="Edge5")
        # Edges between nodes with negative severity_multp should clamp to 0.0 + warning
        edge6 = Edge(id="e6", source_id=node8.id, sink_id=node9.id, name="Edge6")

        cluster1 = Cluster(
            id="c1",
            node_ids=[node5.id, node6.id],
            severity_multiplier=1.3,
            name="ClusterA",
        )

        # Diagram setup
        dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": node1,
                "node2": node2,
                "node3": node3,
                "node4": node4,
                "node5": node5,
                "node6": node6,
                "node7": node7,
                "node8": node8,
                "node9": node9,
            },
            edges={
                "edge1": edge1,
                "edge2": edge2,
                "edge3": edge3,
                "edge4": edge4,
                "edge5": edge5,
                "edge6": edge6,
            },
            clusters={
                "cluster1": cluster1,
            },
            tags={"test_rules"},
        )

        threats = cls.modified_elicit(dfd)

        found = [False for i in range(12)]
        for threat in threats:
            match threat.uid():
                case "TestEdgeRule1@e1":
                    found[0] = True
                    assert math.isclose(threat.severity, 1.1)
                    assert not math.isclose(threat.severity, 1.2)
                case "TestEdgeRule2@e1":
                    found[1] = True
                    assert math.isclose(threat.severity, 2.75)
                case "TestEdgeRule1@e2":
                    found[2] = True
                    assert math.isclose(threat.severity, 1.2)
                case "TestEdgeRule2@e2":
                    found[3] = True
                    assert math.isclose(threat.severity, 3.0)
                case "TestEdgeRule1@e3":
                    found[4] = True
                    assert math.isclose(threat.severity, 1.5)
                case "TestEdgeRule2@e3":
                    found[5] = True
                    assert math.isclose(threat.severity, 3.75)
                case "TestEdgeRule1@e4":
                    found[6] = True
                    assert math.isclose(threat.severity, 1.69)
                case "TestEdgeRule2@e4":
                    found[7] = True
                    assert math.isclose(threat.severity, 4.225)
                case "TestEdgeRule1@e5":
                    found[8] = True
                    assert math.isclose(threat.severity, 2.6)
                case "TestEdgeRule2@e5":
                    found[9] = True
                    assert math.isclose(threat.severity, 6.5)
                case "TestEdgeRule1@e6":
                    found[10] = True
                    assert math.isclose(threat.severity, 0.0)
                case "TestEdgeRule2@e6":
                    found[11] = True
                    assert math.isclose(threat.severity, 0.0)

        assert all(found)
