"""
Runs circuit simulator.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_board import run_analysis
from circuit_drawables import Ground_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_drawables import Simulate_Run_Drawable
from constants import APP_NAME
from constants import DEV_STAGE
from core.gui.board import Board
from core.gui.constants import INFO
from core.gui.constants import LEFT
from core.gui.constants import RIGHT
from core.gui.constants import WARNING
from core.gui.palette import Palette
from Tkinter import Tk

if __name__ == '__main__':
  # create root
  root = Tk()
  root.resizable(0, 0)
  def analyze(circuit, probe_plus, probe_minus):
    """
    Displays a message on the board showing the voltage difference between
        nodes |probe_plus| and |probe_minus| of the given |circuit|.
    """
    assert probe_plus and probe_minus, 'need both +probe and -probs'
    if probe_plus not in circuit.data:
      board.display_message('+probe is disconnected from circuit', WARNING)
    elif probe_minus not in circuit.data:
      board.display_message('-probe is disconnected from circuit', WARNING)
    else:
      probe_difference = circuit.data[probe_plus] - circuit.data[probe_minus]
      board.display_message('%.3f V' % probe_difference, message_type=INFO,
          auto_remove=False)
  # create empty board
  board = Board(root, directed_wires=False)
  # create palette
  palette = Palette(root, board)
  # add circuit components to palette
  palette.add_drawable_type(Power_Drawable, LEFT, None)
  palette.add_drawable_type(Ground_Drawable, LEFT, None)
  palette.add_drawable_type(Resistor_Drawable, LEFT, None,
      on_resistance_changed=lambda: board.set_changed(True))
  palette.add_drawable_type(Probe_Plus_Drawable, LEFT, None,
      disregard_location=True)
  palette.add_drawable_type(Probe_Minus_Drawable, LEFT, None,
      disregard_location=True)
  # add button to simulate circuit
  palette.add_drawable_type(Simulate_Run_Drawable, RIGHT,
      lambda event: run_analysis(board, analyze))
  # shortcuts
  board.add_key_binding('a', lambda: run_analysis(board, analyze))
  # set title
  root.title('%s (%s)' % (APP_NAME, DEV_STAGE))
  # run main loop
  root.mainloop()
