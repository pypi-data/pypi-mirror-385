# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

import typing

from flowstrider import settings


class Attribute(typing.NamedTuple):
    display_name: str
    explanation: str

    # Entity types, the attribute can be applied to ["Node: Interactor",
    # ..."Node: DataStore", "Node: Process", "Edge: Dataflow", "TrustBoundary",
    # ..."DataflowDiagram"]
    applicable_entities: typing.List[str]

    # Values the attribute can take on
    accepted_values: typing.List[typing.Union[str, bool]]

    # Tags of the rule sets which require this attribute
    # ...e.g.: ["stride", "bsi_rules", "linddun_rules"]
    corresponding_rule_sets: typing.List[str]


# Dictionary containing all attributes of entities with corresponding accepted values.
attributes: typing.Dict[str, Attribute] = {}


def init_attributes():
    init_bsi_attributes()
    init_linddun_attributes()


def init_bsi_attributes():
    _ = settings.lang_out_attributes.gettext

    global attributes
    # ===== Attributes for the BSI collection: ============
    # (Partially also used by LINDDUN)
    attributes["auth_factors"] = Attribute(
        _("Authentication factors"),
        _(
            "If authentication is required, which factors will be needed for "
            "authentication. Examples: ['PIN', 'Chip Card', 'OTP'] or "
            "['Digital Certificate', 'Biometric Data']."
        ),
        ["Node: DataStore", "Node: Process"],
        [
            "PIN",
            "OTP",
            "Biometric Data",
            "Digital Certificate",
            "Chip Card",
            "Security Token",
        ],
        ["bsi_rules"],
    )
    attributes["auth_protocol"] = Attribute(
        _("Authentication protocol"),
        _(
            "Which authentication protocol will be used to ensure integrity. "
            "Examples: 'DH_CHAP' or 'FCPAP'"
        ),
        ["Node: DataStore"],
        [
            "DH_CHAP",
            "FCAP",
            "FCPAP",
        ],
        ["bsi_rules"],
    )
    attributes["auth_req"] = Attribute(
        _("Requires authentication"),
        _("Whether any form of authentication is required to access the entity."),
        ["Node: DataStore", "Node: Process"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["encryption_method"] = Attribute(
        _("Encryption method"),
        _(
            "Which method of encryption will be used to encrypt the data. "
            "Examples: 'AES_128' or 'AES_256'"
        ),
        ["Node: DataStore"],
        ["AES_128", "AES_192", "AES_256"],
        ["bsi_rules"],
    )
    attributes["given_permissions"] = Attribute(
        _("Given permissions"),
        _("Actions the actor is priviliged to perform."),
        ["Node: Process", "Node: Interactor"],
        [],
        ["bsi_rules"],
    )
    attributes["handles_confidential_data"] = Attribute(
        _("Handles confidential data"),
        _("Whether the entity handles confidential data."),
        ["Node: DataStore", "Node: Process", "Edge: Dataflow"],
        [True, False],
        ["bsi_rules", "linddun_rules"],
    )
    attributes["handles_logs"] = Attribute(
        _("Handles logs"),
        _("Whether the DataStore handles protocol logging data."),
        ["Node: DataStore"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["hash_function"] = Attribute(
        _("Hash function"),
        _(
            "Which function will be used to store hashed data. Examples: "
            "'SHA3_256' or 'SHA_512_256'."
        ),
        ["Node: DataStore"],
        [
            "SHA3_256",
            "SHA3_384",
            "SHA3_512",
            "SHA_256",
            "SHA_384",
            "SHA_512",
            "SHA_512_256",
        ],
        ["bsi_rules"],
    )
    attributes["http_content_security_policy"] = Attribute(
        ("HTTP Content Security Policy"),
        (
            _(
                "If the HTTP header '{header}' is set appropriately and as "
                "restrictive as possible."
            )
        ).format(header="Content Security Policy"),
        ["Edge: Dataflow"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["http_strict_transport_security"] = Attribute(
        ("HTTP Strict Transport Security"),
        (
            _(
                "If the HTTP header '{header}' is set appropriately and as "
                "restrictive as possible."
            )
        ).format(header="Strict Transport Security"),
        ["Edge: Dataflow"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["http_content_type"] = Attribute(
        ("HTTP Content Type"),
        (
            _(
                "If the HTTP header '{header}' is set appropriately and as "
                "restrictive as possible."
            )
        ).format(header="Content Type"),
        ["Edge: Dataflow"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["http_x_content_options"] = Attribute(
        ("HTTP X Content Options"),
        (
            _(
                "If the HTTP header '{header}' is set appropriately and as "
                "restrictive as possible."
            )
        ).format(header="X Content Options"),
        ["Edge: Dataflow"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["http_cache_control"] = Attribute(
        ("HTTP Cache Control"),
        (
            _(
                "If the HTTP header '{header}' is set appropriately and as "
                "restrictive as possible."
            )
        ).format(header="Cache Control"),
        ["Edge: Dataflow"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["is_san_fabric"] = Attribute(
        _("Is SAN fabric"),
        _(
            "Defines, if the entity is part of the fabric layer of a storage area "
            "network."
        ),
        ["Node: DataStore"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["input_data"] = Attribute(
        _("Input data"),
        _("All types of handled data. Example: ['Session IDs', 'User Requests']."),
        ["Node: Process"],
        [],
        ["bsi_rules"],
    )
    attributes["input_validation"] = Attribute(
        _("Input validation"),
        _("Defines, if the input data is validated."),
        ["Node: Process"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["integrity_check"] = Attribute(
        _("Integrity check"),
        _(
            "If an integrity check (such as a check sum) is used, this should "
            "note the specific check. Examples: 'check sum' or 'digital "
            "certificate'."
        ),
        ["Edge: Dataflow"],
        ["check sum", "digital certificate", "ECDSA"],
        ["bsi_rules"],
    )
    attributes["proxy"] = Attribute(
        _("Uses proxy"),
        _("Whether the dataflow is routed through a TLS-proxy"),
        ["Edge: Dataflow"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["req_permissions"] = Attribute(
        _("Required permissions"),
        _("Which priviliges are required to interact with the process."),
        ["Node: Process", "Node: Interactor"],
        [],
        ["bsi_rules"],
    )
    attributes["signature_scheme"] = Attribute(
        _("Signature scheme"),
        _(
            "If a signature scheme is used, this should note the specific scheme. "
            "Examples:'RSA' or 'ECDSA' or 'LMS'."
        ),
        ["Edge: Dataflow", "Node: DataStore"],
        [
            "DSA",
            "ECDSA",
            "ECGDSA",
            "ECKDSA",
            "LMS",
            "RSA",
            "XMSS",
        ],
        ["bsi_rules"],
    )
    attributes["stores_credentials"] = Attribute(
        _("Stores credentials"),
        _(
            "Whether the DataStore stores Login Credentials or other "
            "authentication data."
        ),
        # Should only be passwords according to the HashedPasswordsNodeRule?
        ["Node: DataStore"],
        [True, False],
        ["bsi_rules"],
    )
    attributes["transport_protocol"] = Attribute(
        _("Transport protocol"),
        _("Which transport protocol the dataflow uses."),
        ["Edge: Dataflow"],
        ["HTTPS", "TLS 1.2", "TLS 1.3"],
        ["bsi_rules"],
    )


def init_linddun_attributes():
    _ = settings.lang_out_attributes.gettext

    global attributes
    # ===== Attributes for the LINDDUN collection: ========
    attributes["data_collection_informed"] = Attribute(
        _("Informs about data collection"),
        _(
            "If this data subject gets informed in detail about which data is being "
            + "collected in which way, what is done with collected data and with "
            + "whom it is shared."
        ),
        ["Node: Interactor"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["data_lifecycle_policy_exists"] = Attribute(
        _("Data lifecycle policy exists"),
        _(
            "If a policy is defined that concerns the lifecycle management of data, "
            + "including principles for creation, storage, sharing, usage, archival "
            + "and destruction of data."
        ),
        ["DataflowDiagram"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["data_retention_minimized"] = Attribute(
        _("Data retention minimized"),
        _(
            "If the application stores data only for the time frame necessary to the "
            "core functionality. For example no mail addresses are stored of users who "
            "already unsubscribed a newsletter."
        ),
        ["Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["data_sharing_minimized"] = Attribute(
        _("Data sharing minimized"),
        _(
            "If the application shares data only with services and external parties "
            "who need it for the functionality of the system."
        ),
        ["Node: Process", "Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["discloses_responses"] = Attribute(
        _("Responses disclose information existence"),
        _(
            "If the entity discloses the existence of information through status "
            + "messages when the query was wrong or not authenticated. E.g. returning "
            + "a 'wrong password' error message revealing the existence of the "
            + "account."
        ),
        ["Node: Process", "Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["handles_personal_data"] = Attribute(
        _("Handles personal data"),
        _("Whether the entity handles personal data."),
        ["Node: Process", "Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["handles_user_data"] = Attribute(
        _("Handles user data"),
        _(
            "If this entity stores or handles any data from users like messages, "
            + "texts, files or full user accounts."
        ),
        ["Node: Process", "Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["is_private_network"] = Attribute(
        _("Is private network"),
        _(
            "If the inside workings of the trust boundary are private and the network "
            + "acts like a blackbox sending and receiving data via dedicated "
            + "interfaces. Internal communication channels would be completely hidden "
            + "to outside viewers."
        ),
        ["TrustBoundary"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["is_user"] = Attribute(
        _("Is a user"),
        _("Whether this interactor node represents human users."),
        ["Node: Interactor"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["leaves_usage_traces"] = Attribute(
        _("Leaves usage traces"),
        _(
            "If the application leaves any traces that a user has used the application "
            + "like log files, traces of temporary files or size of data changing."
        ),
        ["Node: Process", "Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["logs_access"] = Attribute(
        _("Logs access"),
        _("If the process logs access by users."),
        ["Node: Process"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["logs_receipt"] = Attribute(
        _("Logs receipt"),
        _("If the process logs the receipt of messages."),
        ["Node: Process"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["only_necessary_data_analyzed"] = Attribute(
        _("Only necessary data analyzed"),
        _(
            "If the application keeps the analysis of its data to a strictly necessary "
            "level and data is not enriched more than it needs to be for the core "
            "functionality."
        ),
        ["Node: Process", "Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["only_necessary_data_collected"] = Attribute(
        _("Only necessary data collected"),
        _(
            "If the application collects only data that is strictly necessary for its "
            + "core functionality. This includes limiting the amount/size of data "
            + "collected and the collected data not being more fine-grained than "
            + "necessary."
        ),
        ["Node: Process", "Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["own_data_access"] = Attribute(
        _("Own data access"),
        _("If data subjects have access to their own personal data."),
        ["Node: Interactor"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["own_data_modification"] = Attribute(
        _("Own data modification"),
        _(
            "If data subjects have the ability to correct or delete their own personal "
            + "data."
        ),
        ["Node: Interactor"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["personal_data_preferences"] = Attribute(
        _("Personal data preferences"),
        _(
            "Whether or not this data subject is given the option to set their "
            + "preferences "
            + "regarding the collection, handling and sharing of their personal data."
        ),
        ["Node: Interactor"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["privacy_regulation_compliance"] = Attribute(
        _("Privacy regulation compliance"),
        _(
            "If this entity is compliant with privacy regulations of jurisdictions the "
            + "system is used in."
        ),
        ["DataflowDiagram"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["privacy_standards_compliance"] = Attribute(
        _("Privacy standards compliance"),
        _(
            "If the system is compliant with (industry specific) privacy standards and "
            + "best practices."
        ),
        ["DataflowDiagram"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["security_standards_compliance"] = Attribute(
        _("Security standards compliance"),
        _(
            "If the system is compliant with (industry specific) security standards "
            + "and best practices."
        ),
        ["DataflowDiagram"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["stores_signed_data"] = Attribute(
        _("Stores signed data"),
        _(
            "If the data store stores data that has been digitally signed by the "
            + "uploader."
        ),
        ["Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["stores_user_associated_metadata"] = Attribute(
        _("Stores user associated metadata"),
        _(
            "If the data store stores metadata, hidden data or specific patterns that "
            + "could relate to specific users."
        ),
        ["Node: DataStore"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["transmits_signed_data"] = Attribute(
        _("Transmits signed data"),
        _(
            "If the dataflow transmits data that has been digitally signed by the "
            + "sender. Example: signed emails."
        ),
        ["Edge: Dataflow"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["transmits_unique_user_id"] = Attribute(
        _("Transmits unique user identifier"),
        _(
            "If an identifier is transmitted on this dataflow that uniquely "
            + "corresponds to one user. Examples: IP-address, email-address, unique "
            + "pseudonyms"
        ),
        ["Edge: Dataflow"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["transmits_user_data"] = Attribute(
        _("Transmits user data"),
        _(
            "If this dataflow transmits any data directly from users like messages, "
            + "texts or files."
        ),
        ["Edge: Dataflow"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["transmits_user_identity"] = Attribute(
        _("Transmits user identity"),
        _(
            "If this dataflow transmits the clear identity of users such as the full "
            + "name."
        ),
        ["Edge: Dataflow"],
        [True, False],
        ["linddun_rules"],
    )
    attributes["transmits_user_properties"] = Attribute(
        _("Transmits user properties"),
        _(
            "If this dataflow transmits any properties that are dependent on the user "
            + "like OS, browser, screen size, language, etc."
        ),
        ["Edge: Dataflow"],
        [True, False],
        ["linddun_rules"],
    )
