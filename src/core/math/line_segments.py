"""
Utility for line segments.
    (1) Check whether two line segments intersect. Credit to: http://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
    (2) Translate segments.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.util.util import overlap
from math import atan2
from math import cos
from math import pi
from math import sin

def _cross(V, W):
  """
  Returns the magnitude of the cross product of vectors |V| and |W|.
  """
  vx, vy = V
  wx, wy = W
  return vx * wy - vy * wx

def intersect(segment1, segment2):
  """
  If |segment1| or |segment2| has 0 length, returns False.
  If |segment1| and |segment2| intersect and are colliniar, returns 'collinear'.
  Otherwise, if |segment1| and |segment2| intersect at exactly one point,
      returns that point.
  Otherwise, returns False.
  Segments should be given in the form ((x0, y0), (x1, y1)).
  """
  (x00, y00), (x01, y01) = segment1
  x00, y00, x01, y01 = float(x00), float(y00), float(x01), float(y01)
  R = (x01 - x00, y01 - y00)
  if R == (0, 0):
    return False
  (x10, y10), (x11, y11) = segment2
  x10, y10, x11, y11 = float(x10), float(y10), float(x11), float(y11)
  S = (x11 - x10, y11 - y10)
  if S == (0, 0):
    return False
  QmP = (x10 - x00, y10 - y00)
  RcS = float(_cross(R, S))
  QmPcS = _cross(QmP, S)
  QmPcR = _cross(QmP, R)
  if RcS == 0:
    # segments are parallel
    if QmPcR == 0:
      # segments are collinear
      if R[0] == 0:
        return 'collinear' if overlap((min(y00, y01), max(y00, y01)), (min(y10,
            y11), max(y10, y11))) else False
      else:
        for (x, vx, xs) in [(x00, R[0], (x10, x11)), (x10, S[0], (x00, x01))]:
          for ox in xs:
            if 0 <= (ox - x) / vx <= 1:
              return 'collinear'
        return False
    else:
      return False
  t = QmPcS / RcS
  if t < 0 or t > 1:
    return False
  u = QmPcR / RcS
  if u < 0 or u > 1:
    return False
  return (x00 + t * R[0], y00 + t * R[1])

def translate(segment, d):
  """
  Returns a new segment that corresponds to the given |segment| translated
      perpendicularly by |d| units.
  Segment should be given and is returned in the form ((x1, y1), (x2, y2)).
  """
  (x1, y1), (x2, y2) = segment
  if x1 > x2:
    x1, x2 = x2, x1
    y1, y2 = y2, y1
  phi = atan2(y2 - y1, x2 - x1)
  theta = pi / 2 - phi
  dx = d * cos(theta)
  dy = d * sin(theta)
  return ((x1 - dx, y1 - dy), (x2 - dx, y2 - dy))
