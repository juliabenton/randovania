import copy
import re
from typing import List, Dict, Iterator, Tuple, FrozenSet, Iterable

from randovania.game_description.area import Area
from randovania.game_description.area_location import AreaLocation
from randovania.game_description.dock import DockConnection
from randovania.game_description.game_patches import GamePatches
from randovania.game_description.node import Node, DockNode, TeleporterNode
from randovania.game_description.requirements import RequirementSet
from randovania.game_description.resources.resource_info import ResourceInfo, CurrentResources
from randovania.game_description.world import World


class WorldList:
    worlds: List[World]

    _nodes_to_area: Dict[Node, Area]
    _nodes_to_world: Dict[Node, World]
    _nodes: Tuple[Node, ...]

    def __deepcopy__(self, memodict):
        return WorldList(
            worlds=copy.deepcopy(self.worlds, memodict),
        )

    def __init__(self, worlds: List[World]):
        self.worlds = worlds
        self._nodes_to_area, self._nodes_to_world = _calculate_nodes_to_area_world(worlds)

        self._nodes = tuple(self._iterate_over_nodes())

    def _iterate_over_nodes(self) -> Iterator[Node]:
        for world in self.worlds:
            yield from world.all_nodes

    def world_with_name(self, world_name: str) -> World:
        for world in self.worlds:
            if world.name == world_name or world.dark_name == world_name:
                return world
        raise KeyError("Unknown name: {}".format(world_name))

    def world_by_asset_id(self, asset_id: int) -> World:
        for world in self.worlds:
            if world.world_asset_id == asset_id:
                return world
        raise KeyError("Unknown asset_id: {}".format(asset_id))

    def area_by_asset_id(self, asset_id: int) -> Area:
        for area in self.all_areas:
            if area.area_asset_id == asset_id:
                return area
        raise KeyError("Unknown asset_id: {}".format(asset_id))

    def world_with_area(self, area: Area) -> World:
        for world in self.worlds:
            if area in world.areas:
                return world
        raise KeyError("Unknown area: {}".format(area))

    @property
    def all_areas(self) -> Iterator[Area]:
        for world in self.worlds:
            yield from world.areas

    @property
    def all_nodes(self) -> Tuple[Node, ...]:
        return self._nodes

    @property
    def all_worlds_areas_nodes(self) -> Iterable[Tuple[World, Area, Node]]:
        for world in self.worlds:
            for area in world.areas:
                for node in area.nodes:
                    yield world, area, node

    def world_name_from_area(self, area: Area, distinguish_dark_aether: bool = False) -> str:
        world = self.world_with_area(area)

        if distinguish_dark_aether:
            return world.correct_name(area.in_dark_aether)
        else:
            return world.name

    def world_name_from_node(self, node: Node, distinguish_dark_aether: bool = False) -> str:
        return self.world_name_from_area(self.nodes_to_area(node), distinguish_dark_aether)

    def area_name(self, area: Area, distinguish_dark_aether: bool = False, separator: str = "/") -> str:
        return "{}{}{}".format(
            self.world_name_from_area(area, distinguish_dark_aether),
            separator,
            area.name)

    def node_name(self, node: Node, with_world=False, distinguish_dark_aether: bool = False) -> str:
        prefix = "{}/".format(self.world_name_from_node(node, distinguish_dark_aether)) if with_world else ""
        return "{}{}/{}".format(prefix, self.nodes_to_area(node).name, node.name)

    def node_from_name(self, name: str) -> Node:
        match = re.match("(?:([^/]+)/)?([^/]+)/([^/]+)", name)
        if match is None:
            raise ValueError("Invalid name: {}".format(name))

        world_name, area_name, node_name = match.group(1, 2, 3)
        for world in self.worlds:
            if world_name is not None and world_name not in (world.name, world.dark_name):
                continue

            for area in world.areas:
                if area.name != area_name:
                    continue

                for node in area.nodes:
                    if node.name == node_name:
                        return node

        raise ValueError("Unknown name: {}".format(name))

    def nodes_to_world(self, node: Node) -> World:
        return self._nodes_to_world[node]

    def nodes_to_area(self, node: Node) -> Area:
        return self._nodes_to_area[node]

    def resolve_dock_connection(self, world: World, connection: DockConnection) -> Node:
        target_area = world.area_by_asset_id(connection.area_asset_id)
        return target_area.node_with_dock_index(connection.dock_index)

    def resolve_dock_node(self, node: DockNode, patches: GamePatches) -> Node:
        world = self.nodes_to_world(node)
        original_area = self.nodes_to_area(node)

        connection = patches.dock_connection.get((original_area.area_asset_id, node.dock_index),
                                                 node.default_connection)
        return self.resolve_dock_connection(world, connection)

    def resolve_teleporter_node(self, node: TeleporterNode, patches: GamePatches) -> Node:
        connection = patches.elevator_connection.get(node.teleporter_instance_id, node.default_connection)
        return self.resolve_teleporter_connection(connection)

    def resolve_teleporter_connection(self, connection: AreaLocation) -> Node:
        area = self.area_by_area_location(connection)
        if area.default_node_index == 255:
            raise IndexError("Area '{}' does not have a default_node_index".format(area.name))
        return area.nodes[area.default_node_index]

    def connections_from(self, node: Node, patches: GamePatches) -> Iterator[Tuple[Node, RequirementSet]]:
        """
        Queries all nodes from other areas you can go from a given node. Aka, doors and teleporters
        :param patches:
        :param node:
        :return: Generator of pairs Node + RequirementSet for going to that node
        """
        if isinstance(node, DockNode):
            # TODO: respect is_blast_shield: if already opened once, no requirement needed.
            # Includes opening form behind with different criteria
            try:
                target_node = self.resolve_dock_node(node, patches)
                original_area = self.nodes_to_area(node)
                dock_weakness = patches.dock_weakness.get((original_area.area_asset_id, node.dock_index),
                                                          node.default_dock_weakness)

                yield target_node, dock_weakness.requirements
            except IndexError:
                # TODO: fix data to not having docks pointing to nothing
                yield None, RequirementSet.impossible()

        if isinstance(node, TeleporterNode):
            try:
                yield self.resolve_teleporter_node(node, patches), RequirementSet.trivial()
            except IndexError:
                # TODO: fix data to not have teleporters pointing to areas with invalid default_node_index
                print("Teleporter is broken!", node)
                yield None, RequirementSet.impossible()

    def area_connections_from(self, node: Node) -> Iterator[Tuple[Node, RequirementSet]]:
        """
        Queries all nodes from the same area you can go from a given node.
        :param node:
        :return: Generator of pairs Node + RequirementSet for going to that node
        """
        area = self.nodes_to_area(node)
        for target_node, requirements in area.connections[node].items():
            yield target_node, requirements

    def potential_nodes_from(self, node: Node, patches: GamePatches) -> Iterator[Tuple[Node, RequirementSet]]:
        """
        Queries all nodes you can go from a given node, checking doors, teleporters and other nodes in the same area.
        :param node:
        :param patches:
        :return: Generator of pairs Node + RequirementSet for going to that node
        """
        yield from self.connections_from(node, patches)
        yield from self.area_connections_from(node)

    def simplify_connections(self, static_resources: CurrentResources) -> None:
        """
        Simplifies all Node connections, assuming the given resources will never change their quantity.
        This is removes all checking for tricks and difficulties in runtime since these never change.
        :param static_resources:
        :return:
        """
        for world in self.worlds:
            for area in world.areas:
                for connections in area.connections.values():
                    for target, value in connections.items():
                        connections[target] = value.simplify(static_resources)

    def calculate_relevant_resources(self, patches: GamePatches) -> FrozenSet[ResourceInfo]:
        results = set()

        for node in self.all_nodes:
            for _, requirements in self.potential_nodes_from(node, patches):
                for alternative in requirements.alternatives:
                    for individual in alternative.items:
                        results.add(individual.resource)

        return frozenset(results)

    def area_by_area_location(self, location: AreaLocation) -> Area:
        return self.world_by_asset_id(location.world_asset_id).area_by_asset_id(location.area_asset_id)

    def world_by_area_location(self, location: AreaLocation) -> World:
        return self.world_by_asset_id(location.world_asset_id)

    def node_to_area_location(self, node: Node) -> AreaLocation:
        return AreaLocation(
            world_asset_id=self.nodes_to_world(node).world_asset_id,
            area_asset_id=self.nodes_to_area(node).area_asset_id,
        )

    def add_new_node(self, area: Area, node: Node):
        self._nodes_to_area[node] = area
        self._nodes_to_world[node] = self.world_with_area(area)


def _calculate_nodes_to_area_world(worlds: Iterable[World]):
    nodes_to_area = {}
    nodes_to_world = {}

    for world in worlds:
        for area in world.areas:
            for node in area.nodes:
                if node in nodes_to_area:
                    raise ValueError(
                        "Trying to map {} to {}, but already mapped to {}".format(
                            node, area, nodes_to_area[node]))
                nodes_to_area[node] = area
                nodes_to_world[node] = world

    return nodes_to_area, nodes_to_world
