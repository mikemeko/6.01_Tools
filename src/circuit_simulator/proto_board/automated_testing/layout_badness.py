"""
Script to measure badness of a layout.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict

C_WIRE = 1
C_WIRE_LENGTH = 1
C_WIRE_CROSSING = 5
C_DIAGONAL_WIRE = 5
C_WIRE_PIECE_CROSSING = 50
C_WIRE_OCCLUSION = 500

def badness(properties):
  assert isinstance(properties, defaultdict)
  c = 0
  c += C_WIRE_CROSSING * properties['num_wire_crossings']
  c += C_WIRE_OCCLUSION * properties['num_wire_occlusions']
  c += C_DIAGONAL_WIRE * properties['num_diagonal_wires']
  c += C_WIRE_PIECE_CROSSING * properties['num_wire_piece_crossings']
  c += C_WIRE * properties['num_wires']
  c += C_WIRE_LENGTH * properties['total_wire_length']
  return c
