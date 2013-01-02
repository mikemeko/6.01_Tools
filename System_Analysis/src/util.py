"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

class Polynomial:
  """
  TODO(mikemeko)
  """
  def __init__(self, data):
    """
    |data|: a dictionary mapping variable names to their coefficients.
        For example, RX + 2Y is represented by {'X':'R', 'Y':'2'}.
    """
    self.data = data
  def __str__(self):
    return ' + '.join('%s%s' % tuple(reversed(i)) for i in self.data.items())

if __name__ == '__main__':
  poly = Polynomial({'X':'R', 'Y':'2'})
  print poly
