###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Tests
$Id: tests.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import
from __future__ import print_function

import doctest
import unittest

import z3c.form.testing

import j01.form.testing


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             ),
        doctest.DocFileSuite('checker.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             ),
        # widgets
        doctest.DocFileSuite('dictionary.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             setUp=j01.form.testing.setUp, tearDown=j01.form.testing.tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                             ),
        doctest.DocFileSuite('password.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             setUp=j01.form.testing.setUp, tearDown=j01.form.testing.tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                             ),
        doctest.DocFileSuite('field.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             setUp=j01.form.testing.setUp, tearDown=j01.form.testing.tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                             checker=z3c.form.testing.outputChecker,
                             ),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
