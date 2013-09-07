"""
Contains the method to analyze the circuit drawn on a board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_drawables import Ground_Drawable
from circuit_drawables import Motor_Drawable
from circuit_drawables import Motor_Pot_Drawable
from circuit_drawables import Op_Amp_Drawable
from circuit_drawables import Photosensors_Drawable
from circuit_drawables import Pot_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_drawables import Robot_IO_Drawable
from circuit_drawables import Robot_Power_Drawable
from circuit_simulator.simulation.circuit import Circuit
from circuit_simulator.simulation.circuit import Head_Connector
from circuit_simulator.simulation.circuit import Motor
from circuit_simulator.simulation.circuit import Op_Amp
from circuit_simulator.simulation.circuit import Resistor
from circuit_simulator.simulation.circuit import Signalled_Pot
from circuit_simulator.simulation.circuit import Robot_Connector
from circuit_simulator.simulation.circuit import Voltage_Source
from collections import defaultdict
from constants import GROUND
from constants import POWER
from constants import POWER_VOLTS
from core.gui.board import Board
from core.gui.constants import ERROR
from plotters import Head_Plotter
from plotters import Motor_Plotter
from plotters import Probe_Plotter
from plotters import Signalled_Pot_Plotter

def current_name(item, n1, n2):
  """
  Returns a unique name for the current "through" the given unique |item| going
      from node |n1| to node |n2|.
  """
  return '%d %s->%s' % (id(item), n1, n2)

def run_analysis(board, analyze):
  """
  Extracts a Circuit object from what is drawn on the given |board| and calls
      the given function |analyze| on it. The funtion |analyze| should take as
      arguments the circuit, as well as the plotters that are collected.
  """
  assert isinstance(board, Board), 'board must be a Board'
  # remove current message on board, if any
  board.remove_message()
  # components in the circuit
  circuit_components = []
  # analysis plotters
  plotters = []
  # probe labels
  probe_plus, probe_minus = None, None
  # constants for motors, motor_pots, and photosensors
  # we use this state to be able to identify robot head groups
  head_connector_group_ids = set()
  n_motor_plus = defaultdict(str)
  n_motor_minus = defaultdict(str)
  i_motor = defaultdict(str)
  motor_label = defaultdict(str)
  n_motor_pot_top = defaultdict(str)
  n_motor_pot_middle = defaultdict(str)
  n_motor_pot_bottom = defaultdict(str)
  i_motor_pot_top_middle = defaultdict(str)
  i_motor_pot_middle_bottom = defaultdict(str)
  motor_pot_label = defaultdict(str)
  n_photo_left = defaultdict(str)
  n_photo_common = defaultdict(str)
  n_photo_right = defaultdict(str)
  i_photo_left_common = defaultdict(str)
  i_photo_common_right = defaultdict(str)
  photo_lamp_angle_signal = defaultdict(str)
  photo_lamp_distance_signal = defaultdict(str)
  photo_label = defaultdict(str)
  # constants for robot power and robot analog inputs and outputs
  robot_connector_group_ids = set()
  robot_pwr = defaultdict(str)
  robot_gnd = defaultdict(str)
  robot_power_label = defaultdict(str)
  robot_vi1 = defaultdict(lambda: (None, None))
  robot_vi2 = defaultdict(lambda: (None, None))
  robot_vi3 = defaultdict(lambda: (None, None))
  robot_vi4 = defaultdict(lambda: (None, None))
  robot_vo = defaultdict(lambda: (None, None))
  # first identify all power and ground nodes and use the same name for all
  #     power nodes, as well as the same name for all ground nodes
  power_nodes, ground_nodes = set(), set()
  for drawable in board.get_drawables():
    # wires attached to this component
    nodes = [wire.label for wire in drawable.wires()]
    # power component
    if isinstance(drawable, Power_Drawable):
      for node in nodes:
        power_nodes.add(node)
    # ground component
    elif isinstance(drawable, Ground_Drawable):
      for node in nodes:
        ground_nodes.add(node)
    # robot connector component
    elif isinstance(drawable, Robot_Power_Drawable):
      for node in [wire.label for wire in drawable.pwr.wires()]:
        power_nodes.add(node)
      for node in [wire.label for wire in drawable.gnd.wires()]:
        ground_nodes.add(node)
      robot_connector_group_ids.add(drawable.group_id)
      robot_pwr[drawable.group_id] = POWER
      robot_gnd[drawable.group_id] = GROUND
      robot_power_label[drawable.group_id] = drawable.label
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
      board, POWER, GROUND), POWER_VOLTS))
  def maybe_rename_node(node):
    """
    If this |node| is a power node or a ground node, this method returns the
        appropriate unique name, otherwise the original name is returned.
    """
    if node in power_nodes:
      return POWER
    elif node in ground_nodes:
      return GROUND
    return node
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
      resistor = Resistor(n1, n2, current_name(drawable, n1, n2), r)
      resistor.label = drawable.label
      circuit_components.append(resistor)
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
      op_amp = Op_Amp(na1, na2, current_name(drawable, na1, na2), nb1, nb2,
          current_name(drawable, nb1, nb2))
      op_amp.label = drawable.label
      circuit_components.append(op_amp)
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
      pot.label = drawable.label
      circuit_components.append(pot)
      plotters.append(Signalled_Pot_Plotter(pot))
    # motor component
    elif isinstance(drawable, Motor_Drawable):
      plus_nodes = [wire.label for wire in drawable.plus.wires()]
      if len(plus_nodes) != 1:
        board.display_message('Motor+ must be connected to 1 wire', ERROR)
        return
      minus_nodes = [wire.label for wire in drawable.minus.wires()]
      if len(minus_nodes) != 1:
        board.display_message('Motor- must be connected to 1 wire', ERROR)
        return
      plus_node = maybe_rename_node(plus_nodes[0])
      minus_node = maybe_rename_node(minus_nodes[0])
      i = current_name(drawable, n_motor_plus, n_motor_minus)
      if not drawable.group_id:
        motor = Motor(plus_node, minus_node, i)
        motor.label = drawable.label
        circuit_components.append(motor)
        plotters.append(Motor_Plotter(motor))
      else:
        head_connector_group_ids.add(drawable.group_id)
        n_motor_plus[drawable.group_id] = plus_node
        n_motor_minus[drawable.group_id] = minus_node
        i_motor[drawable.group_id] = i
        motor_label[drawable.group_id] = drawable.label
    # motor pot component
    elif isinstance(drawable, Motor_Pot_Drawable):
      pot_top_nodes = [wire.label for wire in drawable.top.wires()]
      if len(pot_top_nodes) != 1:
        board.display_message('Motor pot top must be connected to 1 wire',
            ERROR)
        return
      pot_middle_nodes = [wire.label for wire in drawable.middle.wires()]
      if len(pot_middle_nodes) != 1:
        board.display_message('Motor pot middle must be connected to 1 wire',
            ERROR)
        return
      pot_bottom_nodes = [wire.label for wire in drawable.bottom.wires()]
      if len(pot_bottom_nodes) != 1:
        board.display_message('Motor pot bottom must be connected to 1 wire',
            ERROR)
        return
      head_connector_group_ids.add(drawable.group_id)
      n_motor_pot_top[drawable.group_id] = maybe_rename_node(pot_top_nodes[0])
      n_motor_pot_middle[drawable.group_id] = maybe_rename_node(
          pot_middle_nodes[0])
      n_motor_pot_bottom[drawable.group_id] = maybe_rename_node(
          pot_bottom_nodes[0])
      i_motor_pot_top_middle[drawable.group_id] = current_name(drawable,
          n_motor_pot_top, n_motor_pot_middle)
      i_motor_pot_middle_bottom[drawable.group_id] = current_name(drawable,
          n_motor_pot_middle, n_motor_pot_bottom)
      motor_pot_label[drawable.group_id] = drawable.label
    # photosensor component
    elif isinstance(drawable, Photosensors_Drawable):
      if not drawable.signal_file:
        board.display_message('No signal file loaded for Photosensors', ERROR)
        return
      lamp_signals = {'lamp_angle_signal': None, 'lamp_distance_signal': None}
      execfile(drawable.signal_file, lamp_signals)
      photo_lamp_angle_signal[drawable.group_id] = lamp_signals[
          'lamp_angle_signal']
      photo_lamp_distance_signal[drawable.group_id] = lamp_signals[
          'lamp_distance_signal']
      photo_left_nodes = [wire.label for wire in drawable.left.wires()]
      if len(photo_left_nodes) != 1:
        board.display_message('Photosensor left must be connected to 1 wire',
            ERROR)
        return
      photo_common_nodes = [wire.label for wire in drawable.common.wires()]
      if len(photo_common_nodes) != 1:
        board.display_message('Photosensor common must be connected to 1 wire',
            ERROR)
        return
      photo_right_nodes = [wire.label for wire in drawable.right.wires()]
      if len(photo_right_nodes) != 1:
        board.display_message('Photosensor right must be connected to 1 wire',
            ERROR)
        return
      head_connector_group_ids.add(drawable.group_id)
      n_photo_left[drawable.group_id] = maybe_rename_node(photo_left_nodes[0])
      n_photo_common[drawable.group_id] = maybe_rename_node(
          photo_common_nodes[0])
      n_photo_right[drawable.group_id] = maybe_rename_node(
          photo_right_nodes[0])
      i_photo_left_common[drawable.group_id] = current_name(drawable,
          n_photo_left, n_photo_common)
      i_photo_common_right[drawable.group_id] = current_name(drawable,
          n_photo_common, n_photo_right)
      photo_label[drawable.group_id] = drawable.label
    # motor analog i/o component
    elif isinstance(drawable, Robot_IO_Drawable):
      if len(nodes) != 1:
        board.display_message('Robot IO must be connected to 1 wire', ERROR)
        return
      node = maybe_rename_node(nodes[0])
      robot_connector_group_ids.add(drawable.group_id)
      if drawable.name == 'Vi1':
        robot_vi1[drawable.group_id] = (node, drawable.label)
      elif drawable.name == 'Vi2':
        robot_vi2[drawable.group_id] = (node, drawable.label)
      elif drawable.name == 'Vi3':
        robot_vi3[drawable.group_id] = (node, drawable.label)
      elif drawable.name == 'Vi4':
        robot_vi4[drawable.group_id] = (node, drawable.label)
      elif drawable.name == 'Vo':
        robot_vo[drawable.group_id] = (node, drawable.label)
  # collect robot head pieces together
  for group_id in head_connector_group_ids:
    head_connector = Head_Connector(n_motor_pot_top[group_id],
        n_motor_pot_middle[group_id], n_motor_pot_bottom[group_id],
        i_motor_pot_top_middle[group_id], i_motor_pot_middle_bottom[group_id],
        n_photo_left[group_id], n_photo_common[group_id], n_photo_right[
        group_id], i_photo_left_common[group_id], i_photo_common_right[
        group_id], n_motor_plus[group_id], n_motor_minus[group_id], i_motor[
        group_id], photo_lamp_angle_signal[group_id],
        photo_lamp_distance_signal[group_id])
    head_connector.motor_label = motor_label[group_id]
    head_connector.motor_pot_label = motor_pot_label[group_id]
    head_connector.photo_label = photo_label[group_id]
    circuit_components.append(head_connector)
    plotters.append(Head_Plotter(head_connector))
  # collect robot connector pieces together
  for group_id in robot_connector_group_ids:
    vi1_node, vi1_label = robot_vi1[group_id]
    vi2_node, vi2_label = robot_vi2[group_id]
    vi3_node, vi3_label = robot_vi3[group_id]
    vi4_node, vi4_label = robot_vi4[group_id]
    vo_node, vo_label = robot_vo[group_id]
    robot_connector = Robot_Connector(robot_pwr[group_id], robot_gnd[group_id],
        vi1_node, vi2_node, vi3_node, vi4_node, vo_node)
    robot_connector.label = ','.join(filter(bool, [robot_power_label[group_id],
        vi1_label, vi2_label, vi3_label, vi4_label, vo_label]))
    circuit_components.append(robot_connector)
  # if both probes are given, display probe voltage difference graph
  if probe_plus and probe_minus:
    plotters.append(Probe_Plotter(probe_plus, probe_minus))
  # create and analyze circuit
  circuit = Circuit(circuit_components, GROUND)
  analyze(circuit, plotters)
