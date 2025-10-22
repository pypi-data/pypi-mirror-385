###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Textlines widget
$Id: textlines.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import

import zope.interface

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.textlines

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin


@zope.interface.implementer_only(interfaces.ITextLinesWidget)
class TextLinesWidget(WidgetMixin, z3c.form.browser.textlines.TextLinesWidget):
    """Textarea widget implementation."""

    klass = u'textlines form-control'
    css = u'textlines'
    value = u''


# get
@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTextLinesWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return z3c.form.widget.FieldWidget(field, TextLinesWidget(request))