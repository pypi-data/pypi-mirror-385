# -*- coding: utf-8 -*-
"""
Module common_parsers.py
------------------------
A parser for the decision tree text output;
C5.0 is a opensource decision tree algorithm written in `c` programming language.
For more information please refer to their (official website)[https://www.rulequest.com/see5-unix.html#USE].   
"""
import pyparsing as pp
from .base_parser import BaseParser
from .parser_types import StringType, IntType, FloatType, SetType, BooleanType


class FeatureName(BaseParser):

    def __init__(self, features):
        self.features = features
        super(FeatureName, self).__init__()

    def __init_elem__(self):
        return (
            pp.one_of(
                list(self.features),
                caseless=True
            )
        ).set_results_name("feature_name")
    

class ComparisonOperator(BaseParser):
    __parse_element__ = (
        pp.one_of(
            ['>', '<', '<=', '>=', '=', 'in', '<>', '!='],
            caseless=True
        ).set_results_name('comparison_operator')
    )

    def parse_action(self, tokens:pp.ParseResults):
        t = tokens[0]

        if t[0] == '<>':
            t[0] = '!='
            t['comparison_operator'] = '!='

        elif t[0] == '=':
            t[0] = '=='
            t['comparison_operator'] = "=="
