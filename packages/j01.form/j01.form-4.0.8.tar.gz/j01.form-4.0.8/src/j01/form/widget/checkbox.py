###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Checbox widget
$Id: checkbox.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import

from builtins import str

import z3c.form.browser.widget
import z3c.form.term
import z3c.form.widget
import zope.i18n
import zope.interface
import zope.schema.interfaces
import zope.schema.vocabulary

from j01.form import interfaces
from j01.form.widget.widget import WidgetMixin


# checkbox widgets
@zope.interface.implementer_only(interfaces.ICheckBoxWidget)
class CheckBoxWidget(WidgetMixin, z3c.form.browser.widget.HTMLInputWidget,
    z3c.form.widget.SequenceWidget):
    """CheckBoxWidget using a div wrapper for option tags"""

    showLabel = True
    showItemLabel = True
    klass = u'checkbox-control' # no form-control
    css = u'checkbox'

    def isChecked(self, term):
        return term.token in self.value

    def getChecked(self, term):
        """Get checked marker for input element"""
        return term.token in self.value and 'checked' or None

    def getLabel(self, term):
        """Get label for term"""
        if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
            return zope.i18n.translate(term.title, context=self.request,
                              default=term.title)
        else:
            return str(term.value)

    @property
    def iname(self):
        """Return inuput name"""
        return self.name + ':list'

    @property
    def items(self):
        items = []
        append = items.append
        name = self.iname
        for count, term in enumerate(self.terms):
            append({
                'id': '%s-%i' % (self.id, count),
                'name': name,
                'value': term.token,
                'label': self.getLabel(term),
                'checked': self.getChecked(term),
                # allows to skip label, but don't use non label because the
                # label is used in the error view snippet too
                'showItemLabel': self.showItemLabel,
                })
        return items


@zope.interface.implementer_only(interfaces.ICheckBoxInlineWidget)
class CheckBoxInlineWidget(CheckBoxWidget):
    """CheckBoxWidget using a span wrapper for option tags"""

    showLabel = True
    showItemLabel = True
    klass = u'checkbox-inline-control' # no form-control
    css = u'checkbox-inline'


@zope.interface.implementer_only(interfaces.ISingleCheckBoxWidget)
class SingleCheckBoxWidget(CheckBoxWidget):
    """SingleCheckBoxWidget using a div wrapper for option tags"""

    showLabel = True
    showItemLabel = False
    klass = u'single-checkbox-control' # no form-control
    css = u'single-checkbox'

    def updateTerms(self):
        if self.terms is None:
            self.terms = z3c.form.term.Terms()
            self.terms.terms = zope.schema.vocabulary.SimpleVocabulary((
                zope.schema.vocabulary.SimpleTerm('selected', 'selected',
                                      self.label or self.field.title), ))
        return self.terms


@zope.interface.implementer_only(interfaces.ISingleCheckBoxInlineWidget)
class SingleCheckBoxInlineWidget(SingleCheckBoxWidget):
    """SingleCheckBoxWidget using a span wrapper for option tags"""

    showLabel = False
    showItemLabel = True
    klass = u'single-checkbox-inline-control' # no form-control
    css = u'single-checkbox-inline'



# checkbox picker widgets
JAVASCRIPT = """<script type="text/javascript">
$(document).ready(function(){
    $('input[name="%(name)s"]').picker();
});
</script>
"""


@zope.interface.implementer_only(interfaces.ICheckBoxPickerWidget)
class CheckBoxPickerWidget(CheckBoxWidget):
    """CheckBoxPickerWidget using a div wrapper for option tags"""

    showLabel = True
    showItemLabel = True
    klass = u'checkbox-picker-control'
    css = u'checkbox-picker'

    @property
    def javascript(self):
        return JAVASCRIPT % {
            'name': self.iname.replace('.', '\\\.')
            }


@zope.interface.implementer_only(interfaces.ICheckBoxInlinePickerWidget)
class CheckBoxInlinePickerWidget(CheckBoxPickerWidget):
    """RadioInlinePickerWidget using a span wrapper for option tags"""

    showLabel = True
    showItemLabel = True
    klass = u'checkbox-inline-picker-control'
    css = u'checkbox-inline-picker'

    @property
    def javascript(self):
        return JAVASCRIPT % {
            'name': self.iname.replace('.', '\\\.')
            }


# picker widgets
@zope.interface.implementer_only(interfaces.ISingleCheckBoxPickerWidget)
class SingleCheckBoxPickerWidget(SingleCheckBoxWidget):
    """SingleCheckBoxWidget using a div wrapper for option tags"""

    showLabel = True
    showItemLabel = False
    klass = u'single-checkbox-picker-control' # no form-control
    css = u'single-checkbox-picker'

    @property
    def javascript(self):
        return JAVASCRIPT % {
            'name': self.iname.replace('.', '\\\.')
            }


@zope.interface.implementer_only(interfaces.ISingleCheckBoxInlinePickerWidget)
class SingleCheckBoxInlinePickerWidget(SingleCheckBoxPickerWidget):
    """SingleCheckBoxWidget using a span wrapper for option tags"""

    showLabel = False
    showItemLabel = True
    klass = u'single-checkbox-inline-picker-control' # no form-control
    css = u'single-checkbox-inline-picker'

    @property
    def javascript(self):
        return JAVASCRIPT % {
            'name': self.iname.replace('.', '\\\.')
            }


# get checbox widgets
def getCheckBoxWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, CheckBoxWidget(request))


def getCheckBoxInlineWidget(field, request):
    """IFieldWidget factory for CheckBoxInlineWidget."""
    return z3c.form.widget.FieldWidget(field, CheckBoxInlineWidget(request))


def getSingleCheckBoxWidget(field, request):
    """IFieldWidget factory for SingleCheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, SingleCheckBoxWidget(request))


def getSingleCheckBoxInlineWidget(field, request):
    """IFieldWidget factory for SingleCheckBoxInlineWidget."""
    return z3c.form.widget.FieldWidget(field,
        SingleCheckBoxInlineWidget(request))


# get checkbox picker widgets
def getCheckBoxPickerWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, CheckBoxPickerWidget(request))


def getCheckBoxInlinePickerWidget(field, request):
    """IFieldWidget factory for CheckBoxInlinePickerWidget."""
    return z3c.form.widget.FieldWidget(field,
        CheckBoxInlinePickerWidget(request))


def getSingleCheckBoxPickerWidget(field, request):
    """IFieldWidget factory for SingleCheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field,
        SingleCheckBoxPickerWidget(request))


def getSingleCheckBoxInlinePickerWidget(field, request):
    """IFieldWidget factory for SingleCheckBoxInlineWidget."""
    return z3c.form.widget.FieldWidget(field,
        SingleCheckBoxInlinePickerWidget(request))