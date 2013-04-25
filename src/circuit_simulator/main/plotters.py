"""
TODO(mikemeko)
cleanup
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.simulation.circuit import Head_Connector
from circuit_simulator.simulation.circuit import Motor_Connector
from circuit_simulator.simulation.circuit import Signalled_Pot
from circuit_simulator.simulation.constants import NUM_SAMPLES
from circuit_simulator.simulation.constants import T
from constants import T_SAMPLES
from pylab import figure
from pylab import stem
from pylab import xlabel
from pylab import ylabel

class Plotter:
  """
  Abstract data structure that supports a |plot| method that, given a Board and
      the data for a particular circuit, plots something meaningful about the
      circuit, or displays the errors on the Board, if any.
  """
  def plot(self, board, data):
    """
    |board|: the Board containing the circuit. This can be used to display any
        messages.
    |data|: the data corresponding to the solved circuit.
    All subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')

class Head_Plotter(Plotter):
  """
  TODO(mikemeko)
  """
  def __init__(self, head_connector):
    """
    TODO(mikemeko)
    """
    assert isinstance(head_connector, Head_Connector), ('head_connector must '
        'be a Head_Connector')
    self._head_connector = head_connector
  def plot(self, board, data):
    # motor
    if self._head_connector.motor_present:
      figure()
      xlabel('t')
      ylabel('Motor angle')
      stem(T_SAMPLES, self._head_connector.motor.angle_samples[:-1])
      figure()
      xlabel('t')
      ylabel('Motor velocity')
      stem(T_SAMPLES, self._head_connector.motor.speed_samples[:-1])
    # lamp distance signal
    figure()
    xlabel('t')
    ylabel('Lamp distance')
    stem(T_SAMPLES, self._head_connector.lamp_distance_signal.samples(0, T,
        NUM_SAMPLES))
    # lamp angle signal
    figure()
    xlabel('t')
    ylabel('Lamp angle')
    stem(T_SAMPLES, self._head_connector.lamp_angle_signal.samples(0, T,
        NUM_SAMPLES))

class Motor_Plotter(Plotter):
  """
  Plotter that shows motor angle and velocity vs. time.
  """
  def __init__(self, motor_connector):
    """
    TODO(mikemeko)
    """
    assert isinstance(motor_connector, Motor_Connector), ('motor_connector '
        'must be a Motor_Connector')
    self._motor_connector = motor_connector
  def plot(self, board, data):
    # plot time versus motor angle
    figure()
    xlabel('t')
    ylabel('Motor angle')
    stem(T_SAMPLES, self._motor_connector.angle_samples[:-1])
    # plot time versus motor velocity
    figure()
    xlabel('t')
    ylabel('Motor velocity')
    stem(T_SAMPLES, self._motor_connector.speed_samples[:-1])

class Signalled_Pot_Plotter(Plotter):
  """
  TODO(mikemeko)
  """
  def __init__(self, pot):
    """
    TODO(mikemeko)
    """
    assert isinstance(pot, Signalled_Pot), ('pot must be a Signalled_Pot')
    self._pot = pot
  def plot(self, board, data):
    figure()
    xlabel('t')
    ylabel('Pot alpha')
    stem(T_SAMPLES, self._pot.signal.samples(0, T, NUM_SAMPLES))

class Probe_Plotter(Plotter):
  """
  Plotter that shows the voltage difference accross probes vs. time.
  """
  def __init__(self, probe_plus, probe_minus):
    """
    |probe_plus|, |probe_minus|: probed nodes.
    """
    self._probe_plus = probe_plus
    self._probe_minus = probe_minus
  def plot(self, board, data):
    t_samples, probe_samples = [], []
    for t, solution in data.items():
      # ensure that the probes are in the solved circuits
      assert self._probe_plus in solution, ('+probe is disconnected from '
          'circuit')
      assert self._probe_minus in solution, ('-probe is disconnected from '
          'circuit')
      t_samples.append(t)
      probe_samples.append(
          solution[self._probe_plus] - solution[self._probe_minus])
    figure()
    xlabel('t')
    ylabel('Probe Voltage Difference')
    stem(t_samples, probe_samples)