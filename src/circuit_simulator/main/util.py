"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import RESISTOR_FILL
from constants import RESISTOR_NUM_ZIG_ZAGS
from constants import RESISTOR_OUTLINE

def draw_resistor_zig_zags(canvas, ox, oy, w, h):
  """
  Draws resistor zig zags on the given |canvas| at the given offset (|ox|,
      |oy|). The width |w| and height |h| are used to determine orientation.
  Returns a set containing the canvas ids of the lines used to draw the zig
      zag.
  """
  parts = set()
  parts.add(canvas.create_rectangle(ox, oy, ox + w, oy + h, fill=RESISTOR_FILL,
      outline=RESISTOR_OUTLINE))
  if w > h: # horizontal
    s = w / (2 * RESISTOR_NUM_ZIG_ZAGS)
    parts.add(canvas.create_line(ox, oy + h / 2, ox + s, oy))
    for i in xrange(1, RESISTOR_NUM_ZIG_ZAGS):
      parts.add(canvas.create_line(ox + (2 * i - 1) * s, oy, ox + 2 * i * s,
          oy + h))
      parts.add(canvas.create_line(ox + (2 * i + 1) * s, oy, ox + 2 * i * s,
          oy + h))
    parts.add(canvas.create_line(ox + w, oy  + h / 2, ox + w - s, oy))
  else: # vertical
    s = h / (2 * RESISTOR_NUM_ZIG_ZAGS)
    parts.add(canvas.create_line(ox + w / 2, oy, ox + w, oy + s))
    for i in xrange(1, RESISTOR_NUM_ZIG_ZAGS):
      parts.add(canvas.create_line(ox, oy + 2 * i * s, ox + w,
          oy + (2 * i - 1) * s))
      parts.add(canvas.create_line(ox, oy + 2 * i * s, ox + w,
          oy + (2 * i + 1) * s))
    parts.add(canvas.create_line(ox + w / 2, oy + h, ox + w,
        oy + h - s))
  return parts

def sign(x):
  """
  Returns -1 if |x| is negative, 1 if |x| is positive, or 0 if |x| is 0.
  """
  if x < 0:
    return -1
  elif x > 0:
    return 1
  return 0
