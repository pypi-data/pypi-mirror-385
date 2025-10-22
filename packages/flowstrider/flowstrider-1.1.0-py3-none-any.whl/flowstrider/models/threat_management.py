# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

import typing
from bisect import bisect_left
from dataclasses import dataclass, field
from enum import Enum, auto

from flowstrider import settings
from flowstrider.converters.dfd_to_dot_converter import wrap_text as wrap
from flowstrider.models import dataflowdiagram, threat

from ..helpers.warnings import WarningsCounter


class ThreatManagementState(Enum):
    # These imply future work
    Undecided = auto()
    Delegate = auto()
    Mitigate = auto()
    Avoid = auto()

    # These are final
    Accept = auto()
    Delegated = auto()
    Mitigated = auto()

    def __format__(self, _):
        return f"{self.name}"


@dataclass(frozen=True)
class ThreatManagementItem:
    uid: str = ""
    management_state: ThreatManagementState = ThreatManagementState.Undecided
    explanation: str = ""


ThreatManagementDict = typing.Dict[str, ThreatManagementItem]


@dataclass
class ThreatManagementDatabase:
    per_threat_information: ThreatManagementDict = field(default_factory=dict)

    def update(
        self,
        threats_in: typing.List[threat.Threat],
        dfd: dataflowdiagram.DataflowDiagram,
    ):
        # Sort threats by uid
        threats = threats_in.copy()
        threats.sort(key=lambda threat: threat.uid())

        item_deletion_list = []

        # Iterate over management file:
        for key, management_item in list(self.per_threat_information.items()):
            # Search for corresponding threat to the management item
            index = bisect_left(
                threats, management_item.uid, key=lambda threat: threat.uid()
            )
            if index < len(threats) and threats[index].uid() == management_item.uid:
                # If threat exists for management item, remove threat from list
                # ...(marks as done) and rename management item
                self.per_threat_information[threats[index].display_id(dfd)] = (
                    self.per_threat_information[key]
                )
                if key != threats[index].display_id(dfd):
                    del self.per_threat_information[key]
                del threats[index]
            else:
                # If no threat exists for management item (i.e. threat resolved or uid
                # ...changed):

                # Simple delete if the management item wasn't modified (undecided state)
                if (
                    self.per_threat_information[key].management_state
                    == ThreatManagementState.Undecided
                    and len(self.per_threat_information[key].explanation) == 0
                ):
                    del self.per_threat_information[key]

                # Add to list for deletion with warning otherwise
                else:
                    item_deletion_list.append(key)

        # Remove items for which no threat exists anymore and give warning
        if len(item_deletion_list) > 0:
            global _
            _ = settings.lang_sys.gettext
            print(
                settings.C_WARNING
                + "\n"
                + wrap(
                    _("Warning: ")
                    + settings.lang_sys.ngettext(
                        "the following non-empty threat management item has been"
                        + " deleted because its corresponding threat doesn't exist"
                        + " anymore:",
                        "the following non-empty threat management items have been"
                        + " deleted because their corresponding threats don't exist"
                        + " anymore:",
                        len(item_deletion_list),
                    )
                )
            )
            for item in item_deletion_list:
                WarningsCounter.add_warning()

                print("\n" + wrap(item))
                print(wrap("uid: " + self.per_threat_information[item].uid))
                print(
                    wrap(
                        _("State: ")
                        + "{state}".format(
                            state=self.per_threat_information[item].management_state
                        )
                    )
                )
                if self.per_threat_information[item].explanation:
                    print(
                        wrap(
                            _("Explanation: ")
                            + self.per_threat_information[item].explanation
                        )
                    )

                del self.per_threat_information[item]

            print(settings.C_DEFAULT, end="")

        # Add management items for all remaining threats (for which no existing
        # ...management item was found)
        for threat_ in threats:
            new_item = ThreatManagementItem(uid=threat_.uid())
            self.per_threat_information[threat_.display_id(dfd)] = new_item

    def get(self, threat_: threat.Threat, dfd: dataflowdiagram.DataflowDiagram):
        return self.per_threat_information[threat_.display_id(dfd)]

    def should_fail(
        self,
        threats: typing.List[threat.Threat],
        dfd: dataflowdiagram.DataflowDiagram,
        level: str,
    ) -> typing.List[threat.Threat]:
        return_value = list()
        if level == "off":
            return return_value

        for threat_ in threats:
            threat_management_item = self.get(threat_, dfd)

            # Levels: "off", "undecided", "todo", "all"
            match threat_management_item.management_state:
                case ThreatManagementState.Undecided:
                    if level in ("undecided", "todo", "all"):
                        return_value.append(threat_)
                case (
                    ThreatManagementState.Delegate
                    | ThreatManagementState.Mitigate
                    | ThreatManagementState.Avoid
                ):
                    if level in ("todo", "all"):
                        return_value.append(threat_)
                case (
                    ThreatManagementState.Accept
                    | ThreatManagementState.Delegated
                    | ThreatManagementState.Mitigated
                ):
                    if level in ("all"):
                        return_value.append(threat_)

        return return_value
