# -*- coding: utf-8 -*-
"""
Module tree_parser.py
------------------------
A parser for the decision tree text output;
C5.0 is a opensource decision tree algorithm written in `c` programming language.
For more information please refer to their (official website)[https://www.rulequest.com/see5-unix.html#USE].   
"""
import pyparsing as pp
from .base_parser import BaseParser
from .parser_types import StringType, IntType, FloatType, SetType, BooleanType
from .common_parsers import FeatureName, ComparisonOperator


class RuleNumber(BaseParser):
    __parse_element__ = (
        pp.CaselessLiteral('Rule') + pp.Word(pp.nums) + pp.Literal(":").suppress()
    )

    def parse_action(self, tokens: pp.ParseResults):
        t = tokens[0]
        t['name'] = t[0]
        t['number'] = t[1]
       

class Statistics(BaseParser):

    def __init_elem__(self):
        nm = pp.Or(
            [
                IntType(),
                FloatType(),
            ]
        )
        
        return (
            pp.Literal('(').suppress() +
            # n / m 
            nm + pp.Opt('/' + nm) +
            pp.Literal(',').suppress() +
            pp.CaselessLiteral('lift').suppress() +
            nm +
            pp.Literal(')').suppress()
        )
    
    def parse_action(self, tokens: pp.ParseResults):
        t = tokens[0]
        t['n'] = t[0].value
        if len(t) > 2:
            t['m'] = t[2].value
            t['lift'] = t[3].value
        else:
            t['m'] = None
            t['lift'] = t[1].value


class Prediction(BaseParser):
    
    def __init__(self, labels):
        self.labels = labels
        super(Prediction, self).__init__()

    def __init_elem__(self):
        nm = pp.Or(
            [
                IntType(),
                FloatType(),
            ]
        )
        
        return (
            pp.Literal('->').suppress() +
            pp.CaselessLiteral('class').suppress() +
            pp.one_of([str(l) for l in self.labels], caseless=True) + 
            pp.Literal('[').suppress() + FloatType() + pp.Literal(']').suppress()
        ).set_results_name('prediction')


    def parse_action(self, tokens:pp.ParseResults):
        t = tokens[0]
        label = t[0]
        if isinstance(self.labels[0], str):
            label = f"'{label}'"
        t['label'] = label
        t['confidence'] = t[1].value

class Condition(BaseParser):

    def __init__(self, features):
        self.features = features
        super(Condition, self).__init__()

    def __init_elem__(self):
        value = pp.Or(
            [
                IntType(),
                FloatType(),
                SetType(),
                BooleanType(),
                StringType(),
            ]
        )
        return (
            FeatureName(self.features) + 
            ComparisonOperator() +
            value
        )
    
    def parse_action(self, tokens:pp.ParseResults):
        t = tokens[0]
        t['feature_name'] = t[0].feature_name
        t['operator'] = t[1].comparison_operator
        t['value'] = t[2].value
        

class Rule(BaseParser):

    def __init__(self, features, labels):
        self.features = features
        self.labels = labels
        
        super(Rule, self).__init__()

    def __init_elem__(self):
        return (
            RuleNumber() + 
            Statistics() + 
            pp.Group(pp.OneOrMore(Condition(self.features))) + 
            Prediction(self.labels)
        )
    
    def parse_action(self, tokens: pp.ParseResults):
        t = tokens[0]
        t['rule_number'] = t[0].number
        t['conditions'] = t[2]
        t['confidence'] = t[3].confidence
        t['label'] = t[3].label
    

class RuleSet(BaseParser):

    def __init__(self, features, labels):
        self.features = features
        self.labels = labels
        
        super(RuleSet, self).__init__()

    def __init_elem__(self):
        return (
            pp.Group(
                pp.ZeroOrMore(
                    Rule(self.features, self.labels),
                )
            ) + 
            # pp.CaselessLiteral("Default class:").suppress() +
            pp.Literal("Default class:").suppress() +
            pp.one_of([str(l) for l in self.labels], caseless=True)
        )
    
    def parse_action(self, tokens: pp.ParseResults):
        t = tokens[0]
        t['rules'] = t[0]
        t['default'] = t[1]
        t['labels'] = self.labels
