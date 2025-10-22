# -*- coding: utf-8 -*-
"""
Module c50.py
----------------
C50 algorithm warpper;
C5.0 is a opensource decision tree algorithm written in `c` programming language.
For more information please refer to their (official website)[https://www.rulequest.com/see5-unix.html#USE].   
"""
import pathlib

import pandas as pd
from jinja2 import Environment

from .c50_base import C50Base
from .parsers import Tree


class C50Tree(C50Base):

    def _parse_estimator(self, c50_output):
        tree_parser = Tree(self._features_order, self._labels)
        def_start = c50_output.index("Decision tree:")
        def_end = c50_output.index("Evaluation on training data")
        tree_def = c50_output[def_start: def_end].replace("Decision tree:", "").strip()
        tree_def = tree_def.replace(':   ', '|').replace('    ', '|').replace(':...','|')
        
        # parse tree definition string
        # print("::::tree_def:::::\n", tree_def)
        tree = tree_parser.parse_string(tree_def, parse_all=True)[0]
        tree_nodes = tree.nodes
        sub_trees = tree.sub_trees
        rules, labels, confidences = tree_parser.parse_rules(tree_nodes, sub_trees)

        template_path = pathlib.Path(__file__).parent.resolve()/'templates'/'tree_estimator_template.py.jinja'
        with open(template_path, mode='rt', encoding='utf8') as f:
            estimator_template = f.read()
        
        render_ctx = {
            'labels': self._labels,
            'tree': tree_nodes,
            'sub_trees': sub_trees,
            'rules': rules,
            'predictions': labels,
            'confidences': confidences, 
            'estimator_name': 'Estimator'
        }
        template = Environment().from_string(estimator_template)
        rendered_estimator = template.render( **render_ctx )
         
        return rendered_estimator
