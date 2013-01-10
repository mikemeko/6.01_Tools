"""
Representation for DT LTI systems.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import DEFAULT_NUM_SAMPLES
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
  def sf_update(self, inp_polys):
    """
    This updates the the |updated_out| attribute. It is called once all the
        input variables to this component are described as polynomials only in
        terms of X and Y, given in |inp_polys|.
    """
    raise NotImplementedError('subclasses should implement this')
  def sf_updated(self):
    """
    Returns True if the |updated_out| has been updated, False otherwise.
    """
    return self.updated_out is not None
  @property
  def response_update(self, signals):
    """
    |signals| is a dictionary mapping variables to lists. This appends, if
        possible, the next sample of the output signal of this component.
    """
    raise NotImplementedError('subclasses should implement this')
  def is_last_component(self):
    """
    Returns True if this is the last Component of a system (i.e. outputs "Y").
    """
    return self.out_var is 'Y'

class Gain(Component):
  """
  Representation for a gain.
  """
  def __init__(self, inp_var, out_var, K):
    assert isinstance(K, (float, int, long)), 'K must be a number'
    Component.__init__(self, [inp_var], out_var)
    self.K = K
  def sf_update(self, inp_polys):
    self.updated_out = inp_polys[0].scalar_mult(self.K)
  def response_update(self, signals):
    i = len(signals[self.out_var])
    if len(signals[self.inp_vars[0]]) > i:
      signals[self.out_var].append(self.K * signals[self.inp_vars[0]][i])

class Delay(Component):
  """
  Representation for a delay.
  """
  def __init__(self, inp_var, out_var):
    Component.__init__(self, [inp_var], out_var)
  def sf_update(self, inp_bound):
    self.updated_out = inp_bound[0].shift()
  def response_update(self, signals):
    i = len(signals[self.out_var])
    if i == 0:
      signals[self.out_var].append(0)
    elif len(signals[self.inp_vars[0]]) > i - 1:
      signals[self.out_var].append(signals[self.inp_vars[0]][i - 1])

class Adder(Component):
  """
  Representation for an adder.
  """
  def sf_update(self, inp_bound):
    self.updated_out = reduce(Polynomial.__add__, inp_bound)
  def response_update(self, signals):
    i = len(signals[self.out_var])
    if all(len(signals[v]) > i for v in self.inp_vars):
      signals[self.out_var].append(sum(signals[v][i] for v in self.inp_vars))

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
  def last_component(self):
    """
    Returns the last Component of this system.
    """
    for c in self.components:
      if c.is_last_component():
        return c
  def _solve_sf(self):
    """
    Solves for the system function of this system.
    """
    last_comp = self.last_component()
    var_reps = {'X':Polynomial({'X':R_Polynomial([1])}),
        'Y':Polynomial({'Y':R_Polynomial([1])})}
    while not last_comp.sf_updated():
      for c in self.components:
        if not c.sf_updated() and all(i in var_reps for i in c.inp_vars):
          c.sf_update([var_reps[i] for i in c.inp_vars])
          var_reps[c.out_var] = c.updated_out
    self.sf = System_Function(var_reps['Y'].coeff('X'),
        R_Polynomial([1]) - var_reps['Y'].coeff('Y'))
  def variables(self):
    """
    Returns a set of the variables in this System.
    """
    variables = set()
    for c in self.components:
      for v in c.inp_vars:
        variables.add(v)
      variables.add(c.out_var)
    return variables
  def unit_sample_response(self, num_samples=DEFAULT_NUM_SAMPLES):
    """
    Returns the first |N| samples of the unit sample response of this System,
        starting at n=0.
    """
    signals = {}
    for v in self.variables():
      signals[v] = []
    # input is unit sample signal
    signals['X'] = [1] + [0] * (num_samples - 1)
    while len(signals['Y']) < num_samples:
      for c in self.components:
        c.response_update(signals)
    return signals['Y']
  def poles(self):
    """
    Returns the poles of this system (may include hidden poles).
    """
    return self.sf.poles()
  def zeros(self):
    """
    Returns the zeros of this system (may include hidden zeros).
    """
    return self.sf.zeros()
