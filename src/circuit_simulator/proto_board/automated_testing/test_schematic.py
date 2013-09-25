"""
Script to run protoboard layout given just a schematic netlist file.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.analyze_board import run_analysis
from circuit_simulator.main.constants import FILE_EXTENSION
from circuit_simulator.proto_board.circuit_pieces import Op_Amp_Piece
from circuit_simulator.proto_board.solve import solve_layout
from circuit_simulator.simulation.circuit import Head_Connector
from circuit_simulator.simulation.circuit import Motor
from circuit_simulator.simulation.circuit import Op_Amp
from circuit_simulator.simulation.circuit import Pot
from circuit_simulator.simulation.circuit import Resistor
from circuit_simulator.simulation.circuit import Robot_Connector
from constants import DESERIALIZERS
from core.gui.components import Wire_Connector_Drawable
from core.save.save import open_board_from_file
from mock_board import Mock_Board
from time import time

class Schematic_Tester:
  def __init__(self, solve_mode, solve_order):
    """
    |solve_mode|, |solve_order|: parameters for protoboard solve.
    """
    self.solve_mode = solve_mode
    self.solve_order = solve_order
  def _run_test(self, circuit, *args):
    """
    Attempts to produce the protoboard layout for the given |circut| and returns
        stats corresponding to the layout.
    """
    # variables that depend on the circuit
    num_resistors = 0
    num_pots = 0
    num_op_amps = 0
    num_motors = 0
    head_present = False
    robot_present = False
    for component in circuit.components:
      if isinstance(component, Resistor):
        num_resistors += 1
      elif isinstance(component, Pot):
        num_pots += 1
      elif isinstance(component, Op_Amp):
        num_op_amps += 1
      elif isinstance(component, Motor):
        num_motors += 1
      elif isinstance(component, Head_Connector):
        head_present = True
      elif isinstance(component, Robot_Connector):
        robot_present = True
    component_nodes = [component.nodes() for component in circuit.components]
    num_nodes = len(reduce(set.union, [nodes1 & nodes2 for i, nodes1 in
        enumerate(component_nodes) for nodes2 in component_nodes[i + 1:]],
        set()))
    start_time = time()
    proto_board = solve_layout(circuit, self.solve_mode, self.solve_order)
    stop_time = time()
    solved = proto_board is not None
    solve_time = stop_time - start_time
    # variables that depend on the protoboard (if solved)
    if proto_board:
      num_op_amp_packages = sum(isinstance(piece, Op_Amp_Piece) for piece in
          proto_board.get_pieces())
      num_wires = proto_board.num_wires()
      total_wire_length = sum(wire.length() for wire in proto_board.get_wires())
      num_wire_crosses = proto_board.num_wire_crosses()
    else:
      num_op_amp_packages = None
      num_wires = None
      total_wire_length = None
      num_wire_crosses = None
    return (solved, solve_time, num_resistors, num_pots, num_op_amps,
        num_op_amp_packages, num_motors, head_present, robot_present, num_wires,
        total_wire_length, num_wire_crosses, num_nodes)
  def test_schematic(self, schematic_file):
    """
    Attempts to produce the protoboard layout for the given |schematic_file|, a
        netlist file. Returns stats corresponding to the layout.
    """
    board = Mock_Board()
    open_board_from_file(board, schematic_file, DESERIALIZERS, FILE_EXTENSION)
    return run_analysis(board, self._run_test)
