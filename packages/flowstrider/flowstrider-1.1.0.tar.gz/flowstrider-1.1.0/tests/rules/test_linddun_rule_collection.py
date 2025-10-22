# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest

from flowstrider import settings
from flowstrider.models.common_models import Cluster, Edge, Node
from flowstrider.models.dataflowdiagram import DataflowDiagram
from flowstrider.rules.builtin.linddun_rules.linddun_rule_collection import (
    D1_DetectableUsers,
    D2_DetectableServiceUsage,
    D3_DetectableEvents,
    D4_DetectableRecords,
    DD1_ExcessivelySensitiveData,
    DD2_ExcessiveDataAmount,
    DD3_UnnecessaryDataAnalysis,
    DD4_UnnecessaryDataRetention,
    DD5_OverexposurePersonalData,
    I1_IdentifiedUserRequests,
    I2_IdentifiableUserRequests,
    I3_IdentifiableDataFlows,
    I4_IdentifiableDataRequests,
    I5_IdentifiableDataset,
    L1_LinkedUserRequests,
    L2_LinkableUserRequests,
    L3_LinkableUserPatterns,
    L4_LinkableDataset,
    L5_ProfilingUsers,
    Nc1_NonCompliantProcessing,
    Nc2_NonAdherencePrivacyStandards,
    Nc3_ImproperDataLifecycle,
    Nc4_InsufficientProcessingSecurity,
    Nr1_NonRepudiationOfServiceUsage,
    Nr2_NonRepudiationOfSending,
    Nr3_NonRepudiationOfReceipt,
    Nr4_NonRepudiationOfStorage,
    Nr5_NonRepudiationOfMetadata,
    U1_InsufficientTransparency,
    U2_InsufficientTransparencyOthers,
    U3_InsufficientPrivacyControls,
    U4_InsufficientAccess,
    U5_InsufficientErasure,
)


class TestHelpers(unittest.TestCase):
    # Initialize Localization
    settings.init_localization("en", "sys")
    settings.init_localization("en", "out")


