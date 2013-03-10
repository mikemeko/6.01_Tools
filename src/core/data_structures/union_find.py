"""
Union find (disjoint set) data structure.
Taken from (but modified) http://code.activestate.com/recipes/215912/.
TODO(mikemeko): write my own?
"""

class UnionFind:
  """
  Union find data structure.
  """
  def __init__(self):
    self.num_weights = {}
    self.parent_pointers = {}
    self.num_to_objects = {}
    self.objects_to_num = {}
  def insert_objects(self, objects):
    """
    Insert a sequence of objects into the structure.  All must be Python
        hashable.
    """
    for obj in objects:
      self.find(obj);
  def find(self, obj):
    """
    Finds the root of the set that an object is in. If the object was not
      known, will make it known, and it becomes its own set. |obj| must
      be Python hashable.
    """
    if not obj in self.objects_to_num:
      obj_num = len(self.objects_to_num)
      self.num_weights[obj_num] = 1
      self.objects_to_num[obj] = obj_num
      self.num_to_objects[obj_num] = obj
      self.parent_pointers[obj_num] = obj_num
      return obj
    stk = [self.objects_to_num[obj]]
    par = self.parent_pointers[stk[-1]]
    while par != stk[-1]:
      stk.append(par)
      par = self.parent_pointers[par]
    for i in stk:
      self.parent_pointers[i] = par
    return self.num_to_objects[par]
  def union(self, object1, object2):
    """
    Combines the sets that contain the two objects given. Both objects must be
        Python hashable. If either or both objects are unknown, will make them
        known, and combine them.
    """
    o1p = self.find(object1)
    o2p = self.find(object2)
    if o1p != o2p:
      on1 = self.objects_to_num[o1p]
      on2 = self.objects_to_num[o2p]
      w1 = self.num_weights[on1]
      w2 = self.num_weights[on2]
      if w1 < w2:
        o1p, o2p, on1, on2, w1, w2 = o2p, o1p, on2, on1, w2, w1
      self.num_weights[on1] = w1+w2
      del self.num_weights[on2]
      self.parent_pointers[on2] = on1
  def disjoint_sets(self):
    """
    Returns a list of the disjoints sets.
    """
    sets = {}
    for i in xrange(len(self.objects_to_num)):
      sets[i] = set()
    for i in self.objects_to_num:
      sets[self.objects_to_num[self.find(i)]].add(i)
    out = []
    for i in sets.itervalues():
      if i:
        out.append(i)
    return out
