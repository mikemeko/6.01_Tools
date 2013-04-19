"""
Contains the method to analyze the circuit drawn on a board.
TODO(mikemeko): motor connectors (and possibly robot and head connectors) need
  to be labeled in case there are multiple.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_drawables import Ground_Drawable
from circuit_drawables import Motor_Connector_Drawable
from circuit_drawables import Op_Amp_Drawable
from circuit_drawables import Pot_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_drawables import Robot_Connector_Drawable
from circuit_simulator.simulation.circuit import Circuit
from circuit_simulator.simulation.circuit import Motor
from circuit_simulator.simulation.circuit import Op_Amp
from circuit_simulator.simulation.circuit import Pot
from circuit_simulator.simulation.circuit import Resistor
from circuit_simulator.simulation.circuit import Robot_Connector
from circuit_simulator.simulation.circuit import Voltage_Source
from circuit_simulator.simulation.constants import T
from constants import GROUND
from constants import POWER
from constants import POWER_VOLTS
from core.gui.board import Board
from core.gui.constants import ERROR
from core.gui.constants import WARNING
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

class Probe_Plotter:
  """
  Plotter that shows the voltage difference accross probes with respect to
      time.
  """
  def __init__(self, probe_plus, probe_minus):
    """
    |probe_plus|, |probe_minus|: probed nodes.
    """
    self.probe_plus = probe_plus
    self.probe_minus = probe_minus
  def plot(self, board, data):
    t_samples, probe_samples = [], []
    for t, solution in data.items():
      # ensure that the probes are in the solved circuits
      if self.probe_plus not in solution:
        board.display_message('+probe is disconnected from circuit', WARNING)
        return
      elif self.probe_minus not in solution:
        board.display_message('-probe is disconnected from circuit', WARNING)
        return
      t_samples.append(t)
      probe_samples.append(
          solution[self.probe_plus] - solution[self.probe_minus])
    xlabel('t')
    ylabel('Probe Voltage Difference')
    stem(t_samples, probe_samples)

class Motor_Plotter:
  """
  Plotter that shows motor angle and velocity with respect to time.
  TODO(mikemeko): calibrate correctly with measurements. Don't forget to cap
      minimum and maximum possible motor angle.
  """
  def __init__(self, n1, n2):
    """
    |n1|: Motor + termina.
    |n2|: Motor - terminal.
    """
    self.n1 = n1
    self.n2 = n2
  def plot(self, board, data):
    t_samples, angle_samples, velocity_samples = [], [0], []
    for t, solution in sorted(data.items(), key=lambda (t, sol): t):
      # ensure that motor terminals are in the solved circuits
      if self.n1 not in solution or self.n2 not in solution:
        board.display_message('Motor resistor disconnected from circuit',
            ERROR)
        return
      t_samples.append(t)
      velocity_samples.append(solution[self.n1] - solution[self.n2])
      angle_samples.append(angle_samples[-1] + T * velocity_samples[-1])
    # plot time versus motor angle
    xlabel('t')
    ylabel('Motor angle')
    stem(t_samples, angle_samples[:-1])
    # plot time versus motor velocity
    figure()
    xlabel('t')
    ylabel('Motor velocity')
    stem(t_samples, velocity_samples)

def current_name(drawable, n1, n2):
  """
  Returns a unique name for the current through the given |drawable| going from
      node |n1| to node |n2|.
  """
  return '%d %s->%s' % (id(drawable), n1, n2)

def run_analysis(board, analyze):
  """
  Extracts a Circuit object from what is drawn on the given |board| and calls
      the given function |analyze| on it. The funtion |analyze| should take as
      arguments the circuit, as well as the plotters that are collected.
  TODO(mikemeko): run_analysis gets the job done, but work on a cleaner
      implementation.
  """
  assert isinstance(board, Board), 'board must be a Board'
  # remove current message on board, if any
  board.remove_message()
  # components in the circuit
  circuit_components = []
  # analysis plotters
  plotters = []
  # first identify all power and ground nodes and use the same name for all
  #     power nodes, as well as the same name for all ground nodes
  power_nodes, ground_nodes = set(), set()
  # flag to ensure that there is at most one robot connector
  robot_connector_found = False
  for drawable in board.get_drawables():
    # wires attached to this component
    nodes = [wire.label for wire in drawable.wires()]
    # power component
    if isinstance(drawable, Power_Drawable):
      if len(nodes) != 1:
        board.display_message('Power component must be connected to 1 wire',
            ERROR)
        return
      power_nodes.add(nodes[0])
    # ground component
    if isinstance(drawable, Ground_Drawable):
      if len(nodes) != 1:
        board.display_message('Ground component must be connected to 1 wire',
            ERROR)
        return
      ground_nodes.add(nodes[0])
    # robot connector component
    if isinstance(drawable, Robot_Connector_Drawable):
      if robot_connector_found:
        board.display_message('At most 1 Robot Connector allowed', ERROR)
        return
      robot_connector_found = True
      pin_2_nodes = [wire.label for wire in drawable.pin_connector(2).wires()]
      if len(pin_2_nodes) != 1:
        board.display_message('Robot connector pin 2 must be connected to 1 '
            'wire', ERROR)
        return
      pin_4_nodes = [wire.label for wire in drawable.pin_connector(4).wires()]
      if len(pin_4_nodes) != 1:
        board.display_message('Robot connector pin 4 must be connected to 1 '
            'wire', ERROR)
        return
      power_nodes.add(pin_2_nodes[0])
      ground_nodes.add(pin_4_nodes[0])
      circuit_components.append(Robot_Connector())
  # ensure that there is at least one power component
  if not power_nodes:
    board.display_message('No power components', ERROR)
    return
  # ensure that there is at least one ground component
  if not ground_nodes:
    board.display_message('No ground components', ERROR)
    return
  # ensure that power nodes and ground nodes are disjoint (no short circuit)
  if power_nodes.intersection(ground_nodes):
    board.display_message('Short circuit', ERROR)
    return
  # add voltage source to circuit
  circuit_components.append(Voltage_Source(POWER, GROUND,
      current_name(drawable, POWER, GROUND), POWER_VOLTS))
  def maybe_rename_node(node):
    """
    If this node is a power node or a ground node, this method returns the
        appropriate name, otherwise the original name is returned.
    """
    if node in power_nodes:
      return POWER
    elif node in ground_nodes:
      return GROUND
    return node
  # probe labels
  probe_plus, probe_minus = None, None
  for drawable in board.get_drawables():
    # wires attached to this component
    nodes = [wire.label for wire in drawable.wires()]
    # probe plus component
    if isinstance(drawable, Probe_Plus_Drawable):
      if len(nodes) != 1:
        board.display_message('+probe must be connected to 1 wire', WARNING)
        return
      probe_plus = maybe_rename_node(nodes[0])
    # probe minus component
    elif isinstance(drawable, Probe_Minus_Drawable):
      if len(nodes) != 1:
        board.display_message('-probe must be connected to 1 wire', WARNING)
        return
      probe_minus = maybe_rename_node(nodes[0])
    # resistor component
    # TODO(mikemeko): better check for resistor connections (exactly one node
    #     on each end of the resistor)
    elif isinstance(drawable, Resistor_Drawable):
      if len(nodes) != 2:
        board.display_message('Resistor must be connected to 2 wires', ERROR)
        return
      # get its resistance
      try:
        r = float(drawable.get_resistance())
      except:
        board.display_message('Could not obtain resistance constant', ERROR)
        return
      n1, n2 = map(maybe_rename_node, nodes)
      circuit_components.append(Resistor(n1, n2, current_name(drawable, n1,
          n2), r))
    # op amp component
    elif isinstance(drawable, Op_Amp_Drawable):
      plus_nodes = [wire.label for wire in drawable.plus_port.wires()]
      if len(plus_nodes) != 1:
        board.display_message('Op amp + port must be connected to 1 wire',
            ERROR)
        return
      minus_nodes = [wire.label for wire in drawable.minus_port.wires()]
      if len(minus_nodes) != 1:
        board.display_message('Op amp - port must be connected to 1 wire',
            ERROR)
        return
      out_nodes = [wire.label for wire in drawable.out_port.wires()]
      if len(out_nodes) != 1:
        board.display_message('Op amp output port must be connected to 1 wire',
            ERROR)
        return
      na1, na2, nb1, nb2 = map(maybe_rename_node, (plus_nodes[0],
          minus_nodes[0], out_nodes[0], GROUND))
      circuit_components.append(Op_Amp(na1, na2, current_name(drawable, na1,
          na2), nb1, nb2, current_name(drawable, nb1, nb2)))
    # pot component
    elif isinstance(drawable, Pot_Drawable):
      if not drawable.signal_file:
        board.display_message('No signal file loaded for Pot', ERROR)
        return
      pot_variables = {'pot_r': None, 'pot_signal': None}
      execfile(drawable.signal_file, pot_variables)
      if not pot_variables['pot_r'] or not pot_variables['pot_signal']:
        board.display_message('Invalid Pot signal file', ERROR)
        return
      top_nodes = [wire.label for wire in drawable.top_connector.wires()]
      if len(top_nodes) != 1:
        board.display_message('Pot top node must be connected to 1 wire',
            ERROR)
        return
      middle_nodes = [wire.label for wire in drawable.middle_connector.wires()]
      if len(middle_nodes) != 1:
        board.display_message('Pot middle node must be connected to 1 wire',
            ERROR)
        return
      bottom_nodes = [wire.label for wire in drawable.bottom_connector.wires()]
      if len(bottom_nodes) != 1:
        board.display_message('Pot bottom node must be connected to 1 wire',
            ERROR)
        return
      n_top, n_middle, n_bottom = map(maybe_rename_node, (top_nodes[0],
          middle_nodes[0], bottom_nodes[0]))
      circuit_components.append(Pot(n_top, n_middle, n_bottom, current_name(
          drawable, n_top, n_middle), current_name(drawable, n_middle,
          n_bottom), pot_variables['pot_r'], pot_variables['pot_signal']))
    # motor connector component
    elif isinstance(drawable, Motor_Connector_Drawable):
      pin_5_nodes = [wire.label for wire in drawable.pin_connector(5).wires()]
      if len(pin_5_nodes) != 1:
        board.display_message('Motor connector pin 5 must be connected to 1 '
            'wire', ERROR)
        return
      pin_6_nodes = [wire.label for wire in drawable.pin_connector(6).wires()]
      if len(pin_6_nodes) != 1:
        board.display_message('Motor connector pin 6 must be connected to 1 '
            'wire', ERROR)
        return
      n1, n2 = map(maybe_rename_node, (pin_5_nodes[0], pin_6_nodes[0]))
      circuit_components.append(Motor(n1, n2, current_name(drawable, n1, n2)))
      plotters.append(Motor_Plotter(n1, n2))
  # make sure both of the probes are present
  if not probe_plus and not probe_minus:
    board.display_message('No probes', WARNING)
  elif not probe_plus:
    board.display_message('No +probe', WARNING)
  elif not probe_minus:
    board.display_message('No -probe', WARNING)
  else:
    # add probe plotter to list of plotters
    plotters.append(Probe_Plotter(probe_plus, probe_minus))
    # create and analyze circuit
    circuit = Circuit(circuit_components, GROUND)
    analyze(circuit, plotters)
