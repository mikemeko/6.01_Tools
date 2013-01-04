"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

class R_Polynomial:
  """
  Representation for polynomials in R.
  """
  def __init__(self, coeffs):
    """
    |coeffs|: a list of the coefficients of powers of R.
        For example, 2R**2 + 1 has coefficients [1, 0, 2].
    """
    self.coeffs = coeffs
    self.degree = len(coeffs) - 1
  def coeff(self, exp):
    """
    Returns the coefficient of the R**exp term.
    """
    return self.coeffs[exp] if exp <= self.degree else 0
  def scalar_mult(self, const):
    """
    Returns a new scaled polynomial.
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
    sum_coeffs = []
    for exp in xrange(max(self.degree, other.degree) + 1):
      sum_coeffs.append(self.coeff(exp) + other.coeff(exp))
    return R_Polynomial(sum_coeffs)
  def _prettify(self, coeff, exp):
    if exp == 0:
      return str(coeff)
    elif exp == 1:
      return '%dR' % coeff
    else:
      return '%dR**%d' % (coeff, exp)
  def __str__(self):
    return ' + '.join(self._prettify(self.coeff(exp), exp)
        for exp in xrange(self.degree + 1) if self.coeff(exp) is not 0)

class Polynomial:
  """
  TODO(mikemeko)
  """
  def __init__(self, data):
    """
    |data|: a dictionary mapping variable names to their coefficients.
        For example, RX + 2Y is represented by {'X':R_Polynomial([0, 1]),
        'Y':'[2]'}.
    """
    for var in data:
      assert isinstance(var, str), 'variables must be strings'
      assert isinstance(data[var], R_Polynomial), 'coeff must be R_Polynomials'
    self.data = data
  def coeff(self, var):
    """
    Returns the coefficient for the given variable.
    """
    assert var in self.data, 'var must be in Polynomial'
    return self.data[var]
  def scalar_mult(self, const):
    """
    Returns a new scaled polynomial.
    """
    new_data = {}
    for var in self.data:
      new_data[var] = self.data[var].scalar_mult(const)
    return Polynomial(new_data)
  def shift(self):
    """
    Returns this polynomial multiplied by R.
    """
    new_data = {}
    for var in self.data:
      new_data[var] = self.data[var].shift()
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
  def __sub__(self, other):
    assert isinstance(other, Polynomial), 'other must be a Polynomial'
    return self + other.scalar_mult(-1)
  def __str__(self):
    return ' + '.join('(%s)%s' % tuple(map(str, reversed(item)))
        for item in self.data.items())

if __name__ == '__main__':
  r_poly_1 = R_Polynomial([1,0,2])
  r_poly_2 = R_Polynomial([2,1])
  print r_poly_1.scalar_mult(2) + r_poly_2
  poly_1 = Polynomial({'X':R_Polynomial([1, 1]), 'Y':R_Polynomial([2])})
  poly_2 = Polynomial({'X':R_Polynomial([1]), 'A':R_Polynomial([1])})
  print poly_1
  print poly_2
  print poly_1 + poly_2
  print poly_1.scalar_mult(2)
  print poly_1 - poly_2
  print poly_2.shift()
