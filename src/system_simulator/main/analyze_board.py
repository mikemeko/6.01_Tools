"""
Contains the method to analyze the DT LTI system drawn on a board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.gui.board import Board
from core.gui.components import Wire_Connector_Drawable
from core.gui.constants import ERROR
from core.util.util import is_callable
from system_drawables import Adder_Drawable
from system_drawables import Delay_Drawable
from system_drawables import Gain_Drawable
from system_drawables import IO_Drawable
from system_simulator.simulation.constants import X
from system_simulator.simulation.system import Adder
from system_simulator.simulation.system import Delay
from system_simulator.simulation.system import Gain
from system_simulator.simulation.system import System
from system_simulator.simulation.util import empty

def run_analysis(board, analyze):
  """
  Extracts a System object from what is drawn on the given |board| and calls
      the given function |analyze| on it.
  """
  assert isinstance(board, Board), 'board must be a Board'
  assert is_callable(analyze), 'analyze must be callable'
  # remove current message on the board, if any
  board.remove_message()
  # DT LTI components in the system
  system_components = []
  # X and Y signal names
  X_label, Y_label = None, None
  for drawable in board.get_drawables():
    # input and output signals for current drawable
    inp, out = [], []
    for connector in drawable.connectors:
      inp.extend(wire.label for wire in connector.end_wires)
      out.extend(wire.label for wire in connector.start_wires)
    # gain component
    if isinstance(drawable, Gain_Drawable):
      if len(inp) != 1:
        board.display_message('Gain must have exactly 1 input', ERROR)
        return
      if len(out) != 1:
        board.display_message('Gain must have exactly 1 output', ERROR)
        return
      try:
        K = float(drawable.get_K())
      except Exception:
        board.display_message('Could not obtain gain constant', ERROR)
        return
      system_components.append(Gain(inp[0], out[0], K))
    # delay component
    elif isinstance(drawable, Delay_Drawable):
      if len(inp) != 1:
        board.display_message('Delay must have exactly 1 input', ERROR)
        return
      if len(out) != 1:
        board.display_message('Delay must have exactly 1 output', ERROR)
        return
      system_components.append(Delay(inp[0], out[0]))
    # adder component
    elif isinstance(drawable, Adder_Drawable):
      if len(inp) < 1:
        board.display_message('Adder must have at least 1 input', ERROR)
        return
      if len(out) != 1:
        board.display_message('Adder must have exactly 1 output', ERROR)
        return
      system_components.append(Adder(inp, out[0]))
    # X and Y signals
    elif isinstance(drawable, IO_Drawable):
      # has only one connector
      connector = iter(drawable.connectors).next()
      if drawable.signal == X:
        if not empty(inp):
          board.display_message('X component cannot have any inputs', ERROR)
          return
        if len(out) != 1:
          board.display_message('X component must have exactly 1 output',
              ERROR)
          return
        X_label = out[0]
      else: # drawable.signal == Y
        if not empty(out):
          board.display_message('Y component cannot have any outputs', ERROR)
          return
        if len(inp) != 1:
          board.display_message('Y component must have exactly 1 input', ERROR)
          return
        Y_label = inp[0]
    elif isinstance(drawable, Wire_Connector_Drawable):
      if len(inp) != 1:
        board.display_message('Wire connector must have exactly 1 input',
            ERROR)
        return
    else:
      raise Exception('Found unexpected component on board')
  if X_label is None:
    board.display_message('No input signal found', ERROR)
    return
  if Y_label is None:
    board.display_message('No output signal found', ERROR)
    return
  # if there are no components, we have a wire
  if empty(system_components):
    system_components.append(Gain(X_label, Y_label, 1))
  # create and analyze system
  system = System(system_components, X=X_label, Y=Y_label, display_error=
      lambda message: board.display_message(message, ERROR))
  analyze(system)
