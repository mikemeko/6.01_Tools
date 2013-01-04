"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from poly import Polynomial
from poly import R_Polynomial

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
    Component.__init__(self, [inp], out)
    self.K = K
  def update(self, inp_bound):
    self.new_out = inp_bound[0].scalar_mult(self.K)

class Delay(Component):
  """
  TODO(mikemeko)
  """
  def __init__(self, inp, out):
    Component.__init__(self, [inp], out)
  def update(self, inp_bound):
    self.new_out = inp_bound[0].shift()

class Adder(Component):
  """
  TODO(mikemeko)
  """
  def update(self, inp_bound):
    self.new_out = reduce(lambda p_1, p_2: p_1 + p_2, inp_bound)

def solve_system(components, last_comp):
  """
  TODO(mikemeko)
  """
  # TODO(mikemeko): last_comp can be automatically identified
  covered_variables = {'X':Polynomial({'X':R_Polynomial([1])}),
      'Y':Polynomial({'Y':R_Polynomial([1])})}
  while last_comp.new_out is None:
    for c in components:
      if c.new_out is None and all(i in covered_variables for i in c.inp):
        c.update([covered_variables[i] for i in c.inp])
        covered_variables[c.out] = c.new_out
        break
  return covered_variables['Y']

if __name__ == '__main__':
  comp_1 = Adder(['X', 'D'], 'A')
  comp_2 = Gain('A', 'B', 10)
  comp_3 = Adder(['B', 'Y'], 'C')
  comp_4 = Delay('C', 'Y')
  comp_5 = Delay('Y', 'D')
  components = [comp_1, comp_2, comp_3, comp_4, comp_5]
  print solve_system(components, comp_4)
