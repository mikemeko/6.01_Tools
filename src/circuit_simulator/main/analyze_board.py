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
  # first find ground node
  gnd = None
  for drawable in board.get_drawables():
    nodes = [wire.label for wire in drawable.wires()]
    # ground component
    if isinstance(drawable, Ground_Drawable):
      if len(nodes) != 1:
        board.display_message('There must be exatly one wire connected to '
            'ground component', ERROR)
        return
      gnd = nodes[0]
      break
  else:
    board.display_message('No ground component found', ERROR)
    return
  # probe labels
  probe_plus, probe_minus = None, None
  for drawable in board.get_drawables():
    nodes = [wire.label for wire in drawable.wires()]
    # power component
    if isinstance(drawable, Power_Drawable):
      if len(nodes) != 1:
        board.display_message('There must be exactly one wire connected to '
            'power component', ERROR)
        return
      n1, n2 = nodes[0], gnd
      circuit_components.append(Voltage_Source(n1, n2, current_name(drawable,
          n1, n2), POWER))
    # probe plus
    elif isinstance(drawable, Probe_Plus_Drawable):
      if len(nodes) != 1:
        board.display_message('There must be exactly one wire connected to '
            'probe plus component', ERROR)
        return
      probe_plus = nodes[0]
    # probe minus
    elif isinstance(drawable, Probe_Minus_Drawable):
      if len(nodes) != 1:
        board.display_message('There must be exactly one wire connected to '
            'probe minus component', ERROR)
        return
      probe_minus = nodes[0]
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
      n1, n2 = nodes
      circuit_components.append(Resistor(n1, n2, current_name(drawable, n1,
          n2), r))
  # make sure either both or neither of the probes is present
  if (probe_plus and not probe_minus) or (not probe_plus and probe_minus):
    board.display_message('Either both or neither of the probes should be '
        'present', ERROR)
  # create and analyze circuit
  circuit = Circuit(circuit_components, gnd)
  analyze(circuit, probe_plus, probe_minus)
