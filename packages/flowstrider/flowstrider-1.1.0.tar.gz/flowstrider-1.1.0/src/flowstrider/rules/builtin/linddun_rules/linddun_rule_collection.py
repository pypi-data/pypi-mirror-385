# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

# import re

from flowstrider import settings
from flowstrider.models import dataflowdiagram
from flowstrider.models.common_models import Edge, Node
from flowstrider.rules import attributes_dict
from flowstrider.rules.common_rules import (
    DataflowDiagramRule,
    DataflowDiagramRuleCollection,
    EdgeRule,
    NodeRule,
    meet_any_requirement,
)

tag_interactor = "STRIDE:Interactor"
tag_process = "STRIDE:Process"
tag_datastore = "STRIDE:DataStore"


# Rules derived from LINDDUN https://linddun.org/
# ...especially the LINDDUN GO cards https://linddun.org/go/


# ===== LINKING: ==========================================
class L1_LinkedUserRequests(EdgeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "L1"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Linked User Requests")
        cls.short_description = _(
            "User requests can be linked because they contain a unique identifier"
        )
        cls.long_description = (
            _(
                "A unique identifier means different requests/data can be linked to a"
                + " singular user profile or a specific group. Unique identifiers can"
                + " exist globally or locally, within the system or across the context"
                + " boundary. Examples: IP address or email address. Even if the"
                + " identifier does not reveal one's identity directly, accumulated"
                + " amounts of personal data can lead to 'identifying' threats."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["transmits_unique_user_id"]

        cls.mitigation_options = [_("Remove unique identifiers")]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, edge: Edge, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        potentially_transmits_uuid = not meet_any_requirement(
            edge.attributes.get(cls.attribute_names[0], True), [False]
        )

        return potentially_transmits_uuid


class L2_LinkableUserRequests(EdgeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "L2"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Linkable User Requests Through Combination")
        cls.short_description = _(
            "User requests can be linked because they contain attributes that can be"
            + " combined into quasi-identifiers"
        )
        cls.long_description = (
            _(
                "Many requests contain a lot of different properties that, when"
                + " combined, pose quasi-identifiers enabling the linking to unique"
                + " individuals or groups. Examples for these properties: OS, browser,"
                + " display size, language. Even if the properties do not reveal one's"
                + " identity directly, accumulated amounts of personal data can lead to"
                + " 'identifying' threats."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["transmits_user_properties"]

        cls.mitigation_options = [_("Minimize user properties being transmitted")]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, edge: Edge, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        potentially_transmits_quasi_id = not meet_any_requirement(
            edge.attributes.get(cls.attribute_names[0], True), [False]
        )

        return potentially_transmits_quasi_id


class L3_LinkableUserPatterns(EdgeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "L3"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Linkable User Requests Through Patterns")
        cls.short_description = _(
            "Patterns in the (meta)data contained in user requests can be used to link"
            + " them to each other"
        )
        cls.long_description = (
            _(
                "Profiles can be constructed to distinguish users from one another and"
                + " accumulate associated data. Dinstinguishing can happen based on"
                + " things like the timing of messages, the writing style or other"
                + " message patterns. Even if this data does not reveal one's identity"
                + " directly, accumulated amounts of personal data can lead to"
                + " 'identifying' threats."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["transmits_user_data"]

        cls.mitigation_options = [
            _("Transmit decoy requests"),
            _("Minimize user properties being transmitted"),
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, edge: Edge, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        potentially_transmits_metadata = not meet_any_requirement(
            edge.attributes.get(cls.attribute_names[0], True), [False]
        )

        return potentially_transmits_metadata


class L4_LinkableDataset(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "L4"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Linkable Dataset")
        cls.short_description = _("Stored personal data can be linked to individuals")
        cls.long_description = (
            _(
                "Data can contain a lot of different properties that, when combined,"
                + " pose quasi-identifiers enabling the linking of data to unique"
                + " individuals or groups. An example would be querying average salary"
                + " with a strict set of criteria to reveal the salary of an individual"
                + " employee. Even if the properties do not reveal one's identity"
                + " directly, accumulated amounts of personal data can lead to"
                + " 'identifying' threats."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["handles_user_data"]

        cls.mitigation_options = [_("Minimize collection and storage of user data")]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags

        could_handle_user_data = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return is_data_store and could_handle_user_data


class L5_ProfilingUsers(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "L5"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Profiling Users")
        cls.short_description = _(
            "Users can be profiled by analyzing their data for patterns"
        )
        cls.long_description = (
            _(
                "It may be possible to derive data about individuals by analyzing their"
                + " data. Adversaries could try to collect as much detailed data as"
                + " possible to link data that wasn't intended to be linked. Example:"
                + " Infering a persons medical condition by the frequency of data"
                + " exchanges with a health monitoring machine."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["handles_user_data"]

        cls.mitigation_options = [
            _("Minimize collection and storage of user data"),
            _("Leave out unnecessarily detailed data"),
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_process = tag_process in node.tags

        could_handle_user_data = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return is_process and could_handle_user_data


# ===== Identifying: ======================================
class I1_IdentifiedUserRequests(EdgeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "I1"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Identified User Requests")
        cls.short_description = _(
            "The incoming user requests contain data that directly reveal the user"
            + " identity"
        )
        cls.long_description = (
            _(
                "Individuals may be identified directly through data sent to the system"
                + " such as their full name. Identified data can severely amplify the"
                + " impact of future data breaches and needs stronger security"
                + " measures."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["transmits_user_identity"]

        cls.mitigation_options = [_("Minimize transmission of user identities")]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, edge: Edge, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        could_transmit_ui = not meet_any_requirement(
            edge.attributes.get(cls.attribute_names[0], True), [False]
        )

        return could_transmit_ui


class I2_IdentifiableUserRequests(EdgeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "I2"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Identifiable User Requests")
        cls.short_description = _(
            "The user can be identified because the data in their requests can be used"
            + " to infer who they are"
        )
        cls.long_description = (
            _(
                "Individuals may be identified through data sent to the system. This"
                + " data does not have to be identity information but can still be"
                + " unintentionally specific to a user. Examples: looking up nearby"
                + " businesses, info about a rare illness or specific timing."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["transmits_user_data"]

        cls.mitigation_options = [_("Minimize transmission of user data")]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, edge: Edge, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        could_transmit_user_data = not meet_any_requirement(
            edge.attributes.get(cls.attribute_names[0], True), [False]
        )

        return could_transmit_user_data


class I3_IdentifiableDataFlows(EdgeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "I3"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Identifiable Data Flows")
        cls.short_description = _(
            "Data sent to the system is sufficiently revealing to identify the user"
        )
        cls.long_description = (
            _(
                "Individuals may be identified through identifiable attributes in"
                + " user-submitted data. For example in a feedback form."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["transmits_user_data"]

        cls.mitigation_options = [_("Minimize transmission of user data")]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, edge: Edge, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        could_transmit_user_data = not meet_any_requirement(
            edge.attributes.get(cls.attribute_names[0], True), [False]
        )

        return could_transmit_user_data


class I4_IdentifiableDataRequests(EdgeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "I4"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Identifiable Data Requests")
        cls.short_description = _("Communication contains (quasi-)identifiers")
        cls.long_description = (
            _(
                "Individuals may be identified through quasi-identifiers such as"
                + " IP-address or email-address. The use of pseudonyms to refer to"
                + " individuals may also lead to the identification of the person"
                + " behind it. The possibility of identification rises with the amount"
                + " of data connected with the quasi-identifier and the number of"
                + " services using it."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["transmits_unique_user_id"]

        cls.mitigation_options = [
            _("Remove unique identifiers"),
            _("Don't reuse identifiers in another service"),
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, edge: Edge, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        could_transmit_uui = not meet_any_requirement(
            edge.attributes.get(cls.attribute_names[0], True), [False]
        )

        return could_transmit_uui


class I5_IdentifiableDataset(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "I5"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Identifiable Dataset")
        cls.short_description = _("Stored data can be used to identify individuals")
        cls.long_description = (
            _(
                "Individuals may be identified through connection of unique references"
                + " to an individual or their data. The use of pseudonyms to refer to"
                + " individuals may lead to the identification of the person behind it."
                + " The possibility of identification rises with the amount of data"
                + " connected with the quasi-identifier and the number of services"
                + " using it."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["handles_user_data"]

        cls.mitigation_options = [
            _("Minimize collection and storage of user data"),
            _("Don't reuse identifiers in another service"),
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags

        could_handle_user_data = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return is_data_store and could_handle_user_data


# ===== Non-Repudiation: ==================================
class Nr1_NonRepudiationOfServiceUsage(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "Nr1"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Non-Repudiation of Service Usage")
        cls.short_description = _(
            "Users cannot deny having used a service because of authentication or"
            + " logged access"
        )
        cls.long_description = (
            _(
                "If a service stores credentials with identity information, the"
                + " individuals deniability gets affected. For example: log files"
                + " linking an entry in an internal complaint system to an individual"
                + " employee."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["logs_access"]

        cls.mitigation_options = [
            _(
                "If deniability is required, do not store the data at all or remove any"
                + " attributable data."
            ),
            _("Avoid credentials with identity information."),
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_process = tag_process in node.tags

        could_log_access = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return is_process and could_log_access


class Nr2_NonRepudiationOfSending(EdgeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "Nr2"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Non-Repudiation of Sending")
        cls.short_description = _("Users cannot deny having sent a message")
        cls.long_description = (
            _(
                "Sent or uploaded data that is digitally signed affects the individuals"
                + " deniability. For example: signed emails but also documents,"
                + " requests, etc."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["transmits_signed_data"]

        cls.mitigation_options = [_("Don't require data to be signed")]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, edge: Edge, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        could_sign_data = not meet_any_requirement(
            edge.attributes.get(cls.attribute_names[0], True), [False]
        )

        return could_sign_data


class Nr3_NonRepudiationOfReceipt(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "Nr3"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Non-Repudiation of Receipt")
        cls.short_description = _("Users cannot deny having received a message")
        cls.long_description = (
            _(
                "If (passive) interactions with the system, such as receiving a"
                + " message, have side-effects like logging, the deniability of receipt"
                + " gets affected for the recipient."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["logs_receipt"]

        cls.mitigation_options = [
            _("Don't require read receipts from the recipient"),
            _("Don't log user's browser histories"),
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_process = tag_process in node.tags

        could_log_receipt = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return is_process and could_log_receipt


class Nr4_NonRepudiationOfStorage(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "Nr4"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Non-Repudiation of Storage")
        cls.short_description = _(
            "Users cannot deny claims about data stored in non-repudiable storage"
        )
        cls.long_description = (
            _(
                "If data stored in a database is digitally signed, the repudiation of"
                + " users gets affected. An example would be append-only storage"
                + " systems like blockchains where it is impossible for the data"
                + " subject to later remove their personal data."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["stores_signed_data"]

        cls.mitigation_options = [_("Don't require data to be signed")]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags

        could_store_signed_data = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return is_data_store and could_store_signed_data


class Nr5_NonRepudiationOfMetadata(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "Nr5"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Non-Repudiation of Hidden Data or Metadata")
        cls.short_description = _(
            "Hidden or metadata in a document prevent users from denying claims"
            + " associated with it"
        )
        cls.long_description = (
            _(
                "Metadata, hidden data or specific patterns in stored or transmitted"
                + " data may lead to undesirable deniability issues. For example,"
                + " author or revision metadata in documents or data watermarked with"
                + " hidden artifacts prevents users from denying claims about the data."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["stores_user_associated_metadata"]

        cls.mitigation_options = [_("Minimize included metadata")]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags

        could_store_metadata = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return is_data_store and could_store_metadata


# ===== Detecting: ========================================
class D1_DetectableUsers(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "D1"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Detectable Users")
        cls.short_description = _(
            "Inferring the existence of a user from the system's response"
        )
        cls.long_description = (
            _(
                "Systems may unintentionally reveal the existence of a user by the way"
                + " status messages respond to queries. This is especially relevant"
                + " with informational messages, warnings or errors which respond"
                + " differently when a user does not exist compared to not having"
                + " access rights. An example would be a 'wrong password' error"
                + " message revealing the existence of the account. Even though no"
                + " contents have been leaked, the existence of certain items alone can"
                + " be a stepping stone to security threats."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["discloses_responses", "handles_user_data"]

        cls.mitigation_options = [
            _(
                "Prevent information leakage by not revealing the existence of items in"
                + " system responses"
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags
        is_process = tag_process in node.tags

        could_handle_user_data = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[1], True), [False]
        )

        could_disclose_responses = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return (
            (is_process or is_data_store)
            and could_handle_user_data
            and could_disclose_responses
        )


class D2_DetectableServiceUsage(EdgeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "D2"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Detectable Service Usage")
        cls.short_description = _(
            "Detecting communication between a service and its users"
        )
        cls.long_description = (
            _(
                "If the communication from a user to a service can be observed,"
                + " information may be inferred from that. For example, communication"
                + " with the Tor network can be detected even though the destination is"
                + " concealed. Especially in sensitive contexts (medical,"
                + " whistleblower) the detection of service usage alone may have a"
                + " severe impact."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names1 = ["is_private_network"]

        cls.mitigation_options = (
            _("Minimize communications outside of private networks"),
            _("Transmit decoy data"),
        )
        cls.requirement = _(
            "Every communication outside of trust boundaries with property: "
            + "'{private_network} = True' will trigger this rule"
        ).format(
            private_network=attributes_dict.attributes[
                cls.attribute_names1[0]
            ].display_name
        )

    @classmethod
    def _test(cls, edge: Edge, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        source_clusters = dfd.get_clusters_for_node_id(edge.source_id)
        sink_clusters = dfd.get_clusters_for_node_id(edge.sink_id)

        source_sink_in_same_private_net = False

        # If sink and source aren't in the same private network cluster, trigger
        # ...(even if both are in a private network (but separate ones), the edge could
        # ...traverse a public network)
        for cluster in source_clusters:
            if meet_any_requirement(
                cluster.attributes.get(cls.attribute_names1[0], False), [True]
            ):
                for cluster2 in sink_clusters:
                    if cluster.id == cluster2.id:
                        source_sink_in_same_private_net = True

        if not source_sink_in_same_private_net:
            return True


class D3_DetectableEvents(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "D3"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Detectable Events")
        cls.short_description = _(
            "Detecting side effects or communications triggered by application events"
        )
        cls.long_description = (
            _(
                "Various (unknown) side effects may lead to the detection of used"
                + " applications or user actions. This can include log files on a"
                + " shared system, traces of temporary files by deleted applications"
                + " or the size of data. Sensitive information may be deduced from the"
                + " observation of these side effects."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["leaves_usage_traces"]

        cls.mitigation_options = [
            _(
                "Ensure that all log files get deleted and that deleted data doesn't "
                + "leave traces"
            ),
            _("Dummy traffic may be able to conceal the actual traffic"),
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags
        is_process = tag_process in node.tags

        could_leave_traces = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return (is_process or is_data_store) and could_leave_traces


class D4_DetectableRecords(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "D4"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Detectable Records")
        cls.short_description = _("Detecting the existence of records in a system")
        cls.long_description = (
            _(
                "Systems may unintentionally reveal the existence of data by the way"
                + " status messages respond to queries. This is especially relevant"
                + " with informational messages, warnings or errors which respond"
                + " differently when an item does not exist compared to not having"
                + " access rights. An example would be an 'insufficient access rights'"
                + " error message revealing the existence of a specific record. Even"
                + " though no contents have been leaked, the existence of certain items"
                + " alone can be a stepping stone to security threats."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["discloses_responses"]

        cls.mitigation_options = [
            _(
                "Prevent information leakage by not revealing the existence of items in"
                + " system responses"
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = False"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags
        is_process = tag_process in node.tags

        could_disclose_responses = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], True), [False]
        )

        return (is_process or is_data_store) and could_disclose_responses


# ===== Data Disclosure: ==================================
class DD1_ExcessivelySensitiveData(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "DD1"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Excessively Sensitive Data Collected")
        cls.short_description = _(
            "The system acquires more sensitive or finegrained data than strictly"
            + " necessary for its functionality"
        )
        cls.long_description = (
            _(
                "It should be considered if certain data should really be collected in"
                + " terms of the data being too sensitive, more fine-grained than"
                + " strictly necessary or it being unnecessary metadata. For example, a"
                + " camera application does not necessarily need to record the pictures"
                + " location. Processing excessively sensitive data poses a bigger risk"
                + " in case of potential data breaches."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = [
            "only_necessary_data_collected",
            "handles_confidential_data",
            "handles_personal_data",
        ]

        cls.mitigation_options = [
            _(
                "Assess whether all the data is genuinely necessary for providing the"
                + " system's functionality"
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags
        is_process = tag_process in node.tags

        collects_only_nec_data = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        could_handle_confidential = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[1], True), [False]
        )

        could_handle_personal = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[2], True), [False]
        )

        return (
            (is_process or is_data_store)
            and (could_handle_confidential or could_handle_personal)
            and not collects_only_nec_data
        )


class DD2_ExcessiveDataAmount(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "DD2"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Excessive Amount of Data Collected")
        cls.short_description = _(
            "The system acquires more data than strictly needed for its functionality"
        )
        cls.long_description = (
            _(
                "It should be considered if the amount of data collected is too large,"
                + " the processing happens too frequently or if there are more data"
                + " subjects involved than necessary. For example, posts on social"
                + " networks may include personal data about other individuals."
                + " Processing excessive amounts of data poses a bigger risk as it may"
                + " give way to privacy threats such as pattern analysis."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["only_necessary_data_collected"]

        cls.mitigation_options = [
            _(
                "Evaluate whether regular data collection is necessary for the system's"
                + " functionality."
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags
        is_process = tag_process in node.tags

        collects_only_nec_data = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        return (is_process or is_data_store) and not collects_only_nec_data


class DD3_UnnecessaryDataAnalysis(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "DD3"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Unnecessary Data Analysis")
        cls.short_description = _(
            "Data is further processed, analyzed, or enriched in a way that is not"
            + " strictly necessary for the functionality"
        )
        cls.long_description = (
            _(
                "A system should not enrich/analyze the data more than it is necessary"
                + " for the system's functionality. For example, a camera application"
                + " does not need to perform face-based recognition. Processing of data"
                + " can be used to learn additional sensitive information."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["only_necessary_data_analyzed"]

        cls.mitigation_options = [
            _(
                "Evaluate which types of personal data processing are necessary for"
                + " providing the system's functionality."
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags
        is_process = tag_process in node.tags

        analyzes_only_nec_data = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        return (is_process or is_data_store) and not analyzes_only_nec_data


class DD4_UnnecessaryDataRetention(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "DD4"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Unnecessary Data Retention")
        cls.short_description = _("Data is stored for longer than needed")
        cls.long_description = (
            _(
                "If data is stored for a longer time than necessary it poses a privacy"
                + " risk in case of a data breach. For example, storing email addresses"
                + " of newsletter subscribers long after they have unsubscribed."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["data_retention_minimized"]

        cls.mitigation_options = [
            _(
                "Evaluate your storage policies. Consider how long you store personal"
                + " data and whether you have a process to remove data you no longer"
                + " need."
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags

        retention_minimized = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        return is_data_store and not retention_minimized


class DD5_OverexposurePersonalData(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "DD5"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Overexposure of Personal Data")
        cls.short_description = _(
            "Personal data is shared with more services or external parties than"
            + " necessary"
        )
        cls.long_description = (
            _(
                "For personal data it should be considered to only send it to"
                + " recipients who need it, to not involve unnecessary parties and keep"
                + " the accessibility as low as possible. For example, medical data"
                + " should not be made publicly available and location data from a"
                + " navigation application should not be propagated to the calender or"
                + " mail. Overexposure of personal data may lead to unintended"
                + " consequences, as others could reuse the data for unforeseen"
                + " purposes."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["data_sharing_minimized", "handles_personal_data"]

        cls.mitigation_options = [
            _(
                "Carefully assess the necessity of sharing personal data and ensure"
                + " that the involved parties genuinely require access to that data."
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_data_store = tag_datastore in node.tags
        is_process = tag_process in node.tags

        sharing_minimized = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        could_handle_personal = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[1], True), [False]
        )

        return (
            (is_data_store or is_process)
            and could_handle_personal
            and not sharing_minimized
        )


# ===== Unawareness and Unintervenability: ================
class U1_InsufficientTransparency(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "U1"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Insufficient Transparency")
        cls.short_description = _(
            "Data subjects are insufficiently informed about the collection and"
            + " processing of their personal data"
        )
        cls.long_description = (
            _(
                "Data subjects should be sufficiently informed about what kind of"
                + " personal"
                + " data is collected, the purposes and methods of involved processing"
                + " and with whom the data is being shared in a clear and"
                + " understandable way. For example, awareness about traffic cameras"
                + " collecting facial images next to number plates. Insufficient"
                + " transparency may lead to data subjects being unaware about the"
                + " utilization of their personal data, influencing their right to"
                + " privacy."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["data_collection_informed", "is_user"]

        cls.mitigation_options = [
            _(
                "Data subjects must also be informed on any indirect data collection,"
                + " i.e. from third parties."
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_interactor = tag_interactor in node.tags

        data_coll_informed = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        could_be_user = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[1], True), [False]
        )

        return is_interactor and could_be_user and not data_coll_informed


class U2_InsufficientTransparencyOthers(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "U2"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Insufficient Information when Sharing Data of Others")
        cls.short_description = _(
            "When sharing personal data of others, users are insufficiently informed"
            + " about the further data processing"
        )
        cls.long_description = (
            _(
                "Data subjects should be sufficiently informed about what kind of data"
                + " of others is collected, the purposes and methods of involved"
                + " processing and with whom the data is being shared in a clear and"
                + " understandable way. For example, a user posting a picture on social"
                + " media may not be aware that others in the picture are automatically"
                + " tagged with a facial recognition system. Insufficient transparency"
                + " means, users may not realize they are unintentionally sharing"
                + " personal data of other individuals."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["data_collection_informed", "is_user"]

        cls.mitigation_options = [
            _(
                "Data subjects must also be informed on any processing of personal data"
                + " from others"
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_interactor = tag_interactor in node.tags

        data_coll_informed = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        could_be_user = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[1], True), [False]
        )

        return is_interactor and could_be_user and not data_coll_informed


class U3_InsufficientPrivacyControls(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "U3"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Insufficient Privacy Controls")
        cls.short_description = _(
            "Data subjects have insufficient controls to manage their preferences"
        )
        cls.long_description = (
            _(
                "Users should be given the option to configure what personal data is"
                + " processed and for what purposes. They should also be able alter"
                + " their preferences afterwards. Appropriate control mechanisms are"
                + " required to record data subject preferences and keep track of how"
                + " the data may be further processed."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["personal_data_preferences", "is_user"]

        cls.mitigation_options = [
            _("Privacy-frendly settings should be the default."),
            _(
                "Nudging can raise awareness and induce more privacy-preserving"
                + " behaviour."
            ),
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_interactor = tag_interactor in node.tags

        data_pref = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        could_be_user = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[1], True), [False]
        )

        return is_interactor and could_be_user and not data_pref


class U4_InsufficientAccess(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "U4"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Insufficient Access")
        cls.short_description = _(
            "Data subjects do not have access to their personal data"
        )
        cls.long_description = (
            _(
                "Users should be given the option to access their collected personal"
                + " information through the system or a helpdesk. Lack of access may"
                + " violate the legal rights of data subjects."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["own_data_access", "is_user"]

        cls.mitigation_options = [
            _(
                "Enable the user to access their personal data. (The right to access "
                "is not always absolute. Limitations may exist depending on applicable "
                + "laws (e.g., trade secrets, rights of other data subjects))"
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_interactor = tag_interactor in node.tags

        data_access = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        could_be_user = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[1], True), [False]
        )

        return is_interactor and could_be_user and not data_access


class U5_InsufficientErasure(NodeRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "U5"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Insufficient Rectification or Erasure")
        cls.short_description = _(
            "Data subjects cannot rectify or erase their personal data"
        )
        cls.long_description = (
            _(
                "Users should be given the option to correct or delete their collected"
                + " personal data. For example, when a user deletes his social media"
                + " account, the data should be deleted and not just the account"
                + " disabled."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["own_data_modification", "is_user"]

        cls.mitigation_options = [
            _(
                "Enable the user to correct or delete their personal data. "
                + "(Rectification or erasure can also be performed indirectly (e.g., "
                + "through a customer service ticket))"
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, node: Node, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        is_interactor = tag_interactor in node.tags

        data_modification = meet_any_requirement(
            node.attributes.get(cls.attribute_names[0], False), [True]
        )

        could_be_user = not meet_any_requirement(
            node.attributes.get(cls.attribute_names[1], True), [False]
        )

        return is_interactor and could_be_user and not data_modification


# ===== Non-Compliance: ===================================
class Nc1_NonCompliantProcessing(DataflowDiagramRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "Nc1"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Non-Compliance of Processing with Applicable Regulations")
        cls.short_description = _(
            "The processing of personal data by the system is not compliant with"
            + " applicable privacy regulations"
        )
        cls.long_description = (
            _(
                "Processing and sharing of personal information must adhere to"
                + " jurisdictions in regions it is used in. For example, the system"
                + " must not process information of EU citizens without a valid legal"
                + " ground under GDPR."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["privacy_regulation_compliance"]

        cls.mitigation_options = [
            _(
                "Before processing any personal data, perform an assessment on the"
                + " applicable regulations for your processing activities and system"
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        privacy_regulations_comply = meet_any_requirement(
            dfd.attributes.get(cls.attribute_names[0], False), [True]
        )

        return not privacy_regulations_comply


class Nc2_NonAdherencePrivacyStandards(DataflowDiagramRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "Nc2"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Non-Adherence to Privacy Standards")
        cls.short_description = _(
            "The system is not compliant with privacy standards and best practices"
        )
        cls.long_description = (
            _(
                "The system should adhere to (industry) specific privacy standards and"
                + " implement them adequately. Non-adherence to industry standards and"
                + " best practices makes it more difficult to demonstrate compliance"
                + " with applicable laws."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["privacy_standards_compliance"]

        cls.mitigation_options = [
            _(
                "Check whether there is industry-specific guidance on data processing"
                + " for your sector (e.g., healthcare, manufacturing)"
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        privacy_standards_comply = meet_any_requirement(
            dfd.attributes.get(cls.attribute_names[0], False), [True]
        )

        return not privacy_standards_comply


class Nc3_ImproperDataLifecycle(DataflowDiagramRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "Nc3"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Improper Data Lifecycle Management")
        cls.short_description = _(
            "Data is not properly managed throughout its entire lifecycle within the"
            + " system"
        )
        cls.long_description = (
            _(
                "There should be a data lifecycle management policy defined for the"
                + " data processed within the system. The policy should outline clear"
                + " principles for each phase of the lifecycle (creation, storage,"
                + " sharing, usage, archival, destruction). Improper data lifecycle"
                + " management can result in a loss of overview of the data within the"
                + " system and its maintanance, posing concerns not only for privacy"
                + " and data protection but also security and availability."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["data_lifecycle_policy_exists"]

        cls.mitigation_options = [
            _(
                "Data lifecycle management is a continuous process that must be"
                + " consistently carried out as long as the system is designed,"
                + " developed, and used"
            )
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        lifecycle_policy = meet_any_requirement(
            dfd.attributes.get(cls.attribute_names[0], False), [True]
        )

        return not lifecycle_policy


class Nc4_InsufficientProcessingSecurity(DataflowDiagramRule):
    BASE_SEVERITY = 1.0
    severity = BASE_SEVERITY
    linddun_id = "Nc4"

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.display_name = _("Insufficient Security of Processing")
        cls.short_description = _(
            "Data security measures and processes do not adhere to risk and security"
            + " management best practices and standards"
        )
        cls.long_description = (
            _(
                "There should be a process established to manage security risks and"
                + " identify required countermeasures. The system should then"
                + " incorporate the required countermeasures while regarding industry"
                + " standards and best practices."
            )
            + "\n"
            + _("LINDDUN card ID: ")
            + cls.linddun_id
        )

        cls.attribute_names = ["security_standards_compliance"]

        cls.mitigation_options = [
            _("Consider complementary methods like security threat modeling")
        ]
        cls.requirement = (
            attributes_dict.attributes[cls.attribute_names[0]].display_name + " = True"
        )

    @classmethod
    def _test(cls, dfd: dataflowdiagram.DataflowDiagram) -> bool:
        security_standards_comply = meet_any_requirement(
            dfd.attributes.get(cls.attribute_names[0], False), [True]
        )

        return not security_standards_comply


class LINDDUNRuleCollection(DataflowDiagramRuleCollection):
    tags = {"linddun_rules"}

    @classmethod
    def init_texts(cls):
        _ = settings.lang_out_linddun.gettext
        cls.name = _("LINDDUN rule collection")

        cls.references = [
            ("https://linddun.org/"),
            ("https://downloads.linddun.org/linddun-go/default/v241203/go.pdf"),
        ]

    node_rules = [
        L4_LinkableDataset,
        L5_ProfilingUsers,
        #
        I5_IdentifiableDataset,
        #
        Nr1_NonRepudiationOfServiceUsage,
        Nr3_NonRepudiationOfReceipt,
        Nr4_NonRepudiationOfStorage,
        Nr5_NonRepudiationOfMetadata,
        #
        D1_DetectableUsers,
        D3_DetectableEvents,
        D4_DetectableRecords,
        #
        DD1_ExcessivelySensitiveData,
        DD2_ExcessiveDataAmount,
        DD3_UnnecessaryDataAnalysis,
        DD4_UnnecessaryDataRetention,
        DD5_OverexposurePersonalData,
        #
        U1_InsufficientTransparency,
        U2_InsufficientTransparencyOthers,
        U3_InsufficientPrivacyControls,
        U4_InsufficientAccess,
        U5_InsufficientErasure,
    ]

    edge_rules = [
        L1_LinkedUserRequests,
        L2_LinkableUserRequests,
        L3_LinkableUserPatterns,
        #
        I1_IdentifiedUserRequests,
        I2_IdentifiableUserRequests,
        I3_IdentifiableDataFlows,
        I4_IdentifiableDataRequests,
        #
        Nr2_NonRepudiationOfSending,
        #
        D2_DetectableServiceUsage,
    ]

    dfd_rules = [
        Nc1_NonCompliantProcessing,
        Nc2_NonAdherencePrivacyStandards,
        Nc3_ImproperDataLifecycle,
        Nc4_InsufficientProcessingSecurity,
    ]


__all__ = ["LINDDUNRuleCollection"]
