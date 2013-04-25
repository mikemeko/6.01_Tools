"""
Circuit solving.
Credit to ideas from MIT 6.01 Fall 2012 Software Lab 9.
Equation representation: a list of terms summing to 0, where a term is a tuple
    of the form (coeff, var), where coeff is a number and var is a variable.
    Constants can be represented by (const, None).
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import DEBUG
from constants import MOTOR_INIT_ANGLE
from constants import MOTOR_INIT_SPEED
from constants import MOTOR_RESISTANCE
from constants import HEAD_POT_INIT_ALPHA
from constants import HEAD_POT_RESISTANCE
from constants import NUM_SAMPLES
from constants import OP_AMP_K
from constants import T
from core.math.CT_signal import CT_Signal
from core.math.equation_solver import solve_equations
from core.util.util import clip
from core.util.util import is_number
from math import pi
from traceback import format_exc

class Component:
  """
  Abstract representation for circuit components.
  All subclasses should implement equations() and KCL_update(KCL).
  """
  def __init__(self):
    """
    TODO(mikemeko)
    """
    self.current_time = 0
  def step(self, current_solution):
    """
    TODO(mikemeko)
    be sure to remind to call parent step.
    """
    self.current_time += T
  @property
  def equations(self):
    """
    Returns a list of the equations that represent the constraints imposed by
        this Component at the current time.
    All subclasses should implement this method.
    """
    raise NotImplementedError('subclasses should implement this')
  @property
  def KCL_update(self, KCL):
    """
    |KCL| is a dictionary mapping circuit nodes to a list of the currents
        leaving (+) and entering (-) them. This method should update |KCL|
        based on its state at the current time.
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
    Component.__init__(self)
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
  def equations(self):
    return [self.equation()]
  def KCL_update(self, KCL):
    KCL[self.n1] = KCL.get(self.n1, []) + [(1, self.i)]
    KCL[self.n2] = KCL.get(self.n2, []) + [(-1, self.i)]

class Voltage_Source(One_Port):
  """
  Representation for voltage source component.
  """
  def __init__(self, n1, n2, i, v0=None):
    """
    |v0|: the voltage difference (|n1| - |n2|) this voltage source provides.
    """
    One_Port.__init__(self, n1, n2, i)
    self.v0 = v0
  def set_v0(self, v0):
    """
    TODO(mikemeko)
    """
    self.v0 = v0
  def equation(self):
    assert self.v0 is not None, 'v0 has not been set'
    # n1 - n0 = v0
    return [(1, self.n1), (-1, self.n2), (-self.v0, None)]

class Current_Source(One_Port):
  """
  TODO(mikemeko)
  """
  def __init__(self, n1, n2, i, i0=None):
    """
    TODO(mikemeko)
    """
    One_Port.__init__(self, n1, n2, i)
    self.i0 = i0
  def set_i0(self, i0):
    """
    TODO(mikemeko)
    """
    self.i0 = i0
  def equation(self):
    assert self.i0 is not None, 'i0 has not been set'
    # i = i0
    return [(1, self.i), (-self.i0, None)]

class Resistor(One_Port):
  """
  Representation for resistor component.
  """
  def __init__(self, n1, n2, i, r=None):
    """
    |r|: resistance (impedance) of this resistor.
    """
    One_Port.__init__(self, n1, n2, i)
    self.r = r
  def set_r(self, r):
    """
    TODO(mikemeko)
    """
    self.r = r
  def equation(self):
    assert self.r is not None, 'r has not been set'
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
    Component.__init__(self)
    self.voltage_sensor = Voltage_Sensor(na1, na2, ia)
    self.vcvs = VCVS(na1, na2, nb1, nb2, ib, K)
    self.na1 = na1
    self.na2 = na2
    self.nb1 = nb1
    self.nb2 = nb2
  def equations(self):
    return [self.voltage_sensor.equation(), self.vcvs.equation()]
  def KCL_update(self, KCL):
    self.voltage_sensor.KCL_update(KCL)
    self.vcvs.KCL_update(KCL)

