"""
Representation for polynomials:
  (1) Polynomials in R. For example 2R**2 + 1.
  (2) Polynomials in signal variables. For example (R)X + (2)Y.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

class R_Polynomial:
  """
  Representation for polynomials in R.
  """
  def __init__(self, coeffs):
    """
    |coeffs|: a list of the coefficients of powers of R. For example, 2R**2 + 1
        has coefficients [1, 0, 2].
    TODO(mikemeko): trim 0s?
    """
    self.coeffs = coeffs
    self.degree = len(coeffs) - 1
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
    return R_Polynomial([0] + self.coeffs)
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
  def _prettify(self, coeff, exp):
    """
    Returns a prettified version of |coeff|*R**|exp|.
    """
    # TODO(mikemeko): improve this!
    if coeff == 0:
      return '0'
    elif exp == 0:
      return str(coeff)
    coeff_str = str(coeff) if coeff is not 1 else ''
    if exp == 1:
      return '%sR' % coeff_str
    else:
      return '%sR^%d' % (coeff_str, exp)
  def __str__(self):
    # TODO(mikemeko): improve this!
    return '+'.join(self._prettify(self.coeff(exp), exp)
        for exp in xrange(self.degree + 1) if self.coeff(exp) is not 0)

class R_Ratio:
  """
  TODO(mikemeko)
  """
  def __init__(self, numerator, denominator=R_Polynomial([1])):
    """
    TODO(mikemeko)
    """
    assert isinstance(numerator, R_Polynomial), ('numerator must be an '
        'R_Polynomial')
    assert isinstance(denominator, R_Polynomial), ('denominator must be an '
        'R_Polynomial')
    self.numerator = numerator
    self.denominator = denominator
  def scalar_mult(self, const):
    """
    TODO(mikemeko)
    """
    return R_Ratio(self.numerator.scalar_mult(const), self.denominator)
  def shift(self):
    """
    TODO(mikemeko)
    """
    return R_Ratio(self.numerator.shift(), self.denominator)
  def __add__(self, other):
    assert isinstance(other, R_Ratio), 'other must be an R_Ratio'
    n1, d1 = self.numerator, self.denominator
    n2, d2 = other.numerator, other.denominator
    return R_Ratio(n1 * d2 + n2 * d1, d1 * d2)
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
  def __sub__(self, other):
    assert isinstance(other, R_Ratio), 'other must be an R_Ratio'
    return self + other.scalar_mult(-1)
  def __str__(self):
    return '%s / %s' % (str(self.numerator), str(self.denominator))

class Polynomial:
  """
  Representation for polynomials in signal variables.
  """
  def __init__(self, data):
    """
    |data|: a dictionary mapping variable names to their coefficients. For
        example, RX + 2Y is represented by {X:R_Polynomial([0, 1]),
        Y:R_Polynomial([2])}.
    TODO(mikemeko): update
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
    return set(self.data.keys())
  def coeff(self, var):
    """
    Returns the coefficient (an R_Ratio) for the given variable.
    """
    return self.data.get(var, R_Ratio(R_Polynomial([0])))
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
    TODO(mikemeko)
    """
    assert isinstance(var, str), 'var must be a string'
    assert isinstance(poly, Polynomial), 'poly must be a Polynomial'
    # TODO(mikemeko): assert var in this poly
    new_data = dict(self.data)
    # TODO(mikemeko): method for has_variable
    if var in self.data:
      del new_data[var]
      for v in poly.variables():
        new_data[v] = self.coeff(v) + (self.coeff(var) * poly.coeff(v))
    return Polynomial(new_data)
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
    return '+'.join('(%s)%s' % tuple(map(str, reversed(item)))
        for item in self.data.items())

if __name__ == '__main__':
  p = Polynomial({'X':R_Ratio(R_Polynomial([0, 1])),
      'Y':R_Ratio(R_Polynomial([2]))})
  print p
  print 'X =', Polynomial({'A':R_Ratio(R_Polynomial([0, 1])),
      'B':R_Ratio(R_Polynomial([2]))})
  print p.substitute('X', Polynomial({'A':R_Ratio(R_Polynomial([0, 1])),
      'B':R_Ratio(R_Polynomial([2]))}))
