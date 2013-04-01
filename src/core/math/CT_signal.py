"""
Representation for Continuous Time (CT) signals.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

class CT_Signal:
  """
  Representation for CT signals.
  """
  @property
  def sample(t):
    """
    Returns the value of this signal at the given time |t|. Every subclass
        should implement this method.
    """
    raise NotImplementedError('subclasses should implement this.')
