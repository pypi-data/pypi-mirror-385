# -*- coding: utf-8 -*-
"""
Module names_file_builder.py
--------------------------------
A builder class for the Names Files.
An essential file for the `C5.0` is the names file *(e.g. hypothyroid.names)* 
that describes the attributes and target classes. 
There are two important subgroups of attributes:
 - The value of an explicitly-defined attribute is given directly in the data in one of several forms. 
 A **discrete** attribute has a value drawn from a set of nominal values, 
 a **continuous** attribute has a numeric value, 
 a **date** attribute holds a calendar date, 
 a **time** attribute holds a clock time, 
 a **timestamp** attribute holds a date and time, 
 and a **label** attribute serves only to identify a particular case (the targets).
 - The value of an **implicitly-defined** attribute is specified by a formula.
 **Currently, this builder do not work with such attribute definition.**

For more information please refer to the (C5.0)[https://www.rulequest.com/see5-unix.html#USE] official website.   
"""
import numpy as np
import pandas as pd


class NamesFileBuilder(object):
    
    def __init__(self):

        self.BUILDER_TYPE_MAP = {
            'category': self._build_categorical_entry,
            'number': self._build_numeric_entry,
            'bool': self._build_bool_entry,
            'datetime64[ns]': self._build_datetime_entry,
        }
        self._result = ""
        self.features_order = list()
    
    def save(self, path: str):
        with open(file=path, mode='wt', encoding='utf-8') as f:
            f.write(self._result)
        
    def build_and_save(self, path: str, dataset: pd.DataFrame, target_name: str):
        self.build(dataset=dataset, target_name=target_name)
        self.save(path=path)
    
    def build(self, dataset: pd.DataFrame, target_name: str):
        rows = list()
        rows.append(
            f'{target_name}.\n'
        )
        
        for name, dtype in dataset.dtypes.to_dict().items():
            # saving the attr order
            self.features_order.append(name)

            dtype_name = str(dtype)
            if dtype_name == 'object':
                continue
            
            if 'int' in dtype_name or 'float' in dtype_name:
                dtype_name = 'number'

            rows.append(
                self.BUILDER_TYPE_MAP[dtype_name](dtype, name)
            )
        
        self._result = '\n'.join(rows)
        
        return self._result
        
    def _build_categorical_entry(self, dtype: pd.CategoricalDtype, name: str):
        categories = ', '.join(dtype.categories.values)
        return f'{name}:     {categories}.'
    
    def _build_numeric_entry(self, dtype: np.dtype, name:str):
        return f'{name}:     continuous.'
    
    def _build_bool_entry(self, dtype: np.dtype, name:str):
        return f'{name}:     True, False.'
    
    def _build_datetime_entry(self, dtype: np.dtype, name:str):
        if name.startswith('time_'):
            return f'{name}:     time.'
        
        elif name.startswith('dt_') or name.startswith('date_'):
            return f'{name}:     date.'
        
        elif name.startswith('datetime_'):
            return f'{name}:     timestamp.'
