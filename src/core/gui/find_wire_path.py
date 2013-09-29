"""
Script to find a good path of wires from one point on a board to another,
    attempting not to cross drawables and other wires already on the board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BEND_COST
from constants import BOARD_GRID_SEPARATION
from constants import CROSS_COST
from core.search.search import a_star
from core.search.search import Search_Node
from core.util.util import sign
from util import snap

def drawable_coverage(drawable):
  """
  Returns a set of points on the board covered by the given |drawable|.
  """
  ox, oy = drawable.offset
  w, h = drawable.width, drawable.height
  return set([(x, y) for x in xrange(ox, ox + w + 1, BOARD_GRID_SEPARATION) for
      y in xrange(oy, oy + h + 1, BOARD_GRID_SEPARATION)])

def wire_coverage(start, end):
  """
  Returns a set of the points on the board that would be covered by a wire going
      from point |start| to point |end|.
  """
  x1, y1 = start
  x2, y2 = end
  if x1 == x2:
    return set([(x1, y) for y in xrange(min(y1, y2), max(y1, y2) + 1,
        BOARD_GRID_SEPARATION)])
  elif abs(x1 - x2) > abs(y1 - y2):
    m = (y2 - y1) / float(x2 - x1)
    return set([(x, snap(y1 + m * (x - x1))) for x in xrange(min(x1, x2), max(
        x1, x2) + 1, BOARD_GRID_SEPARATION)])
  else:
    m = (x2 - x1) / float(y2 - y1)
    return set([(snap(x1 + m * (y - y1)), y) for y in xrange(min(y1, y2), max(
        y1, y2) + 1, BOARD_GRID_SEPARATION)])

def manhattan_dist(start, end):
  """
  Returns the Manhattan distance on the board from point |start| to point |end|.
  """
  x1, y1 = start
  x2, y2 = end
  return (abs(x1 - x2) + abs(y1 - y2)) / BOARD_GRID_SEPARATION

class Wire_Path_Search_Node(Search_Node):
  """
  Search_Node for wire path search.
  """
  def __init__(self, board_coverage, current_point, num_bends=0, direction=None,
      parent=None, cost=0):
    Search_Node.__init__(self, (board_coverage, current_point, num_bends,
        direction), parent, cost)
  def get_children(self):
    board_coverage, current_point, num_bends, direction = self.state
    x, y = current_point
    children = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
      new_x = x + dx * BOARD_GRID_SEPARATION
      new_y = y + dy * BOARD_GRID_SEPARATION
      new_wire_coverage = wire_coverage((new_x, new_y), current_point)
      bend = direction is not None and direction != (dx, dy)
      cost = (self.cost + 1 + CROSS_COST * (len(board_coverage &
          new_wire_coverage)) + BEND_COST * bend)
      children.append(Wire_Path_Search_Node(board_coverage, (new_x, new_y),
          num_bends + bend, (dx, dy), self, cost))
    return children

def goal_test_for_end_point(end_point):
  def goal_test(state):
    board_coverage, current_point, num_bends, direction = state
    return current_point == end_point
  return goal_test

def heuristic_for_end_point(end_point):
  def heuristic(state):
    board_coverage, current_point, num_bends, direction = state
    x1, y1 = current_point
    x2, y2 = end_point
    return manhattan_dist(current_point, end_point) + BEND_COST * (
        (x1 != x2) and (y1 != y2))
  return heuristic

def get_board_coverage(board):
  """
  Returns a set of the points on the |board| that are covered by drawables and
      wires. Connectors are not included.
  """
  coverage = set()
  for drawable in board.get_drawables():
    coverage |= drawable_coverage(drawable)
    for wire in drawable.wires():
      coverage |= wire_coverage(wire.start_connector.center,
          wire.end_connector.center)
  for drawable in board.get_drawables():
    for connector in drawable.connectors:
      coverage.remove(connector.center)
  return coverage

def condensed_points(points):
  """
  Returns a collapsed version of |points| so that there are no three consecutive
      collinear points.
  """
  assert len(points) >= 1
  condensed = points[:1]
  for i in xrange(1, len(points) - 1):
    _x, _y = condensed[-1]
    x, y = points[i]
    x_, y_ = points[i + 1]
    if sign(x - _x) != sign(x_ - x) or sign(y - _y) != sign(y_ - y):
      condensed.append(points[i])
  condensed.append(points[-1])
  return condensed

def path_coverage(path):
  """
  Returns a set of the points on the board covered by the given |path| of
      points.
  """
  coverage = set()
  for i in xrange(len(path) - 1):
    coverage |= wire_coverage(path[i], path[i + 1])
  return coverage

def find_wire_path_simple(board, start_point, end_point):
  """
  Returns a list of tuples indicating a path from |start_point| to |end_point|
      on the |board|, doing an exhaustive search for paths including up to 2
      bends.
  """
  x1, y1 = start_point
  x2, y2 = end_point
  if x1 == x2 or y1 == y2:
    return [start_point, end_point]
  else:
    paths = [[(x1, y1), (x1, y2), (x2, y2)], [(x1, y1), (x2, y1), (x2, y2)]]
    x_sign = 1 if x1 <= x2 else -1
    for x in xrange(x1 + x_sign * BOARD_GRID_SEPARATION, x2, x_sign *
        BOARD_GRID_SEPARATION):
      paths.append([(x1, y1), (x, y1), (x, y2), (x2, y2)])
    y_sign = 1 if y1 <= y2 else -1
    for y in xrange(y1 + y_sign * BOARD_GRID_SEPARATION, y2, y_sign *
        BOARD_GRID_SEPARATION):
      paths.append([(x1, y1), (x1, y), (x2, y), (x2, y2)])
    board_coverage = get_board_coverage(board)
    return min(paths, key=lambda path: len(board_coverage & path_coverage(
        path)))

def find_wire_path(board, start_point, end_point):
  """
  Returns a list of tuples indicating a path from |start_point| to |end_point|
      on the |board|, doing an overall search. If the overall search takes too
      long, uses find_wire_path_simple.
  """
  board_coverage = get_board_coverage(board)
  if end_point not in board_coverage:
    board_coverage = frozenset(board_coverage)
  else:
    board_coverage = frozenset()
  search_result = a_star(Wire_Path_Search_Node(board_coverage, start_point),
      goal_test_for_end_point(end_point), heuristic_for_end_point(end_point),
      max_states_to_expand=3000)
  if search_result:
    return condensed_points([state[1] for state in search_result.get_path()])
  else:
    return find_wire_path_simple(board, start_point, end_point)
