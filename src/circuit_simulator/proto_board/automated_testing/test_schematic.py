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

class Schematic_Tester:
  def __init__(self, resistors_as_components, cost_type, solve_mode,
      solve_order, best_first, filter_wire_lengths):
    self.resistors_as_components = resistors_as_components
    self.cost_type = cost_type
    self.solve_mode = solve_mode
    self.solve_order = solve_order
    self.best_first = best_first
    self.filter_wire_lengths = filter_wire_lengths
  def _run_test(self, circuit, *args):
    """
    Attempts to produce the protoboard layout for the given |circut| and returns
        stats corresponding to the layout.
    """
    num_resistors = 0
    num_pots = 0
    num_op_amps = 0
    num_motors = 0
    head_present = False
    robot_present = False
    pin_nodes = []
    def add_pin_nodes(*args):
      for pin_node in args:
        if pin_node:
          pin_nodes.append(pin_node)
    for component in circuit.components:
      if isinstance(component, Resistor):
        num_resistors += 1
        add_pin_nodes(component.n1, component.n2)
      elif isinstance(component, Pot):
        num_pots += 1
        add_pin_nodes(component.n_top, component.n_middle, component.n_bottom)
      elif isinstance(component, Op_Amp):
        num_op_amps += 1
        add_pin_nodes(component.na1, component.na2, component.nb1)
      elif isinstance(component, Motor):
        num_motors += 1
        add_pin_nodes(component.motor_plus, component.motor_minus)
      elif isinstance(component, Head_Connector):
        head_present = True
        add_pin_nodes(component.n_pot_top, component.n_pot_middle,
            component.n_pot_bottom, component.n_photo_left,
            component.n_photo_common, component.n_photo_right,
            component.n_motor_plus, component.n_motor_minus)
      elif isinstance(component, Robot_Connector):
        robot_present = True
        add_pin_nodes(component.pwr, component.gnd, component.Vi1,
            component.Vi2, component.Vi3, component.Vi4, component.Vo)
    interconnecting_nodes = set()
    for i, node in enumerate(pin_nodes):
      if node in (pin_nodes[:i] + pin_nodes[i + 1:]):
        interconnecting_nodes.add(node)
    num_nodes = len(interconnecting_nodes)
    num_schematic_pins = sum(n in interconnecting_nodes for n in pin_nodes)
    solve_data = solve_layout(circuit,
        resistors_as_components=self.resistors_as_components,
        cost_type=self.cost_type, mode=self.solve_mode, order=self.solve_order,
        best_first=self.best_first,
        filter_wire_lengths=self.filter_wire_lengths, verbose=False)
    proto_board = solve_data['proto_board']
    loc_pairs = solve_data['loc_pairs']
    num_loc_pairs = len(loc_pairs) if loc_pairs is not None else None
    placement_time = solve_data['placement_time']
    wiring_time = solve_data['wiring_time']
    num_expanded = solve_data['num_expanded']
    solved = proto_board is not None
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
    return (
        solved,
        placement_time,
        wiring_time,
        num_expanded,
        num_schematic_pins,
        num_resistors,
        num_pots,
        num_op_amps,
        num_op_amp_packages,
        num_motors,
        head_present,
        robot_present,
        num_wires,
        total_wire_length,
        num_wire_crosses,
        num_nodes,
        num_loc_pairs,
        proto_board)
  def test_schematic(self, schematic_file):
    """
    Attempts to produce the protoboard layout for the given |schematic_file|, a
        netlist file. Returns stats corresponding to the layout.
    """
    board = Mock_Board()
    open_board_from_file(board, schematic_file, DESERIALIZERS, FILE_EXTENSION)
    return run_analysis(board, self._run_test)
