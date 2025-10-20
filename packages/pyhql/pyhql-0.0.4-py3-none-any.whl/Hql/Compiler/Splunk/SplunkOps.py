from Hql.Expressions import Expression
from Hql.Operators import Operator

from typing import Optional, Union

class SplunkOp():
    def __init__(self):
        self.pipes = []
        self.post_ops:list[Operator] = []
        self.remap = dict()

    def compile(self):
        ...

class Spath(SplunkOp):
    def __init__(self, lh:Expression, rh:Expression):
        SplunkOp.__init__(self)
        self.lh = lh
        self.rh = rh
