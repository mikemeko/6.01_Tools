"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from util import Polynomial
from util import R_Polynomial

class Component:
  """
  TODO(mikemeko)
  """
  def __init__(self, inp, out):
    self.inp = inp
    self.out = out
    self.new_out = None
  def update(self):
    # TODO(mikemeko)
    pass

class Gain(Component):
  """
  TODO(mikemeko)
  """
  def __init__(self, inp, out, K):
    Component.__init__(self, inp, out)
    self.K = K
  def update(self, inp_bound):
    self.new_out = inp_bound.scalar_mult(self.K)

class Delay(Component):
  """
  TODO(mikemeko)
  """
  def update(self, inp_bound):
    self.new_out = inp_bound.shift()

def solve_system(components, last_comp, num_variables):
  """
  TODO(mikemeko)
  """
  covered_variables = {'X':Polynomial({'X':R_Polynomial([1])}),
      'Y':Polynomial({'Y':R_Polynomial([1])})}
  while len(covered_variables) < num_variables:
    for comp in components:
      if comp.new_out is None and comp.inp in covered_variables:
        comp.update(covered_variables[comp.inp])
        covered_variables[comp.out] = comp.new_out
        break
  last_comp.update(covered_variables[last_comp.inp])
  return covered_variables[last_comp.out] - last_comp.new_out

if __name__ == '__main__':
  comp_1 = Gain('X', 'A', 2)
  comp_2 = Delay('A', 'Y')
  components = [comp_1, comp_2]
  print solve_system(components, comp_2, 3)
