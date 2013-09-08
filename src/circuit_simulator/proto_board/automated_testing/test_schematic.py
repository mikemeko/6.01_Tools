"""
Script to run protoboard layout given just a schematic netlist file.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.analyze_board import run_analysis
from circuit_simulator.main.constants import FILE_EXTENSION
from circuit_simulator.proto_board.solve import solve_layout
from constants import DESERIALIZERS
from core.save.save import open_board_from_file
from mock_board import Mock_Board
from time import time

def _run_test(circuit, *args):
  """
  Attempts to produce the protoboard layout for the given |circut|. Returns the
      found layout (may be None if none could be found), and the amount of time
      spent in the process.
  """
  start_time = time()
  proto_board = solve_layout(circuit)
  stop_time = time()
  return proto_board, stop_time - start_time

def test_schematic(schematic_file):
  """
  Attempts to produce the protoboard layout for the given |schematic_file|, a
      netlist file. Prints out statistics for the attempt.
  """
  print 'Schematic: %s' % schematic_file
  print
  board = Mock_Board()
  open_board_from_file(board, schematic_file, DESERIALIZERS, FILE_EXTENSION)
  proto_board, running_time = run_analysis(board, _run_test)
  print
  print 'Success: %s' % (proto_board is not None)
  print 'Time spent: %s seconds' % running_time

if __name__ == '__main__':
  test_schematic('circuit_simulator/main/samples/angle_controller.circsim')
