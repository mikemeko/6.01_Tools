"""
Representation for DT LTI systems.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from poly import Polynomial
from poly import R_Polynomial
from system_function import System_Function

class Component:
  """
  Representation for a component in a DT LTI system: gain, delay, or adder.
  """
  def __init__(self, inp_vars, out_var):
    """
    |imp_vars|: a list of the names of the input variables to this component.
    |out_var|: the name of the output variable of this component.
    """
    self.inp_vars = inp_vars
    self.out_var = out_var
    self.updated_out = None
  @property
  def update(self, inp_polys):
    """
    This updates the the |updated_out| attribute. It is called once all the
    input variables are described as polynomials only in X and Y.
    """
    raise NotImplementedError('subclasses should implement this')
  def updated(self):
    """
    Returns True if the |updated_out| has been updated, False otherwise.
    """
    return self.updated_out is not None

class Gain(Component):
  """
  Representation for a gain.
  """
  def __init__(self, inp_var, out_var, K):
    assert isinstance(K, (float, int, long)), 'K must be a number'
    Component.__init__(self, [inp_var], out_var)
    self.K = K
  def update(self, inp_polys):
    self.updated_out = inp_polys[0].scalar_mult(self.K)

class Delay(Component):
  """
  Representation for a delay.
  """
  def __init__(self, inp_var, out_var):
    Component.__init__(self, [inp_var], out_var)
  def update(self, inp_bound):
    self.updated_out = inp_bound[0].shift()

class Adder(Component):
  """
  Representation for an adder.
  """
  def update(self, inp_bound):
    self.updated_out = reduce(Polynomial.__add__, inp_bound)

class System:
  """
  Representation for a DT LTI system.
  """
  def __init__(self, components):
    """
    |components|: a list of the instances of Component in this System.
    """
    self.components = components
    self.sf = None
    self._solve_sf()
  def _solve_sf(self):
    """
    Solves for the system function of this system.
    """
    last_comp = None # the component that outputs Y
    for c in self.components:
      if c.out_var is 'Y':
        last_comp = c
        break
    assert last_comp is not None, 'a component that outputs Y is required'
    covered_variables = {'X':Polynomial({'X':R_Polynomial([1])}),
        'Y':Polynomial({'Y':R_Polynomial([1])})}
    while not last_comp.updated():
      for c in self.components:
        if not c.updated() and all(i in covered_variables for i in c.inp_vars):
          c.update([covered_variables[i] for i in c.inp_vars])
          covered_variables[c.out_var] = c.updated_out
    self.sf = System_Function(covered_variables['Y'].coeff('X'),
        R_Polynomial([1]) - covered_variables['Y'].coeff('Y'))
  def get_unit_sample_response(self):
    """
    TODO(mikemeko)
    """
    variables = set()
    for c in self.components:
      for v in c.inp_vars:
        variables.add(v)
      variables.add(c.out_var)
    signals = dict(zip(variables, [[] for v in variables]))
    # unit sample signal (approximation)
    signals['X'] = [1] + [0] * 99
    while len(signals['Y']) < len(signals['X']):
      for c in self.components:
        inp = c.inp_vars
        out = c.out_var
        i = len(signals[out])
        if isinstance(c, Gain):
          if len(signals[inp[0]]) > i:
            signals[out].append(c.K * signals[inp[0]][i])
        elif isinstance(c, Delay):
          if i == 0:
            signals[out].append(0)
          elif len(signals[inp[0]]) > i - 1:
            signals[out].append(signals[inp[0]][i - 1])
        elif isinstance(c, Adder):
          if all(len(signals[v]) > i for v in inp):
            signals[out].append(sum(signals[v][i] for v in inp))
    return signals['Y']
  def get_poles(self):
    """
    Returns the poles of this system (may include hidden poles).
    """
    return self.sf.poles()
  def get_zeros(self):
    """
    Returns the zeros of this system (may include hidden zeros).
    """
    return self.sf.zeros()
