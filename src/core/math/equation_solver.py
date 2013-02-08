"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from numpy import matrix
from numpy.linalg import solve

def solve_equations(equations):
  """
  TODO(mikemeko)
  """
  var_list = list(reduce(set.union, (set(var for coeff, var in eqn if var)
      for eqn in equations)))
  num_vars = len(var_list)
  var_index = {var_list[i]: i for i in xrange(num_vars)}
  A, b = [], []
  for equation in equations:
    coeffs, const = [0] * num_vars, 0
    for coeff, var in equation:
      if var:
        coeffs[var_index[var]] += coeff
      else:
        const += coeff
    A.append(coeffs)
    b.append([const])
  x = solve(matrix(A), matrix(b))
  return {var_list[i]: x[i, 0] for i in xrange(num_vars)}
