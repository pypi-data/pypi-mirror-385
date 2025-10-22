# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

import typing

import pytest

from flowstrider.models import common_models, dataflowdiagram, threat, threat_management
from flowstrider.rules import elicit


@pytest.fixture
def data_dfd():
    node1 = common_models.Node(
        id="node1",
        name="Node 1 Name",
        tags=["STRIDE:Process"],
        attributes={},
    )
    node2 = common_models.Node(
        id="node2",
        name="Node 2 Name",
        tags=["STRIDE:DataStore"],
        attributes={},
    )
    edge1 = common_models.Edge(
        id="edge1",
        source_id="node2",
        sink_id="node1",
        name="Edge 1 Name",
        tags=["STRIDE:Dataflow"],
        attributes={},
    )
    cluster1 = common_models.Cluster(
        id="cluster1",
        node_ids="node1",
        name="Cluster 1 Name",
        tags=[],
        attributes={},
    )

    dfd = dataflowdiagram.DataflowDiagram(
        id="dfd_test_threat_management",
        nodes={"node1": node1, "node2": node2},
        edges={"edge1": edge1},
        clusters={"cluster1": cluster1},
        name="DFD Name",
        tags="bsi_rules",
    )

    return dfd


def test_update(data_dfd: dataflowdiagram.DataflowDiagram, capsys):
    management_db = threat_management.ThreatManagementDatabase()

    results: typing.List[threat.Threat] = elicit(data_dfd)

    # Fill threat management database based on dfd and threats found
    management_db.update(results, data_dfd)

    assert len(management_db.per_threat_information) == 14
    management_item_name_list = [
        "Hashing of Passwords@Node 2 Name",
        "Encryption of Confidential Data@Node 2 Name",
        "Authentication Protocols for SAN fabric@Node 2 Name",
        "Multi Factor Authentication@Node 1 Name",
        "Multi Factor Authentication@Node 2 Name",
        "Multi Factor Authentication for High Security@Node 1 Name",
        "Multi Factor Authentication for High Security@Node 2 Name",
        "Least Privileges@Node 1 Name",
        "Input Validation@Node 1 Name",
        "Signature of Logging Data@Node 2 Name",
        "Untrustworthy Data Flow@Edge 1 Name: Node 2 Name -> Node 1 Name",
        "Secure HTTP Configuration@Edge 1 Name: Node 2 Name -> Node 1 Name",
        "Integrity of External Entities@Edge 1 Name: Node 2 Name -> Node 1 Name",
        "Use of Proxies@Edge 1 Name: Node 2 Name -> Node 1 Name",
    ]
    management_item_id_list = [
        "HashedPasswordsNodeRule@node2",
        "EncryptionOfConfidentialDataNodeRule@node2",
        "AuthenticationProtocolNodeRule@node2",
        "MFANodeRule@node1",
        "MFANodeRule@node2",
        "MFAHighSecurityNodeRule@node1",
        "MFAHighSecurityNodeRule@node2",
        "PermissionNodeRule@node1",
        "InputValidationNodeRule@node1",
        "LoggingDataNodeRule@node2",
        "UntrustworthyDataflowEdgeRule@edge1",
        "SecureHTTPConfigEdgeRule@edge1",
        "IntegrityOfExternalEntitiesEdgeRule@edge1",
        "UseOfProxiesEdgeRule@edge1",
    ]
    for item_name in management_item_name_list:
        assert item_name in management_db.per_threat_information
        assert (
            management_db.per_threat_information[item_name].uid
            in management_item_id_list
        )
        assert (
            management_db.per_threat_information[item_name].management_state
            == threat_management.ThreatManagementState.Undecided
        )

    # Change some management states
    key = "Hashing of Passwords@Node 2 Name"
    old_item = management_db.per_threat_information[key]
    new_item = threat_management.ThreatManagementItem(
        old_item.uid,
        threat_management.ThreatManagementState.Accept,
        "Example explanation 1",
    )
    management_db.per_threat_information[key] = new_item

    key = "Multi Factor Authentication for High Security@Node 1 Name"
    old_item = management_db.per_threat_information[key]
    new_item = threat_management.ThreatManagementItem(
        old_item.uid,
        threat_management.ThreatManagementState.Mitigate,
        "Example explanation 2",
    )
    management_db.per_threat_information[key] = new_item

    key = "Use of Proxies@Edge 1 Name: Node 2 Name -> Node 1 Name"
    old_item = management_db.per_threat_information[key]
    new_item = threat_management.ThreatManagementItem(
        old_item.uid,
        threat_management.ThreatManagementState.Delegated,
        "Example explanation 3",
    )
    management_db.per_threat_information[key] = new_item

    # Change names of some elements in the dfd
    old_node = data_dfd.nodes["node1"]
    new_node = common_models.Node(
        old_node.id, "Node 1 new Name", old_node.tags, old_node.attributes
    )
    data_dfd.nodes["node1"] = new_node

    old_node = data_dfd.nodes["node2"]
    new_node = common_models.Node(
        old_node.id, "Node 2 new Name", old_node.tags, old_node.attributes
    )
    data_dfd.nodes["node2"] = new_node

    old_edge = data_dfd.edges["edge1"]
    new_edge = common_models.Edge(
        old_edge.id,
        old_edge.source_id,
        old_edge.sink_id,
        "Edge 1 new Name",
        old_edge.tags,
        old_edge.attributes,
    )
    data_dfd.edges["edge1"] = new_edge

    # After changing names of elements and updating, the old management states
    # ...should still be saved
    results: typing.List[threat.Threat] = elicit(data_dfd)

    management_db.update(results, data_dfd)

    assert len(management_db.per_threat_information) == 14
    management_item_name_list = [
        "Hashing of Passwords@Node 2 new Name",
        "Encryption of Confidential Data@Node 2 new Name",
        "Authentication Protocols for SAN fabric@Node 2 new Name",
        "Multi Factor Authentication@Node 1 new Name",
        "Multi Factor Authentication@Node 2 new Name",
        "Multi Factor Authentication for High Security@Node 1 new Name",
        "Multi Factor Authentication for High Security@Node 2 new Name",
        "Least Privileges@Node 1 new Name",
        "Input Validation@Node 1 new Name",
        "Signature of Logging Data@Node 2 new Name",
        "Untrustworthy Data Flow@Edge 1 new Name: Node 2 new Name -> Node 1 new Name",
        "Secure HTTP Configuration@Edge 1 new Name: Node 2 new Name -> Node 1 new Name",
        "Integrity of External Entities@Edge 1 new Name: Node 2 new Name -> Node 1 new "
        + "Name",
        "Use of Proxies@Edge 1 new Name: Node 2 new Name -> Node 1 new Name",
    ]
    for item_name in management_item_name_list:
        assert item_name in management_db.per_threat_information
        assert (
            management_db.per_threat_information[item_name].uid
            in management_item_id_list
        )

    # Check if old management states are still to be found
    assert (
        management_db.per_threat_information[
            "Hashing of Passwords@Node 2 new Name"
        ].management_state
        == threat_management.ThreatManagementState.Accept
    )
    assert (
        management_db.per_threat_information[
            "Hashing of Passwords@Node 2 new Name"
        ].explanation
        == "Example explanation 1"
    )
    assert (
        management_db.per_threat_information[
            "Multi Factor Authentication for High Security@Node 1 new Name"
        ].management_state
        == threat_management.ThreatManagementState.Mitigate
    )
    assert (
        management_db.per_threat_information[
            "Multi Factor Authentication for High Security@Node 1 new Name"
        ].explanation
        == "Example explanation 2"
    )
    assert (
        management_db.per_threat_information[
            "Use of Proxies@Edge 1 new Name: Node 2 new Name -> Node 1 new Name"
        ].management_state
        == threat_management.ThreatManagementState.Delegated
    )
    assert (
        management_db.per_threat_information[
            "Use of Proxies@Edge 1 new Name: Node 2 new Name -> Node 1 new Name"
        ].explanation
        == "Example explanation 3"
    )
    assert (
        management_db.per_threat_information[
            "Encryption of Confidential Data@Node 2 new Name"
        ].management_state
        == threat_management.ThreatManagementState.Undecided
    )
    assert (
        management_db.per_threat_information[
            "Encryption of Confidential Data@Node 2 new Name"
        ].explanation
        == ""
    )

    # When updating with less threats, the deleted threats should appear as a warning
    results: typing.List[threat.Threat] = elicit(data_dfd)
    results.pop()
    results.pop()

    management_db.update(results, data_dfd)

    assert len(management_db.per_threat_information) == 12

    captured = capsys.readouterr()
    assert (
        "Warning: the following non-empty threat management item has been deleted "
        + "because\nits corresponding threat doesn't exist anymore:\n\n"
        + "Use of Proxies@Edge 1 new Name: Node 2 new Name -> Node 1 new Name\n"
        + "uid: UseOfProxiesEdgeRule@edge1\n"
        + "State: Delegated\n"
        + "Explanation: Example explanation 3"
    ) in captured.out


