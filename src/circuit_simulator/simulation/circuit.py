"""
Representation for circuit components and circuits.
Credit to ideas from MIT 6.01 Fall 2012 Software Lab 9.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import OP_AMP_K
from core.math.equation_solver import solve_equations

class One_Port:
  """
  Representation for a circuit component across which a voltage difference
      develops and through which a current flows.
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
        for this one port. An equation should be given in the form of a list of
        terms summing to 0, where a term is a tuple of the form (coeff, var),
        where coeff is a number and var is a variable. Constants can be
        represented by (const, None).
    """
    raise Exception('subclasses should implement this')

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
    # n1 - n2 = ir
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
    This component ensures the constraint |nb1| - |nb2| = |K|(|na1| - |na2|)
    """
    One_Port.__init__(self, nb1, nb2, i)
    self.na1 = na1
    self.na2 = na2
    self.K = K
  def equation(self):
    # nb1 - nb2 = K(na1 - na2)
    return [(1, self.n1), (-1, self.n2), (self.K, self.na2),
        (-self.K, self.na1)]

class Op_Amp:
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
  def parts(self):
    """
    Returns a collection of the one-ports that constitute this op amp.
    """
    return (self.voltage_sensor, self.vcvs)

class Circuit:
  """
  Representation for a circuit.
  """
  def __init__(self, components, gnd):
    """
    |components|: a list of the components (one ports) in this circuit.
    |gnd|: the ground node in this circuit.
    """
    assert all(isinstance(c, One_Port) for c in components), ('all components '
        'must be one ports')
    self.components = components
    self.gnd = gnd
    # self.data contains all values of the currents and voltages in this
    #     circuit, if solved correctly, None otherwise
    self.data = self._solve()
  def _solve(self):
    """
    Solves this circuit and returns a dictionary mapping all the variables (
        i.e. voltages and currents) to their respective values. If circuit
        cannot be solved, returns None.
    """
    # accumulate and solve system of equations
    # component equations
    equations = [component.equation() for component in self.components]
    # one KCL equation per node in the circuit (excluding ground node)
    KCL = {}
    for component in self.components:
      KCL[component.n1] = KCL.get(component.n1, []) + [(1, component.i)]
      KCL[component.n2] = KCL.get(component.n2, []) + [(-1, component.i)]
    equations.extend([KCL[n] for n in KCL if n is not self.gnd])
    # assert that ground voltage is 0
    equations.append([(1, self.gnd)])
    try:
      return solve_equations(equations)
    except:
      return None
