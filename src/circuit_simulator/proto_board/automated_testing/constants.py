"""
Automated test constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.circuit_drawables import Ground_Drawable
from circuit_simulator.main.circuit_drawables import Motor_Drawable
from circuit_simulator.main.circuit_drawables import Motor_Pot_Drawable
from circuit_simulator.main.circuit_drawables import Op_Amp_Drawable
from circuit_simulator.main.circuit_drawables import Photosensors_Drawable
from circuit_simulator.main.circuit_drawables import Pot_Drawable
from circuit_simulator.main.circuit_drawables import Power_Drawable
from circuit_simulator.main.circuit_drawables import Probe_Minus_Drawable
from circuit_simulator.main.circuit_drawables import Probe_Plus_Drawable
from circuit_simulator.main.circuit_drawables import Resistor_Drawable
from circuit_simulator.main.circuit_drawables import Robot_IO_Drawable
from circuit_simulator.main.circuit_drawables import Robot_Power_Drawable
from core.gui.components import Wire
from core.gui.components import Wire_Connector_Drawable

DESERIALIZERS = (Power_Drawable, Ground_Drawable, Probe_Plus_Drawable,
    Probe_Minus_Drawable, Resistor_Drawable, Op_Amp_Drawable, Pot_Drawable,
    Motor_Drawable, Motor_Pot_Drawable, Photosensors_Drawable,
    Robot_Power_Drawable, Robot_IO_Drawable, Wire_Connector_Drawable, Wire)
