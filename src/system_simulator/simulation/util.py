"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Mike Mekonnen)'

from constants import DEFAULT_ROUND_DIGITS

def complex_str(c, ndigits=DEFAULT_ROUND_DIGITS):
  """
  Returns a string representing the complex number |c| with the real and
      imaginary parts rounded to |ndigits| digits after the decimal points.
  """
  assert isinstance(c, complex), 'c must be a complex number'
  def rounded(f):
    s = str(round(f, ndigits))
    return s[:s.find('.') + ndigits + 1]
  if c.real and c.imag:
    sign = '+' if c.imag > 0 else '-'
    return '%s %s %sj' % (rounded(c.real), sign, rounded(abs(c.imag)))
  elif not c.real and c.imag:
    return '%sj' % rounded(c.imag)
  else:
    return '%s' % rounded(c.real)