# ===== LINKING: ==========================================
class TestL1_LinkedUserRequests(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id="n1", name="ProcessA")
        self.node2 = Node(id="n2", name="ProcessB")
        self.node3 = Node(id="n3", name="ProcessC")

        # Edge that doesn't define if it transmits unique user ids should trigger
        self.edge1 = Edge(
            id="e1",
            source_id=self.node1.id,
            sink_id=self.node3.id,
            attributes={},
        )

        # Edge that doesn't transmit unique user ids shouldn't trigger
        self.edge2 = Edge(
            id="e2",
            source_id=self.node3.id,
            sink_id=self.node2.id,
            attributes={"transmits_unique_user_id": False},
        )

        # Edge that does transmit unique user ids should trigger
        self.edge3 = Edge(
            id="e3",
            source_id=self.node2.id,
            sink_id=self.node3.id,
            attributes={"transmits_unique_user_id": True},
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={"node1": self.node1, "node2": self.node2, "node3": self.node3},
            edges={
                "edge1": self.edge1,
                "edge2": self.edge2,
                "edge3": self.edge3,
            },
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = L1_LinkedUserRequests._test(self.edge1, self.dfd)
        self.assertTrue(result)
        L1_LinkedUserRequests.set_status(self.edge1)
        self.assertTrue(
            L1_LinkedUserRequests.req_status
            == "Attribute missing: Transmits unique user identifier"
        )

    def test_rule_doesnt_apply_if_not_transmits_unique_user_identifier(self):
        result = L1_LinkedUserRequests._test(self.edge2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_unique_user_identifier(self):
        result = L1_LinkedUserRequests._test(self.edge3, self.dfd)
        self.assertTrue(result)
        L1_LinkedUserRequests.set_status(self.edge3)
        self.assertTrue(
            L1_LinkedUserRequests.req_status
            == "Transmits unique user identifier = True"
        )


class TestL2_LinkableUserRequests(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id="n1", name="ProcessA")
        self.node2 = Node(id="n2", name="ProcessB")
        self.node3 = Node(id="n3", name="ProcessC")

        # Edge that doesn't define if it transmits user properties should trigger
        self.edge1 = Edge(
            id="e1",
            source_id=self.node1.id,
            sink_id=self.node3.id,
            attributes={},
        )

        # Edge that doesn't transmit user properties shouldn't trigger
        self.edge2 = Edge(
            id="e2",
            source_id=self.node3.id,
            sink_id=self.node2.id,
            attributes={"transmits_user_properties": False},
        )

        # Edge that does transmit user properties should trigger
        self.edge3 = Edge(
            id="e3",
            source_id=self.node2.id,
            sink_id=self.node3.id,
            attributes={"transmits_user_properties": True},
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={"node1": self.node1, "node2": self.node2, "node3": self.node3},
            edges={
                "edge1": self.edge1,
                "edge2": self.edge2,
                "edge3": self.edge3,
            },
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = L2_LinkableUserRequests._test(self.edge1, self.dfd)
        self.assertTrue(result)
        L2_LinkableUserRequests.set_status(self.edge1)
        self.assertTrue(
            L2_LinkableUserRequests.req_status
            == "Attribute missing: Transmits user properties"
        )

    def test_rule_doesnt_apply_if_not_transmits_user_data(self):
        result = L2_LinkableUserRequests._test(self.edge2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_user_data(self):
        result = L2_LinkableUserRequests._test(self.edge3, self.dfd)
        self.assertTrue(result)
        L2_LinkableUserRequests.set_status(self.edge3)
        self.assertTrue(
            L2_LinkableUserRequests.req_status == "Transmits user properties = True"
        )


class TestL3_LinkableUserPatterns(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id="n1", name="ProcessA")
        self.node2 = Node(id="n2", name="ProcessB")
        self.node3 = Node(id="n3", name="ProcessC")

        # Edge that doesn't define if it transmits user data should trigger
        self.edge1 = Edge(
            id="e1",
            source_id=self.node1.id,
            sink_id=self.node3.id,
            attributes={},
        )

        # Edge that doesn't transmit user data shouldn't trigger
        self.edge2 = Edge(
            id="e2",
            source_id=self.node3.id,
            sink_id=self.node2.id,
            attributes={"transmits_user_data": False},
        )

        # Edge that does transmit user data should trigger
        self.edge3 = Edge(
            id="e3",
            source_id=self.node2.id,
            sink_id=self.node3.id,
            attributes={"transmits_user_data": True},
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={"node1": self.node1, "node2": self.node2, "node3": self.node3},
            edges={
                "edge1": self.edge1,
                "edge2": self.edge2,
                "edge3": self.edge3,
            },
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = L3_LinkableUserPatterns._test(self.edge1, self.dfd)
        self.assertTrue(result)
        L3_LinkableUserPatterns.set_status(self.edge1)
        self.assertTrue(
            L3_LinkableUserPatterns.req_status
            == "Attribute missing: Transmits user data"
        )

    def test_rule_doesnt_apply_if_not_transmits_user_data(self):
        result = L3_LinkableUserPatterns._test(self.edge2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_user_data(self):
        result = L3_LinkableUserPatterns._test(self.edge3, self.dfd)
        self.assertTrue(result)
        L3_LinkableUserPatterns.set_status(self.edge3)
        self.assertTrue(
            L3_LinkableUserPatterns.req_status == "Transmits user data = True"
        )


class TestL4_LinkableDataset(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it stores user data should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that doesn't store user data shouldnt trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"handles_user_data": False},
            tags=["STRIDE:DataStore"],
        )
        # Node that does store user data should trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"handles_user_data": True},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = L4_LinkableDataset._test(self.node1, self.dfd)
        self.assertTrue(result)
        L4_LinkableDataset.set_status(self.node1)
        self.assertTrue(
            L4_LinkableDataset.req_status == "Attribute missing: Handles user data"
        )

    def test_rule_doesnt_apply_if_not_handles_user_data(self):
        result = L4_LinkableDataset._test(self.node2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_handles_user_data(self):
        result = L4_LinkableDataset._test(self.node3, self.dfd)
        self.assertTrue(result)
        L4_LinkableDataset.set_status(self.node3)
        self.assertTrue(L4_LinkableDataset.req_status == "Handles user data = True")

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = L4_LinkableDataset._test(self.node4, self.dfd)
        self.assertFalse(result)


class TestL5_ProfilingUsers(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it processes user data should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:Process"]
        )
        # Node that doesn't process user data shouldnt trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"handles_user_data": False},
            tags=["STRIDE:Process"],
        )
        # Node that does process user data should trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"handles_user_data": True},
            tags=["STRIDE:Process"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Datastore"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = L5_ProfilingUsers._test(self.node1, self.dfd)
        self.assertTrue(result)
        L5_ProfilingUsers.set_status(self.node1)
        self.assertTrue(
            L5_ProfilingUsers.req_status == "Attribute missing: Handles user data"
        )

    def test_rule_doesnt_apply_if_not_handles_user_data(self):
        result = L5_ProfilingUsers._test(self.node2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_handles_user_data(self):
        result = L5_ProfilingUsers._test(self.node3, self.dfd)
        self.assertTrue(result)
        L5_ProfilingUsers.set_status(self.node3)
        self.assertTrue(L5_ProfilingUsers.req_status == "Handles user data = True")

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = L5_ProfilingUsers._test(self.node4, self.dfd)
        self.assertFalse(result)


# ===== Identifying: ======================================
class TestI1_IdentifiedUserRequests(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id="n1", name="ProcessA")
        self.node2 = Node(id="n2", name="ProcessB")
        self.node3 = Node(id="n3", name="ProcessC")

        # Edge that doesn't define if it transmits user ids should trigger
        self.edge1 = Edge(
            id="e1",
            source_id=self.node1.id,
            sink_id=self.node3.id,
            attributes={},
        )

        # Edge that doesn't transmit user ids shouldn't trigger
        self.edge2 = Edge(
            id="e2",
            source_id=self.node3.id,
            sink_id=self.node2.id,
            attributes={"transmits_user_identity": False},
        )

        # Edge that does transmit user ids should trigger
        self.edge3 = Edge(
            id="e3",
            source_id=self.node2.id,
            sink_id=self.node3.id,
            attributes={"transmits_user_identity": True},
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={"node1": self.node1, "node2": self.node2, "node3": self.node3},
            edges={
                "edge1": self.edge1,
                "edge2": self.edge2,
                "edge3": self.edge3,
            },
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = I1_IdentifiedUserRequests._test(self.edge1, self.dfd)
        self.assertTrue(result)
        I1_IdentifiedUserRequests.set_status(self.edge1)
        self.assertTrue(
            I1_IdentifiedUserRequests.req_status
            == "Attribute missing: Transmits user identity"
        )

    def test_rule_doesnt_apply_if_not_transmits_user_identity(self):
        result = I1_IdentifiedUserRequests._test(self.edge2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_user_identity(self):
        result = I1_IdentifiedUserRequests._test(self.edge3, self.dfd)
        self.assertTrue(result)
        I1_IdentifiedUserRequests.set_status(self.edge3)
        self.assertTrue(
            I1_IdentifiedUserRequests.req_status == "Transmits user identity = True"
        )


class TestI2_IdentifiableUserRequests(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id="n1", name="ProcessA")
        self.node2 = Node(id="n2", name="ProcessB")
        self.node3 = Node(id="n3", name="ProcessC")

        # Edge that doesn't define if it transmits user data should trigger
        self.edge1 = Edge(
            id="e1",
            source_id=self.node1.id,
            sink_id=self.node3.id,
            attributes={},
        )

        # Edge that doesn't transmit user data shouldn't trigger
        self.edge2 = Edge(
            id="e2",
            source_id=self.node3.id,
            sink_id=self.node2.id,
            attributes={"transmits_user_data": False},
        )

        # Edge that does transmit user data should trigger
        self.edge3 = Edge(
            id="e3",
            source_id=self.node2.id,
            sink_id=self.node3.id,
            attributes={"transmits_user_data": True},
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={"node1": self.node1, "node2": self.node2, "node3": self.node3},
            edges={
                "edge1": self.edge1,
                "edge2": self.edge2,
                "edge3": self.edge3,
            },
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = I2_IdentifiableUserRequests._test(self.edge1, self.dfd)
        self.assertTrue(result)
        I2_IdentifiableUserRequests.set_status(self.edge1)
        self.assertTrue(
            I2_IdentifiableUserRequests.req_status
            == "Attribute missing: Transmits user data"
        )

    def test_rule_doesnt_apply_if_not_transmits_user_data(self):
        result = I2_IdentifiableUserRequests._test(self.edge2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_user_data(self):
        result = I2_IdentifiableUserRequests._test(self.edge3, self.dfd)
        self.assertTrue(result)
        I2_IdentifiableUserRequests.set_status(self.edge3)
        self.assertTrue(
            I2_IdentifiableUserRequests.req_status == "Transmits user data = True"
        )


class TestI3_IdentifiableDataFlows(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id="n1", name="ProcessA")
        self.node2 = Node(id="n2", name="ProcessB")
        self.node3 = Node(id="n3", name="ProcessC")

        # Edge that doesn't define if it transmits user data should trigger
        self.edge1 = Edge(
            id="e1",
            source_id=self.node1.id,
            sink_id=self.node3.id,
            attributes={},
        )

        # Edge that doesn't transmit user data shouldn't trigger
        self.edge2 = Edge(
            id="e2",
            source_id=self.node3.id,
            sink_id=self.node2.id,
            attributes={"transmits_user_data": False},
        )

        # Edge that does transmit user data should trigger
        self.edge3 = Edge(
            id="e3",
            source_id=self.node2.id,
            sink_id=self.node3.id,
            attributes={"transmits_user_data": True},
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={"node1": self.node1, "node2": self.node2, "node3": self.node3},
            edges={
                "edge1": self.edge1,
                "edge2": self.edge2,
                "edge3": self.edge3,
            },
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = I3_IdentifiableDataFlows._test(self.edge1, self.dfd)
        self.assertTrue(result)
        I3_IdentifiableDataFlows.set_status(self.edge1)
        self.assertTrue(
            I3_IdentifiableDataFlows.req_status
            == "Attribute missing: Transmits user data"
        )

    def test_rule_doesnt_apply_if_not_transmits_user_data(self):
        result = I3_IdentifiableDataFlows._test(self.edge2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_user_data(self):
        result = I3_IdentifiableDataFlows._test(self.edge3, self.dfd)
        self.assertTrue(result)
        I3_IdentifiableDataFlows.set_status(self.edge3)
        self.assertTrue(
            I3_IdentifiableDataFlows.req_status == "Transmits user data = True"
        )


class TestI4_IdentifiableDataRequests(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id="n1", name="ProcessA")
        self.node2 = Node(id="n2", name="ProcessB")
        self.node3 = Node(id="n3", name="ProcessC")

        # Edge that doesn't define if it transmits unique user ids should trigger
        self.edge1 = Edge(
            id="e1",
            source_id=self.node1.id,
            sink_id=self.node3.id,
            attributes={},
        )

        # Edge that doesn't transmit unique user ids shouldn't trigger
        self.edge2 = Edge(
            id="e2",
            source_id=self.node3.id,
            sink_id=self.node2.id,
            attributes={"transmits_unique_user_id": False},
        )

        # Edge that does transmit unique user ids should trigger
        self.edge3 = Edge(
            id="e3",
            source_id=self.node2.id,
            sink_id=self.node3.id,
            attributes={"transmits_unique_user_id": True},
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={"node1": self.node1, "node2": self.node2, "node3": self.node3},
            edges={
                "edge1": self.edge1,
                "edge2": self.edge2,
                "edge3": self.edge3,
            },
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = I4_IdentifiableDataRequests._test(self.edge1, self.dfd)
        self.assertTrue(result)
        I4_IdentifiableDataRequests.set_status(self.edge1)
        self.assertTrue(
            I4_IdentifiableDataRequests.req_status
            == "Attribute missing: Transmits unique user identifier"
        )

    def test_rule_doesnt_apply_if_not_transmits_unique_user_id(self):
        result = I4_IdentifiableDataRequests._test(self.edge2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_unique_user_id(self):
        result = I4_IdentifiableDataRequests._test(self.edge3, self.dfd)
        self.assertTrue(result)
        I4_IdentifiableDataRequests.set_status(self.edge3)
        self.assertTrue(
            I4_IdentifiableDataRequests.req_status
            == "Transmits unique user identifier = True"
        )


class TestI5_IdentifiableDataset(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it stores user data should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that doesn't store user data shouldn't trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"handles_user_data": False},
            tags=["STRIDE:DataStore"],
        )
        # Node that does store user data should trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"handles_user_data": True},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = I5_IdentifiableDataset._test(self.node1, self.dfd)
        self.assertTrue(result)
        I5_IdentifiableDataset.set_status(self.node1)
        self.assertTrue(
            I5_IdentifiableDataset.req_status == "Attribute missing: Handles user data"
        )

    def test_rule_doesnt_apply_if_not_handles_user_data(self):
        result = I5_IdentifiableDataset._test(self.node2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_handles_user_data(self):
        result = I5_IdentifiableDataset._test(self.node3, self.dfd)
        self.assertTrue(result)
        I5_IdentifiableDataset.set_status(self.node3)
        self.assertTrue(I5_IdentifiableDataset.req_status == "Handles user data = True")

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = I5_IdentifiableDataset._test(self.node4, self.dfd)
        self.assertFalse(result)


# ===== Non-Repudiation: ==================================
class TestNr1_NonRepudiationOfServiceUsage(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it logs access should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:Process"]
        )
        # Node that doesn't log access shouldn't trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"logs_access": False},
            tags=["STRIDE:Process"],
        )
        # Node that does log access should trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"logs_access": True},
            tags=["STRIDE:Process"],
        )

        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Datastore"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = Nr1_NonRepudiationOfServiceUsage._test(self.node1, self.dfd)
        self.assertTrue(result)
        Nr1_NonRepudiationOfServiceUsage.set_status(self.node1)
        self.assertTrue(
            Nr1_NonRepudiationOfServiceUsage.req_status
            == "Attribute missing: Logs access"
        )

    def test_rule_doesnt_apply_if_access_not_logged(self):
        result = Nr1_NonRepudiationOfServiceUsage._test(self.node2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_access_logged(self):
        result = Nr1_NonRepudiationOfServiceUsage._test(self.node3, self.dfd)
        self.assertTrue(result)
        Nr1_NonRepudiationOfServiceUsage.set_status(self.node3)
        self.assertTrue(
            Nr1_NonRepudiationOfServiceUsage.req_status == "Logs access = True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = Nr1_NonRepudiationOfServiceUsage._test(self.node4, self.dfd)
        self.assertFalse(result)


class TestNr2_NonRepudiationOfSending(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id="n1", name="ProcessA")
        self.node2 = Node(id="n2", name="ProcessB")
        self.node3 = Node(id="n3", name="ProcessC")

        # Edge that doesn't define if it transmits signed data should trigger
        self.edge1 = Edge(
            id="e1",
            source_id=self.node1.id,
            sink_id=self.node3.id,
            attributes={},
        )

        # Edge that doesn't transmit signed data shouldn't trigger
        self.edge2 = Edge(
            id="e2",
            source_id=self.node3.id,
            sink_id=self.node2.id,
            attributes={"transmits_signed_data": False},
        )

        # Edge that does transmit signed data should trigger
        self.edge3 = Edge(
            id="e3",
            source_id=self.node2.id,
            sink_id=self.node3.id,
            attributes={"transmits_signed_data": True},
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={"node1": self.node1, "node2": self.node2, "node3": self.node3},
            edges={
                "edge1": self.edge1,
                "edge2": self.edge2,
                "edge3": self.edge3,
            },
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = Nr2_NonRepudiationOfSending._test(self.edge1, self.dfd)
        self.assertTrue(result)
        Nr2_NonRepudiationOfSending.set_status(self.edge1)
        self.assertTrue(
            Nr2_NonRepudiationOfSending.req_status
            == "Attribute missing: Transmits signed data"
        )

    def test_rule_doesnt_apply_if_not_transmits_signed_data(self):
        result = Nr2_NonRepudiationOfSending._test(self.edge2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_signed_data(self):
        result = Nr2_NonRepudiationOfSending._test(self.edge3, self.dfd)
        self.assertTrue(result)
        Nr2_NonRepudiationOfSending.set_status(self.edge3)
        self.assertTrue(
            Nr2_NonRepudiationOfSending.req_status == "Transmits signed data = True"
        )


class TestNr3_NonRepudiationOfReceipt(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it logs receipt should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:Process"]
        )
        # Node that doesn't log receipt shouldnt trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"logs_receipt": False},
            tags=["STRIDE:Process"],
        )
        # Node that does log receipt should trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"logs_receipt": True},
            tags=["STRIDE:Process"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Datastore"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = Nr3_NonRepudiationOfReceipt._test(self.node1, self.dfd)
        self.assertTrue(result)
        Nr3_NonRepudiationOfReceipt.set_status(self.node1)
        self.assertTrue(
            Nr3_NonRepudiationOfReceipt.req_status == "Attribute missing: Logs receipt"
        )

    def test_rule_doesnt_apply_if_not_transmits_signed_data(self):
        result = Nr3_NonRepudiationOfReceipt._test(self.node2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_signed_data(self):
        result = Nr3_NonRepudiationOfReceipt._test(self.node3, self.dfd)
        self.assertTrue(result)
        Nr3_NonRepudiationOfReceipt.set_status(self.node3)
        self.assertTrue(Nr3_NonRepudiationOfReceipt.req_status == "Logs receipt = True")

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = Nr3_NonRepudiationOfReceipt._test(self.node4, self.dfd)
        self.assertFalse(result)


class TestNr4_NonRepudiationOfStorage(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it stores signed data should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that doesn't store signed data shouldnt trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"stores_signed_data": False},
            tags=["STRIDE:DataStore"],
        )
        # Node that does store signed data should trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"stores_signed_data": True},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = Nr4_NonRepudiationOfStorage._test(self.node1, self.dfd)
        self.assertTrue(result)
        Nr4_NonRepudiationOfStorage.set_status(self.node1)
        self.assertTrue(
            Nr4_NonRepudiationOfStorage.req_status
            == "Attribute missing: Stores signed data"
        )

    def test_rule_doesnt_apply_if_not_transmits_signed_data(self):
        result = Nr4_NonRepudiationOfStorage._test(self.node2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_transmits_signed_data(self):
        result = Nr4_NonRepudiationOfStorage._test(self.node3, self.dfd)
        self.assertTrue(result)
        Nr4_NonRepudiationOfStorage.set_status(self.node3)
        self.assertTrue(
            Nr4_NonRepudiationOfStorage.req_status == "Stores signed data = True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = Nr4_NonRepudiationOfStorage._test(self.node4, self.dfd)
        self.assertFalse(result)


class TestNr5_NonRepudiationOfMetadata(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it stores user associated metadata should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that doesn't store user associated metadata shouldnt trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"stores_user_associated_metadata": False},
            tags=["STRIDE:DataStore"],
        )
        # Node that does store user associated metadata should trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"stores_user_associated_metadata": True},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = Nr5_NonRepudiationOfMetadata._test(self.node1, self.dfd)
        self.assertTrue(result)
        Nr5_NonRepudiationOfMetadata.set_status(self.node1)
        self.assertTrue(
            Nr5_NonRepudiationOfMetadata.req_status
            == "Attribute missing: Stores user associated metadata"
        )

    def test_rule_doesnt_apply_if_not_stores_user_associated_metadata(self):
        result = Nr5_NonRepudiationOfMetadata._test(self.node2, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_stores_user_associated_metadata(self):
        result = Nr5_NonRepudiationOfMetadata._test(self.node3, self.dfd)
        self.assertTrue(result)
        Nr5_NonRepudiationOfMetadata.set_status(self.node3)
        self.assertTrue(
            Nr5_NonRepudiationOfMetadata.req_status
            == "Stores user associated metadata = True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = Nr5_NonRepudiationOfMetadata._test(self.node4, self.dfd)
        self.assertFalse(result)


# ===== Detecting: ========================================
class TestD1_DetectableUsers(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define anything should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that doesn't define if it discloses data in the responses should trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"handles_user_data": True},
            tags=["STRIDE:Process"],
        )
        # Node that does disclose data in the responses should trigger if it also stores
        # ...user data or doesn't define it
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"discloses_responses": True},
            tags=["STRIDE:DataStore"],
        )
        self.node4 = Node(
            id="n4",
            name="ProcessD",
            attributes={"discloses_responses": True, "handles_user_data": True},
            tags=["STRIDE:Process"],
        )
        # Node that does disclose data in the responses but doesn't store user data
        # ...shouldn't trigger
        self.node5 = Node(
            id="n5",
            name="ProcessE",
            attributes={"discloses_responses": True, "handles_user_data": False},
            tags=["STRIDE:DataStore"],
        )
        self.node7 = Node(
            id="n7",
            name="ProcessG",
            attributes={"handles_user_data": False},
            tags=["STRIDE:Process"],
        )
        # Node that doesn't disclose data in the responses shouldn't trigger
        self.node6 = Node(
            id="n6",
            name="ProcessF",
            attributes={"discloses_responses": False, "handles_user_data": True},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node8 = Node(
            id="n8", name="ProcessH", attributes={}, tags=["STRIDE:Interactor"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
                "node5": self.node5,
                "node6": self.node6,
                "node7": self.node7,
                "node8": self.node8,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = D1_DetectableUsers._test(self.node1, self.dfd)
        self.assertTrue(result)
        D1_DetectableUsers.set_status(self.node1)
        self.assertTrue(
            D1_DetectableUsers.req_status
            == "Attribute missing: Responses disclose information existence\nAttribute"
            + " missing: Handles user data"
        )
        result = D1_DetectableUsers._test(self.node2, self.dfd)
        self.assertTrue(result)
        D1_DetectableUsers.set_status(self.node2)
        self.assertTrue(
            D1_DetectableUsers.req_status
            == "Attribute missing: Responses disclose information existence\nHandles"
            + " user data = True"
        )

    def test_rule_doesnt_apply_if_doesnt_disclose_information(self):
        result = D1_DetectableUsers._test(self.node5, self.dfd)
        self.assertFalse(result)
        result = D1_DetectableUsers._test(self.node6, self.dfd)
        self.assertFalse(result)
        result = D1_DetectableUsers._test(self.node7, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_discloses_information(self):
        result = D1_DetectableUsers._test(self.node3, self.dfd)
        self.assertTrue(result)
        D1_DetectableUsers.set_status(self.node3)
        self.assertTrue(
            D1_DetectableUsers.req_status
            == "Responses disclose information existence = True\nAttribute missing:"
            + " Handles user data"
        )
        result = D1_DetectableUsers._test(self.node4, self.dfd)
        self.assertTrue(result)
        D1_DetectableUsers.set_status(self.node4)
        self.assertTrue(
            D1_DetectableUsers.req_status
            == "Responses disclose information existence = True\nHandles user data ="
            + " True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = D1_DetectableUsers._test(self.node8, self.dfd)
        self.assertFalse(result)


class TestD2_DetectableServiceUsage(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id="n1", name="ProcessA")
        self.node2 = Node(id="n2", name="ProcessB")
        self.node3 = Node(id="n3", name="ProcessC")
        self.node4 = Node(id="n4", name="ProcessD")
        self.node5 = Node(id="n5", name="ProcessE")
        self.node6 = Node(id="n6", name="ProcessE")
        self.node7 = Node(id="n7", name="ProcessE")

        # Edge inside non private network should trigger
        self.edge1 = Edge(
            id="e1",
            source_id=self.node1.id,
            sink_id=self.node2.id,
            attributes={},
        )
        self.edge2 = Edge(
            id="e2",
            source_id=self.node3.id,
            sink_id=self.node4.id,
            attributes={},
        )

        # Edge between non private networks should trigger
        self.edge3 = Edge(
            id="e3",
            source_id=self.node1.id,
            sink_id=self.node4.id,
            attributes={},
        )
        self.edge4 = Edge(
            id="e4",
            source_id=self.node1.id,
            sink_id=self.node7.id,
            attributes={},
        )

        # Edge between private and non private networks should trigger
        self.edge5 = Edge(
            id="e5",
            source_id=self.node1.id,
            sink_id=self.node5.id,
            attributes={},
        )
        self.edge6 = Edge(
            id="e6",
            source_id=self.node7.id,
            sink_id=self.node6.id,
            attributes={},
        )

        # Edge inside private network should not trigger
        self.edge7 = Edge(
            id="e7",
            source_id=self.node6.id,
            sink_id=self.node5.id,
            attributes={},
        )

        self.cluster1 = Cluster(
            id="c1",
            node_ids=[
                self.node1.id,
                self.node2.id,
            ],
            attributes={},
        )
        self.cluster2 = Cluster(
            id="c2",
            node_ids=[
                self.node3.id,
                self.node4.id,
            ],
            attributes={"is_private_network": False},
        )
        self.cluster3 = Cluster(
            id="c3",
            node_ids=[
                self.node5.id,
                self.node6.id,
            ],
            attributes={"is_private_network": True},
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
                "node5": self.node5,
                "node6": self.node6,
                "node7": self.node7,
            },
            edges={
                "edge1": self.edge1,
                "edge2": self.edge2,
                "edge3": self.edge3,
                "edge4": self.edge4,
                "edge5": self.edge5,
                "edge6": self.edge6,
                "edge7": self.edge7,
            },
            clusters={
                "cluster1": self.cluster1,
                "cluster2": self.cluster2,
                "cluster3": self.cluster3,
            },
        )

    def test_rule_does_apply_if_inside_non_private_network(self):
        result = D2_DetectableServiceUsage._test(self.edge1, self.dfd)
        self.assertTrue(result)
        result = D2_DetectableServiceUsage._test(self.edge2, self.dfd)
        self.assertTrue(result)

    def test_rule_does_apply_if_between_non_private_network(self):
        result = D2_DetectableServiceUsage._test(self.edge3, self.dfd)
        self.assertTrue(result)
        result = D2_DetectableServiceUsage._test(self.edge4, self.dfd)
        self.assertTrue(result)

    def test_rule_does_apply_if_between_private_and_public_network(self):
        result = D2_DetectableServiceUsage._test(self.edge5, self.dfd)
        self.assertTrue(result)
        result = D2_DetectableServiceUsage._test(self.edge6, self.dfd)
        self.assertTrue(result)

    def test_rule_doesnt_apply_if_inside_private_network(self):
        result = D2_DetectableServiceUsage._test(self.edge7, self.dfd)
        self.assertFalse(result)


class TestD3_DetectableEvents(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it leaves usage traces should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that leaves usage traces should trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"leaves_usage_traces": True},
            tags=["STRIDE:Process"],
        )
        # Node thtat doesn't leave usage traces shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"leaves_usage_traces": False},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Interactor"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_leaves_usage_traces(self):
        result = D3_DetectableEvents._test(self.node1, self.dfd)
        self.assertTrue(result)
        D3_DetectableEvents.set_status(self.node1)
        self.assertTrue(
            D3_DetectableEvents.req_status == "Attribute missing: Leaves usage traces"
        )
        result = D3_DetectableEvents._test(self.node2, self.dfd)
        self.assertTrue(result)
        D3_DetectableEvents.set_status(self.node2)
        self.assertTrue(D3_DetectableEvents.req_status == "Leaves usage traces = True")

    def test_rule_doesnt_apply_if_not_leaves_usage_traces(self):
        result = D3_DetectableEvents._test(self.node3, self.dfd)
        self.assertFalse(result)

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = D3_DetectableEvents._test(self.node4, self.dfd)
        self.assertFalse(result)


class TestD4_DetectableRecords(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it discloses data in the responses should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that does disclose data in the responses should trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"discloses_responses": True},
            tags=["STRIDE:Process"],
        )
        # Node that doesn't disclose data in the responses shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"discloses_responses": False},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Interactor"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = D4_DetectableRecords._test(self.node1, self.dfd)
        self.assertTrue(result)
        D4_DetectableRecords.set_status(self.node1)
        self.assertTrue(
            D4_DetectableRecords.req_status
            == "Attribute missing: Responses disclose information existence"
        )

    def test_rule_does_apply_if_discloses_information(self):
        result = D4_DetectableRecords._test(self.node2, self.dfd)
        self.assertTrue(result)
        D4_DetectableRecords.set_status(self.node2)
        self.assertTrue(
            D4_DetectableRecords.req_status
            == "Responses disclose information existence = True"
        )

    def test_rule_doesnt_apply_if_doesnt_disclose_information(self):
        result = D4_DetectableRecords._test(self.node3, self.dfd)
        self.assertFalse(result)

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = D4_DetectableRecords._test(self.node4, self.dfd)
        self.assertFalse(result)


# ===== Data Disclosure: ==================================
class TestDD1_ExcessivelySensitiveData(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define anything should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that doesn't define if it collects only necessary data should trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"handles_confidential_data": True},
            tags=["STRIDE:Process"],
        )
        self.node8 = Node(
            id="n8",
            name="ProcessH",
            attributes={
                "handles_personal_data": True,
                "handles_confidential_data": False,
            },
            tags=["STRIDE:DataStore"],
        )
        # Node that does doesn't collect only necessary data should trigger if it also
        # ...handles confidential data or doesn't define it
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"only_necessary_data_collected": False},
            tags=["STRIDE:DataStore"],
        )
        self.node4 = Node(
            id="n4",
            name="ProcessD",
            attributes={
                "only_necessary_data_collected": False,
                "handles_confidential_data": True,
                "handles_personal_data": False,
            },
            tags=["STRIDE:Process"],
        )
        self.node9 = Node(
            id="n9",
            name="ProcessI",
            attributes={
                "only_necessary_data_collected": False,
                "handles_confidential_data": False,
                "handles_personal_data": True,
            },
            tags=["STRIDE:DataStore"],
        )
        self.node10 = Node(
            id="n10",
            name="ProcessJ",
            attributes={
                "only_necessary_data_collected": False,
                "handles_confidential_data": False,
            },
            tags=["STRIDE:Process"],
        )
        self.node11 = Node(
            id="n11",
            name="ProcessK",
            attributes={
                "only_necessary_data_collected": False,
                "handles_personal_data": False,
            },
            tags=["STRIDE:DataStore"],
        )
        # Node that doesnt collect only necessary data but doesn't handle confidential
        # ...data shouldn't trigger
        self.node5 = Node(
            id="n5",
            name="ProcessE",
            attributes={
                "only_necessary_data_collected": False,
                "handles_confidential_data": False,
                "handles_personal_data": False,
            },
            tags=["STRIDE:Process"],
        )
        self.node7 = Node(
            id="n7",
            name="ProcessG",
            attributes={
                "handles_confidential_data": False,
                "handles_personal_data": False,
            },
            tags=["STRIDE:DataStore"],
        )
        # Node that does only handle necessary data shouldn't trigger
        self.node6 = Node(
            id="n6",
            name="ProcessF",
            attributes={
                "only_necessary_data_collected": True,
                "handles_confidential_data": True,
                "handles_personal_data": True,
            },
            tags=["STRIDE:Process"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node12 = Node(
            id="n12", name="ProcessL", attributes={}, tags=["STRIDE:Interactor"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
                "node5": self.node5,
                "node6": self.node6,
                "node7": self.node7,
                "node8": self.node8,
                "node9": self.node9,
                "node10": self.node10,
                "node11": self.node11,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = DD1_ExcessivelySensitiveData._test(self.node1, self.dfd)
        self.assertTrue(result)
        DD1_ExcessivelySensitiveData.set_status(self.node1)
        self.assertTrue(
            DD1_ExcessivelySensitiveData.req_status
            == "Attribute missing: Only necessary data collected\n"
            + "Attribute missing: Handles confidential data\n"
            + "Attribute missing: Handles personal data"
        )
        result = DD1_ExcessivelySensitiveData._test(self.node2, self.dfd)
        self.assertTrue(result)
        DD1_ExcessivelySensitiveData.set_status(self.node2)
        self.assertTrue(
            DD1_ExcessivelySensitiveData.req_status
            == "Attribute missing: Only necessary data collected\n"
            + "Handles confidential data = True\n"
            + "Attribute missing: Handles personal data"
        )
        result = DD1_ExcessivelySensitiveData._test(self.node8, self.dfd)
        self.assertTrue(result)
        DD1_ExcessivelySensitiveData.set_status(self.node8)
        self.assertTrue(
            DD1_ExcessivelySensitiveData.req_status
            == "Attribute missing: Only necessary data collected\n"
            + "Handles confidential data = False\n"
            + "Handles personal data = True"
        )

    def test_rule_doesnt_apply_if_does_only_collect_necessary_data(self):
        result = DD1_ExcessivelySensitiveData._test(self.node5, self.dfd)
        self.assertFalse(result)
        result = DD1_ExcessivelySensitiveData._test(self.node6, self.dfd)
        self.assertFalse(result)
        result = DD1_ExcessivelySensitiveData._test(self.node7, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_collects_only_necessary_data(self):
        result = DD1_ExcessivelySensitiveData._test(self.node3, self.dfd)
        self.assertTrue(result)
        DD1_ExcessivelySensitiveData.set_status(self.node3)
        self.assertTrue(
            DD1_ExcessivelySensitiveData.req_status
            == "Only necessary data collected = False\n"
            + "Attribute missing: Handles confidential data\n"
            + "Attribute missing: Handles personal data"
        )
        result = DD1_ExcessivelySensitiveData._test(self.node4, self.dfd)
        self.assertTrue(result)
        DD1_ExcessivelySensitiveData.set_status(self.node4)
        self.assertTrue(
            DD1_ExcessivelySensitiveData.req_status
            == "Only necessary data collected = False\n"
            + "Handles confidential data = True\n"
            + "Handles personal data = False"
        )
        result = DD1_ExcessivelySensitiveData._test(self.node9, self.dfd)
        self.assertTrue(result)
        DD1_ExcessivelySensitiveData.set_status(self.node9)
        self.assertTrue(
            DD1_ExcessivelySensitiveData.req_status
            == "Only necessary data collected = False\n"
            + "Handles confidential data = False\n"
            + "Handles personal data = True"
        )
        result = DD1_ExcessivelySensitiveData._test(self.node10, self.dfd)
        self.assertTrue(result)
        DD1_ExcessivelySensitiveData.set_status(self.node10)
        self.assertTrue(
            DD1_ExcessivelySensitiveData.req_status
            == "Only necessary data collected = False\n"
            + "Handles confidential data = False\n"
            + "Attribute missing: Handles personal data"
        )
        result = DD1_ExcessivelySensitiveData._test(self.node11, self.dfd)
        self.assertTrue(result)
        DD1_ExcessivelySensitiveData.set_status(self.node11)
        self.assertTrue(
            DD1_ExcessivelySensitiveData.req_status
            == "Only necessary data collected = False\n"
            + "Attribute missing: Handles confidential data\n"
            + "Handles personal data = False"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = DD1_ExcessivelySensitiveData._test(self.node12, self.dfd)
        self.assertFalse(result)


class TestDD2_ExcessiveDataAmount(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it collects only necessary data should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that doesn't collect only necessary data should trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"only_necessary_data_collected": False},
            tags=["STRIDE:Process"],
        )
        # Node that does only handle necessary data shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"only_necessary_data_collected": True},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Interactor"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = DD2_ExcessiveDataAmount._test(self.node1, self.dfd)
        self.assertTrue(result)
        DD2_ExcessiveDataAmount.set_status(self.node1)
        self.assertTrue(
            DD2_ExcessiveDataAmount.req_status
            == "Attribute missing: Only necessary data collected"
        )

    def test_rule_doesnt_apply_if_does_only_collect_necessary_data(self):
        result = DD2_ExcessiveDataAmount._test(self.node3, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_collects_only_necessary_data(self):
        result = DD2_ExcessiveDataAmount._test(self.node2, self.dfd)
        self.assertTrue(result)
        DD2_ExcessiveDataAmount.set_status(self.node2)
        self.assertTrue(
            DD2_ExcessiveDataAmount.req_status
            == "Only necessary data collected = False"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = DD2_ExcessiveDataAmount._test(self.node4, self.dfd)
        self.assertFalse(result)


class TestDD3_UnnecessaryDataAnalysis(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it analyses only necessarily should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that doesn't only analyse necessarily should trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"only_necessary_data_analyzed": False},
            tags=["STRIDE:DataStore"],
        )
        # Node that does only analysen e necessary data shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"only_necessary_data_analyzed": True},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Interactor"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = DD3_UnnecessaryDataAnalysis._test(self.node1, self.dfd)
        self.assertTrue(result)
        DD3_UnnecessaryDataAnalysis.set_status(self.node1)
        self.assertTrue(
            DD3_UnnecessaryDataAnalysis.req_status
            == "Attribute missing: Only necessary data analyzed"
        )

    def test_rule_doesnt_apply_if_does_only_analyze_necessarily(self):
        result = DD3_UnnecessaryDataAnalysis._test(self.node3, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_analyzes_only_necessarily(self):
        result = DD3_UnnecessaryDataAnalysis._test(self.node2, self.dfd)
        self.assertTrue(result)
        DD3_UnnecessaryDataAnalysis.set_status(self.node2)
        self.assertTrue(
            DD3_UnnecessaryDataAnalysis.req_status
            == "Only necessary data analyzed = False"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = DD3_UnnecessaryDataAnalysis._test(self.node4, self.dfd)
        self.assertFalse(result)


class TestDD4_UnnecessaryDataRetention(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define if it data retention is minimized should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:DataStore"]
        )
        # Node that doesn't minimize data retention should trigger
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"data_retention_minimized": False},
            tags=["STRIDE:DataStore"],
        )
        # Node that does minimize data retention shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"data_retention_minimized": True},
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node4 = Node(
            id="n4", name="ProcessD", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = DD4_UnnecessaryDataRetention._test(self.node1, self.dfd)
        self.assertTrue(result)
        DD4_UnnecessaryDataRetention.set_status(self.node1)
        self.assertTrue(
            DD4_UnnecessaryDataRetention.req_status
            == "Attribute missing: Data retention minimized"
        )

    def test_rule_doesnt_apply_if_minimizes_data_retention(self):
        result = DD4_UnnecessaryDataRetention._test(self.node3, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_minimizes_data_retention(self):
        result = DD4_UnnecessaryDataRetention._test(self.node2, self.dfd)
        self.assertTrue(result)
        DD4_UnnecessaryDataRetention.set_status(self.node2)
        self.assertTrue(
            DD4_UnnecessaryDataRetention.req_status
            == "Data retention minimized = False"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = DD4_UnnecessaryDataRetention._test(self.node4, self.dfd)
        self.assertFalse(result)


class TestDD5_OverexposurePersonalData(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define anything should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:Process"]
        )
        # Node that doesnt minimize data sharing should trigger if handles personal data
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"data_sharing_minimized": False},
            tags=["STRIDE:Process"],
        )
        self.node4 = Node(
            id="n4",
            name="ProcessD",
            attributes={"data_sharing_minimized": False, "handles_personal_data": True},
            tags=["STRIDE:Process"],
        )
        # Node that does minimize data sharing shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"data_sharing_minimized": True},
            tags=["STRIDE:DataStore"],
        )
        self.node5 = Node(
            id="n5",
            name="ProcessE",
            attributes={"data_sharing_minimized": True, "handles_personal_data": True},
            tags=["STRIDE:Process"],
        )

        # Node that doesn't store personal data shouldn't trigger
        self.node6 = Node(
            id="n6",
            name="ProcessF",
            attributes={"handles_personal_data": False},
            tags=["STRIDE:Process"],
        )
        self.node7 = Node(
            id="n7",
            name="ProcessG",
            attributes={
                "handles_personal_data": False,
                "data_sharing_minimized": False,
            },
            tags=["STRIDE:DataStore"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node8 = Node(
            id="n8", name="ProcessH", attributes={}, tags=["STRIDE:Interactor"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
                "node5": self.node5,
                "node6": self.node6,
                "node7": self.node7,
                "node8": self.node8,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = DD5_OverexposurePersonalData._test(self.node1, self.dfd)
        self.assertTrue(result)
        DD5_OverexposurePersonalData.set_status(self.node1)
        self.assertTrue(
            DD5_OverexposurePersonalData.req_status
            == "Attribute missing: Data sharing minimized\n"
            + "Attribute missing: Handles personal data"
        )

    def test_rule_doesnt_apply_if_data_sharing_minimized(self):
        result = DD5_OverexposurePersonalData._test(self.node3, self.dfd)
        self.assertFalse(result)
        result = DD5_OverexposurePersonalData._test(self.node5, self.dfd)
        self.assertFalse(result)
        result = DD5_OverexposurePersonalData._test(self.node6, self.dfd)
        self.assertFalse(result)
        result = DD5_OverexposurePersonalData._test(self.node7, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_minimized_data_sharing(self):
        result = DD5_OverexposurePersonalData._test(self.node2, self.dfd)
        self.assertTrue(result)
        DD5_OverexposurePersonalData.set_status(self.node2)
        self.assertTrue(
            DD5_OverexposurePersonalData.req_status
            == "Data sharing minimized = False\n"
            + "Attribute missing: Handles personal data"
        )
        result = DD5_OverexposurePersonalData._test(self.node4, self.dfd)
        self.assertTrue(result)
        DD5_OverexposurePersonalData.set_status(self.node4)
        self.assertTrue(
            DD5_OverexposurePersonalData.req_status
            == "Data sharing minimized = False\n" + "Handles personal data = True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = DD5_OverexposurePersonalData._test(self.node8, self.dfd)
        self.assertFalse(result)


# ===== Unawareness and Unintervenability: ================
class TestU1_InsufficientTransparency(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define anything should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:Interactor"]
        )
        # Node that doesn't get informed about data collection should trigger
        # ...if it is a user
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"data_collection_informed": False},
            tags=["STRIDE:Interactor"],
        )
        self.node4 = Node(
            id="n4",
            name="ProcessD",
            attributes={"data_collection_informed": False, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        self.node8 = Node(
            id="n8",
            name="ProcessH",
            attributes={"is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that does inform about personal data shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"data_collection_informed": True},
            tags=["STRIDE:Interactor"],
        )
        self.node5 = Node(
            id="n5",
            name="ProcessE",
            attributes={"data_collection_informed": True, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that isn't a user shouldn't trigger
        self.node6 = Node(
            id="n6",
            name="ProcessF",
            attributes={"is_user": False},
            tags=["STRIDE:Interactor"],
        )
        self.node7 = Node(
            id="n7",
            name="ProcessG",
            attributes={"data_collection_informed": False, "is_user": False},
            tags=["STRIDE:Interactor"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node9 = Node(
            id="n9", name="ProcessI", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
                "node5": self.node5,
                "node6": self.node6,
                "node7": self.node7,
                "node8": self.node8,
                "node9": self.node9,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = U1_InsufficientTransparency._test(self.node1, self.dfd)
        self.assertTrue(result)
        U1_InsufficientTransparency.set_status(self.node1)
        self.assertTrue(
            U1_InsufficientTransparency.req_status
            == "Attribute missing: Informs about data collection\n"
            + "Attribute missing: Is a user"
        )

    def test_rule_doesnt_apply_if_informs_about_personal_data(self):
        result = U1_InsufficientTransparency._test(self.node3, self.dfd)
        self.assertFalse(result)
        result = U1_InsufficientTransparency._test(self.node5, self.dfd)
        self.assertFalse(result)

    def test_rule_doesnt_apply_if_not_a_user(self):
        result = U1_InsufficientTransparency._test(self.node6, self.dfd)
        self.assertFalse(result)
        result = U1_InsufficientTransparency._test(self.node7, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_informs_about_personal_data(self):
        result = U1_InsufficientTransparency._test(self.node2, self.dfd)
        self.assertTrue(result)
        U1_InsufficientTransparency.set_status(self.node2)
        self.assertTrue(
            U1_InsufficientTransparency.req_status
            == "Informs about data collection = False\n"
            + "Attribute missing: Is a user"
        )
        result = U1_InsufficientTransparency._test(self.node4, self.dfd)
        self.assertTrue(result)
        U1_InsufficientTransparency.set_status(self.node4)
        self.assertTrue(
            U1_InsufficientTransparency.req_status
            == "Informs about data collection = False\n" + "Is a user = True"
        )
        result = U1_InsufficientTransparency._test(self.node8, self.dfd)
        self.assertTrue(result)
        U1_InsufficientTransparency.set_status(self.node8)
        self.assertTrue(
            U1_InsufficientTransparency.req_status
            == "Attribute missing: Informs about data collection\n" + "Is a user = True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = U1_InsufficientTransparency._test(self.node9, self.dfd)
        self.assertFalse(result)


class TestU2_InsufficientTransparencyOthers(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define anything should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:Interactor"]
        )
        # Node that doesn't get informed about data collection should trigger
        # ...if it is a user
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"data_collection_informed": False},
            tags=["STRIDE:Interactor"],
        )
        self.node4 = Node(
            id="n4",
            name="ProcessD",
            attributes={"data_collection_informed": False, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        self.node8 = Node(
            id="n8",
            name="ProcessH",
            attributes={"is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that gets informed about personal data shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"data_collection_informed": True},
            tags=["STRIDE:Interactor"],
        )
        self.node5 = Node(
            id="n5",
            name="ProcessE",
            attributes={"data_collection_informed": True, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that isn't a user shouldn't trigger
        self.node6 = Node(
            id="n6",
            name="ProcessF",
            attributes={"is_user": False},
            tags=["STRIDE:Interactor"],
        )
        self.node7 = Node(
            id="n7",
            name="ProcessG",
            attributes={"data_collection_informed": False, "is_user": False},
            tags=["STRIDE:Interactor"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node9 = Node(
            id="n9", name="ProcessI", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
                "node5": self.node5,
                "node6": self.node6,
                "node7": self.node7,
                "node8": self.node8,
                "node9": self.node9,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = U2_InsufficientTransparencyOthers._test(self.node1, self.dfd)
        self.assertTrue(result)
        U2_InsufficientTransparencyOthers.set_status(self.node1)
        self.assertTrue(
            U2_InsufficientTransparencyOthers.req_status
            == "Attribute missing: Informs about data collection\n"
            + "Attribute missing: Is a user"
        )

    def test_rule_doesnt_apply_if_informs_about_personal_data(self):
        result = U2_InsufficientTransparencyOthers._test(self.node3, self.dfd)
        self.assertFalse(result)
        result = U2_InsufficientTransparencyOthers._test(self.node5, self.dfd)
        self.assertFalse(result)

    def test_rule_doesnt_apply_if_not_a_user(self):
        result = U2_InsufficientTransparencyOthers._test(self.node6, self.dfd)
        self.assertFalse(result)
        result = U2_InsufficientTransparencyOthers._test(self.node7, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_informs_about_personal_data(self):
        result = U2_InsufficientTransparencyOthers._test(self.node2, self.dfd)
        self.assertTrue(result)
        U2_InsufficientTransparencyOthers.set_status(self.node2)
        self.assertTrue(
            U2_InsufficientTransparencyOthers.req_status
            == "Informs about data collection = False\n"
            + "Attribute missing: Is a user"
        )
        result = U2_InsufficientTransparencyOthers._test(self.node4, self.dfd)
        self.assertTrue(result)
        U2_InsufficientTransparencyOthers.set_status(self.node4)
        self.assertTrue(
            U2_InsufficientTransparencyOthers.req_status
            == "Informs about data collection = False\n" + "Is a user = True"
        )
        result = U2_InsufficientTransparencyOthers._test(self.node8, self.dfd)
        self.assertTrue(result)
        U2_InsufficientTransparencyOthers.set_status(self.node8)
        self.assertTrue(
            U2_InsufficientTransparencyOthers.req_status
            == "Attribute missing: Informs about data collection\n" + "Is a user = True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = U2_InsufficientTransparencyOthers._test(self.node9, self.dfd)
        self.assertFalse(result)


class TestU3_InsufficientPrivacyControls(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define anything should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:Interactor"]
        )
        # Node that doesn't get data preference options should trigger if it is a user
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"personal_data_preferences": False},
            tags=["STRIDE:Interactor"],
        )
        self.node4 = Node(
            id="n4",
            name="ProcessD",
            attributes={"personal_data_preferences": False, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        self.node8 = Node(
            id="n8",
            name="ProcessH",
            attributes={"is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that gets data preference options shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"personal_data_preferences": True},
            tags=["STRIDE:Interactor"],
        )
        self.node5 = Node(
            id="n5",
            name="ProcessE",
            attributes={"personal_data_preferences": True, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that isn't a user shouldn't trigger
        self.node6 = Node(
            id="n6",
            name="ProcessF",
            attributes={"is_user": False},
            tags=["STRIDE:Interactor"],
        )
        self.node7 = Node(
            id="n7",
            name="ProcessG",
            attributes={"personal_data_preferences": False, "is_user": False},
            tags=["STRIDE:Interactor"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node9 = Node(
            id="n9", name="ProcessI", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
                "node5": self.node5,
                "node6": self.node6,
                "node7": self.node7,
                "node8": self.node8,
                "node9": self.node9,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = U3_InsufficientPrivacyControls._test(self.node1, self.dfd)
        self.assertTrue(result)
        U3_InsufficientPrivacyControls.set_status(self.node1)
        self.assertTrue(
            U3_InsufficientPrivacyControls.req_status
            == "Attribute missing: Personal data preferences\n"
            + "Attribute missing: Is a user"
        )

    def test_rule_doesnt_apply_if_informs_about_personal_data(self):
        result = U3_InsufficientPrivacyControls._test(self.node3, self.dfd)
        self.assertFalse(result)
        result = U3_InsufficientPrivacyControls._test(self.node5, self.dfd)
        self.assertFalse(result)

    def test_rule_doesnt_apply_if_not_a_user(self):
        result = U3_InsufficientPrivacyControls._test(self.node6, self.dfd)
        self.assertFalse(result)
        result = U3_InsufficientPrivacyControls._test(self.node7, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_informs_about_personal_data(self):
        result = U3_InsufficientPrivacyControls._test(self.node2, self.dfd)
        self.assertTrue(result)
        U3_InsufficientPrivacyControls.set_status(self.node2)
        self.assertTrue(
            U3_InsufficientPrivacyControls.req_status
            == "Personal data preferences = False\n" + "Attribute missing: Is a user"
        )
        result = U3_InsufficientPrivacyControls._test(self.node4, self.dfd)
        self.assertTrue(result)
        U3_InsufficientPrivacyControls.set_status(self.node4)
        self.assertTrue(
            U3_InsufficientPrivacyControls.req_status
            == "Personal data preferences = False\n" + "Is a user = True"
        )
        result = U3_InsufficientPrivacyControls._test(self.node8, self.dfd)
        self.assertTrue(result)
        U3_InsufficientPrivacyControls.set_status(self.node8)
        self.assertTrue(
            U3_InsufficientPrivacyControls.req_status
            == "Attribute missing: Personal data preferences\n" + "Is a user = True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = U3_InsufficientPrivacyControls._test(self.node9, self.dfd)
        self.assertFalse(result)


class TestU4_InsufficientAccess(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define anything should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:Interactor"]
        )
        # Node that doesn't have access to own data should trigger if it is a user
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"own_data_access": False},
            tags=["STRIDE:Interactor"],
        )
        self.node4 = Node(
            id="n4",
            name="ProcessD",
            attributes={"own_data_access": False, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        self.node8 = Node(
            id="n8",
            name="ProcessH",
            attributes={"is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that does have access to own data shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"own_data_access": True},
            tags=["STRIDE:Interactor"],
        )
        self.node5 = Node(
            id="n5",
            name="ProcessE",
            attributes={"own_data_access": True, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that isn't a user shouldn't trigger
        self.node6 = Node(
            id="n6",
            name="ProcessF",
            attributes={"is_user": False},
            tags=["STRIDE:Interactor"],
        )
        self.node7 = Node(
            id="n7",
            name="ProcessG",
            attributes={"own_data_access": False, "is_user": False},
            tags=["STRIDE:Interactor"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node9 = Node(
            id="n9", name="ProcessI", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
                "node5": self.node5,
                "node6": self.node6,
                "node7": self.node7,
                "node8": self.node8,
                "node9": self.node9,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = U4_InsufficientAccess._test(self.node1, self.dfd)
        self.assertTrue(result)
        U4_InsufficientAccess.set_status(self.node1)
        self.assertTrue(
            U4_InsufficientAccess.req_status
            == "Attribute missing: Own data access\n" + "Attribute missing: Is a user"
        )

    def test_rule_doesnt_apply_if_can_access_own_data(self):
        result = U4_InsufficientAccess._test(self.node3, self.dfd)
        self.assertFalse(result)
        result = U4_InsufficientAccess._test(self.node5, self.dfd)
        self.assertFalse(result)

    def test_rule_doesnt_apply_if_not_a_user(self):
        result = U4_InsufficientAccess._test(self.node6, self.dfd)
        self.assertFalse(result)
        result = U4_InsufficientAccess._test(self.node7, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_cant_access_own_data(self):
        result = U4_InsufficientAccess._test(self.node2, self.dfd)
        self.assertTrue(result)
        U4_InsufficientAccess.set_status(self.node2)
        self.assertTrue(
            U4_InsufficientAccess.req_status
            == "Own data access = False\n" + "Attribute missing: Is a user"
        )
        result = U4_InsufficientAccess._test(self.node4, self.dfd)
        self.assertTrue(result)
        U4_InsufficientAccess.set_status(self.node4)
        self.assertTrue(
            U4_InsufficientAccess.req_status
            == "Own data access = False\n" + "Is a user = True"
        )
        result = U4_InsufficientAccess._test(self.node8, self.dfd)
        self.assertTrue(result)
        U4_InsufficientAccess.set_status(self.node8)
        self.assertTrue(
            U4_InsufficientAccess.req_status
            == "Attribute missing: Own data access\n" + "Is a user = True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = U4_InsufficientAccess._test(self.node9, self.dfd)
        self.assertFalse(result)


class TestU5_InsufficientErasure(unittest.TestCase):
    def setUp(self):
        # Node that doesn't define anything should trigger
        self.node1 = Node(
            id="n1", name="ProcessA", attributes={}, tags=["STRIDE:Interactor"]
        )
        # Node that can't modify own data should trigger if it is a user
        self.node2 = Node(
            id="n2",
            name="ProcessB",
            attributes={"own_data_modification": False},
            tags=["STRIDE:Interactor"],
        )
        self.node4 = Node(
            id="n4",
            name="ProcessD",
            attributes={"own_data_modification": False, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        self.node8 = Node(
            id="n8",
            name="ProcessH",
            attributes={"is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that can mofify own data shouldn't trigger
        self.node3 = Node(
            id="n3",
            name="ProcessC",
            attributes={"own_data_modification": True},
            tags=["STRIDE:Interactor"],
        )
        self.node5 = Node(
            id="n5",
            name="ProcessE",
            attributes={"own_data_modification": True, "is_user": True},
            tags=["STRIDE:Interactor"],
        )
        # Node that isn't a user shouldn't trigger
        self.node6 = Node(
            id="n6",
            name="ProcessF",
            attributes={"is_user": False},
            tags=["STRIDE:Interactor"],
        )
        self.node7 = Node(
            id="n7",
            name="ProcessG",
            attributes={"own_data_modification": False, "is_user": False},
            tags=["STRIDE:Interactor"],
        )
        # Node with not applicable tag shouldn't trigger
        self.node9 = Node(
            id="n9", name="ProcessI", attributes={}, tags=["STRIDE:Process"]
        )

        # Diagram setup
        self.dfd = DataflowDiagram(
            name="Test DFD",
            id="d1",
            nodes={
                "node1": self.node1,
                "node2": self.node2,
                "node3": self.node3,
                "node4": self.node4,
                "node5": self.node5,
                "node6": self.node6,
                "node7": self.node7,
                "node8": self.node8,
                "node9": self.node9,
            },
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = U5_InsufficientErasure._test(self.node1, self.dfd)
        self.assertTrue(result)
        U5_InsufficientErasure.set_status(self.node1)
        self.assertTrue(
            U5_InsufficientErasure.req_status
            == "Attribute missing: Own data modification\n"
            + "Attribute missing: Is a user"
        )

    def test_rule_doesnt_apply_if_can_modify_own_data(self):
        result = U5_InsufficientErasure._test(self.node3, self.dfd)
        self.assertFalse(result)
        result = U5_InsufficientErasure._test(self.node5, self.dfd)
        self.assertFalse(result)

    def test_rule_doesnt_apply_if_not_a_user(self):
        result = U5_InsufficientErasure._test(self.node6, self.dfd)
        self.assertFalse(result)
        result = U5_InsufficientErasure._test(self.node7, self.dfd)
        self.assertFalse(result)

    def test_rule_does_apply_if_cant_modify_own_data(self):
        result = U5_InsufficientErasure._test(self.node2, self.dfd)
        self.assertTrue(result)
        U5_InsufficientErasure.set_status(self.node2)
        self.assertTrue(
            U5_InsufficientErasure.req_status
            == "Own data modification = False\n" + "Attribute missing: Is a user"
        )
        result = U5_InsufficientErasure._test(self.node4, self.dfd)
        self.assertTrue(result)
        U5_InsufficientErasure.set_status(self.node4)
        self.assertTrue(
            U5_InsufficientErasure.req_status
            == "Own data modification = False\n" + "Is a user = True"
        )
        result = U5_InsufficientErasure._test(self.node8, self.dfd)
        self.assertTrue(result)
        U5_InsufficientErasure.set_status(self.node8)
        self.assertTrue(
            U5_InsufficientErasure.req_status
            == "Attribute missing: Own data modification\n" + "Is a user = True"
        )

    def test_rule_doesnt_apply_if_wrong_tag(self):
        result = U5_InsufficientErasure._test(self.node9, self.dfd)
        self.assertFalse(result)


# ===== Non-Compliance: ===================================
class TestNc1_NonCompliantProcessing(unittest.TestCase):
    def setUp(self):
        # DFD that doesn't define anything should trigger
        self.dfd1 = DataflowDiagram(
            name="Test DFD1", id="d1", attributes={}, nodes={}, edges={}, clusters={}
        )
        # DFD that doesn't comply with privacy regulations should trigger
        self.dfd2 = DataflowDiagram(
            name="Test DFD2",
            id="d2",
            attributes={"privacy_regulation_compliance": False},
            nodes={},
            edges={},
            clusters={},
        )
        # DFD that does comply with privacy regulations shouldn't trigger
        self.dfd3 = DataflowDiagram(
            name="Test DFD3",
            id="d3",
            attributes={"privacy_regulation_compliance": True},
            nodes={},
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = Nc1_NonCompliantProcessing._test(self.dfd1)
        self.assertTrue(result)
        Nc1_NonCompliantProcessing.set_status(self.dfd1)
        self.assertTrue(
            Nc1_NonCompliantProcessing.req_status
            == "Attribute missing: Privacy regulation compliance"
        )

    def test_rule_doesnt_apply_if_complies_with_regulations(self):
        result = Nc1_NonCompliantProcessing._test(self.dfd3)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_complies_with_regulations(self):
        result = Nc1_NonCompliantProcessing._test(self.dfd2)
        self.assertTrue(result)
        Nc1_NonCompliantProcessing.set_status(self.dfd2)
        self.assertTrue(
            Nc1_NonCompliantProcessing.req_status
            == "Privacy regulation compliance = False"
        )


class TestNc2_NonAdherencePrivacyStandards(unittest.TestCase):
    def setUp(self):
        # DFD that doesn't define anything should trigger
        self.dfd1 = DataflowDiagram(
            name="Test DFD1", id="d1", attributes={}, nodes={}, edges={}, clusters={}
        )
        # DFD that doesn't comply with privacy regulations should trigger
        self.dfd2 = DataflowDiagram(
            name="Test DFD2",
            id="d2",
            attributes={"privacy_standards_compliance": False},
            nodes={},
            edges={},
            clusters={},
        )
        # DFD that does comply with privacy regulations shouldn't trigger
        self.dfd3 = DataflowDiagram(
            name="Test DFD3",
            id="d3",
            attributes={"privacy_standards_compliance": True},
            nodes={},
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = Nc2_NonAdherencePrivacyStandards._test(self.dfd1)
        self.assertTrue(result)
        Nc2_NonAdherencePrivacyStandards.set_status(self.dfd1)
        self.assertTrue(
            Nc2_NonAdherencePrivacyStandards.req_status
            == "Attribute missing: Privacy standards compliance"
        )

    def test_rule_doesnt_apply_if_complies_with_standards(self):
        result = Nc2_NonAdherencePrivacyStandards._test(self.dfd3)
        self.assertFalse(result)

    def test_rule_does_apply_if_not_complies_with_standards(self):
        result = Nc2_NonAdherencePrivacyStandards._test(self.dfd2)
        self.assertTrue(result)
        Nc2_NonAdherencePrivacyStandards.set_status(self.dfd2)
        self.assertTrue(
            Nc2_NonAdherencePrivacyStandards.req_status
            == "Privacy standards compliance = False"
        )


class TestNc3_ImproperDataLifecycle(unittest.TestCase):
    def setUp(self):
        # DFD that doesn't define anything should trigger
        self.dfd1 = DataflowDiagram(
            name="Test DFD1", id="d1", attributes={}, nodes={}, edges={}, clusters={}
        )
        # DFD that doesn't define a data lifecycle policy should trigger
        self.dfd2 = DataflowDiagram(
            name="Test DFD2",
            id="d2",
            attributes={"data_lifecycle_policy_exists": False},
            nodes={},
            edges={},
            clusters={},
        )
        # DFD that does have a data lifecycle policy defined shouldn't trigger
        self.dfd3 = DataflowDiagram(
            name="Test DFD3",
            id="d3",
            attributes={"data_lifecycle_policy_exists": True},
            nodes={},
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = Nc3_ImproperDataLifecycle._test(self.dfd1)
        self.assertTrue(result)
        Nc3_ImproperDataLifecycle.set_status(self.dfd1)
        self.assertTrue(
            Nc3_ImproperDataLifecycle.req_status
            == "Attribute missing: Data lifecycle policy exists"
        )

    def test_rule_doesnt_apply_if_policy_defined(self):
        result = Nc3_ImproperDataLifecycle._test(self.dfd3)
        self.assertFalse(result)

    def test_rule_does_apply_if_no_policy(self):
        result = Nc3_ImproperDataLifecycle._test(self.dfd2)
        self.assertTrue(result)
        Nc3_ImproperDataLifecycle.set_status(self.dfd2)
        self.assertTrue(
            Nc3_ImproperDataLifecycle.req_status
            == "Data lifecycle policy exists = False"
        )


class TestNc4_InsufficientProcessingSecurity(unittest.TestCase):
    def setUp(self):
        # DFD that doesn't define anything should trigger
        self.dfd1 = DataflowDiagram(
            name="Test DFD1", id="d1", attributes={}, nodes={}, edges={}, clusters={}
        )
        # DFD that doesn't comply with security standards should trigger
        self.dfd2 = DataflowDiagram(
            name="Test DFD2",
            id="d2",
            attributes={"security_standards_compliance": False},
            nodes={},
            edges={},
            clusters={},
        )
        # DFD that does comply with security standards shouldn't trigger
        self.dfd3 = DataflowDiagram(
            name="Test DFD3",
            id="d3",
            attributes={"security_standards_compliance": True},
            nodes={},
            edges={},
            clusters={},
        )

    def test_rule_does_apply_if_not_defined(self):
        result = Nc4_InsufficientProcessingSecurity._test(self.dfd1)
        self.assertTrue(result)
        Nc4_InsufficientProcessingSecurity.set_status(self.dfd1)
        self.assertTrue(
            Nc4_InsufficientProcessingSecurity.req_status
            == "Attribute missing: Security standards compliance"
        )

    def test_rule_doesnt_apply_if_security_compliance(self):
        result = Nc4_InsufficientProcessingSecurity._test(self.dfd3)
        self.assertFalse(result)

    def test_rule_does_apply_if_no_security_compliance(self):
        result = Nc4_InsufficientProcessingSecurity._test(self.dfd2)
        self.assertTrue(result)
        Nc4_InsufficientProcessingSecurity.set_status(self.dfd2)
        self.assertTrue(
            Nc4_InsufficientProcessingSecurity.req_status
            == "Security standards compliance = False"
        )
