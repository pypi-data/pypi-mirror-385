# -*- coding: utf-8 -*-
"""
Module c50_base.py
----------------
C50 rules algorithm warpper;
C5.0 is a opensource decision tree algorithm written in `c` programming language.
For more information please refer to their (official website)[https://www.rulequest.com/see5-unix.html#USE].   
"""
from typing import Union
import pathlib

import subprocess as sp

from uuid import uuid4

import pandas as pd
from jinja2 import Environment

from .names_file_builder import NamesFileBuilder
from .parsers import RuleSet
from .estimator_loader import load_estimator


class C50Base(object):

    def __init__(self, working_dir='/tmp', estimator_id=None):
        if estimator_id is None:
            self.id = str(uuid4()).rsplit('-', maxsplit=1)[-1]
        else:
            self.id = estimator_id
        
        p = pathlib.Path(working_dir)
        if not (p.exists() and p.is_dir()):
            p.mkdir() 
        
        self.working_dir = working_dir
        self._estimator = None
        # the order in which the features are defined in the .names file;
        # this attribute is initialized in the `self._write_names_file` method.
        self._features_order: list = None
        self._labels: list = None
    
    @property
    def estimator(self):
        if self._estimator is None:
            Estimator = load_estimator(f'{self.working_dir}/estimator_{self.id}.py')
            self._estimator = Estimator()
        return self._estimator
    
    @property
    def labels_map(self):
        return self.estimator.labels_map

    def fit(
        self, 
        x_train: pd.DataFrame, 
        y_train: pd.Series, 
        x_test: Union[pd.DataFrame, None]=None, 
        y_test: Union[pd.Series, None]=None,
        descrete_values_subset=False,
        winnow=False,
        disable_global_prunning=False,
        prunning_confidence_factor: Union[float, None]=None,
        initial_tree_constraint_degree=2,
        data_sampling=None,
        sampling_seed=None,
        weights=None,
        stack_size=20000, # 20MB
    ):
        self._labels = y_train.unique().tolist()

        train_set = pd.concat([x_train, y_train], axis=1)
        if x_test is not None:
            test_set = pd.concat([x_test, y_test], axis=1)
        else:
            test_set = None

        self._write_files(
            train_set=train_set,
            test_set=test_set,
            target_name=y_train.name,
            weights=weights
        )
        
        extra_args = self._get_extra_args(
            descrete_values_subset=descrete_values_subset,
            winnow=winnow,
            disable_global_prunning=disable_global_prunning,
            prunning_confidence_factor=prunning_confidence_factor,
            initial_tree_constraint_degree=initial_tree_constraint_degree,
            data_sampling=data_sampling,
            sampling_seed=sampling_seed,
            weights=weights,
        )
        base_path = str(pathlib.Path(__file__).parent.parent.resolve())
        bash_execute_command = f'ulimit -Ss {stack_size} && "{base_path}/bin/c5.0" -f "{self.working_dir}/c5.0-{self.id}" {extra_args}'
        
        c50 = sp.run([bash_execute_command], shell=True, stdout=sp.PIPE, stderr=sp.PIPE)

        c50_output = c50.stdout.decode('utf-8')
        stderr = c50.stderr.decode('utf-8')
        with open(f'{self.working_dir}/c5.0-{self.id}.output.txt', 'w') as f:
            f.write(c50_output)

        if c50.returncode == 0:
            self._parse_output(c50_output)
        else:
            raise RuntimeError(
                "C5.0 binary execution failed with code {}\n\n{}\n\n{}".format(
                    c50.returncode, 
                    stderr,
                    c50_output
                )
            )
    
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
        extra_args = []
        if descrete_values_subset:
            extra_args.append('-s')
        
        if winnow:
            extra_args.append('-w')
        
        # if show_cut_threshold_info:
        #     # extra_params.append('-p')
        #     pass

        if disable_global_prunning:
            extra_args.append('-g')
        
        if prunning_confidence_factor is not None:
            # prunning_error_rate = 100 disables the initial prunning
            extra_args.append(f'-c {prunning_confidence_factor}')
        
        if initial_tree_constraint_degree is not None and initial_tree_constraint_degree != 2:
            extra_args.append(f'-m {initial_tree_constraint_degree}')
        
        if data_sampling is not None:
            extra_args.append(f'-S {data_sampling}')
        
        if sampling_seed is not None:
            extra_args.append(f'-I {sampling_seed}')
        
        if weights is None:
            extra_args.append('-e')
        
        return ' '.join(extra_args)

    def predict(self, X):
        if type(X) is pd.Series:
            X = X.to_frame().T
        # TODO transform dictionaries into DataFrame
        
        return self.estimator.predict(X)
    
    def predict_proba(self, X):
        return self.estimator.predict_proba(X)

    # def batch_predict(self,X):
    #     return self.estimator.batch_predict(X)

    def _write_names_file(self, dataset, target_name):

        builder = NamesFileBuilder()
        builder.build_and_save(
            path=f'{self.working_dir}/c5.0-{self.id}.names',
            dataset=dataset,
            target_name=target_name
        )
        self._features_order = builder.features_order
    
    def _write_data_files(self, train_set: pd.DataFrame, test_set: pd.DataFrame):
        
        train_set.loc[:, self._features_order].to_csv(
            f'{self.working_dir}/c5.0-{self.id}.data', 
            # f'/tmp/c5.0-{self.id}.data', 
            header=False, 
            index=False,
            na_rep='?',
        )

        if test_set is not None:
            test_set.loc[:, self._features_order].to_csv(
                f'{self.working_dir}/c5.0-{self.id}.test', 
                header=False, 
                index=False,
                na_rep='?',
            )
    
    def _write_weights_file(self, weights):

        template_path = pathlib.Path(__file__).parent.resolve()/'templates'/'weights.costs.jinja'
        with open(template_path, mode='rt', encoding='utf8') as f:
            weights_template = f.read()
        
        template = Environment().from_string(weights_template)
        rendered_estimator = template.render(weights=weights)

        with open(f'{self.working_dir}/c5.0-{self.id}.costs', 'w') as f:
            f.write(rendered_estimator)

    def _write_files(
        self, train_set: pd.DataFrame, 
        test_set: Union[pd.DataFrame, None], 
        target_name: str,
        weights: Union[pd.DataFrame, None]
    ):
        self._write_names_file(
            dataset=train_set,
            target_name=target_name
        )

        self._write_data_files(
            train_set=train_set,
            test_set=test_set
        )
        if weights is not None:
            self._write_weights_file(weights)

    def _parse_output(self, c50_output, rule_based=False):

        rendered_estimator = self._parse_estimator(c50_output)
        with open(f'{self.working_dir}/estimator_{self.id}.py', 'w') as f:
            f.write(rendered_estimator)

    def _parse_estimator(self, c50_output):
        pass
