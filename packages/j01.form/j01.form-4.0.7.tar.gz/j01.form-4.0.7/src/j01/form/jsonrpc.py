###############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
from __future__ import absolute_import
from zope.interface import implementer

import zope.component
import zope.interface

from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IErrorViewSnippet

from p01.jsonrpc.interfaces import IJSONRPCPublisher
from p01.jsonrpc.interfaces import IJSONRPCRequest
from p01.jsonrpc.publisher import MethodPublisher

from j01.form import interfaces
import j01.form.layer


@implementer(IJSONRPCPublisher)
class J01Validator(MethodPublisher):

    zope.component.adapts(interfaces.IForm, IJSONRPCRequest)


    def j01Validate(self, id, value):
        """Validate the value for the witdget with the given DOM field id."""
        res = u'OK'
        errorView = None

        # get last part from id as fieldName
        names = id.split('-')
        fieldName = names[len(names)-1]
        # optimize setUpWidgetValidation in your form and only setup the
        # relevant widget if possible
        self.context.setUpWidgetValidation(name=fieldName)

        # get widget by fieldName
        widget = self.context.widgets.get(fieldName)
        if widget is not None:
            content = self.context.widgets.content
            form = self.context.widgets.form
            try:
                value = IDataConverter(widget).toFieldValue(value)
                validator = zope.component.getMultiAdapter(
                    (content, self.request, self.context,
                     getattr(widget, 'field', None), widget), IValidator)
                error = validator.validate(value)

            except (zope.schema.ValidationError, ValueError) as error:
                errorView = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     form, content), IErrorViewSnippet)
                errorView.update()

        if errorView is not None:
            res = errorView.render()
        return {'id':id, 'result':res}