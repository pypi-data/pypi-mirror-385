# -*- coding: utf-8 -*-
"""
Module c50_rules.py
----------------
C50 rules algorithm warpper;
C5.0 is a opensource decision tree algorithm written in `c` programming language.
For more information please refer to their (official website)[https://www.rulequest.com/see5-unix.html#USE].   
"""
import pathlib

import pandas as pd
from jinja2 import Environment

from .c50_base import C50Base
from .parsers import RuleSet


class C50Rules(C50Base):


    @property
    def rules(self):
        return self.estimator.rules

    def _get_extra_args(
        self,
        descrete_values_subset=False,
        winnow=False,
        disable_global_prunning=False,
        prunning_confidence_factor=None,
        initial_tree_constraint_degree=2,
        data_sampling=None,
        sampling_seed=None,
        weights=None,
        
    ):
        extra_args = super()._get_extra_args(
            descrete_values_subset=descrete_values_subset,
            winnow=winnow,
            disable_global_prunning=disable_global_prunning,
            prunning_confidence_factor=prunning_confidence_factor,
            initial_tree_constraint_degree=initial_tree_constraint_degree,
            data_sampling=data_sampling,
            sampling_seed=sampling_seed,
            weights=weights,
        )
        
        return '-r ' + extra_args


    def _parse_estimator(self, c50_output):
        rules_parser = RuleSet(self._features_order, self._labels)
        def_start = c50_output.index("Rules:")
        def_end = c50_output.index("Evaluation on training data")
        rules_def = c50_output[def_start: def_end].replace("Rules:", "").strip()
        
        # parse rules definition string
        # print("::::rules_def:::::\n", rules_def)
        rule_set = rules_parser.parse_string(rules_def, parse_all=True)[0]
        
        template_path = pathlib.Path(__file__).parent.resolve()/'templates'/'rule_estimator_template.py.jinja'
        with open(template_path, mode='rt', encoding='utf8') as f:
            estimator_template = f.read()
        
        render_ctx = {
            'labels': self._labels,
            'rule_set': rule_set,
            'estimator_name': 'Estimator'
        }
        template = Environment().from_string(estimator_template)
        rendered_estimator = template.render( **render_ctx )
         
        return rendered_estimator
