from . import Function
from Hql.Context import register_func, Context
from Hql.Data import Data
from typing import Optional

@register_func('bincount')
class bincount(Function):
    def __init__(self, args:list, conf:Optional[dict]=None):
        # allows 1 to infinity args
        super().__init__(args, 1, 1)
        
    def eval(self, ctx:'Context', **kwargs):
        return Data()
