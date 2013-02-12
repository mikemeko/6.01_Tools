"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_drawables import Ground_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Resistor_Drawable
from constants import POWER
from circuit_simulator.simulation.circuit import Circuit
from circuit_simulator.simulation.circuit import Resistor
from circuit_simulator.simulation.circuit import Voltage_Source
from core.gui.board import Board
from core.gui.constants import ERROR
from core.util.util import is_callable

def current_name(drawable, n1, n2):
  """
  TODO(mikemeko)
  """
  return '%s %s->%s' % (str(drawable), n1, n2)

def run_analysis(board, analyze):
  """
  TODO(mikemeko)
  """
  assert isinstance(board, Board), 'board must be a Board'
  assert is_callable(analyze), 'analyze must be callable'
  # remove current message on board, if any
  board.remove_message()
  # elements of the circuit
  circuit_components = []
  # first find power and ground nodes
  pwr, gnd = set(), set()
  for drawable in board.get_drawables():
    nodes = [wire.label for wire in drawable.wires()]
    # power component
    if isinstance(drawable, Power_Drawable):
      if len(nodes) != 1:
        board.display_message('There must be exactly one wire connected to '
            'power component', ERROR)
        return
      pwr.add(nodes[0])
    # ground component
    if isinstance(drawable, Ground_Drawable):
      if len(nodes) != 1:
        board.display_message('There must be exatly one wire connected to '
            'ground component', ERROR)
        return
      gnd.add(nodes[0])
  if not pwr:
    board.display_message('No power component found', ERROR)
    return
  if not gnd:
    board.display_message('No ground component found', ERROR)
    return
  if pwr.intersection(gnd):
    board.display_message('Short circuit', ERROR)
    return
  pwr_rep = iter(pwr).next()
  gnd_rep = iter(gnd).next()
  # add voltage source to circuit
  circuit_components.append(Voltage_Source(pwr_rep, gnd_rep,
      current_name(drawable, pwr_rep, gnd_rep), POWER))
  def validate_node(node):
    """
    TODO(mikemeko)
    """
    if node in pwr:
      return pwr_rep
    elif node in gnd:
      return gnd_rep
    return node
  # probe labels
  probe_plus, probe_minus = None, None
  for drawable in board.get_drawables():
    nodes = [wire.label for wire in drawable.wires()]
    # probe plus
    if isinstance(drawable, Probe_Plus_Drawable):
      if len(nodes) != 1:
        board.display_message('There must be exactly one wire connected to '
            'probe plus component', ERROR)
        return
      probe_plus = validate_node(nodes[0])
    # probe minus
    elif isinstance(drawable, Probe_Minus_Drawable):
      if len(nodes) != 1:
        board.display_message('There must be exactly one wire connected to '
            'probe minus component', ERROR)
        return
      probe_minus = validate_node(nodes[0])
    # resistor component
    elif isinstance(drawable, Resistor_Drawable):
      if len(nodes) != 2:
        board.display_message('There must be exactly two wires connected to '
            'resistor component', ERROR)
        return
      try:
        r = float(drawable.get_resistance())
      except:
        board.display_message('Could not obtain resistance constant', ERROR)
        return
      n1, n2 = map(validate_node, nodes)
      circuit_components.append(Resistor(n1, n2, current_name(drawable, n1,
          n2), r))
  # make sure either both or neither of the probes is present
  if (probe_plus and not probe_minus) or (not probe_plus and probe_minus):
    board.display_message('Either both or neither of the probes should be '
        'present', ERROR)
  # create and analyze circuit
  circuit = Circuit(circuit_components, gnd_rep)
  analyze(circuit, probe_plus, probe_minus)
