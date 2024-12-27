#!/usr/bin/env bash
python generate_lexer.py lexical_spec1.txt
python generate_parser.py grammar_spec1.txt
python compiler.py test1.code