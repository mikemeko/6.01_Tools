"""
Representation for DT LTI systems.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import X
from constants import Y
from constants import DEFAULT_NUM_SAMPLES
from poly import Polynomial
from poly import R_Polynomial
from poly import R_Ratio
from system_function import System_Function
from util import is_number

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
  @property
  def get_poly(self):
    """
    Returns a Polynomial in the variables in self.inp_vars that describes
        self.out_var.
    """
    raise NotImplementedError('subclasses should implement this')
  @property
  def response_update(self, signals):
    """
    |signals| is a dictionary mapping variables to lists. This appends, if
        possible, the next sample of the output signal of this component.
    """
    raise NotImplementedError('subclasses should implement this')

class Gain(Component):
  """
  Representation for a gain.
  """
  def __init__(self, inp_var, out_var, K):
    assert is_number(K), 'K must be a number'
    Component.__init__(self, [inp_var], out_var)
    self.inp_var = inp_var
    self.K = K
  def get_poly(self):
    # out = K * inp
    return Polynomial({self.inp_var: R_Ratio(R_Polynomial([self.K]))})
  def response_update(self, signals):
    i = len(signals[self.out_var])
    if len(signals[self.inp_var]) > i:
      signals[self.out_var].append(self.K * signals[self.inp_var][i])
  def __str__(self):
    return 'Gain inp=%s out=%s K=%f' % (self.inp_var, self.out_var, self.K)

class Delay(Component):
  """
  Representation for a delay.
  """
  def __init__(self, inp_var, out_var):
    Component.__init__(self, [inp_var], out_var)
    self.inp_var = inp_var
  def get_poly(self):
    # out = R * inp
    return Polynomial({self.inp_var: R_Ratio(R_Polynomial([0, 1]))})
  def response_update(self, signals):
    i = len(signals[self.out_var])
    if i == 0:
      signals[self.out_var].append(0)
    elif len(signals[self.inp_var]) > i - 1:
      signals[self.out_var].append(signals[self.inp_var][i - 1])
  def __str__(self):
    return 'Delay inp=%s out=%s' % (self.inp_var, self.out_var)

class Adder(Component):
  """
  Representation for an adder.
  """
  def get_poly(self):
    # out = sum(inp)
    data = {}
    for var in self.inp_vars:
      data[var] = R_Ratio(R_Polynomial.one())
    return Polynomial(data)
  def response_update(self, signals):
    i = len(signals[self.out_var])
    if all(len(signals[v]) > i for v in self.inp_vars):
      signals[self.out_var].append(sum(signals[v][i] for v in self.inp_vars))
  def __str__(self):
    return 'Adder inp=%s out=%s' % (str(self.inp_vars), self.out_var)

class System:
  """
  Representation for a DT LTI system.
  """
  def __init__(self, components, X=X, Y=Y):
    """
    |components|: a list of the instances of Component in this System.
    |X|: the input signal of this system.
    |Y|: the output signal of this system.
    """
    self.components = components
    self.X = X
    self.Y = Y
    self.sf = None
    self._solve_sf()
  def _solve_for_var(self, var, poly):
    """
    Returns a Polynomial for |var| after solving the equation |var| = |poly|.
    """
    assert isinstance(var, str), 'variable name must be a string'
    assert isinstance(poly, Polynomial), 'poly must be a Polynomial'
    if var not in poly.variables():
      return poly.copy()
    # var = k1 * var + k2 * other => var = k2 / (1 - k1) * other
    new_data = {}
    denominator = R_Ratio(R_Polynomial.one()) - poly.coeff(var)
    for v in poly.variables():
      if v is not var:
        new_data[v] = poly.coeff(v) / denominator
    return Polynomial(new_data)
  def _solve_sf(self):
    """
    Solves for the system function of this system.
    """
    # create initial mapping of output variables to their respective
    # representations in terms of input variables
    out_var_reps = {}
    for component in self.components:
      out_var_reps[component.out_var] = component.get_poly()
    # eliminate one output variable at a time until all but self.Y are gone
    for component in self.components:
      out_var_to_eliminate = component.out_var
      if out_var_to_eliminate is not self.Y:
        new_rep = self._solve_for_var(out_var_to_eliminate,
            out_var_reps.pop(out_var_to_eliminate))
        for out_var in out_var_reps:
          out_var_reps[out_var] = out_var_reps[out_var].substitute(
              out_var_to_eliminate, new_rep)
    # TODO(mikemeko): better error messages here
    assert len(out_var_reps) == 1, 'unable to solve for system function'
    assert self.Y in out_var_reps, 'unable to solve for system function'
    assert set(out_var_reps[self.Y].variables()).issubset(
        set([self.X, self.Y])), 'unable to solve for system function'
    # solve for self.Y in terms of only self.X and obtain system function
    self.sf = System_Function(self._solve_for_var(self.Y,
        out_var_reps[self.Y]).coeff(self.X))
  def variables(self):
    """
    Returns a set of the variables in this System.
    """
    for c in self.components:
      for v in c.inp_vars:
        yield v
      yield c.out_var
  def unit_sample_response(self, num_samples=DEFAULT_NUM_SAMPLES):
    """
    Returns the first |num_samples| samples of the unit sample response of this
        System, starting at n=0.
    """
    signals = {}
    for v in self.variables():
      signals[v] = []
    # input is unit sample signal
    signals[self.X] = [1] + [0] * (num_samples - 1)
    while len(signals[self.Y]) < num_samples:
      for c in self.components:
        c.response_update(signals)
    return signals[self.Y]
  def poles(self):
    """
    Returns the poles of this system (may include hidden poles).
    """
    assert self.sf is not None, 'no system function'
    return self.sf.poles()
  def zeros(self):
    """
    Returns the zeros of this system (may include hidden zeros).
    """
    assert self.sf is not None, 'no system function'
    return self.sf.zeros()
  def __str__(self):
    return 'System inp=%s out=%s\nComponents=%s' % (self.X, self.Y,
        str(map(str, self.components)))
