from typing import TYPE_CHECKING, Union, Optional
import polars as pl

from .__proto__ import Expression
from Hql.Types.Hql import HqlTypes as hqlt

if TYPE_CHECKING:
    from Hql.Context import Context
    from Hql.Data import Series
    import datetime

class Literal(Expression):
    def __init__(self, hql_type:hqlt.HqlType) -> None:
        Expression.__init__(self)
        assert isinstance(hql_type, hqlt.HqlType)
        self.literal = True
        self.hql_type = hql_type

    def make_series(self) -> 'Series':
        from Hql.Data import Series
        series = Series(pl.Series([self.value]), self.hql_type)
        return series.cast()

    def decompile(self, ctx: 'Context') -> str:
        return str(self.value)

class TypeExpression(Literal):
    def __init__(self, hql_type:str):
        Literal.__init__(self, hqlt.HqlType(pl.String()))
        self.hql_type = hql_type

    def decompile(self, ctx: 'Context') -> str:
        return self.hql_type
        
    def eval(self, ctx:'Context', **kwargs):
        return hqlt.from_name(self.hql_type)()

# A string literal
# literally a string
# we strip off quotes when constructing as the parser doesn't remove them for us.
class StringLiteral(Literal):
    def __init__(self, value:str, lquote:str="'", rquote:str="'"):
        Literal.__init__(self, hqlt.string())

        self.lquote = lquote
        self.rquote = rquote
        self.value = value
    
    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value
        }

    def decompile(self, ctx: 'Context') -> str:
        return self.lquote + self.value + self.rquote
        
    def eval(self, ctx:'Context', **kwargs):
        value = self.value
        if '@' not in self.lquote:
            value = value.encode('utf-8').decode('unicode_escape')

        # if 'h' in self.lquote.lower():
        #     value = bytes.fromhex(value).decode('utf-8')

        if kwargs.get('as_pl', False):
            return pl.lit(value)
        return value

class MultiString(Literal):
    def __init__(self, strlits:Optional[list[StringLiteral]]=None):
        from Hql.Context import Context
        from Hql.Data import Data
        Literal.__init__(self, hqlt.string())
        self.strlits = strlits if strlits else []
        
        running = ''
        for i in self.strlits:
            running += i.eval(Context(Data()))
        self.value = running
    
    def to_dict(self) -> Union[None, dict]:
        return {
            'type': self.type,
            'value': [x.to_dict() for x in self.strlits]
        }

    def decompile(self, ctx: 'Context') -> str:
        return ' '.join([x.decompile(ctx) for x in self.strlits])

    def eval(self, ctx:'Context', **kwargs):
        if kwargs.get('as_pl', False):
            return pl.lit(self.value)
        return self.value

# Integer
# An integer
# Z
# unreal, not real
class Integer(Literal):
    def __init__(self, value:Union[str, int]):
        Literal.__init__(self, hqlt.int())
        self.value = int(value)
    
    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value
        }

    def decompile(self, ctx: 'Context') -> str:
        return str(self.value)
        
    def eval(self, ctx:'Context', **kwargs):
        if kwargs.get('as_pl', False):
            return pl.lit(self.value)
        return self.value

class IP4(Literal):
    def __init__(self, value:int):
        Literal.__init__(self, hqlt.ip4())
        self.value = value
        
    def to_dict(self):
        s = pl.Series([self.value])
        human = hqlt.ip4().human(s)
        
        return {
            'type': self.type,
            'value': human
        }

    def decompile(self, ctx: 'Context') -> str:
        # just stealing how I did this for the ip4 type
        d = 0xFF
        c = d << 8
        b = c << 8
        a = b << 8
        i = self.value

        return f'{(i & a) >> 24}.{(i & b) >> 16}.{(i & c) >> 8}.{i & d}'
        
    def eval(self, ctx:'Context', **kwargs):
        return self.value

class Float(Literal):
    def __init__(self, value:Union[str, float]):
        Literal.__init__(self, hqlt.float())
        self.value = float(value)
        
    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value
        }

    def decompile(self, ctx: 'Context') -> str:
        return str(self.value)
        
    def eval(self, ctx:'Context', **kwargs):
        if kwargs.get('as_pl', False):
            return pl.lit(self.value)
        return self.value

class Bool(Literal):
    def __init__(self, value:str):
        Literal.__init__(self, hqlt.bool())
        self.value = value.lower() == 'true'
        
    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value
        }

    def decompile(self, ctx: 'Context') -> str:
        return str(self.value)
        
    def eval(self, ctx:'Context', **kwargs):
        if kwargs.get('as_pl', False):
            return pl.lit(self.value)
        return self.value

class Multivalue(Literal):
    def __init__(self, value:list[Literal]) -> None:
        self.super_type = hqlt.resolve_conflict([x.hql_type for x in value])
        Literal.__init__(self, hqlt.multivalue(type(self.super_type)))

        series = pl.Series([x.value for x in value])
        self.value = self.hql_type.cast(series)

    def decompile(self, ctx: 'Context') -> str:
        dec = [x.decompile(ctx) for x in self.value]
        return 'make_mv(' + ', '.join(dec) + ')'

class Datetime(Literal):
    def __init__(self, value:Union[StringLiteral, 'datetime.datetime']) -> None:
        from dateutil import parser
        Literal.__init__(self, hqlt.datetime())

        if isinstance(value, StringLiteral):
            self.value:'datetime.datetime' = parser.parse(value.value)
        else:
            self.value = value

    def decompile(self, ctx: 'Context') -> str:
        inner = StringLiteral(self.value.isoformat())
        return 'datetime(' + inner.decompile(ctx) + ')'

