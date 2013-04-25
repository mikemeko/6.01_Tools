"""
Contains the method to analyze the circuit drawn on a board.
TODO(mikemeko): some items need to be labeled in case there are multiple.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_drawables import Ground_Drawable
from circuit_drawables import Head_Connector_Drawable
from circuit_drawables import Motor_Connector_Drawable
from circuit_drawables import Op_Amp_Drawable
from circuit_drawables import Pot_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_drawables import Robot_Connector_Drawable
from circuit_simulator.simulation.circuit import Circuit
from circuit_simulator.simulation.circuit import Head_Connector
from circuit_simulator.simulation.circuit import Motor_Connector
from circuit_simulator.simulation.circuit import Op_Amp
from circuit_simulator.simulation.circuit import Resistor
from circuit_simulator.simulation.circuit import Signalled_Pot
from circuit_simulator.simulation.circuit import Robot_Connector
from circuit_simulator.simulation.circuit import Voltage_Source
from constants import GROUND
from constants import POWER
from constants import POWER_VOLTS
from core.gui.board import Board
from core.gui.constants import ERROR
from plotters import Head_Plotter
from plotters import Motor_Plotter
from plotters import Probe_Plotter
from plotters import Signalled_Pot_Plotter

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
      for node in nodes:
        power_nodes.add(node)
    # ground component
    if isinstance(drawable, Ground_Drawable):
      for node in nodes:
        ground_nodes.add(node)
    # robot connector component
    if isinstance(drawable, Robot_Connector_Drawable):
      if robot_connector_found:
        board.display_message('At most 1 Robot Connector allowed', ERROR)
        return
      robot_connector_found = True
      pin_2_nodes = [wire.label for wire in drawable.pin_connector(2).wires()]
      for node in pin_2_nodes:
        power_nodes.add(node)
      pin_4_nodes = [wire.label for wire in drawable.pin_connector(4).wires()]
      for node in pin_4_nodes:
        ground_nodes.add(node)
      # add robot connector to circuit components, so that we know it's there
      #     and that we don't need to connect to a power supply
      circuit_components.append(Robot_Connector())
  # ensure that there is at least one power component
  if not power_nodes:
    board.display_message('No power nodes', ERROR)
    return
  # ensure that there is at least one ground component
  if not ground_nodes:
    board.display_message('No ground nodes', ERROR)
    return
  # ensure that power nodes and ground nodes are disjoint (no short circuit)
  if power_nodes.intersection(ground_nodes):
    board.display_message('Short circuit', ERROR)
    return
  # add voltage source to circuit
  circuit_components.append(Voltage_Source(POWER, GROUND, current_name(
      drawable, POWER, GROUND), POWER_VOLTS))
  def maybe_rename_node(node):
    """
    If this node is a power node or a ground node, this method returns the
        appropriate unique name, otherwise the original name is returned.
    """
    if node in power_nodes:
      return POWER
    elif node in ground_nodes:
      return GROUND
    return node
  # probe labels
  probe_plus, probe_minus = None, None
  # flag to ensure that there is at most one head connector
  head_connector_found = False
  for drawable in board.get_drawables():
    # wires attached to this component
    nodes = [wire.label for wire in drawable.wires()]
    # probe plus component
    if isinstance(drawable, Probe_Plus_Drawable):
      if len(nodes) > 1:
        board.display_message('+probe can be connected to at most 1 wire',
            ERROR)
        return
      if nodes:
        probe_plus = maybe_rename_node(nodes[0])
    # probe minus component
    elif isinstance(drawable, Probe_Minus_Drawable):
      if len(nodes) > 1:
        board.display_message('-probe can be connected to at most 1 wire',
            ERROR)
        return
      if nodes:
        probe_minus = maybe_rename_node(nodes[0])
    # resistor component
    elif isinstance(drawable, Resistor_Drawable):
      resistor_connector_it = iter(drawable.connectors)
      connector_1_nodes = list(resistor_connector_it.next().wires())
      connector_2_nodes = list(resistor_connector_it.next().wires())
      # resistor is proper only if it has exactly one wire attached to each end
      if len(connector_1_nodes) != 1 or len(connector_2_nodes) != 1:
        board.display_message('Each end of resistor must be connected to 1 '
            'wire', ERROR)
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
      pot = Signalled_Pot(n_top, n_middle, n_bottom, current_name(drawable,
          n_top, n_middle), current_name(drawable, n_middle, n_bottom),
          pot_variables['pot_r'], pot_variables['pot_signal'])
      circuit_components.append(pot)
      plotters.append(Signalled_Pot_Plotter(pot))
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
      motor_connector = Motor_Connector(n1, n2, current_name(drawable, n1, n2))
      circuit_components.append(motor_connector)
      plotters.append(Motor_Plotter(motor_connector))
    # head connector component
    elif isinstance(drawable, Head_Connector_Drawable):
      if head_connector_found:
        board.display_message('At most 1 Head Connector allowed', ERROR)
        return
      head_connector_found = True
      if not drawable.signal_file:
        board.display_message('No signal file loaded for Head Connector',
            ERROR)
        return
      lamp_signals = {'lamp_angle_signal': None, 'lamp_distance_signal': None}
      execfile(drawable.signal_file, lamp_signals)
      pin_nodes = []
      for i in xrange(1, 9):
        pin_i_nodes = [wire.label for wire in drawable.pin_connector(i).wires(
            )]
        if len(pin_i_nodes) > 1:
          board.display_message('Head Connector pin %d cannot be connected to '
              'more than 1 wire' % i, ERROR)
          return
        pin_nodes.append(maybe_rename_node(pin_i_nodes[0]) if pin_i_nodes else
            None)
      (pot_top, pot_middle, pot_bottom, photo_left, photo_common, photo_right,
          motor_plus, motor_minus) = pin_nodes
      # pot check
      if any([pot_top, pot_middle, pot_bottom]) and not all([pot_top,
          pot_middle, pot_bottom]):
        board.display_message('Head Connector pot must be either fully '
            'connected or fully disconnected', ERROR)
        return
      # left photodetector check
      if any([photo_left, photo_common]) and not all([photo_left,
          photo_common]):
        board.display_message('Head Connector left photodetector must be '
            'either fully connected or fully disconnected', ERROR)
        return
      # right photodetector check
      if any([photo_right, photo_common]) and not all([photo_right,
          photo_common]):
        board.display_message('Head Connector right photodetector must be '
            'either fully connected or fully disconnected', ERROR)
        return
      # motor check
      if any([motor_plus, motor_minus]) and not all([motor_plus, motor_minus]):
        board.display_message('Head Connector motor must be either fully '
            'connected or fully disconnected', ERROR)
        return
      head_connector = Head_Connector(pot_top, pot_middle, pot_bottom,
          current_name(drawable, pot_top, pot_middle), current_name(drawable,
          pot_middle, pot_bottom), photo_left, photo_common, photo_right,
          current_name(drawable, photo_left, photo_common), current_name(
          drawable, photo_common, photo_right), motor_plus, motor_minus,
          current_name(drawable, motor_plus, motor_minus), lamp_signals[
          'lamp_angle_signal'], lamp_signals['lamp_distance_signal'])
      circuit_components.append(head_connector)
      plotters.append(Head_Plotter(head_connector))
  # if both probes are given, display probe voltage difference graph
  if probe_plus and probe_minus:
    plotters.append(Probe_Plotter(probe_plus, probe_minus))
  # create and analyze circuit
  circuit = Circuit(circuit_components, GROUND)
  analyze(circuit, plotters)
