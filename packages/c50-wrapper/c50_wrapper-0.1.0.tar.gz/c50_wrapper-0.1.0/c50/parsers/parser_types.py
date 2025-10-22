# -*- coding: utf-8 -*-
"""
Module parser_types.py
------------------------
Base decision tree output parser;
C5.0 is a opensource decision tree algorithm written in `c` programming language.
For more information please refer to their (official website)[https://www.rulequest.com/see5-unix.html#USE].   
"""
import pyparsing as pp
from .base_parser import BaseParser


class StringType(BaseParser):
    """ Grammar for the String Type;"""
    __parse_element__ = (
        pp.Word(pp.alphanums + "_-!&()%$#@*?|/\\;").set_results_name('value')
    ).set_name('string')

    def parse_action(self, tokens: pp.ParseResults):
        t = tokens[0]
        t['value'] = f"'{t.value}'"
        t[0] = t.value
        # t[0] = f"'{t[0].value}'"

class FloatType(BaseParser):
    """ Grammar form the Float Type;"""
    __parse_element__ = pp.common.sci_real.set_results_name('value')



class IntType(BaseParser):
    """ Grammar for the Int Type;"""
    __parse_element__ = pp.Combine(
        pp.Optional(pp.Literal("-")) + 
        pp.common.integer
    ).set_results_name('value')


class SetType(BaseParser):
    """ Grammar for the set type"""
    
    def __init_elem__(self) -> pp.ParserElement:
        value = pp.Or([StringType(), FloatType(), IntType()])

        return pp.Combine(
            pp.Literal('{').set_parse_action(pp.replace_with("[")) + 
            value + 
            pp.ZeroOrMore(
                pp.Literal(',') + pp.ZeroOrMore(pp.Literal('|')).suppress() + value
            ) +
            pp.Literal('}').set_parse_action(pp.replace_with("]")),
            join_string=' ',
            adjacent=False
        ).set_results_name('value')

class BooleanType(BaseParser):
    """ Grammar for the Boolean Type"""
    __parse_element__ = pp.one_of(['True', 'False']).set_results_name("value")