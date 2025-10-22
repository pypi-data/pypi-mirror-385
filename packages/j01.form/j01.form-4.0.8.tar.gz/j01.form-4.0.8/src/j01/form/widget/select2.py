##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: select2.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import
from zope.interface import implementer_only

import zope.interface

import z3c.form.widget
import z3c.form.interfaces

import j01.select2.widget

from j01.form import interfaces
from j01.form.widget.widget import WidgetMixin


@implementer_only(interfaces.ISelect2Widget)
class Select2Widget(WidgetMixin, j01.select2.widget.Select2Widget):
    """Selects input widget"""


    klass = u'select2-control'
    css = u'select2'


@implementer_only(interfaces.ISingleSelect2Widget)
class SingleSelect2Widget(WidgetMixin, j01.select2.widget.SingleSelect2Widget):
    """Selects input widget"""


    klass = u'select2-single-control'
    css = u'select2'


@implementer_only(interfaces.ITagListSelect2Widget)
class TagListSelect2Widget(WidgetMixin,
    j01.select2.widget.TagListSelect2Widget):
    """Widget for IList of ITextLine

    This widget is based on a IList of ITextLine field, this means we can enter
    custom text data and the JSON-RPC callback is used for autosuggest
    useable input.

    """


    klass = u'select2-taglist-control'
    css = u'select2-taglist'


@implementer_only(interfaces.ISingleTagSelect2Widget)
class SingleTagSelect2Widget(WidgetMixin,
    j01.select2.widget.SingleTagSelect2Widget):
    """Widget for ITextLine supporting jsonrpc autosuggest callback"""


    klass = u'select2-singletag-control'
    css = u'select2-singletag'


@implementer_only(interfaces.ILiveListSelect2Widget)
class LiveListSelect2Widget(WidgetMixin,
    j01.select2.widget.LiveListSelect2Widget):
    """Widget for IList of IChoice"""


    klass = u'select2-livelist-control'
    css = u'select2-livelist'


@implementer_only(interfaces.ILiveTagSelect2Widget)
class LiveTagSelect2Widget(WidgetMixin,
    j01.select2.widget.LiveTagSelect2Widget):
    """Widget for IList of IChoice"""


    klass = u'select2-livelist-control'
    css = u'select2-livelist'


# HTML select element
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getSelect2Widget(field, request):
    """IFieldWidget factory for Select2Widget."""
    return z3c.form.widget.FieldWidget(field, Select2Widget(request))


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getPromptSelect2Widget(field, request):
    """IFieldWidget factory for Select2Widget."""
    widget = z3c.form.widget.FieldWidget(field, Select2Widget(request))
    widget.prompt = True
    return widget


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getSingleSelect2Widget(field, request):
    """IFieldWidget factory for SingleSelect2Widget."""
    widget = z3c.form.widget.FieldWidget(field, SingleSelect2Widget(request))
    widget.multiple = None
    return widget


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getPromptSingleSelect2Widget(field, request):
    """IFieldWidget factory for SingleSelect2Widget."""
    widget = z3c.form.widget.FieldWidget(field, SingleSelect2Widget(request))
    widget.prompt = True
    widget.multiple = None
    return widget


# single tagging
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getSingleTagSelect2Widget(field, request):
    """IFieldWidget factory for SingleTagSelect2Widget."""
    return z3c.form.widget.FieldWidget(field, SingleTagSelect2Widget(request))

def setUpSingleTagSelect2Widget(source):
    def inner(field, request):
        widget = getSingleTagSelect2Widget(field, request)
        widget.source = source
        return widget
    return inner


# tagging
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTagListSelect2Widget(field, request):
    """IFieldWidget factory for TagListSelect2Widget."""
    return z3c.form.widget.FieldWidget(field, TagListSelect2Widget(request))

def setUpTagListSelect2Widget(source):
    def inner(field, request):
        widget = getTagListSelect2Widget(field, request)
        widget.source = source
        return widget
    return inner


# live list
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getLiveListSelect2Widget(field, request):
    """IFieldWidget factory for LiveListSelect2Widget."""
    return z3c.form.widget.FieldWidget(field, LiveListSelect2Widget(request))


# live tag
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getLiveTagSelect2Widget(field, request):
    """IFieldWidget factory for LiveTagSelect2Widget."""
    return z3c.form.widget.FieldWidget(field, LiveTagSelect2Widget(request))
