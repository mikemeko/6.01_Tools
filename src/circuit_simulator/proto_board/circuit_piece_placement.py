"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from copy import deepcopy
from sys import maxint
from util import dist

# TODO: put in another file
# TODO: is this as good as it can be?
def loc_pairs_to_connect(placement):
  loc_pairs = []
  handled_locs = set()
  for piece in placement:
    for node in piece.nodes:
      for loc_1 in piece.locs_for(node):
        if loc_1 in handled_locs:
          continue
        handled_locs.add(loc_1)
        other_locs = reduce(lambda l_1, l_2: l_1 + l_2, (
            other_piece.locs_for(node) for other_piece in placement))
        other_locs.remove(loc_1)
        if other_locs:
          loc_2 = min(other_locs, key=lambda loc: dist(loc_1, loc))
          loc_pairs.append((loc_1, loc_2))
          handled_locs.add(loc_2)
  return tuple(loc_pairs)

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
