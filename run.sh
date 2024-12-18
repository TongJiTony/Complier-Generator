#!/usr/bin/env bash
python generate_lexer.py lexical_spec.txt
python generate_parser.py grammar_spec.txt
python compiler.py test.code