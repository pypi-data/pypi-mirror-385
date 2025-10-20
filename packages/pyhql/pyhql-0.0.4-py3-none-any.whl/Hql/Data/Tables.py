from typing import TYPE_CHECKING, Union

import polars as pl
from polars.dataframe.group_by import GroupBy

from .Schema import Schema
from .Series import Series
from Hql.Exceptions import HqlExceptions as hqle
from Hql.PolarsTools import pltools
from Hql.Types.Hql import HqlTypes as hqlt

import logging

'''
Table for a structure of data, includes schema definition.
Mimics a pl.DataFrame
'''
class Table():
    def __init__(
            self,
            df:Union[pl.DataFrame, None]=None,
            series:Union[Series, None]=None,
            init_data:Union[list[dict], None]=None,
            schema:Union[Schema, dict, None]=None,
            name:Union[str, None]=None
        ):
        
        if isinstance(df, pl.DataFrame):
            self.df = df
        else:
            self.df = pl.DataFrame()
            
        if isinstance(schema, dict):
            schema = Schema(schema=schema)
        
        self.name = name if name else ''
        self.series = None
        self.schema = Schema() # safe default
       
        # rely on self.agg being None for the existence of an aggregation
        self.agg:Union[None, GroupBy] = None
        self.agg_paths:list[list[str]] = []
        self.agg_schema:Schema = Schema()

        if series:
            self.series = series

        elif init_data and not schema:
            self.schema = Schema(init_data)
            init_data = self.schema.adjust_mv(init_data)
            pl_schema = self.schema.gen_pl_schema()
            self.df = pl.from_dicts(init_data, schema=pl_schema)
        
        elif init_data and schema:
            self.schema = schema
            self.df = pl.from_dicts(init_data, schema=schema.convert_schema(target='polars'))
        
        elif not self.df.is_empty() and schema:
            self.schema = schema
            self.df = schema.apply(self.df)

        elif not self.df.is_empty() and not schema:
            self.schema = Schema(data=self.df)

        elif schema:
            logging.warning('Schema defined in table without data')
            self.schema = schema

        else:
            self.schema = Schema()

    def __len__(self):
        if hasattr(self.df, '__len__'):
            return len(self.df)
        return 0

    def to_dicts(self):
        human = self.schema.present_complex(self.df)
        return human.to_dicts()

    def get_schema(self):
        return self.schema.to_dict()

    def set_schema(self, schema:Schema):
        self.df = schema.apply(self.df)
        self.schema = schema

    def get_type(self, path:list[str]):
        if self.schema:
            return self.schema.get_type(path)
        return None

    def drop(self, path:list[str], df:Union[pl.DataFrame, None]=None, idx:int=0) -> Union[pl.DataFrame, "Table"]:
        if isinstance(df, type(None)) and idx != 0:
            raise hqle.CompilerException('Logic error? Would reinit df with a non-zero index.')

        if isinstance(df, type(None)):
            self.schema.drop(path)
            assert isinstance(self.df, pl.DataFrame)
            df = self.df
        assert not isinstance(df, type(None))

        new = {}
        for col in df:
            if col.name == path[idx]:
                if idx == len(path) - 1:
                    # silent drop
                    continue
                
                if col.dtype == pl.Struct:
                    rec = self.drop(path, df=pl.DataFrame(col).unnest(col.name), idx=idx+1)
                    
                    if not isinstance(rec, pl.DataFrame):
                        raise hqle.CompilerException('Logic error? Final recursion step hit before end.')

                    if not rec.is_empty():
                        new[col.name] = rec.to_struct()
                
            # Not dropping
            else:
                new[col.name] = col
        
        # end of recursion
        if idx == 0:
            self.df = pl.DataFrame(new)
            return self
            
        return pl.DataFrame(new)
    
    def drop_many(self, paths:list[list[str]]):
        for path in paths:
            self.drop(path)
        return self
        
    '''
    Truncates the dataset to a given amount
    '''
    def truncate(self, amount:int):
        self.df = self.df[:amount]

    '''
    Runs a polars filter on the table
    '''
    def filter(self, expr:pl.Expr):
        try:
            self.df = self.df.filter(expr)
        except pl.exceptions.ColumnNotFoundError as e:
            raise hqle.UnreferencedFieldException(e.args[0])
        
    def get_value(self, path:list[str]):
        return pltools.get_element_value(self.df, path)

    @staticmethod
    def merge_rows(tables:list['Table']):
        if not tables:
            return Table()
        
        # Quick short circuit
        if len(tables) == 1:
            return tables[0]
        
        name = tables[0].name
        
        schemas = []
        for table in tables:
            schemas.append(table.schema)
        schema = Schema.merge(schemas).schema
        
        # generate col groups
        longest_len = 0
        col_groups = dict()
        for table in tables:
            # skip empty dataframes
            if isinstance(table.df, type(None)) or table.df.is_empty():
                continue

            for col in table.df:
                longest_len = len(col) if len(col) > longest_len else longest_len
                if col.name not in col_groups:
                    col_groups[col.name] = []
                col_groups[col.name].append(col)

        new = dict()
        for key in col_groups:
            for col in col_groups[key]:
                if longest_len > len(col):
                    if len(col) == 1:
                        col = pl.Series([col[0]] * longest_len)
                    else:
                        pad = longest_len - len(col)
                        col = col.extend(pl.Series([None] * pad))

                if key not in new:
                    new[key] = col
                    continue
                
                # Canon conflict
                if not isinstance(new[key], list) and new[key].dtype == pl.Struct and col.dtype == pl.Struct:
                    l = Table(df=new[key].struct.unnest(), name=name)
                    r = Table(df=col.struct.unnest(), name=name)
                    
                    new[key] = Table.merge_rows([l, r]).df.to_struct()
                    continue

                if not isinstance(schema[key], hqlt.multivalue):
                    schema[key] = hqlt.multivalue(schema[key])
                    new[key] = [new[key], col]
                else:
                    new[key].append(col)                
                
        df = pl.DataFrame(new)
        schema = Schema(schema=schema)
                
        return Table(df=df, schema=schema, name=name)

    @staticmethod
    def merge(tables:list["Table"], merge_rows=True):
        from Hql.Types.Compiler import CompilerType

        if merge_rows:
            return Table.merge_rows(tables)

        if not tables:
            return Table()
        
        # Quick short circuit
        if len(tables) == 1:
            return tables[0]

        groups = dict()
        for table in tables:
            if table.name in groups:
                groups[table.name].append(table)
            else:
                groups[table.name] = [table]

        name = tables[0].name
        
        schemas = []
        for table in tables:
            schemas.append(table.schema)
        schema = Schema.merge(schemas).schema

        # Makes an assumption that the above merge converted field names accurately
        # in the case of a conflict, e.g. they get split into types.
        new = []
        for table in tables:
            cur = table.df
            curs = table.schema.schema
            for key in curs:
                if isinstance(curs[key], CompilerType):
                    dup_key = f'{key}_{curs[key].name}'
                else:
                    dup_key = f'{key}_object'

                # Linter hates this one simple trick!
                if dup_key in schema:
                    cur = cur.rename({key: dup_key})
            new.append(cur)
        
        df = pl.concat(new, how='diagonal')
        return Table(df=df, schema=schema, name=name)

    '''
    Takes in a list of path parts
    client.ip.src
    ['client', 'ip', 'src']
    Returns a Table with just the data of that path
    If not found then it returns an empty table with the parent name.
    '''
    def select(self, field:list[str]):
        if not self.assert_field(field):
            return Table(name=self.name)
        
        df = pltools.get_element(self.df, field)
        schema = self.schema.select(field)

        return Table(df=df, schema=schema, name=self.name)

    def unnest(self, field:list[str]) -> Union[Series, 'Table']:
        if not isinstance(self.schema, Schema):
            raise hqle.CompilerException('Attempting to unnest an uninitalized table object with a None Schema')

        if not self.assert_field(field):
            raise hqle.QueryException(f"Could not unnest field {'.'.join(field)} from table {self.name}")
        
        df = self.get_value(field)
        dtype = self.schema.unnest(field).schema
        
        if isinstance(df, pl.Series):
            if not isinstance(dtype, hqlt.HqlType):
                raise hqle.CompilerException('Attempting to initialize a series with a non-hqlt type')

            return Series(df, stype=dtype)            
            
        else:
            schema = Schema(schema=dtype)
            return Table(df=df, schema=schema, name=self.name)

    '''
    Returns the deep stripped value of a DataFrame with a single value.
    So {'destination': {'ip': hqlt.ip4}} would just return hqlt.ip4.
    A more complex case is:

    {
        'destination': {
            'ip': hqlt.ip4,
            'port': hqlt.short
        }
    }

    Which would just return:

    {
        'ip': hqlt.ip4,
        'port': hqlt.short
    }

    The idea here is if you want to extract the value of a function, this does it.
    '''
    def strip(self):
        cur = self.df
        path = []
        while isinstance(cur, pl.DataFrame) and len(cur.columns) == 1:
            key = cur.columns[0]
            cur = pltools.get_element_value(cur, [key])
            path.append(key)
        
        # Using this instead of strip to ensure we're in sync
        schema = self.schema.unnest(path).schema

        if isinstance(cur, pl.Series):
            if isinstance(schema, dict):
                raise hqle.CompilerException('Schema generated for series is a dict!')

            series = Series(cur, stype=schema)
            return Table(series=series, name=self.name)
            
        if not isinstance(schema, dict):
            raise hqle.CompilerException('Schema generated for a dataframe is a non-dict!')

        return Table(df=cur, schema=schema, name=self.name)

    def rename(self, src:list[str], dest:list[str]):
        if not self.assert_field(src):
            raise hqle.QueryException('Attempting to rename a non-existing field')
        
        #if self.assert_field(dest):
        #    raise hqle.QueryException('Attempting to rename field into an existing field')
        
        value = self.pop(src).unnest(src)
        if isinstance(value, Series):
            schema = value.type
            value = value.series

        else:
            schema = value.schema.schema
            value = value.df

        if not isinstance(schema, (dict, hqlt.HqlType)):
            raise hqle.CompilerException(f'Attempting to rename with schema of type {type(schema)}')
        
        self.insert(dest, value, schema)
    
    # Inserts a piece of data at a given name
    def insert(
            self,
            name:list[str],
            value:Union[pl.DataFrame, pl.Series],
            vtype:Union[hqlt.HqlType, dict],
            cur_df:Union[None, pl.DataFrame]=None,
            idx:int=0
        ) -> pl.DataFrame:
        if isinstance(cur_df, type(None)):
            cur_df = self.df
            
        split = name[idx]
                
        # Endpoint
        if idx == len(name) - 1:
            # Find a unique name
            if split in cur_df:
                i = 0
                while f'{split}_{i}' in cur_df:
                    i += 1
                split = f'{split}_{i}'
                name[idx] = split
                        
            self.schema.set(name, vtype)
            new = pl.DataFrame({name[-1]: value})
        
        # Not the end, but we're now free to do whatever we want
        elif split not in cur_df:
            recurse = self.insert(name, value, vtype, cur_df=pl.DataFrame(), idx=idx + 1)
            new = pl.DataFrame({split: recurse.to_struct()})
        
        # Recurse up a nested object
        elif cur_df[split].dtype == pl.Struct:        
            recurse = self.insert(name, value, vtype, cur_df=cur_df.select(split).unnest(split), idx=idx + 1)
            cur_df = cur_df.remove(split)
            new = pl.DataFrame({split: recurse})
        
        # Conflict, a base type is where we're trying to put a struct
        else:
            i = 0
            while f'{split}_{i}' in cur_df:
                # Merging case
                if cur_df[f'{split}_{i}'].dtype == pl.Struct:
                    break
                i += 1
            split = f'{split}_{i}'
            name[idx] = split
         
            if cur_df[split].dtype == pl.Struct:
                recurse = self.insert(name, value, vtype, cur_df=cur_df.select(split).unnest(split), idx=idx + 1)
            else:
                recurse = self.insert(name, value, vtype, cur_df=pl.DataFrame(), idx=idx + 1)
            
            new = pl.DataFrame({split: recurse})
        
        new = pl.concat([new, cur_df], how='horizontal')
        
        if idx == 0:
            self.df = new
        
        return new

    def remove(self, name:list[str], cur_df:Union[None, pl.DataFrame]=None, idx:int=0):
        if isinstance(cur_df, type(None)):
            cur_df = self.df
            
        if idx == 0 and not self.assert_field(name):
            return cur_df
            
        split = name[idx]
        mask = cur_df.remove(split)
        
        if idx == len(name) - 1:
            return mask
        
        if cur_df[split].dtype == pl.Struct:
            recurse = self.remove(name, cur_df=cur_df.unnest(split), idx=idx + 1)
            
            if not recurse.is_empty():
                recurse = pl.DataFrame({split: recurse})
                merged = pl.concat([mask, recurse], how='horizontal')
            else:
                merged = mask
        else:
            merged = mask

        return merged
            
    def pop(self, name:list[str]):
        if not self.assert_field(name):
            raise hqle.QueryException('Attempting to pop a non-existing field')
        
        # Schema is tracked through the select
        value = self.select(name)
        self.schema.pop(name)
        self.remove(name)
        
        return value
    
    # Asserts by checking against schema
    # Schema should always be sync'd with the table data
    def assert_field(self, field:list[str]):
        return self.schema.assert_field(field)
    
    def cast_in_place(self, path:list[str], cast_type:hqlt.HqlType):
        if not self.assert_field(path):
            return None
        
        self.schema.set(path, cast_type)
        self.df = self.schema.apply(self.df)

        return self
    
    def join(self, right:"Table", on:str, kind:str):
        schema = self.schema.join(right.schema, on, kind)

        if kind == 'inner':
            df = self.df.join(right.df, on=on, how='inner')
        
        elif kind == 'leftsemi':
            df = self.df.join(right.df, on=on, how='semi')

        elif kind == 'rightsemi':
            df = right.df.join(self.df, on=on, how='semi')

        elif kind == 'leftouter':
            df = self.df.join(right.df, on=on, how='left')

        elif kind == 'rightouter':
            df = right.df.join(self.df, on=on, how='left')

        elif kind == 'fullouter':
            df = self.df.join(right.df, on=on, how='full')

        elif kind == 'leftanti':
            df = self.df.join(right.df, on=on, how='anti')

        elif kind == 'rightanti':
            df = right.df.join(right.df, on=on, how='anti')

        elif kind == 'innerunique':
            left = self.df.unique(subset=[on])
            df = left.join(right.df, on=on, how='inner')

        else:
            raise hqle.QueryException(f'Invalid join kind {kind} used')
        
        return Table(df=df, schema=schema, name=self.name)

    '''
    Sorts by expression, if they exist
    '''
    def sort(self, exprs:list[pl.Expr], orders:Union[None, list[bool]]=None, nulls:Union[None, list[bool]]=None):
        orders = [True for x in exprs] if orders is None else orders
        nulls = [x for x in orders] if nulls is None else nulls
        exprs = exprs if isinstance(exprs, list) else [exprs]
        
        if len(orders) < len(exprs):
            logging.warning('Passing incomplete list of orders to table sort, defaulting to desc for missing values')
            for i in range(len(exprs) - len(orders)):
                orders.append(True)
                
        if len(nulls) < len(exprs):
            logging.warning('Passing incomplete list of nulls to table sort, defaulting to last for missing values')
            for i in range(len(exprs) - len(nulls)):
                nulls.append(True)
        
        texprs = []
        torders = []
        tnulls = []
        for idx, expr in enumerate(exprs):
            try:
                self.df.select(expr)
                texprs.append(exprs[idx])
                torders.append(orders[idx])
                tnulls.append(nulls[idx])
            except:
                continue

        # No applicable sort
        if not len(texprs):
            return self
        
        self.df = self.df.sort(by=texprs, descending=torders, nulls_last=tnulls)
        return self
