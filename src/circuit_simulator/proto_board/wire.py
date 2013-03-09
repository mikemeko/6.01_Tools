"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

class Wire:
  def __init__(self, loc_1, loc_2):
    self.loc_1 = loc_1
    self.loc_2 = loc_2
    self.r_1, self.c_1 = loc_1
    self.r_2, self.c_2 = loc_2
    self.row_support = min(self.r_1, self.r_2), max(self.r_1, self.r_2)
    self.column_support = min(self.c_1, self.c_2), max(self.c_1, self.c_2)
  def _supports_intersect(self, s_1, s_2):
    m_1, M_1 = s_1
    m_2, M_2 = s_2
    if m_1 == M_1:
      return m_2 <= m_1 <= M_2
    return m_1 <= m_2 <= M_1 or m_1 <= M_2 <= M_1
  def crosses(self, other):
    return (self._supports_intersect(self.row_support, other.row_support) and
        self._supports_intersect(self.column_support, other.column_support))
  def __hash__(self):
    return hash((self.loc_1, self.loc_2))
