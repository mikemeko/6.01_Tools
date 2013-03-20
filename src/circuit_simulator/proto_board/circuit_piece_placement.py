"""
Tools to figure out a good placement of circuit pieces on the proto board given
    the pieces.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_pieces import Circuit_Piece
from copy import deepcopy
from core.data_structures.disjoint_set_forest import Disjoint_Set_Forest
from core.data_structures.queue import Queue
from sys import maxint
from util import dist

def loc_pairs_for_node(node_locs):
  """
  Returns a list of pairs of nodes to connect so that all of the locations in
      |node_locs| are connected. This is essentially an MST problem where the
      locations are the nodes and the weight of an edge between two locations
      is the distance (manhattan) between the two locations. We use Kruskal's
      greedy algorithm.
  """
  # find all possible pairs of locations
  all_loc_pairs = [(loc_1, loc_2) for i, loc_1 in enumerate(node_locs) for
      loc_2 in node_locs[i + 1:]]
  # sort in increasing order of loc pair distance
  all_loc_pairs.sort(key=lambda loc_pair: dist(*loc_pair))
  disjoint_loc_pair_sets = Disjoint_Set_Forest()
  # initialize the graph as fully disconnected
  for loc in node_locs:
    disjoint_loc_pair_sets.make_set(loc)
  mst_loc_pairs = []
  # add edges to the graph until fully connected, but use the least expensive
  # edges to do so in the process
  for (loc_1, loc_2) in all_loc_pairs:
    if (disjoint_loc_pair_sets.find_set(loc_1) !=
        disjoint_loc_pair_sets.find_set(loc_2)):
      disjoint_loc_pair_sets.union(loc_1, loc_2)
      mst_loc_pairs.append((loc_1, loc_2))
  return mst_loc_pairs

def locs_for_node(pieces, node):
  """
  Returns a list of all the locations associated with the given |node| among
      all of the pieces in |pieces|.
  """
  return reduce(list.__add__, (piece.locs_for(node) for piece in pieces), [])

def all_nodes(pieces):
  """
  Returns a list of all of the nodes present in the given collection of
      |pieces|.
  """
  return reduce(set.union, (piece.nodes for piece in pieces), set())

def loc_pairs_to_connect(pieces):
  """
  Returns a tuple of the locations pairs to connect so that the |pieces| are
      appropriately connected.
  """
  return tuple(reduce(list.__add__, (loc_pairs_for_node(locs_for_node(pieces,
      node)) for node in all_nodes(pieces))))

def set_locations(pieces):
  """
  Given a (ordered) list of |pieces|, assigns them locations on the proto
      board. Tries to center the pieces in the middle of the proto board, and
      leaves a space of 2 columns between each consecuitive pair of pieces.
  TODO(mikemeko): can we do better?
  """
  col = 28 - sum(piece.width + 2 for piece in pieces) / 2
  for i, piece in enumerate(pieces):
    piece.top_left_loc = (6, col)
    col += piece.width + 2

def cost(placement):
  """
  Returns a heuristic cost of the given |placement| - the sum of the distances
      between the loc pairs that would need to be connected.
  """
  set_locations(placement)
  return sum(dist(*loc_pair) for loc_pair in loc_pairs_to_connect(placement))

def find_placement(pieces):
  """
  Given a list of |pieces|, returns a placement of the pieces that requires
      comparatively small wiring. Finding the absolute best placement is too
      expensive. All pieces are placed in the middle strip of the proto board.
  """
  assert isinstance(pieces, list), 'pieces must be a list'
  assert all(isinstance(piece, Circuit_Piece) for piece in pieces), ('all '
      'items in pieces must be Circuit_Pieces')
  pieces = deepcopy(pieces)
  # order pieces in decreasing number of nodes
  pieces.sort(key=lambda piece: -len(piece.nodes))
  queue = Queue()
  def add_to_queue(piece):
    queue.push(piece)
    if piece in pieces:
      pieces.remove(piece)
  placement = []
  placement_cost = maxint
  while pieces:
    add_to_queue(pieces[0])
    while queue:
      current_piece = queue.pop()
      # try inserting the current piece at all possible indicies in the current
      #     placement, consider both regular and inverted piece
      best_placement = None
      best_placement_cost = maxint
      # all indicies in which the piece can be inserted
      for i in xrange(len(placement) + 1):
        # both regular and inverted piece
        for piece in [current_piece, current_piece.inverted()]:
          new_placement = deepcopy(placement)
          new_placement.insert(i, piece)
          new_placement_cost = cost(new_placement)
          if new_placement_cost < best_placement_cost:
            best_placement = new_placement
            best_placement_cost = new_placement_cost
      placement = best_placement
      placement_cost = best_placement_cost
      # add pieces connected to this piece to the queue
      for piece in reduce(list.__add__, [[piece for piece in pieces if node
          in piece.nodes] for node in current_piece.nodes], []):
        add_to_queue(piece)
    return placement, placement_cost