class Pot(Component):
  """
  Representation for pot component.
  """
  def __init__(self, n_top, n_middle, n_bottom, i_top_middle, i_middle_bottom,
      r, alpha):
    """
    |n_top|: top terminal node.
    |n_middle|: middle terminal node.
    |n_bottom|: bottom terminal node.
    |i_top_middle|: current from |n_top| to |n_middle|.
    |i_middle_bottom|: current from |n_middle| to |n_bottom|.
    |r|: total resistance.
    TODO(mikemeko): assert not null?
    """
    assert is_number(alpha), 'alpha must be a number'
    Component.__init__(self)
    self.n_top = n_top
    self.n_middle = n_middle
    self.n_bottom = n_bottom
    self.r = r
    self.alpha = clip(alpha, 0, 1)
    self._resistor_1 = Resistor(n_top, n_middle, i_top_middle,
        (1 - self.alpha) * r)
    self._resistor_2 = Resistor(n_middle, n_bottom, i_middle_bottom,
        self.alpha * r)
  def set_alpha(self, alpha):
    """
    TODO(mikemeko)
    """
    self.alpha = clip(alpha, 0, 1)
  def step(self, current_solution):
    self._resistor_1.set_r((1 - self.alpha) * self.r)
    self._resistor_2.set_r(self.alpha * self.r)
    Component.step(self, current_solution)
  def equations(self):
    return [self._resistor_1.equation(), self._resistor_2.equation()]
  def KCL_update(self, KCL):
    self._resistor_1.KCL_update(KCL)
    self._resistor_2.KCL_update(KCL)

class Signalled_Pot(Pot):
  """
  TODO(mikemeko)
  """
  def __init__(self, n_top, n_middle, n_bottom, i_top_middle, i_middle_bottom,
      r, signal):
    """
    TODO(mikemeko)
    |signal|: CT_Signal dictating the value of alpha (how much the shaft is
        turned) for this pot.
    """
    assert isinstance(signal, CT_Signal), 'signal must be a CT_Signal'
    Pot.__init__(self, n_top, n_middle, n_bottom, i_top_middle,
        i_middle_bottom, r, signal(0))
    self.signal = signal
    self.alpha_samples = [self.alpha]
  def step(self, current_solution):
    self.set_alpha(self.signal(self.current_time))
    self.alpha_samples.append(self.alpha)
    Pot.step(self, current_solution)

class Motor_Connector(One_Port):
  """
  TODO(mikemeko)
  """
  def __init__(self, n1, n2, i):
    """
    TODO(mikemekko)
    """
    One_Port.__init__(self, n1, n2, i)
    self._resistor = Resistor(n1, n2, i, MOTOR_RESISTANCE)
    self.angle_samples = [MOTOR_INIT_ANGLE]
    self.speed_samples = [MOTOR_INIT_SPEED]
  def step(self, current_solution):
    # TODO(mikemeko): calibration
    assert self.n1 in current_solution, '%s not in current solution' % self.n1
    assert self.n2 in current_solution, '%s not in current solution' % self.n2
    # TODO(mikemeko): order of updates
    self.angle_samples.append(self.angle_samples[-1] + T *
        self.speed_samples[-1])
    self.speed_samples.append(current_solution[self.n1] -
        current_solution[self.n2])
    One_Port.step(self, current_solution)
  def equations(self):
    return self._resistor.equations()
  def KCL_update(self, KCL):
    self._resistor.KCL_update(KCL)

class Robot_Connector(Component):
  """
  Representation for a robot connector.
  """
  def equations(self):
    return []
  def KCL_update(self, KCL):
    pass

