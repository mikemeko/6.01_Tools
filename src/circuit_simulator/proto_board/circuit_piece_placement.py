"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from copy import deepcopy
from sys import maxint
from util import dist

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
  cost = 0
  set_locations(placement)
  for piece in placement:
    for node in piece.nodes:
      piece_node_locs = piece.locs_for(node)
      other_node_locs = reduce(lambda l_1, l_2: l_1 + l_2,
          (other_piece.locs_for(node) for other_piece in placement if
          other_piece != piece), [])
      if other_node_locs:
        cost += min(dist(loc_1, loc_2) for loc_1 in piece_node_locs for
            loc_2 in other_node_locs)
  return cost

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
