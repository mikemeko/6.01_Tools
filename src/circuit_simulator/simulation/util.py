"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

def get_resistor_color_indices(r):
  """
  Returns a list of the indices (in
    circuit_simulator.proto_board.constants.RESISTOR_COLORS) of the three colors
    that display the given resistance |r|.
  """
  coeff, exp = ('%.1E' % max(r, 10)).split('E+')
  return map(int, str(int(10 * float(coeff)))) + [int(exp) - 1]