class Head_Connector(Component):
  """
  Representation for a head connector.
  """
  def __init__(self, n_pot_top, n_pot_middle, n_pot_bottom, i_pot_top_middle,
      i_pot_middle_bottom, n_photo_left, n_photo_common, n_photo_right,
      i_photo_left_common, i_photo_common_right, n_motor_plus, n_motor_minus,
      i_motor, lamp_angle_signal, lamp_distance_signal):
    """
    TODO(mikemeko)
    """
    assert isinstance(lamp_angle_signal, CT_Signal), ('lamp_angle_signal must '
        'be a CT_Signal')
    assert isinstance(lamp_distance_signal, CT_Signal), ('lamp_distance_signal'
        ' must be a CT_Signal')
    Component.__init__(self)
    # neck pot
    self.pot_present = all([n_pot_top, n_pot_middle, n_pot_bottom,
        i_pot_top_middle, i_pot_middle_bottom])
    if self.pot_present:
      self.pot = Pot(n_pot_top, n_pot_middle, n_pot_bottom, i_pot_top_middle,
          i_pot_middle_bottom, HEAD_POT_RESISTANCE, HEAD_POT_INIT_ALPHA)
    # photodetectors
    # TODO(mikemeko): order of node names
    init_lamp_angle = lamp_angle_signal(0)
    init_lamp_distance = lamp_distance_signal(0)
    self.photo_left_present = all([n_photo_left, n_photo_common,
        i_photo_left_common])
    if self.photo_left_present:
      self.photo_left = Current_Source(n_photo_left, n_photo_common,
          i_photo_left_common, self._photodetector_constant(init_lamp_angle,
          init_lamp_distance, 'left'))
    self.photo_right_present = all([n_photo_right, n_photo_common,
        i_photo_common_right])
    if self.photo_right_present:
      self.photo_right = Current_Source(n_photo_right, n_photo_common,
          i_photo_common_right, self._photodetector_constant(init_lamp_angle,
          init_lamp_distance, 'right'))
    # motor
    self.motor_present = all([n_motor_plus, n_motor_minus, i_motor])
    # TODO(mikemeko): check this
    if self.pot_present:
      assert self.motor_present
    if self.motor_present:
      self.motor = Motor_Connector(n_motor_plus, n_motor_minus, i_motor)
    # lamp signals
    self.lamp_angle_signal = lamp_angle_signal
    self.lamp_distance_signal = lamp_distance_signal
    # all pin nodes in order
    self.pin_nodes = [n_pot_top, n_pot_middle, n_pot_bottom, n_photo_left,
        n_photo_common, n_photo_right, n_motor_plus, n_motor_minus]
  def _photodetector_constant(self, lamp_angle, lamp_distance, side):
    """
    TODO(mikemeko)
    update correctly
    """
    assert side in ('left', 'right'), 'side muste be either "left" or "right"'
    return 1. / lamp_distance
  def step(self, current_solution):
    # TODO(mikemeko): order
    if self.pot_present:
      current_motor_angle = self.motor.angle_samples[-1]
      # TODO(mikemeko): does this make sense?
      self.pot.set_alpha((current_motor_angle / (2 * pi) + 0.5) % 1)
      self.pot.step(current_solution)
    current_lamp_angle = self.lamp_angle_signal(self.current_time)
    current_lamp_distance = self.lamp_distance_signal(self.current_time)
    if self.photo_left_present:
      # TODO(mikemeko): better model
      self.photo_left.set_i0(self._photodetector_constant(current_lamp_angle,
          current_lamp_distance, 'left'))
      self.photo_left.step(current_solution)
    if self.photo_right_present:
      # TODO(mikemeko): better model
      self.photo_right.set_i0(self._photodetector_constant(current_lamp_angle,
          current_lamp_distance, 'right'))
      self.photo_right.step(current_solution)
    if self.motor_present:
      self.motor.step(current_solution)
    Component.step(self, current_solution)
  def _present_components(self):
    components = []
    if self.pot_present:
      components.append(self.pot)
    if self.photo_left_present:
      components.append(self.photo_left)
    if self.photo_right_present:
      components.append(self.photo_right)
    if self.motor_present:
      components.append(self.motor)
    return components
  def equations(self):
    return reduce(list.__add__, (component.equations() for component in
        self._present_components()), [])
  def KCL_update(self, KCL):
    for component in self._present_components():
      component.KCL_update(KCL)

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
      equations = reduce(list.__add__, (component.equations() for component in
          self.components), [])
      # one KCL equation per node in the circuit (excluding ground node)
      KCL = {}
      for component in self.components:
        component.KCL_update(KCL)
      equations.extend([KCL[node] for node in KCL if node is not self.gnd])
      # assert that ground voltage is 0
      equations.append([(1, self.gnd)])
      # solve system of equations
      data[n * T] = solve_equations(equations)
      # step components TODO(mikemeko)
      for component in self.components:
        component.step(data[n * T])
    return data
