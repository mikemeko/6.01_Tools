"""
Representations for:
    (1) Polynomials in R.
    (2) Ratios of polynomials in R.
    (2) Polynomials in signal variables (where a variable's coefficient is a
            ratio of polynomials in R).
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.util.util import empty
from core.util.util import is_number

class R_Polynomial:
  """
  Representation for polynomials in R.
  """
  def __init__(self, coeffs):
    """
    |coeffs|: a non-empty iterable of the coefficients of powers of R.
    For example, 2R**2 + 1 has coefficients [1, 0, 2].
    """
    # check precondition on coeffs
    assert not empty(coeffs), 'coeffs cannot be empty'
    try:
      for val in coeffs:
        assert is_number(val)
    except:
      raise Exception('coeffs must be an iterable containing numbers')
    # make coeffs a tuple so that it's immutable
    self.coeffs = tuple(coeffs)
    # record the degree of this polynomial
    self.degree = len(self.coeffs) - 1
  def coeff(self, exp):
    """
    Returns the coefficient of the R**|exp| term.
    """
    return self.coeffs[exp] if exp <= self.degree else 0
  def scalar_mult(self, const):
    """
    Returns |const| times this polynomial.
    """
    return R_Polynomial([const * self.coeff(exp)
        for exp in xrange(self.degree + 1)])
  def shift(self):
    """
    Returns R times this polynomial.
    """
    return R_Polynomial([0] + list(self.coeffs))
  def is_zero(self):
    """
    Returns True if this polynomial is 0, False otherwise.
    """
    return not any(self.coeffs)
  @staticmethod
  def one():
    """
    Returns an R_Polynomial for 1.
    """
    return R_Polynomial([1])
  @staticmethod
  def zero():
    """
    Returns an R_Polynomial for 0.
    """
    return R_Polynomial([0])
  def __add__(self, other):
    assert isinstance(other, R_Polynomial), 'other must be an R_Polynomial'
    new_coeffs = []
    for exp in xrange(max(self.degree, other.degree) + 1):
      new_coeffs.append(self.coeff(exp) + other.coeff(exp))
    return R_Polynomial(new_coeffs)
  def __sub__(self, other):
    assert isinstance(other, R_Polynomial), 'other must be an R_Polynomial'
    return self + other.scalar_mult(-1)
  def __mul__(self, other):
    assert isinstance(other, R_Polynomial), 'other must be an R_Polynomial'
    new_coeffs = [0] * (self.degree + other.degree + 1)
    for exp1 in xrange(self.degree + 1):
      for exp2 in xrange(other.degree + 1):
        new_coeffs[exp1 + exp2] += self.coeff(exp1) * other.coeff(exp2)
    return R_Polynomial(new_coeffs)
  def __str__(self):
    if self.degree == 0:
      return str(self.coeff(0))
    elif self.is_zero():
      return '0'
    else:
      # build up string one exponent at a time, paying attention to exceptions
      coeff_0 = self.coeff(0)
      s = ''
      if coeff_0:
        s = 'xxx' # we return s[3:]
        s += str(coeff_0)
      coeff_1 = self.coeff(1)
      if abs(coeff_1) == 1:
        s += ' - R' if coeff_1 < 0 else ' + R'
      elif coeff_1:
        s += (' - %sR' if coeff_1 < 0 else ' + %sR') % str(abs(coeff_1))
      for exp in xrange(2, self.degree + 1):
        coeff_exp = self.coeff(exp)
        if abs(coeff_exp) == 1:
          s += (' - R^%s' if coeff_exp < 0 else ' + R^%s') % str(exp)
        elif coeff_exp:
          s += (' - %sR^%s' if coeff_exp < 0 else ' + %sR^%s') % (
              str(abs(coeff_exp)), str(exp))
      return s[3:]

class R_Ratio:
  """
  Representation for ratios of polynomials in R.
  """
  def __init__(self, numerator, denominator=R_Polynomial.one()):
    """
    |numerator|: R_Polynomial for the numerator of this ratio.
    |denominator|: non-zero R_Polynomial for the denominator of this ratio.
    """
    assert isinstance(numerator, R_Polynomial), ('numerator must be an '
        'R_Polynomial')
    assert isinstance(denominator, R_Polynomial), ('denominator must be an '
        'R_Polynomial')
    assert not denominator.is_zero(), 'denominator cannot be 0'
    self.numerator = numerator
    self.denominator = denominator
  def scalar_mult(self, const):
    """
    Returns |const| times this ratio.
    """
    return R_Ratio(self.numerator.scalar_mult(const), self.denominator)
  def shift(self):
    """
    Returns R times this ratio.
    """
    return R_Ratio(self.numerator.shift(), self.denominator)
  @staticmethod
  def one():
    """
    Returns an R_Ratio for 1.
    """
    return R_Ratio(R_Polynomial.one())
  @staticmethod
  def zero():
    """
    Returns an R_Ratio for 0.
    """
    return R_Ratio(R_Polynomial.zero())
  def __add__(self, other):
    assert isinstance(other, R_Ratio), 'other must be an R_Ratio'
    n1, d1 = self.numerator, self.denominator
    n2, d2 = other.numerator, other.denominator
    return R_Ratio(n1 * d2 + n2 * d1, d1 * d2)
  def __sub__(self, other):
    assert isinstance(other, R_Ratio), 'other must be an R_Ratio'
    return self + other.scalar_mult(-1)
  def __mul__(self, other):
    assert isinstance(other, R_Ratio), 'other must be an R_Ratio'
    n1, d1 = self.numerator, self.denominator
    n2, d2 = other.numerator, other.denominator
    return R_Ratio(n1 * n2, d1 * d2)
  def __div__(self, other):
    assert isinstance(other, R_Ratio), 'other must be an R_Ratio'
    n1, d1 = self.numerator, self.denominator
    n2, d2 = other.numerator, other.denominator
    return R_Ratio(n1 * d2, n2 * d1)
  def __str__(self):
    return '(%s) / (%s)' % (str(self.numerator), str(self.denominator))

class Polynomial:
  """
  Representation for polynomials in signal variables.
  """
  def __init__(self, data):
    """
    |data|: a dictionary mapping variable names to their coefficients,
        represented as R_Ratios.
    """
    assert isinstance(data, dict), 'data must be a dict'
    for var in data:
      assert isinstance(var, str), 'variable names must be strings'
      assert isinstance(data[var], R_Ratio), 'coeff must be R_Ratio'
    self.data = data
  def variables(self):
    """
    Returns the variables in this polynomial.
    """
    return self.data.keys()
  def has_variable(self, var):
    """
    Returns True if this polynomial has the variable |var|, False otherwise.
    """
    return var in self.data
  def coeff(self, var):
    """
    Returns the coefficient (an R_Ratio) for the given variable.
    """
    return self.data.get(var, R_Ratio.zero())
  def scalar_mult(self, const):
    """
    Returns |const| times this polynomial.
    """
    new_data = {}
    for var in self.data:
      new_data[var] = self.coeff(var).scalar_mult(const)
    return Polynomial(new_data)
  def shift(self):
    """
    Returns R times this polynomial.
    """
    new_data = {}
    for var in self.data:
      new_data[var] = self.coeff(var).shift()
    return Polynomial(new_data)
  def substitute(self, var, poly):
    """
    Returns a new polynomial with the variable |var| substituted by the given
        polynomial |poly|.
    """
    assert isinstance(var, str), 'variable name must be a string'
    assert isinstance(poly, Polynomial), 'poly must be a Polynomial'
    new_data = dict(self.data)
    if self.has_variable(var):
      del new_data[var]
      for v in poly.variables():
        new_data[v] = self.coeff(v) + (self.coeff(var) * poly.coeff(v))
    return Polynomial(new_data)
  def copy(self):
    """
    Returns a copy of this polynomial.
    """
    return Polynomial(self.data)
  def __add__(self, other):
    assert isinstance(other, Polynomial), 'other must be a Polynomial'
    new_data = {}
    for var in self.data:
      if var in other.data:
        new_data[var] = self.coeff(var) + other.coeff(var)
      else:
        new_data[var] = self.coeff(var)
    for var in other.data:
      if var not in new_data:
        new_data[var] = other.coeff(var)
    return Polynomial(new_data)
  def __str__(self):
    return ' + '.join('(%s)%s' % tuple(map(str, reversed(item)))
        for item in self.data.items())
