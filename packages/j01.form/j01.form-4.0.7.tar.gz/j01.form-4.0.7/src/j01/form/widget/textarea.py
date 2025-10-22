###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Textarea widget
$Id: textarea.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.widget

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin


@zope.interface.implementer_only(interfaces.ITextAreaWidget)
class TextAreaWidget(WidgetMixin, z3c.form.browser.widget.HTMLTextAreaWidget,
    z3c.form.widget.Widget):
    """Textarea widget"""

    klass = u'textarea-control form-control'
    css = u'textarea'
    value = u''


# get
@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTextAreaWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return z3c.form.widget.FieldWidget(field, TextAreaWidget(request))