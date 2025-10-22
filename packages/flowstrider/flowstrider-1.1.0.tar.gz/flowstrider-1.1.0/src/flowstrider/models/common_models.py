# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

import typing
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    """
    Represents a node.

    Attributes:
        id (str): A unique identifier for the node.
        name (str): The name of the node.
        tags (Set[str]): A set of tags used to specify the type
            of the node: datastore, process, or external entity
            ['STRIDE:DataStore', 'STRIDE:Process', 'STRIDE:Interactor'].
        attributes (Dict[str, Any]): A dictionary containing metadata
            about the node (see supported metadata).
        severity_multiplier (float): Multiplier for the severity of threats found at
            this node.
    """

    id: str
    name: str = ""
    tags: typing.Set[str] = field(default_factory=set)
    attributes: typing.Dict[str, typing.Any] = field(default_factory=dict)
    severity_multiplier: float = 1.0


@dataclass(frozen=True)
class Edge:
    """
    Represents a edge.

    Attributes:
        id (str): A unique identifier of the edge.
        source_id (str): ID of the source node.
        sink_id (str): ID of the sink node.
        name (str): Name of the edge.
        tags (Set[str]): A set of tags used to specify
            the type of the edge: data flow [STRIDE:Dataflow].
        attributes (Dict[str, Any]): A dictionary containing
            metadata about the edge.
            (see supported metadata).
    """

    id: str
    source_id: str
    sink_id: str
    name: str = ""
    tags: typing.Set[str] = field(default_factory=set)
    attributes: typing.Dict[str, typing.Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Cluster:
    """
    Represents a cluster.

    Attributes:
        id (str): A unique identifier of the cluster.
        node_ids (Set[str]): IDs of the nodes in the cluster.
        name (str): Name of the cluster.
        tags (Set[str]): A set of tags used to specify
            the type of the cluster ["STRIDE:TrustBoundary"].
        attributes (Dict[str, Any]): A dictionary containing
            metadata about the cluster.
            Currently, no additional metadata is used here.
        severity_multiplier (float): Multiplier for the severity of threats found in
            this cluster.
    """

    id: str
    node_ids: typing.Set[str]
    name: str = ""
    tags: typing.Set[str] = field(default_factory=set)
    attributes: typing.Dict[str, typing.Any] = field(default_factory=dict)
    severity_multiplier: float = 1.0
