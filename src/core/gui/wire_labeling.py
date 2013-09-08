"""
Script to correctly lable the wires that interconnect a group of drawables.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from components import Wire_Connector_Drawable
from constants import DEBUG_DISPLAY_WIRE_LABELS

def _label_wires_from(drawable, relabeled_wires, label):
  """
  Labels wires starting from the given |drawable|. Labels all wires that are
      not already in |relabeled_wires|. |label| is the smallest possible label
      to use. Recursively labels wires connected by wire connectors. Returns
      the maximum label used in the process.
  """
  # maximum label that could have been used in this step of labeling
  max_label = label
  for connector in drawable.connectors:
    for wire in connector.wires():
      # if the drawable is a wire connector, then reuse the same label
      # otherwise, use a new label for each wire
      # Note: only wires that are connected by wire connectors can have the
      #     same label
      if not isinstance(drawable, Wire_Connector_Drawable):
        label = max_label = max_label + 1
      # only label a wire if it has not already been labeled
      if wire not in relabeled_wires:
        # label wire and mark it labeled
        wire.label = str(label)
        relabeled_wires.add(wire)
        # display label for debugging
        if DEBUG_DISPLAY_WIRE_LABELS:
          wire.redraw(self._canvas)
        # propagate labeling if the other end of the wire is a wire connector
        # use the same label for wires that follow
        next_drawable = wire.other_connector(connector).drawable
        if isinstance(next_drawable, Wire_Connector_Drawable):
          max_label = max(max_label, _label_wires_from(next_drawable,
              relabeled_wires, label))
  return max_label

def label_wires(drawables):
  """
  Labels the wires that interconnect the given |drawables| such that two wires
      have the same label if and only if they are connected via wire connectors.
  """
  # relabel all wires
  relabeled_wires = set()
  label = 0
  for drawable in drawables:
    # increment label to pass to the next drawable so that disconnected wires
    #     are never given the same label
    label = _label_wires_from(drawable, relabeled_wires, label) + 1
