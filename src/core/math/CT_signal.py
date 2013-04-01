"""
Representation for Continuous Time (CT) signals.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

class CT_Signal:
  """
  Representation for CT signals.
  """
  # TODO(mikemeko): means of combination
  @property
  def sample(t):
    """
    Returns the value of this signal at the given time |t|. Every subclass
        should implement this method.
    """
    raise NotImplementedError('subclasses should implement this.')

class Function_CT_Signal:
  """
  CT signal with samples based on an underlying function.
  """
  def __init__(self, f):
    """
    |f|: function used to produce samples.
    """
    CT_Signal.__init__(self)
    self.f = f
  def sample(self, t):
    return self.f(t)
