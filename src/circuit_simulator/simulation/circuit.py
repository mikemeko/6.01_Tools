"""
TODO(mikemeko)
Remember to acknowledge software lab 9.
"""

from core.math.equation_solver import solve_equations

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

class One_Port:
  """
  TODO(mikemeko)
  """
  def __init__(self, n1, n2, i):
    """
    TODO(mikemeko)
    """
    self.n1 = n1
    self.n2 = n2
    self.i = i
  @property
  def equation(self):
    """
    TODO(mikemeko)
    """
    raise Exception('subclasses should implement this')

class Voltage_Source(One_Port):
  """
  TODO(mikemeko)
  """
  def __init__(self, n1, n2, i, v0):
    """
    TODO(mikemeko)
    """
    One_Port.__init__(self, n1, n2, i)
    self.v0 = v0
  def equation(self):
    return [(1, self.n1), (-1, self.n2), (-self.v0, None)]

class Resistor(One_Port):
  """
  TODO(mikemeko)
  """
  def __init__(self, n1, n2, i, r):
    """
    TODO(mikemeko)
    """
    One_Port.__init__(self, n1, n2, i)
    self.r = r
  def equation(self):
    return [(1, self.n1), (-1, self.n2), (-self.r, self.i)]

class Circuit:
  """
  TODO(mikemeko)
  """
  def __init__(self, components, gnd):
    """
    TODO(mikemeko)
    """
    assert all(isinstance(c, One_Port) for c in components), ('all components '
        'must be one ports')
    self.components = components
    self.gnd = gnd
    self.data = None # TODO(mikemeko): clarify
    self._solve()
  def _solve(self):
    equations = []
    KCL = {}
    for component in self.components:
      equations.append(component.equation())
      KCL[component.n1] = KCL.get(component.n1, []) + [(1, component.i)]
      KCL[component.n2] = KCL.get(component.n2, []) + [(-1, component.i)]
    equations.extend([KCL[n] for n in KCL if n is not self.gnd])
    equations.append([(1, self.gnd)])
    self.data = solve_equations(equations)

if __name__ == '__main__':
  c = Circuit([Voltage_Source('e1', 'e0', 'i3', 10), Resistor('e1', 'e2', 'i1',
      3), Resistor('e2', 'e0', 'i2', 3)], 'e0')
  print c.data
