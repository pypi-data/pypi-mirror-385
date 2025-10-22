# -*- coding: utf-8 -*-
"""
Module base_parser.py
------------------------
Base decision tree output parser;
C5.0 is a opensource decision tree algorithm written in `c` programming language.
For more information please refer to their (official website)[https://www.rulequest.com/see5-unix.html#USE].   
"""
import pyparsing as pp

class BaseParser(pp.Group):
    """ The BaseGrammar element class;
    """
    __parse_element__ : pp.ParserElement = None
    __results_name__ = None
    # dtype to parser map
    dtype_parser_map = dict()

    def __init__(self):
        _cls = self.__class__
        if _cls.__parse_element__ is None:
            # set instance __parse_element__ attribute
            self.__parse_element__ = self.__init_elem__()

        # sanity claring
        # Clearing all previously added actions
        self.__parse_element__.set_parse_action(None)
        # add set_element_type_attr parse action
        self.__parse_element__.add_parse_action(self._set_element_type_attr)

        super(BaseParser, self).__init__(self.__parse_element__)

        if self.__results_name__:
            self.set_results_name(self.__results_name__)

        self.add_parse_action(self.parse_action)
        self.add_condition(self._conditions)
        _cls.dtype_parser_map[_cls.__name__] = self


    def _set_element_type_attr(self, tokens: pp.ParseResults):
        """ Adds dtype attribute to the ParseResults object;
        """
        tokens['dtype'] = self.__class__.__name__

    def __init_elem__(self) -> pp.ParserElement:
        pass
    
    def parse_action(self, tokens: pp.ParseResults) -> None:
        pass

    def _conditions(self, tokens: pp.ParseResults) ->bool:
        return True
