#!/usr/bin/env bash
python generate_lexer.py lexical_spec2.txt
python generate_parser.py grammar_spec2.txt
python compiler.py test2.code