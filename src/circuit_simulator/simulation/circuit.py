"""
Circuit solving.
Credit to ideas from MIT 6.01 Fall 2012 Software Lab 9.
Equation representation: a list of terms summing to 0, where a term is a tuple
    of the form (coeff, var), where coeff is a number and var is a variable.
    Constants can be represented by (const, None).
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import DEBUG
from constants import NUM_SAMPLES
from constants import OP_AMP_K
from constants import T
from core.math.CT_signal import CT_Signal
from core.math.equation_solver import solve_equations
from core.util.util import clip
from traceback import format_exc

class Component:
  """
  Abstract representation for circuit components.
  All subclasses should implement equations(t) and KCL_update(t, KCL).
  """
  @property
  def equations(self, t):
    """
    Returns a list of the equations that represent the constraints imposed by
        this Component at the given time |t|.
    All subclasses should implement this method.
    """
    raise NotImplementedError('subclasses should implement this')
  @property
  def KCL_update(self, t, KCL):
    """
    |KCL| is a dictionary mapping circuit nodes to a list of the currents
        leaving (+) and entering (-) them. This method should update |KCL|
        based on its state at the given time |t|.
    All subclasses should implement this method.
    """
    raise NotImplementedError('subclasses should implement this')

class One_Port(Component):
  """
  Abstract representation for a circuit component across which a voltage
      difference develops and through which a current flows.
  """
  def __init__(self, n1, n2, i):
    """
    |n1|: first (+) node this one port is connected to.
    |n2|: second (-) node this one port is connected to.
    |i|: the current through this one port, flowing from |n1| to |n2|.
    """
    self.n1 = n1
    self.n2 = n2
    self.i = i
  @property
  def equation(self):
    """
    Returns an equation representing the constraint that needs to be satisfied
        for this one port.
    All subclasses should implement this method.
    """
    raise NotImplementedError('subclasses should implement this')
  def equations(self, t):
    return [self.equation()]
  def KCL_update(self, t, KCL):
    KCL[self.n1] = KCL.get(self.n1, []) + [(1, self.i)]
    KCL[self.n2] = KCL.get(self.n2, []) + [(-1, self.i)]

class Voltage_Source(One_Port):
  """
  Representation for voltage source component.
  """
  def __init__(self, n1, n2, i, v0):
    """
    |v0|: the voltage difference (|n1| - |n2|) this voltage source provides.
    """
    One_Port.__init__(self, n1, n2, i)
    self.v0 = v0
  def equation(self):
    # n1 - n0 = v0
    return [(1, self.n1), (-1, self.n2), (-self.v0, None)]

class Resistor(One_Port):
  """
  Representation for resistor component.
  """
  def __init__(self, n1, n2, i, r):
    """
    |r|: resistance (impedance) of this resistor.
    """
    One_Port.__init__(self, n1, n2, i)
    self.r = r
  def equation(self):
    # n1 - n2 = i * r
    return [(1, self.n1), (-1, self.n2), (-self.r, self.i)]

class Voltage_Sensor(One_Port):
  """
  Representation for a voltage sensor, to be used as a part of op amps.
  """
  def equation(self):
    # i = 0
    return [(1, self.i)]

class VCVS(One_Port):
  """
  Representation for a voltage-controlled voltage source, to be used as a part
      of op amps.
  """
  def __init__(self, na1, na2, nb1, nb2, i, K):
    """
    |na1|, |na2|: input nodes.
    |nb1|, |nb2|: output nodes.
    |i|: current into node |nb1|.
    |K|: VCVS constant of proportionality.
    """
    One_Port.__init__(self, nb1, nb2, i)
    self.na1 = na1
    self.na2 = na2
    self.nb1 = nb1
    self.nb2 = nb2
    self.K = K
  def equation(self):
    # nb1 - nb2 = K * (na1 - na2)
    return [(1, self.nb1), (-1, self.nb2), (self.K, self.na2),
        (-self.K, self.na1)]

class Op_Amp(Component):
  """
  Representation for an op amp as a two port: composed of a voltage sensor and
      a voltage-controlled voltage source.
  TODO(mikemeko): detect positive feedback
  """
  def __init__(self, na1, na2, ia, nb1, nb2, ib, K=OP_AMP_K):
    """
    |na1|, |na2|: input nodes to the two port.
    |ia1|: current into node |na1|.
    |nb1|, |nb2|: output nodes of the two port.
    |ib1|: current into node |nb1|.
    |K|: VCVS constant of proportionality.
    """
    self.voltage_sensor = Voltage_Sensor(na1, na2, ia)
    self.vcvs = VCVS(na1, na2, nb1, nb2, ib, K)
    self.na1 = na1
    self.na2 = na2
    self.nb1 = nb1
    self.nb2 = nb2
  def equations(self, t):
    return [self.voltage_sensor.equation(), self.vcvs.equation()]
  def KCL_update(self, t, KCL):
    self.voltage_sensor.KCL_update(t, KCL)
    self.vcvs.KCL_update(t, KCL)

class Pot(Component):
  """
  Representation for pot component.
  """
  def __init__(self, n_top, n_middle, n_bottom, i_top_middle, i_middle_bottom,
      r, signal):
    """
    |n_top|: top terminal node.
    |n_middle|: middle terminal node.
    |n_bottom|: bottom terminal node.
    |i_top_middle|: current from |n_top| to |n_middle|.
    |i_middle_bottom|: current from |n_middle| to |n_bottom|.
    |r|: total resistance.
    |signal|: CT_Signal dictating the value of alpha (how much the shaft is
        turned) for this pot.
    """
    assert isinstance(signal, CT_Signal), 'signal must be a CT_Signal'
    self.n_top = n_top
    self.n_middle = n_middle
    self.n_bottom = n_bottom
    self.i_top_middle = i_top_middle
    self.i_middle_bottom = i_middle_bottom
    self.r = r
    self.signal = signal
  def _resistors_at(self, t):
    """
    Returns the top and bottom Resistors at the given time |t|.
    """
    # ensure that alpha is between 0 and 1
    alpha = clip(self.signal(t), 0, 1)
    return Resistor(self.n_top, self.n_middle, self.i_top_middle,
        (1 - alpha) * self.r), Resistor(self.n_middle, self.n_bottom,
        self.i_middle_bottom, alpha * self.r)
  def equations(self, t):
    return [resistor.equation() for resistor in self._resistors_at(t)]
  def KCL_update(self, t, KCL):
    for resistor in self._resistors_at(t):
      resistor.KCL_update(t, KCL)

class Circuit:
  """
  Representation for a circuit.
  """
  def __init__(self, components, gnd):
    """
    |components|: a list of the Components in this circuit.
    |gnd|: the ground node in this circuit.
    """
    self.components = components
    self.gnd = gnd
    # try to solve the circuit
    try:
      self.data = self._solve()
    except:
      self.data = None
      if DEBUG:
        print format_exc()
  def _solve(self):
    """
    Solves this circuit and returns a dictionary mapping all the sampled times
        to dictionaries mapping all the variables (i.e. voltages and currents)
        to their values.
    """
    data = {}
    for n in xrange(NUM_SAMPLES):
      # accumulate and solve system of equations
      # component equations
      equations = reduce(list.__add__, (component.equations(n * T) for
          component in self.components), [])
      # one KCL equation per node in the circuit (excluding ground node)
      KCL = {}
      for component in self.components:
        component.KCL_update(n * T, KCL)
      equations.extend([KCL[node] for node in KCL if node is not self.gnd])
      # assert that ground voltage is 0
      equations.append([(1, self.gnd)])
      # solve system of equations
      data[n * T] = solve_equations(equations)
    return data
