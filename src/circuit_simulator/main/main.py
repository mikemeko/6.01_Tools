"""
Runs circuit simulator.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_board import run_analysis
from circuit_drawables import Ground_Drawable
from circuit_drawables import Head_Connector_Drawable
from circuit_drawables import Motor_Drawable
from circuit_drawables import Motor_Pot_Drawable
from circuit_drawables import Op_Amp_Drawable
from circuit_drawables import Photosensors_Drawable
from circuit_drawables import Pot_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Proto_Board_Run_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_drawables import Robot_Pin_Drawable
from circuit_drawables import Simulate_Run_Drawable
from circuit_simulator.proto_board.circuit_piece_placement import all_nodes
from circuit_simulator.proto_board.circuit_piece_placement import (
    loc_pairs_to_connect)
from circuit_simulator.proto_board.circuit_piece_placement import (
    locs_for_node)
from circuit_simulator.proto_board.circuit_to_circuit_pieces import (
    get_piece_placement)
from circuit_simulator.proto_board.constants import GROUND_RAIL
from circuit_simulator.proto_board.constants import POWER_RAIL
from circuit_simulator.proto_board.constants import RAIL_LEGAL_COLUMNS
from circuit_simulator.proto_board.find_proto_board_wiring import find_wiring
from circuit_simulator.proto_board.proto_board import Proto_Board
from circuit_simulator.proto_board.util import node_disjoint_set_forest
from circuit_simulator.proto_board.visualization.visualization import (
    visualize_proto_board)
from circuit_simulator.simulation.circuit import Robot_Connector
from constants import APP_NAME
from constants import BOARD_HEIGHT
from constants import BOARD_WIDTH
from constants import DEV_STAGE
from constants import FILE_EXTENSION
from constants import GROUND
from constants import PALETTE_HEIGHT
from constants import POWER
from constants import PROBE_INIT_PADDING
from constants import PROBE_SIZE
from core.gui.app_runner import App_Runner
from core.gui.board import Board
from core.gui.components import Wire
from core.gui.components import Wire_Connector_Drawable
from core.gui.constants import LEFT
from core.gui.constants import RIGHT
from core.gui.constants import ERROR
from pylab import show
from sys import argv
from Tkinter import Toplevel

def on_init(board):
  """
  Method called when a new circuit simulator |board| is created.
  """
  assert isinstance(board, Board), 'board must be a Board'
  # create probe drawables and connect minus probe to ground
  minus_probe = Probe_Minus_Drawable()
  board.add_drawable(minus_probe, (PROBE_INIT_PADDING, PROBE_INIT_PADDING))
  ground = Ground_Drawable().rotated().rotated()
  board.add_drawable(ground, (PROBE_SIZE + 2 * PROBE_INIT_PADDING,
      PROBE_INIT_PADDING))
  x1, y1 = iter(minus_probe.connectors).next().center
  x2, y2 = iter(ground.connectors).next().center
  board.add_wire(x1, y1, x2, y2)
  board.add_drawable(Probe_Plus_Drawable(), (
      PROBE_INIT_PADDING, PROBE_SIZE + 2 * PROBE_INIT_PADDING))

if __name__ == '__main__':
  app_runner = App_Runner(on_init, APP_NAME, DEV_STAGE, FILE_EXTENSION, (
      Power_Drawable, Ground_Drawable, Probe_Plus_Drawable,
      Probe_Minus_Drawable, Resistor_Drawable, Op_Amp_Drawable, Pot_Drawable,
      Motor_Drawable, Motor_Pot_Drawable, Photosensors_Drawable,
      Robot_Pin_Drawable, Wire_Connector_Drawable, Wire), BOARD_WIDTH,
      BOARD_HEIGHT, PALETTE_HEIGHT, False, True, argv[1] if len(argv) > 1 else
      None)
  def simulate(circuit, plotters):
    """
    Displays the plot that are drawn by the |plotters|.
    """
    # ensure that circuit was successfully solved
    if circuit.data:
      # show label tooltips on board
      app_runner.board.show_label_tooltips()
      # show analysis plots
      for plotter in plotters:
        plotter.plot(circuit.data)
      show()
    else:
      app_runner.board.display_message('Could not solve circuit', ERROR)
  def proto_board_layout(circuit, plotters):
    """
    Finds a way to layout the given |circuit| on a proto board and displays the
        discovered proto board.
    """
    try:
      # get a placement for the appropriate circuit pieces
      placement, resistor_node_pairs = get_piece_placement(circuit)
      # put each of the pieces on the proto board
      proto_board = Proto_Board()
      for piece in placement:
        proto_board = proto_board.with_piece(piece)
      # get all the nodes in the circuit and their respective locations on the
      #     proto board
      nodes = all_nodes(placement)
      node_locs_mapping = dict(zip(nodes, map(lambda node: locs_for_node(
          placement, node), nodes)))
      # force the bottom two rails to be power and ground rails
      node_locs_mapping[GROUND].append((GROUND_RAIL, iter(
          RAIL_LEGAL_COLUMNS).next()))
      node_locs_mapping[POWER].append((POWER_RAIL, iter(
          RAIL_LEGAL_COLUMNS).next()))
      # find wiring on the proto board to interconnect all locations of the same
      #     node
      proto_board = proto_board.with_loc_disjoint_set_forest(
          node_disjoint_set_forest(node_locs_mapping))
      proto_board = find_wiring(loc_pairs_to_connect(placement,
          resistor_node_pairs), proto_board)
      # show labels on board for easy schematic-layout matching
      app_runner.board.show_label_tooltips()
      # visualize proto board
      show_pwr_gnd_pins = not any([isinstance(component, Robot_Connector) for
          component in circuit.components])
      visualize_proto_board(proto_board, Toplevel(), show_pwr_gnd_pins)
    except:
      app_runner.board.display_message('Could not find proto board wiring',
          ERROR, False)
  # add circuit components to palette
  app_runner.palette.add_drawable_type(Power_Drawable, LEFT, None)
  app_runner.palette.add_drawable_type(Ground_Drawable, LEFT, None)
  app_runner.palette.add_drawable_type(Resistor_Drawable, LEFT, None,
      board=app_runner.board)
  app_runner.palette.add_drawable_type(Pot_Drawable, LEFT, None,
      on_signal_file_changed=lambda: app_runner.board.set_changed(True))
  app_runner.palette.add_drawable_type(Op_Amp_Drawable, LEFT, None)
  app_runner.palette.add_drawable_type(Head_Connector_Drawable, LEFT, None,
      types_to_add=[(Motor_Drawable, {}), (Motor_Pot_Drawable, {}), (
      Photosensors_Drawable, {'on_signal_file_changed':
      lambda: app_runner.board.set_changed(True)})])
  app_runner.palette.add_drawable_type(Motor_Drawable, LEFT, None)
  app_runner.palette.add_drawable_type(Robot_Pin_Drawable, LEFT, None)
  # add buttons to analyze circuit
  app_runner.palette.add_drawable_type(Simulate_Run_Drawable, RIGHT,
      lambda event: run_analysis(app_runner.board, simulate))
  app_runner.palette.add_drawable_type(Proto_Board_Run_Drawable, RIGHT,
      lambda event: run_analysis(app_runner.board, proto_board_layout))
  # shortcuts
  app_runner.board.add_key_binding('s', lambda: run_analysis(app_runner.board,
      simulate))
  app_runner.board.add_key_binding('p', lambda: run_analysis(app_runner.board,
      proto_board_layout))
  # run
  app_runner.run()
