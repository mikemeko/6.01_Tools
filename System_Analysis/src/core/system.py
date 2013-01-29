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

class Component:
  """
  Representation for a component in a DT LTI system: gain, delay, or adder.
  """
  def __init__(self, inp_vars, out_var):
    """
    |imp_vars|: a list of the names of the input variables to this component.
    |out_var|: the name of the output variable of this component.
    TODO(mikemeko): update
    """
    self.inp_vars = inp_vars
    self.out_var = out_var
  #@property
  #def sf_update(self, inp_polys):
  #  """
  #  This updates the the |updated_out| attribute. It is called once all the
  #      input variables to this component are described as polynomials only in
  #      terms of X and Y, given in |inp_polys|.
  #  """
  #  raise NotImplementedError('subclasses should implement this')
  #def sf_updated(self):
  #  """
  #  Returns True if the |updated_out| has been updated, False otherwise.
  #  """
  #  return self.updated_out is not None
  @property
  def get_poly(self):
    """
    TODO(mikemeko)
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
    assert isinstance(K, (float, int, long)), 'K must be a number'
    Component.__init__(self, [inp_var], out_var)
    self.inp_var = inp_var
    self.K = K
  #def sf_update(self, inp_polys):
  #  self.updated_out = inp_polys[0].scalar_mult(self.K)
  def get_poly(self):
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
  #def sf_update(self, inp_bound):
  #  self.updated_out = inp_bound[0].shift()
  def get_poly(self):
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
  #def sf_update(self, inp_bound):
  #  self.updated_out = reduce(Polynomial.__add__, inp_bound)
  def get_poly(self):
    data = {}
    for var in self.inp_vars:
      data[var] = R_Ratio(R_Polynomial([1]))
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
    """
    self.components = components
    self.X = X
    self.Y = Y
    self.sf = None
    self._solve_sf()
  def last_component(self):
    """
    Returns the last Component of this system.
    """
    for c in self.components:
      if c.out_var == self.Y:
        return c
  def _solve_for_var(self, var, poly):
    """
    TODO(mikemeko)
    """
    assert isinstance(var, str)
    assert isinstance(poly, Polynomial)
    if var not in poly.variables():
      return poly
    new_data = {}
    denominator = R_Ratio(R_Polynomial([1])) - poly.coeff(var)
    for v in poly.variables():
      if v is not var:
        new_data[v] = poly.coeff(v) / denominator
    return Polynomial(new_data)
  def _solve_sf(self):
    """
    Solves for the system function of this system.
    TODO(mikemeko): this fails for some systems, bug fix in progress!
    """
    variables = {}
    for component in self.components:
      variables[component.out_var] = component.get_poly()
      print component.out_var, '=', variables[component.out_var]
    print
    for component in self.components:
      var = component.out_var
      if var is not self.Y:
        print 'removing', var
        poly = self._solve_for_var(var, variables.pop(var))
        for v in variables:
          variables[v] = variables[v].substitute(var, poly)
        for v in variables:
          print v,'=',variables[v]
        print
    # TODO(mikemeko): assert some stuff here
    self.sf = System_Function(self._solve_for_var(self.Y,
        variables[self.Y]).coeff(self.X))
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
    signals[self.X] = [1] + [0] * (num_samples - 1)
    while len(signals[self.Y]) < num_samples:
      for c in self.components:
        c.response_update(signals)
    return signals[self.Y]
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
  def __str__(self):
    return 'System inp=%s out=%s\nComponents=%s' % (self.X, self.Y,
        str(map(str, self.components)))

if __name__ == '__main__':
  A, B, C, D, E, F = 'A', 'B', 'C', 'D', 'E', 'F'
  sys = System([Adder([X, F], A),
                Gain(A, B, 1),
                Adder([B, D], C),
                Delay(C, E),
                Adder([C, E], Y),
                Gain(E, D, 11),
                Gain(Y, F, -1)])
  print sys.sf
