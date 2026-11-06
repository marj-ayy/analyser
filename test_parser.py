#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test the calculator in infix syntax
"""

import io
import definitions as defs
from parser import parse, ParserError

PARSER_NAME = 'parser'
PARSER_UNDER_TEST = 'parse'

# Prints each test
verbose_test = True

def verbose_info(msg):
    if verbose_test:
        print(msg)

# Stop testing on the first encountered error
stop_on_first_error = True

#################################
## Fonctions génériques de test

# DRIVERS de tests avec et sans valeur calculée

def test(input_descr, expr, msg):
    """Perform a test.
       Raise an exception if it fails and stop_on_first_error == True"""
    if stop_on_first_error:
        #assert expr, msg
        if not expr:
            print(msg)
            exit(1)
    else:
        verbose_info(input_descr)
        if not expr:
            print(msg)
    return

# TODO: Very similar to the one in test_lexer, refactor
def test_single(function_to_test, test_input, expected_result):
    input_descr = "@ " + function_to_test + " on " + repr(test_input) + " expect: " + repr(expected_result)
    verbose_info(input_descr)
    try:
        result = eval(function_to_test)(io.StringIO(test_input+defs.EOI))
        test(input_descr,
             result is None,
             "found " + repr(result))
    except TypeError as e:
        if not stop_on_first_error:
            print("Type error for " + function_to_test +"("+test_input+"): " + repr(e))
        else:
            raise e from None
    except Exception as exn:
        if not stop_on_first_error:
            print(input_descr)
            print("ERROR: uncaught exception " + repr(exn))
        else:
            raise exn from None

def test_all_w_result(function_to_test, test_inputs, start_msg=None):
    if start_msg is None:
        start_msg = function_to_test
    print("@---- ", start_msg)
    for (i, v) in test_inputs:
        test_single(function_to_test, i, v)
    print()

def test_parsing_error(test_input):
    input_descr = "@ " + PARSER_NAME + " on " + repr(test_input) + ", parsing error expected"
    verbose_info(input_descr)
    try:
        result = eval(PARSER_UNDER_TEST)(io.StringIO(test_input+defs.EOI))
        if not stop_on_first_error:
            print("Unexpected result for " + PARSER_UNDER_TEST + "(" + test_input + "): " + repr(result))
        else:
            print("@ unexpected result:", result)
            exit(1)
    except ParserError as e:
        verbose_info("@ parsing error found: " + repr(e))
        verbose_info("@ => OK")


#################################
## Les tests proprement dits.

# Exemples basiques
def exec_basic_tests():
    test_all_w_result(PARSER_UNDER_TEST,
                      [("7;",[7]),
                       ("123+321;",[444]),
                       ("1-2;",[-1]),
                       ("12*3;",[36]),
                       ("12/3;",[4]),
                       ("12^3;",[1728]),
                       ("5!;",[120])],
                      "tests de base")

def exec_test_multiop():
    test_all_w_result(PARSER_UNDER_TEST,
                      [("3 * 4 + 1 - 3 ; #1 * (#1 / 2) ;", [10, 50]),
                       ("1 + 2 * 3 ; -4 + #1 * #1 ;", [7, 45]),
                       ("2*3 + 1 ; #1 * #1 - 4 ;", [7, 45]),
                       ("1 - 1 - 1 ; 1 - (1 - 1) ;", [-1, 1]),
                       ("1 - - 1 - 1 ; 1 - (-1 - 1) ; 1 - -(1 - 1) ;", [1, 3, 1]),
                       ("60 / 10 / 2 ; 60 / (10 / 2) ;", [3, 12]),
                       ("- ((1 + 2) * - ((3 - 5))) ; ", [-6]),
                       ("2^1^3^2;",[2]),
                       ("(2^1)^3^2;",[512])],
                      "tests avec plusieurs opérations")

# Tests autour de n*(n+1)/2
def exec_text_sum(N):
    test_single(PARSER_UNDER_TEST,
                "1;" + "".join(["{0}+#{1};".format(i,i-1) for i in range(2,N)]),
                [i * (i+1)//2 for i in range(1,N)])
    r = [i for i in range(1,N)]
    r.append((N-1)*N//2)
    l = [str(i)+";" for i in range(1,N)]
    for i in range(1, N-1):
        l.append("#{0}+".format(i))
        l.append("#{0};".format(N-1))
    test_single(PARSER_UNDER_TEST, "".join(l), r)

# Tests de k parmi n
def exec_test_binomial():
    k_parmi_n="#2-#1;#1!;#2!;#3!;#5/#4/#6;"
    test_all_w_result(PARSER_UNDER_TEST,
                      [("1;2;"+k_parmi_n, [1, 2, 1, 1, 2, 1, 2]),
                       ("1;3;"+k_parmi_n, [1, 3, 2, 1, 6, 2, 3]),
                       ("2;3;"+k_parmi_n, [2, 3, 1, 2, 6, 1, 3]),
                       ("1;4;"+k_parmi_n, [1, 4, 3, 1, 24, 6, 4]),
                       ("2;4;"+k_parmi_n, [2, 4, 2, 2, 24, 2, 6]),
                       ("3;6;"+k_parmi_n, [3, 6, 3, 6, 720, 6, 20])],
                      "tests binomiaux")

# Tests avec erreurs
def exec_test_parsing_error():
    test_parsing_error(";")
    test_parsing_error("123+321")
    test_parsing_error("123+321; 1")
    test_parsing_error("3 * 4 + 1 - 3 ; #1 (#1 / 2) ;")
    test_parsing_error("3 * / 1 - 3 ; #1 * (#1 / 2) ;")
    test_parsing_error("3 * 4 + 1 - 3 #1 * (#1 / 2) ;")
    test_parsing_error("(1 2 ;")
    test_parsing_error("- ((1 + 2 * - ((3 - 5))) ; ")
    test_parsing_error("- (1 + 2)) * - ((3 - 5)) ; ")
    test_parsing_error("!5;")
    test_parsing_error("5! / ;")


# Si ce fichier est lancé directement, on exécute les tests
if __name__ == '__main__':
    exec_basic_tests()
    exec_test_multiop()
    exec_text_sum(20)
    exec_test_binomial()
    exec_test_parsing_error()
    print("\n@ all tests done !")
