"""
Automated tests on final (combined) algorithm.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.analyze_board import run_analysis
from circuit_simulator.main.constants import FILE_EXTENSION
from circuit_simulator.proto_board.automated_testing.constants import (
    DESERIALIZERS)
from circuit_simulator.proto_board.automated_testing.mock_board import (
    Mock_Board)
from circuit_simulator.proto_board.automated_testing.test_schematic import (
    get_circuit_stats)
from circuit_simulator.proto_board.solve import combined_solve_layout
from core.save.save import open_board_from_file
from os import walk
from os.path import basename
from os.path import join
from os.path import normpath
from sys import argv
from time import clock

def _run(circuit, *args):
  num_schematic_pins = get_circuit_stats(circuit)[-1]
  start_time = clock()
  solve_data = combined_solve_layout(circuit, verbose=False)
  end_time = clock()
  return (solve_data['proto_board'], solve_data['num_runs'],
      solve_data['num_forced_wires'], end_time - start_time, num_schematic_pins)

def _test(file_name):
  board = Mock_Board()
  open_board_from_file(board, file_name, DESERIALIZERS, FILE_EXTENSION)
  return run_analysis(board, _run)

if __name__ == '__main__':
  header = (
      'file',
      'run #',
      'solved',
      'total_time',
      'num_schematic_pins',
      'num_wires',
      'num_wire_crosses',
      'total_wire_length',
      'num_runs',
      'num_forced_wires',
      'num_piece_crosses',
      'num_diagonal_wires',
      'num_occlusions')
  output_file_name = ('circuit_simulator/proto_board/automated_testing/'
      'final_algorithm_test/%s_results' % basename(normpath(argv[1])))
  open(output_file_name, 'w').write(';'.join(header))
  for dir_path, dir_names, file_names in walk(argv[1]):
    num_files = len(file_names)
    for n, file_name in enumerate(file_names):
      print '%d/%d' % (n + 1, num_files)
      if file_name.endswith(FILE_EXTENSION):
        print file_name
        for i in xrange(10):
          print 'run %d' % (i + 1)
          (proto_board, num_runs, num_forced_wires, total_time,
              num_schematic_pins) = _test(join(dir_path, file_name))
          solved = proto_board is not None
          if solved:
            num_wires = proto_board.num_wires()
            num_wire_crosses = proto_board.num_wire_crosses()
            total_wire_length = sum(wire.length() for wire in
                proto_board.get_wires())
            num_piece_crosses = proto_board.num_wire_piece_crosses()
            num_diagonal_wires = proto_board.num_diagonal_wires()
            num_occlusions = proto_board.num_occlusions()
          else:
            num_wires = None
            num_wire_crosses = None
            total_wire_length = None
            num_piece_crosses = None
            num_diagonal_wires = None
            num_occlusions = None
          results = [line.strip() for line in open(output_file_name,
              'r').readlines()]
          results.append(';'.join(map(str, (file_name, i, solved, total_time,
              num_schematic_pins, num_wires, num_wire_crosses,
              total_wire_length, num_runs, num_forced_wires, num_piece_crosses,
              num_diagonal_wires, num_occlusions))))
          open(output_file_name, 'w').write('\n'.join(results))
