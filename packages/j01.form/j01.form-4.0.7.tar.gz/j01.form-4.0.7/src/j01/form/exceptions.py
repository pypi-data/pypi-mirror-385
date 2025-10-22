###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Exceptions

$Id: exceptions.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import

import zope.schema

_ = zope.i18nmessageid.MessageFactory('p01')


# password confirmation
class PasswordComparsionError(zope.schema.ValidationError):
    __doc__ = _("""Password doesn't compare with confirmation value""")