"""
Representation for Continuous Time (CT) signals.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.util.util import is_callable
from core.util.util import is_number

class CT_Signal:
  """
  Representation for CT signals.
  TODO(mikemeko): create nice means of combining CT_Signals, adding, etc.
  """
  @property
  def sample(t):
    """
    Returns the value of this signal at the given time |t|. Every subclass
        should implement this method.
    """
    raise NotImplementedError('subclasses should implement this')
  def samples(self, t_0, T, num_samples):
    """
    TODO(mikemeko)
    """
    return [self.sample(t_0 + n * T) for n in xrange(num_samples)]
  def __call__(self, t):
    return self.sample(t)

class Constant_CT_Signal(CT_Signal):
  """
  Constant CT signal.
  """
  def __init__(self, k):
    """
    |k|: constant value.
    """
    assert is_number(k), 'k must be a number'
    self.k = k
  def sample(self, t):
    return self.k

class Function_CT_Signal(CT_Signal):
  """
  CT signal with samples based on an underlying function.
  """
  def __init__(self, f):
    """
    |f|: function used to produce samples.
    """
    assert is_callable(f), 'f must be callable'
    self.f = f
  def sample(self, t):
    return self.f(t)
