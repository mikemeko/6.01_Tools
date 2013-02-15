"""
Contains the method to analyze the circuit drawn on a board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_drawables import Ground_Drawable
from circuit_drawables import Op_Amp_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_simulator.simulation.circuit import Circuit
from circuit_simulator.simulation.circuit import Op_Amp
from circuit_simulator.simulation.circuit import Resistor
from circuit_simulator.simulation.circuit import Voltage_Source
from constants import GROUND
from constants import POWER
from constants import POWER_VOLTS
from core.gui.board import Board
from core.gui.constants import ERROR
from core.gui.constants import WARNING
from core.util.util import is_callable

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
      arguments the circuit, as well as the labels for the positive and
      negative probe, in that order.
  """
  assert isinstance(board, Board), 'board must be a Board'
  assert is_callable(analyze), 'analyze must be callable'
  # remove current message on board, if any
  board.remove_message()
  # components in the circuit
  circuit_components = []
  # first identify all power and ground nodes and use the same name for all
  #     power nodes, as well as the same name for all ground nodes
  power_nodes, ground_nodes = set(), set()
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
      op_amp = Op_Amp(na1, na2, current_name(drawable, na1, na2), nb1, nb2,
          current_name(drawable, nb1, nb2))
      circuit_components.extend(op_amp.parts())
  # make sure both of the probes are present
  if not probe_plus and not probe_minus:
    board.display_message('No probes', WARNING)
  elif not probe_plus:
    board.display_message('No +probe', WARNING)
  elif not probe_minus:
    board.display_message('No -probe', WARNING)
  else:
    # create and analyze circuit
    circuit = Circuit(circuit_components, GROUND)
    analyze(circuit, probe_plus, probe_minus)
