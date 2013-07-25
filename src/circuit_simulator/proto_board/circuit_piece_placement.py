"""
Tools to figure out a good placement of circuit pieces on the proto board given
    the pieces.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_pieces import Circuit_Piece
# TODO(mikemeko): this is kind of hacky, coupled with board parsing
from circuit_simulator.main.constants import GROUND
from circuit_simulator.main.constants import POWER
from collections import defaultdict
from constants import CIRCUIT_PIECE_SEPARATION
from constants import GROUND_RAIL
from constants import POWER_RAIL
from constants import PROTO_BOARD_WIDTH
from constants import RAIL_LEGAL_COLUMNS
from constants import RAIL_ROWS
from copy import deepcopy
from core.data_structures.disjoint_set_forest import Disjoint_Set_Forest
from core.data_structures.queue import Queue
from itertools import permutations
from itertools import product
from sys import maxint
from util import dist

def closest_rail_loc(loc, rail_r):
  """
  Returns the closest rail location in row |rail_r| to the location |loc|.
  """
  assert rail_r in RAIL_ROWS, 'rail_r must be a rail row'
  r, c = loc
  return (rail_r, min(RAIL_LEGAL_COLUMNS, key=lambda col: abs(c - col)))

def loc_pairs_for_node(node_locs, node):
  """
  Returns a list of tuples of the form  (loc_1, loc_2, node) such that the set
      of locations in |nodes_locs| is fully connected if all the output pairs of
      locations are connected. This is essentially an MST problem where the
      locations are the nodes and the weight of an edge between two locations
      is the distance (manhattan) between the two locations. We use Kruskal's
      greedy algorithm. |node| is the corresponding node in for the locations
      in the circuit.
  """
  if node == GROUND or node == POWER:
    return [(loc, closest_rail_loc(loc, GROUND_RAIL if node == GROUND else
        POWER_RAIL), node) for loc in node_locs]
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
      mst_loc_pairs.append((loc_1, loc_2, node))
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

def loc_pairs_to_connect(pieces, resistors):
  """
  Returns a tuple of the locations pairs to connect so that the |pieces| and
      |resistors| are appropriately connected. Each location pairs
      comes with a flag indicating whether or not to include a resistor. Each
      location pair also comes with the node for the pair. If there is to be a
      resistor between the locations, the node of the first location is given (
      both nodes can be obtained from the flag, the first is given for the sake
      of consistency).
  """
  # find loc pairs to connect not taking resistors into account
  loc_pairs = reduce(list.__add__, (loc_pairs_for_node(locs_for_node(pieces,
      node), node) for node in all_nodes(pieces) if node))
  # find loc pairs to connect for resistors
  # TODO(mikemeko): method here is very ad hoc
  occurences = defaultdict(int)
  flagged_loc_pairs = []
  for loc_1, loc_2, node in loc_pairs:
    occurences[loc_1] += 1
    occurences[loc_2] += 1
    flagged_loc_pairs.append((loc_1, loc_2, None, node))
  for resistor in resistors:
    loc_1, loc_2 = min(product(locs_for_node(pieces, resistor.n1),
        locs_for_node(pieces, resistor.n2)), key=lambda (loc_1, loc_2): 5 * (
        occurences[loc_1] + occurences[loc_2]) + dist(loc_1, loc_2))
    occurences[loc_1] += 1
    occurences[loc_2] += 1
    flagged_loc_pairs.append((loc_1, loc_2, resistor, resistor.n1))
  return flagged_loc_pairs

def set_locations(pieces):
  """
  Given a (ordered) list of |pieces|, assigns them locations on the proto
      board. Tries to center the pieces in the middle of the proto board, and
      leaves a space of 2 columns between each consecuitive pair of pieces.
  TODO(mikemeko): can we do better?
  """
  # put the pieces as much at the center of the proto board as possible
  col = (PROTO_BOARD_WIDTH - sum(piece.width + CIRCUIT_PIECE_SEPARATION for
      piece in pieces)) / 2 + 1
  for piece in pieces:
    piece.top_left_loc = (piece.top_left_row, col)
    col += piece.width + CIRCUIT_PIECE_SEPARATION

def cost(placement):
  """
  Returns a heuristic cost of the given |placement| - the sum of the distances
      between the loc pairs that would need to be connected.
  TODO(mikemeko): here, the concept of distance should take into account the
      presence of the circuit pieces, i.e. it should factor having to wire
      around the pieces.
  """
  set_locations(placement)
  return sum(dist(loc_1, loc_2) for loc_1, loc_2, resistor_flag, node in
      loc_pairs_to_connect(placement, []))

def find_placement(pieces):
  """
  Given a list of |pieces|, returns a placement of the pieces that requires
      comparatively small wiring. Finding the absolute best placement is too
      expensive.
  """
  assert isinstance(pieces, list), 'pieces must be a list'
  assert all(isinstance(piece, Circuit_Piece) for piece in pieces), ('all '
      'items in pieces must be Circuit_Pieces')
  pieces = deepcopy(pieces)
  # order pieces in decreasing number of nodes
  pieces.sort(key=lambda piece: -len(piece.nodes))
  queue = Queue()
  def add_to_queue(piece):
    if piece in pieces:
      queue.push(piece)
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
          for top_left_row in piece.possible_top_left_rows:
            piece.top_left_row = top_left_row
            new_placement = deepcopy(placement)
            new_placement.insert(i, piece)
            new_placement_cost = cost(new_placement)
            if new_placement_cost < best_placement_cost:
              best_placement = deepcopy(new_placement)
              best_placement_cost = new_placement_cost
      placement = best_placement
      placement_cost = best_placement_cost
      # add pieces connected to this piece to the queue
      for piece in reduce(list.__add__, [[piece for piece in pieces if node
          in piece.nodes] for node in current_piece.nodes], []):
        add_to_queue(piece)
  return placement, placement_cost

def _find_placement(pieces):
  """
  find_placement that looks at every possibility. Takes too long!
  """
  piece_options = []
  for piece in pieces:
    options = []
    for p in [piece, piece.inverted()]:
      for top_left_row in piece.possible_top_left_rows:
        option = deepcopy(p)
        option.top_left_row = top_left_row
        options.append(option)
    piece_options.append(options)
  best_placement = None
  best_cost = maxint
  for perm in permutations(piece_options):
    perm_best = min(product(*perm), key=cost)
    perm_best_cost = cost(perm_best)
    if perm_best_cost < best_cost:
      best_placement = perm_best
      best_cost = perm_best_cost
  return best_placement, best_cost
