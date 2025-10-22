# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

import typing
from dataclasses import dataclass

from flowstrider.models import common_models, dataflowdiagram

Location: typing.TypeAlias = typing.Union[
    common_models.Node, common_models.Edge, dataflowdiagram.DataflowDiagram, str
]


def location_str(location: Location, dfd: dataflowdiagram.DataflowDiagram):
    if isinstance(location, common_models.Node):
        return location.name if location.name != "" else location.id
    elif isinstance(location, common_models.Edge):
        return (
            f"{location.name if location.name != '' else location.id}: "
            + f"{location_str(dfd.nodes[location.source_id], dfd)} -> "
            + f"{location_str(dfd.nodes[location.sink_id], dfd)}"
        )
    elif isinstance(location, dataflowdiagram.DataflowDiagram):
        return location.name if location.name != "" else location.id
    else:
        return location


@dataclass(frozen=True)
class Threat:
    source: str
    source_internal: str
    location: Location
    severity: float  # 0 is lowest severity
    short_description: str
    long_description: str
    mitigation_options: typing.List[str]
    requirement: str
    req_status: str

    def uid(self) -> str:
        """Unique identifier for each individal threat"""
        if isinstance(self.location, str):
            return f"{self.source_internal}@{self.location}"
        else:
            return f"{self.source_internal}@{self.location.id}"

    def display_id(self, dfd: dataflowdiagram.DataflowDiagram) -> str:
        """Display identifier for each individal threat; takes names instead of id of
        elements and is localized; not suitable as a unique id
        """
        return f"{self.source}@{location_str(self.location, dfd)}"

    def location_str(self, dfd: dataflowdiagram.DataflowDiagram) -> str:
        return location_str(self.location, dfd)
