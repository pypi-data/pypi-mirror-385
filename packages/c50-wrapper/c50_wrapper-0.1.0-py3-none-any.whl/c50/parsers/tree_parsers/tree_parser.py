# -*- coding: utf-8 -*-
"""
Module tree_parser.py
------------------------
A parser for the decision tree text output;
C5.0 is a opensource decision tree algorithm written in `c` programming language.
For more information please refer to their (official website)[https://www.rulequest.com/see5-unix.html#USE].   
"""
import pyparsing as pp
from ..base_parser import BaseParser
from ..parser_types import StringType, IntType, FloatType, SetType, BooleanType
from ..common_parsers import FeatureName, ComparisonOperator


class NodeLevelMarks(BaseParser):
    __parse_element__ = pp.ZeroOrMore(
        pp.Literal('|')
    ).set_results_name('node_level_marks')


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
            pp.one_of([str(l) for l in self.labels], caseless=True) + 
            pp.Literal('(').suppress() + nm + pp.Opt('/' + nm) + pp.Literal(')').suppress()
        ).set_results_name('prediction')


    def parse_action(self, tokens:pp.ParseResults):
        t = tokens[0]
        label = t[0]
        if isinstance(self.labels[0], str):
            label = f"'{label}'"
        
        t['label'] = label
        t['n'] = float(t[1].value)
        # print('>>>>>>', t[1].value, type(t[1].value))
        # print('>>>>>>222', t, t.as_dict())
        if len(t) > 2:
            # print('>>>>>33>', t[3].value, type(t[3].value))
            t['m'] = float(t[3].value)
        else:
            t['m'] = 0
        t['confidence'] = (t.n - t.m + 1)/ (t.n + 2) 


class SubTreeCall(BaseParser):

    def __init_elem__(self):
        return pp.ungroup(
            pp.Literal('[').suppress() +
            pp.Combine(
                pp.CaselessLiteral('S') +
                IntType()
            ) +
            pp.Literal(']').suppress()
        ).set_results_name('subtree_name')         

class TreeNode(BaseParser):

    def __init__(self, features, labels):
        self.features = features
        self.labels = labels
        super(TreeNode, self).__init__()

    def __init_elem__(self):
        value = pp.Or(
            [
                IntType(),
                FloatType(),
                BooleanType(),
                SetType(),
                StringType(),
            ]
        )
        return (
            NodeLevelMarks() + 
            FeatureName(self.features) + 
            ComparisonOperator() +
            value + 
            ~pp.White() + pp.Literal(":").suppress() +
            pp.Opt(
                pp.Or(
                    [ Prediction(self.labels), SubTreeCall() ]
                )
            )
        )
    
    def parse_action(self, tokens:pp.ParseResults):
        t = tokens[0]
        # number of '|' (level marks)
        t['node_level'] = len(t[0].node_level_marks)
        t['feature_name'] = t[1].feature_name
        t['operator'] = t[2].comparison_operator
        t['value'] = t[3].value
        # if node has a prediction element
        if len(t) == 5:
            if t[4].dtype == 'Prediction':
                t['has_subtree_call'] = False
                t['subtree_name'] = None
                t['is_terminal'] = True
                t['label'] = t[4].label
                t['confidence'] = t[4].confidence
            
            elif t[4].dtype == 'SubTreeCall':
                t['has_subtree_call'] = True
                t['subtree_name'] = t[4].subtree_name
                t['is_terminal'] = False
                t['label'] = None
                t['confidence'] =None

        else:
            t['has_subtree_call'] = False
            t['subtree_name'] = None
            t['is_terminal'] = False
            t['label'] = None
            t['confidence'] =None


class Tree(BaseParser):

    def __init__(self, features, labels):
        self.features = features
        self.labels = labels
        self.rules = list()
        self.r_labels = list()
        self.r_confidences = list()
        super(Tree, self).__init__()

    def __init_elem__(self):
        return (
            pp.Group(pp.OneOrMore(
                TreeNode(self.features, self.labels)
            )).set_results_name('nodes') +
            pp.Group(pp.ZeroOrMore(
                SubTree(self.features, self.labels)
            )).set_results_name('sub_trees')
        )
    
    def parse_action(self, tokens: pp.ParseResults):
        t = tokens[0]
        t['nodes'] = t[0]
        t['sub_trees'] = t[1]
        for tree in t['sub_trees'].copy():
            t['sub_trees'][tree.name] = tree

    def parse_rules(self, nodes, sub_trees, rule=''):
        current = -1
        if len(nodes) == 0:
            return self.rules, self.r_labels
        
        while current < (len(nodes) -1):
            current = self._parse_rules(nodes, sub_trees, current + 1, rule)
        
        return self.rules, self.r_labels, self.r_confidences

    def _parse_rules(self, nodes, sub_trees, current, rule):
        # if current > 0 and nodes[current].node_level <=
        if len(rule) > 0:
            rule += f" & `{nodes[current].feature_name}` {nodes[current].operator} {nodes[current].value}"
        else:
            rule += f"`{nodes[current].feature_name}` {nodes[current].operator} {nodes[current].value}"
        
        if nodes[current].has_subtree_call:
            _, _, _ = self.parse_rules(
                nodes=sub_trees[
                    nodes[current].subtree_name
                    ].nodes,
                sub_trees=sub_trees,
                rule=rule
            )
        
        if nodes[current].is_terminal:
            self.rules.append(rule)
            self.r_labels.append(nodes[current].label)
            self.r_confidences.append(nodes[current].confidence)
            return current
        
        if current == (len(nodes) -1):
            return current
        
        new_current = current
        while nodes[new_current + 1].node_level > nodes[current].node_level:
            new_current = self._parse_rules(
                nodes, 
                sub_trees, 
                new_current+1, 
                rule
            )

            if new_current == (len(nodes) - 1):
                return new_current
        
        return new_current

        
class SubTree(BaseParser):

    def __init__(self, features, labels):
        self.features = features
        self.labels = labels
        super(SubTree, self).__init__()
    
    def __init_elem__(self):
        
        _sub_tree_name = pp.ungroup(
            pp.Literal('SubTree').suppress() +
            pp.Literal('[').suppress() +
            pp.Combine(
                pp.CaselessLiteral('S') +
                IntType()
            ) +
            pp.Literal(']').suppress()
        ).set_results_name('name')

        _sub_tree = pp.Group(pp.OneOrMore(
                TreeNode(self.features, self.labels)
            )).set_results_name('nodes')
        
        return _sub_tree_name + _sub_tree
    
    def parse_action(self, tokens: pp.ParseResults):
        t = tokens[0]
        t['name'] = t[0]
        t['nodes'] = t[1]
