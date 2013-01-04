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
    self.new_out = inp_bound[0].scalar_mult(self.K)

class Delay(Component):
  """
  TODO(mikemeko)
  """
  def update(self, inp_bound):
    self.new_out = inp_bound[0].shift()

class Adder(Component):
  """
  TODO(mikemeko)
  """
  def update(self, inp_bound):
    self.new_out = reduce(lambda p_1, p_2: p_1 + p_2, inp_bound)

def solve_system(components, last_comp, num_variables):
  """
  TODO(mikemeko)
  """
  covered_variables = {'X':Polynomial({'X':R_Polynomial([1])}),
      'Y':Polynomial({'Y':R_Polynomial([1])})}
  while len(covered_variables) < num_variables:
    for c in components:
      if c.new_out is None and all(i in covered_variables for i in c.inp):
        c.update([covered_variables[i] for i in c.inp])
        covered_variables[c.out] = c.new_out
        break
  last_comp.update([covered_variables[i] for i in last_comp.inp])
  return covered_variables[last_comp.out] - last_comp.new_out

if __name__ == '__main__':
  comp_1 = Delay(['A'], 'Y')
  comp_2 = Adder(['X','Y'], 'A')
  components = [comp_1, comp_2]
  print solve_system(components, comp_1, 3)
