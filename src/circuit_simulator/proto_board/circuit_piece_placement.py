"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from copy import deepcopy
from core.data_structures.disjoint_set_forest import Disjoint_Set_Forest
from sys import maxint
from util import dist

def loc_pairs_for_node(node_locs):
  all_loc_pairs = [(loc_1, loc_2) for i, loc_1 in enumerate(node_locs) for
      loc_2 in node_locs[i + 1:]]
  all_loc_pairs.sort(key=lambda loc_pair: dist(*loc_pair))
  disjoint_loc_pair_sets = Disjoint_Set_Forest()
  for loc in node_locs:
    disjoint_loc_pair_sets.make_set(loc)
  mst_loc_pairs = []
  for (loc_1, loc_2) in all_loc_pairs:
    if (disjoint_loc_pair_sets.find_set(loc_1) !=
        disjoint_loc_pair_sets.find_set(loc_2)):
      disjoint_loc_pair_sets.union(loc_1, loc_2)
      mst_loc_pairs.append((loc_1, loc_2))
  return mst_loc_pairs

def locs_for_node(placement, node):
  return reduce(list.__add__, (piece.locs_for(node) for piece in placement),
      [])

def all_nodes(placement):
  return reduce(set.union, (piece.nodes for piece in placement), set())

def loc_pairs_to_connect(placement):
  return tuple(reduce(list.__add__, (loc_pairs_for_node(locs_for_node(
      placement, node)) for node in all_nodes(placement))))

def set_locations(pieces):
  # starting col
  col = 28 - sum(piece.width + 2 for piece in pieces) / 2
  for i, piece in enumerate(pieces):
    piece.top_left_loc = (6, col)
    col += piece.width + 2

def cost(placement):
  """
  TODO(mikemeko)
  """
  set_locations(placement)
  return sum(dist(*loc_pair) for loc_pair in loc_pairs_to_connect(placement))

def find_placement(pieces):
  """
  TODO(mikemeko)
  """
  # TODO: write a queue class
  queue = []
  def add_to_queue(piece):
    pieces.remove(piece)
    queue.append(piece)
  placement = []
  placement_cost = maxint
  piece_with_most_nodes = max(pieces, key=lambda piece: len(piece.nodes))
  add_to_queue(piece_with_most_nodes)
  while queue:
    current_piece = queue.pop(0)
    best_placement = None
    best_placement_cost = maxint
    for i in xrange(len(placement) + 1):
      for piece in [current_piece, current_piece.inverted()]:
        new_placement = placement[:]
        new_placement.insert(i, piece)
        new_placement_cost = cost(new_placement)
        if new_placement_cost < best_placement_cost:
          # TODO: deepcopy because pieces get changed through the iteration
          best_placement = deepcopy(new_placement)
          best_placement_cost = new_placement_cost
    placement = best_placement
    placement_cost = best_placement_cost
    for node in current_piece.nodes:
      for piece in pieces:
        if node in piece.nodes:
          # TODO: modifying pieces while iterating through it
          add_to_queue(piece)
  return placement, placement_cost
