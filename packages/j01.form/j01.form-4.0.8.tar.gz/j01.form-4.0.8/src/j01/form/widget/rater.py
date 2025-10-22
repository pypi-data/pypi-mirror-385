###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Text widget
$Id: rater.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import
from zope.interface import implementer_only

import zope.interface
import zope.component

import z3c.form.widget
import z3c.form.interfaces

import j01.rater.widget
import j01.rater.interfaces

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin


@implementer_only(interfaces.IRatingWidget)
class RatingWidget(WidgetMixin, j01.rater.widget.RatingWidget):
    """RatingWidget widget"""


    klass = u'j01-rater-control j01-rater-five-star-control form-control'
    css = u'j01-rater'


@implementer_only(interfaces.IFiveStarRatingWidget)
class FiveStarRatingWidget(RatingWidget):
    """FiveStarRatingWidget widget"""


    klass = u'j01-rater-control j01-rater-five-star-control form-control'
    css = u'j01-rater'

    increment = 1
    isHalfStar = False


@implementer_only(interfaces.IFiveHalfStarRatingWidget)
class FiveHalfStarRatingWidget(RatingWidget):
    """FiveHalfStarRatingWidget widget"""


    klass = u'j01-rater-control j01-rater-five-half-star-control form-control'
    css = u'j01-rater'

    increment = 0.5
    isHalfStar = True


@implementer_only(interfaces.IFiveHalfStarFullRatingWidget)
class FiveHalfStarFullRatingWidget(RatingWidget):
    """FiveHalfStarFullRatingWidget widget"""


    klass = u'j01-rater-control j01-rater-five-half-star-control form-control'
    css = u'j01-rater'

    increment = 1
    isHalfStar = True


# get
@zope.component.adapter(j01.rater.interfaces.IFiveStarRatingField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getFiveStarRatingWidget(field, request):
    """IFieldWidget factory for IFiveStarRatingWidget."""
    return z3c.form.widget.FieldWidget(field, FiveStarRatingWidget(request))


@zope.component.adapter(j01.rater.interfaces.IFiveHalfStarRatingField,
    IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getFiveHalfStarRatingWidget(field, request):
    """IFieldWidget factory for IFiveHalfStarRatingWidget."""
    return z3c.form.widget.FieldWidget(field, FiveHalfStarRatingWidget(request))


@zope.component.adapter(j01.rater.interfaces.IFiveHalfStarFullRatingField,
    IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getFiveHalfStarFullRatingWidget(field, request):
    """IFieldWidget factory for IPasswordWidget."""
    return z3c.form.widget.FieldWidget(field,
        FiveHalfStarFullRatingWidget(request))