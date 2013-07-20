"""
Script to find a good path of wires from one point on a board to another,
    attempting not to cross drawables and other wires already on the board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from find_wire_path import wire_coverage
from find_wire_path import get_board_coverage

def path_coverage(path):
  """
  Returns a set of the crossing points covered by the given |path| of points.
  """
  coverage = set()
  for i in xrange(len(path) - 1):
    coverage |= wire_coverage(path[i], path[i + 1])
  return coverage

def find_wire_path(board, start_point, end_point):
  """
  Returns a list of tuples indicating a path from |start_point| to |end_point|
      on the |board|.
  """
  x1, y1 = start_point
  x2, y2 = end_point
  if x1 == x2 or y1 == y2:
    return [start_point, end_point]
  else:
    paths = [[(x1, y1), (x1, y2), (x2, y2)], [(x1, y1), (x2, y1), (x2, y2)]]
    board_coverage = get_board_coverage(board)
    return min(paths, key=lambda path: len(board_coverage & path_coverage(
        path)))

