# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "hexdoc-hexcasting",
#     "networkx",
#     "scipy",
# ]
# ///

# pyright: reportUnknownArgumentType=information
# pyright: reportUnknownMemberType=information
# pyright: reportUnknownVariableType=information

from __future__ import annotations

import itertools

import networkx as nx
from hexdoc.core import ResourceLocation
from hexdoc.model import HexdocModel
from hexdoc_hexcasting.utils.pattern import Direction, PatternInfo


class HexCoord(HexdocModel, frozen=True):
    q: int
    r: int

    @classmethod
    def delta_of(cls, direction: Direction) -> HexCoord:
        match direction:
            case Direction.NORTH_EAST:
                return cls(q=1, r=-1)
            case Direction.EAST:
                return cls(q=1, r=0)
            case Direction.SOUTH_EAST:
                return cls(q=0, r=1)
            case Direction.SOUTH_WEST:
                return cls(q=-1, r=1)
            case Direction.WEST:
                return cls(q=-1, r=0)
            case Direction.NORTH_WEST:
                return cls(q=0, r=-1)

    def delta(self, other: HexCoord) -> HexCoord:
        return HexCoord(q=self.q - other.q, r=self.r - other.r)

    def immediate_delta(self, other: HexCoord) -> Direction:
        match other.delta(self):
            case HexCoord(q=1, r=0):
                return Direction.EAST
            case HexCoord(q=0, r=1):
                return Direction.SOUTH_EAST
            case HexCoord(q=-1, r=1):
                return Direction.SOUTH_WEST
            case HexCoord(q=-1, r=0):
                return Direction.WEST
            case HexCoord(q=0, r=-1):
                return Direction.NORTH_WEST
            case HexCoord(q=1, r=-1):
                return Direction.NORTH_EAST
            case _:
                raise ValueError(f"Points are not adjacent: {self}, {other}")

    def __add__(self, other: HexCoord | Direction) -> HexCoord:
        if isinstance(other, Direction):
            other = HexCoord.delta_of(other)
        return HexCoord(q=self.q + other.q, r=self.r + other.r)


ANGLES = "wedsaq"


def overlay_patterns(
    op_id: ResourceLocation,
    patterns: list[tuple[PatternInfo, HexCoord]],
) -> PatternInfo:
    # construct a graph G overlaying all patterns

    G = nx.Graph()

    for pattern, origin in patterns:
        cursor = origin
        compass = pattern.startdir
        G.add_edge(cursor, cursor + compass)

        for angle in pattern.signature:
            cursor += compass
            compass = Direction((compass.value + ANGLES.find(angle)) % len(Direction))
            G.add_edge(cursor, cursor + compass)

    # find a path that visits each edge at least once
    # https://en.wikipedia.org/wiki/Chinese_postman_problem#Undirected_solution_and_T-joins

    # create a graph G2 with only the odd-degree nodes in G
    G2 = nx.Graph()
    for node, degree in nx.degree(G):
        if degree % 2 != 0:
            G2.add_node(node)

    # find the shortest paths from each node in G2 to every other node in G
    dists = {}
    paths = {}
    for node in G2:
        d, p = nx.single_source_dijkstra(G, node)
        dists[node] = d
        paths[node] = p

    # construct a complete graph on G2, where edges represent shortest paths in G
    for u in G2:
        for v in G2:
            if u != v:
                G2.add_edge(u, v, weight=dists[u][v])

    # find a minimum weight perfect matching in G2
    # the edges of this matching represent paths in G which form the T-join
    matching = nx.min_weight_matching(G2)

    # find the T-join by taking the union of all paths in the matching
    t_join = set()
    for u, v in matching:
        for pair in itertools.pairwise(paths[u][v]):
            t_join.add(frozenset(pair))

    # create an Eulerian multigraph G3 from G by doubling all edges in the T-join
    G3 = nx.MultiGraph(G)
    G3.add_edges_from(t_join)

    # find an Euler path in G3; this is the merged pattern that we're looking for
    path: list[tuple[HexCoord, HexCoord]] = list(nx.eulerian_path(G3))

    # convert the path into an angle signature

    signature = ""
    startdir = compass = path[0][0].immediate_delta(path[0][1])

    for v, w in path[1:]:
        next_compass = v.immediate_delta(w)
        signature += ANGLES[(next_compass.value - compass.value) % len(ANGLES)]
        compass = next_compass

    return PatternInfo(
        startdir=startdir,
        signature=signature,
        is_per_world=True,
        id=op_id,
    )


if __name__ == "__main__":
    # note: you'd generate the inputs for this instead of hardcoding it
    overlay = overlay_patterns(
        op_id=ResourceLocation("lapisworks", "create_enchsent"),
        patterns=[
            (
                PatternInfo(
                    startdir=Direction.NORTH_WEST,
                    signature="aqaeawdwwwdwqwdwwwdweqqaqwedeewqded",
                    id=ResourceLocation("lapisworks", "create_enchsent1"),
                ),
                HexCoord(q=0, r=0),
            ),
            (
                PatternInfo(
                    startdir=Direction.NORTH_WEST,
                    signature="aqaeawdwwwdwqwdwwwdwewweaqa",
                    id=ResourceLocation("lapisworks", "create_enchsent2"),
                ),
                HexCoord(q=0, r=0),
            ),
            (
                PatternInfo(
                    startdir=Direction.NORTH_EAST,
                    signature="wdwewdwwwdwwwdwqwdwwwdw",
                    id=ResourceLocation("lapisworks", "create_enchsent3"),
                ),
                HexCoord(q=1, r=0),
            ),
            (
                PatternInfo(
                    startdir=Direction.NORTH_WEST,
                    signature="aqaeawdwwwdwqwdwwwdweqaawddeweaqa",
                    id=ResourceLocation("lapisworks", "create_enchsent4"),
                ),
                HexCoord(q=0, r=0),
            ),
            (
                PatternInfo(
                    startdir=Direction.NORTH_WEST,
                    signature="wdwwwdwqwdwwwdweqaawdde",
                    id=ResourceLocation("lapisworks", "create_enchsent5"),
                ),
                HexCoord(q=1, r=0),
            ),
            (
                PatternInfo(
                    startdir=Direction.NORTH_WEST,
                    signature="wdwwwdwqwdwwwdwweeeee",
                    id=ResourceLocation("lapisworks", "create_enchsent6"),
                ),
                HexCoord(q=1, r=0),
            ),
        ],
    )
    print(overlay)