def test_should_fail(data_dfd):
    management_db = threat_management.ThreatManagementDatabase()

    results: typing.List[threat.Threat] = elicit(data_dfd)

    # Fill threat management database based on dfd and threats found
    management_db.update(results, data_dfd)

    # Change management states of the management items
    key = "Encryption of Confidential Data@Node 2 Name"
    old_item = management_db.per_threat_information[key]
    new_item = threat_management.ThreatManagementItem(
        old_item.uid, threat_management.ThreatManagementState.Delegate, ""
    )
    management_db.per_threat_information[key] = new_item

    key = "Authentication Protocols for SAN fabric@Node 2 Name"
    old_item = management_db.per_threat_information[key]
    new_item = threat_management.ThreatManagementItem(
        old_item.uid, threat_management.ThreatManagementState.Mitigate, ""
    )
    management_db.per_threat_information[key] = new_item

    key = "Multi Factor Authentication@Node 1 Name"
    old_item = management_db.per_threat_information[key]
    new_item = threat_management.ThreatManagementItem(
        old_item.uid, threat_management.ThreatManagementState.Avoid, ""
    )
    management_db.per_threat_information[key] = new_item

    key = "Multi Factor Authentication@Node 2 Name"
    old_item = management_db.per_threat_information[key]
    new_item = threat_management.ThreatManagementItem(
        old_item.uid, threat_management.ThreatManagementState.Accept, ""
    )
    management_db.per_threat_information[key] = new_item

    key = "Multi Factor Authentication for High Security@Node 1 Name"
    old_item = management_db.per_threat_information[key]
    new_item = threat_management.ThreatManagementItem(
        old_item.uid, threat_management.ThreatManagementState.Delegated, ""
    )
    management_db.per_threat_information[key] = new_item

    key = "Multi Factor Authentication for High Security@Node 2 Name"
    old_item = management_db.per_threat_information[key]
    new_item = threat_management.ThreatManagementItem(
        old_item.uid, threat_management.ThreatManagementState.Mitigated, ""
    )
    management_db.per_threat_information[key] = new_item

    # With level 'all' there should still be 14 threats
    relevant_results = management_db.should_fail(results, data_dfd, "all")
    assert len(relevant_results) == 14
    for relevant_res in relevant_results:
        assert relevant_res in results

    # With level 'todo' there should be 11 threats left
    relevant_results = management_db.should_fail(results, data_dfd, "todo")
    assert len(relevant_results) == 11

    # With level 'undecided' there should be 8 threats left
    relevant_results = management_db.should_fail(results, data_dfd, "undecided")
    assert len(relevant_results) == 8

    # With level 'off' there should be no threats left
    relevant_results = management_db.should_fail(results, data_dfd, "off")
    assert len(relevant_results) == 0
