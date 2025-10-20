from . import Function
from Hql.Exceptions import HqlExceptions as hqle
from Hql.Context import register_func, Context
from typing import Optional

@register_func('service')
class service(Function):
    def __init__(self, args:list, conf:Optional[dict]=None):
        Function.__init__(self, args, 1, -1)
        self.preprocess = True
        
    def eval(self, ctx:'Context', **kwargs):
        from Hql.Hac import Source
        
        src = kwargs.get('receiver', None)
        if not src:
            src = Source(ctx)
            src.product('*')
        assert isinstance(src, Source)

        for i in self.args:
            arg = i.eval(ctx, as_str=True)
            if not isinstance(arg, str):
                raise hqle.QueryException(f"Invalid argument type passed to function service {type(i)} eval'd to {type(arg)}")
            src.service(arg)

        return src
