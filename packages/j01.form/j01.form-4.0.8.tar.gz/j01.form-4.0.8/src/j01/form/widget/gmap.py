###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Text widget
$Id: gmap.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import
from zope.interface import implementer_only

import zope.interface

import z3c.form.interfaces
import z3c.form.widget

import m01.gmap.widget

from j01.form import interfaces
from j01.form.widget.widget import WidgetMixin


@implementer_only(interfaces.IGMapWidget)
class GMapWidget(WidgetMixin, m01.gmap.widget.GMapWidget):
    """Text input type widget"""


    klass = u'gmap-control form-control'
    css = u'gmap'


@implementer_only(interfaces.IGeoPointGMapWidget)
class GeoPointGMapWidget(WidgetMixin, m01.gmap.widget.GeoPointGMapWidget):
    """Text input type widget"""


    klass = u'gmap-point-control form-control'
    css = u'gmap-point'


# gmap
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getGMapWidget(field, request):
    """IFieldWidget factory for GMapWidget."""
    return z3c.form.widget.FieldWidget(field, GMapWidget(request))


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getGeoPointGMapWidget(field, request):
    """IFieldWidget factory for GMapWidget."""
    return z3c.form.widget.FieldWidget(field, GeoPointGMapWidget(request))