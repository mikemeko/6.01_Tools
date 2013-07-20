"""
Script to find a good path of wires from one point on a board to another,
    attempting not to cross drawables and other wires already on the board.
TODO(mikemeko): this script is currently NOT used as it is too slow, maybe
    improve and use. We currently use the simpler file_wire_path_simple.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BOARD_GRID_SEPARATION
from core.search.search import a_star
from core.search.search import Search_Node

def drawable_coverage(drawable):
  """
  Returns a set of all the crossing points on the board covered by the given
      |drawable|.
  """
  ox, oy = drawable.offset
  w, h = drawable.width, drawable.height
  return set([(x, y) for x in xrange(ox, ox + w + 1, BOARD_GRID_SEPARATION) for
      y in xrange(oy, oy + h + 1, BOARD_GRID_SEPARATION)])

def wire_coverage(start, end):
  """
  Returns a set of all the crossing points on the board that would be covered by
      a wire going from point |start| to point |end|.
  """
  x1, y1 = start
  x2, y2 = end
  assert x1 == x2 or y1 == y2
  if x1 == x2:
    return set([(x1, y) for y in xrange(min(y1, y2), max(y1, y2) + 1,
        BOARD_GRID_SEPARATION)])
  else: # y1 == y2
    return set([(x, y1) for x in xrange(min(x1, x2), max(x1, x2) + 1,
        BOARD_GRID_SEPARATION)])

def manhattan_dist(start, end):
  """
  Returns the Manhattan distance from point |start| to point |end|.
  """
  x1, y1 = start
  x2, y2 = end
  return abs(x1 - x2) + abs(y1 - y2)

class Wire_Path_Search_Node(Search_Node):
  """
  Search_Node for wire path search.
  """
  def __init__(self, board_width, board_height, occupied_locs, current_point,
      end_point, last_point=None, parent=None, cost=0):
    """
    |board_width|, |board_height|: width and height of the board on which we are
        finding a path.
    |occupied_locs|: a set of the crossing points on the board that are already
        occupied by drawables and wires.
    |current_point|: current point on the wire path.
    |end_point|: target end of the wire path.
    |last_point|: the last point (prior to the current point) on the path.
    """
    self.board_width = board_width
    self.board_height = board_height
    self.occupied_locs = occupied_locs
    Search_Node.__init__(self, (last_point, current_point, end_point), parent,
        cost)
  def get_children(self):
    last_point, current_point, end_point = self.state
    if last_point:
      lx, ly = last_point
    x, y = current_point
    next_points = []
    d = manhattan_dist(current_point, end_point)
    if not last_point or x == lx:
      for _x in xrange(x - d, x + d + 1, BOARD_GRID_SEPARATION):
        next_points.append((_x, y))
    if not last_point or y == ly:
      for _y in xrange(y - d, y + d + 1, BOARD_GRID_SEPARATION):
        next_points.append((x, _y))
    children = []
    for point in next_points:
      if point != current_point:
        new_wire_coverage = wire_coverage(point, current_point)
        cost = self.cost + manhattan_dist(point, current_point) + 1000 * len(
            self.occupied_locs & new_wire_coverage) + 1000
        children.append(Wire_Path_Search_Node(self.board_width,
            self.board_height, self.occupied_locs, point, end_point,
            current_point, self, cost))
    return children

def goal_test(state):
  """
  Goal test for the search.
  """
  last_point, current_point, end_point = state
  return current_point == end_point

def heuristic(state):
  """
  Heuristic for the search.
  """
  last_point, current_point, end_point = state
  x1, y1 = current_point
  x2, y2 = end_point
  return manhattan_dist(current_point, end_point)

def get_board_coverage(board):
  """
  Returns a set of the crossing points on the |board| that are covered by
      drawables and wires.
  """
  coverage = set()
  for drawable in board.get_drawables():
    coverage |= drawable_coverage(drawable)
    for wire in drawable.wires():
      coverage |= wire_coverage(wire.start_connector.center,
          wire.end_connector.center)
  return coverage

def find_wire_path(board, start_point, end_point):
  """
  Returns a list of tuples indicating a path from |start_point| to |end_point|
      on the |board|.
  """
  return [state[1] for state in a_star(Wire_Path_Search_Node(board.width,
      board.height, get_occupied_locs(board), start_point, end_point),
      goal_test, heuristic).get_path()]

