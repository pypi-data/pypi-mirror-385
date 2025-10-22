###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Select widget
$Id: select.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import

import zope.component
import zope.interface
import zope.i18n
import zope.i18nmessageid
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.widget

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin

_ = zope.i18nmessageid.MessageFactory('p01')


class SelectWidgteBase(WidgetMixin, z3c.form.browser.widget.HTMLSelectWidget,
    z3c.form.widget.SequenceWidget):
    """Select widget base class"""

    klass = u'select-control form-control'
    css = u'select'
    prompt = False

    noValueMessage = _('No value')
    promptMessage = _('Select a value ...')

    # Internal attributes
    _adapterValueAttributes = \
        z3c.form.widget.SequenceWidget._adapterValueAttributes + \
        ('noValueMessage', 'promptMessage', 'prompt')

    def isSelected(self, term):
        return term.token in self.value

    @property
    def items(self):
        if self.terms is None:  # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })

        ignored = set(self.value)

        def addItem(idx, term, prefix=''):
            selected = self.isSelected(term)
            if selected and term.token in ignored:
                ignored.remove(term.token)
            id = '%s-%s%i' % (self.id, prefix, idx)
            content = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                content = zope.i18n.translate(
                    term.title, context=self.request, default=term.title)
            items.append(
                {'id': id, 'value': term.token, 'content': content,
                 'selected': selected})

        for idx, term in enumerate(self.terms):
            addItem(idx, term)

        if ignored:
            # some values are not displayed, probably they went away from the vocabulary
            for idx, token in enumerate(sorted(ignored)):
                try:
                    term = self.terms.getTermByToken(token)
                except LookupError:
                    # just in case the term really went away
                    continue

                addItem(idx, term, prefix='missing-')
        return items

################################################################################
#
# select widget

@zope.interface.implementer_only(interfaces.ISelectWidget)
class SelectWidget(SelectWidgteBase):
    """Select widget"""
    pass


@zope.interface.implementer_only(interfaces.IMultiSelectWidget)
class MultiSelectWidget(SelectWidget):
    """Select widget implementation."""

    prompt = False
    size = 5
    multiple = 'multiple'


################################################################################
#
# select picker, see http://silviomoreto.github.io/bootstrap-select/ for options

SELECT_DROPDOWN_WIDGET_JAVASCRIPT = """<script>
  $('#%s').dropdown({%s
  });
</script>
"""

def j01SelectDropDownJavaScript(id, data):
    """Select drop down javaScript generator"""
    lines = []
    append = lines.append
    for key, value in list(data.items()):
        # apply functions
        if value is None:
            continue
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif isinstance(value, (list, int)):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, str):
            append("\n    %s: '%s'" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))
    settings = ','.join(lines)
    return SELECT_DROPDOWN_WIDGET_JAVASCRIPT % (id, settings)


class SelectDropDownWidgetMixin(SelectWidget):
    """Selet dropdown widget base class

    OPTION  DEFAULT

    speed   300
    Animation speed in ms. Set to 0 to disable animation.

    easing  easeInOutCirc
    Easing method to use.
    All built-in jQuery methods are supported, as well as those provided with
    jQuery Transit.

    margin  20
    Amount of space in px between the edge of the dropdown menu and browser
    window.

    collision   true
    Enable collision detection.

    If enabled, the dropdown menu will reposition based on the available
    visible space.

    autoResize  200
    The number of ms to set the auto resize/reposition timer interval to.
    Set 0 to disable automatic resizing

    scrollSelected  true
    Scroll to first selected item when the dropdown or a menu is opened.

    keyboard    true
    Enable keyboard navigation.

    nested  true
    Whether or not to enable multi-level nesting.
    If disabled, all items will be displayed in a single menu.

    selectParents   false
    Whether or not to add menu parents as selectable items.
    If disabled and nested is also disabled, parent items will be displayed as
    text labels.

    multi   false
    Whether or not to enable multiple item selection.
    If populating a dropdown from a select element, set to null to auto-detect
    based on the multiple attribute.

    minSelect   0
    Minimum number of selectable items.

    maxSelect   0
    Maximum number of selectable items.

    selectLinks false
    Whether or not to make links selectable.

    followLinks true
    Whether or not to follow link URLs.

    closeText   Close
    Text/title used for the close button.

    autoClose   true
    Whether or not to close automatically when the dropdown loses focus.

    autoCloseMax    true
    Whether or not to close the dropdown when the maximum number of selectable
    items has been reached.

    autoCloseLink   false
    Whether or not to close the dropdown when a link is clicked.

    closeReset  true
    Whether or not to reset the dropdown when it is closed.
    When resetting, all menus are reverted back to their original positions.

    toggleText  Please select
    Default text used for the toggle button.

    autoToggle  true
    Whether or not to update the toggle button text with the selected item(s)
    text.

    autoToggleLink  false
    Whether or not to update the toggle button text when a link is selected.
    Requires autoToggle to be enabled.

    autoToggleHTML  false
    Replace the toggle text with HTML contents of selected item(s) HTML
    contents.
    Requires autoToggle to be enabled.

    titleText   Please select
    Default title text. Set to null to match the default toggle text.

    autoTitle   true
    Whether or not to update the title text with the menu title.
    In nested menus, the menu title is determined from the current parent item.

    """

    speed = 300
    easing = 'easeInOutCirc'
    margin = 20
    collision = True
    autoResize = None # 200
    scrollSelected = True
    keyboard = True
    nested = False
    selectParents = False
    minSelect = 0
    maxSelect = 0
    selectLinks = False
    followLinks = True
    autoClose = True
    autoCloseMax = True
    autoCloseLink = False
    closeReset = True
    autoToggle = True
    autoToggleLink = False
    autoToggleHTML = False
    autoTitle = True

    closeText = _(u"Close")
    toggleText = _(u"Please select")
    titleText = _(u"Please select")

    @property
    def txtClose(self):
        return zope.i18n.translate(self.closeText)

    @property
    def txtToggle(self):
        return zope.i18n.translate(self.toggleText)

    @property
    def txtTitle(self):
        return zope.i18n.translate(self.titleText)

    @property
    def settings(self):
        data = {}
        multi = self.multiple == 'multiple'
        if multi:
            data['multi'] = multi
        if self.speed != 300:
            data['speed'] = self.speed
        if self.easing != 'easeInOutCirc':
            data['easing'] = self.easing
        if self.margin != 20:
            data['margin'] = self.margin
        if self.collision is False:
            data['collision'] = self.collision
        if self.autoResize is not None:
            data['autoResize'] = self.autoResize
        if self.scrollSelected is False:
            data['scrollSelected'] = self.scrollSelected
        if self.keyboard is False:
            data['keyboard'] = self.keyboard
        if self.nested is True:
            data['nested'] = self.nested
        if self.selectParents is True:
            data['selectParents'] = self.selectParents
        minSelect = self.minSelect
        if minSelect is not None and minSelect != 0:
            data['minSelect'] = minSelect
        maxSelect = self.maxSelect
        if maxSelect is not None and maxSelect != 0:
            data['maxSelect'] = maxSelect
        if self.selectLinks is True:
            data['selectLinks'] = self.selectLinks
        if self.followLinks is False:
            data['followLinks'] = self.followLinks
        if self.autoClose is False:
            data['autoClose'] = self.autoClose
        if self.autoCloseMax is False:
            data['autoCloseMax'] = self.autoCloseMax
        if self.autoCloseLink is True:
            data['autoCloseLink'] = self.autoCloseLink
        if self.closeReset is False:
            data['closeReset'] = self.closeReset
        if self.autoToggle is False:
            data['autoToggle'] = self.autoToggle
        if self.autoToggleLink is True:
            data['autoToggleLink'] = self.autoToggleLink
        if self.autoToggleHTML is True:
            data['autoToggleHTML'] = self.autoToggleHTML
        if self.autoTitle is False:
            data['autoTitle'] = self.autoTitle
        return data

    @property
    def javascript(self):
        return j01SelectDropDownJavaScript(self.id, self.settings)


@zope.interface.implementer_only(interfaces.ISelectDropDownWidget)
class SelectDropDownWidget(SelectDropDownWidgetMixin, SelectWidget):
    """SelectDropDownWidget"""

    klass = u'select-dropdown-control form-control'
    css = u'select-dropdown'


@zope.interface.implementer_only(interfaces.IMultiSelectDropDownWidget)
class MultiSelectDropDownWidget(SelectDropDownWidgetMixin, MultiSelectWidget):
    """MultiSelectDropDownWidget"""

    klass = u'select-dropdown-control form-control'
    css = u'select-dropdown'

    @property
    def minSelect(self):
        return self.field.min_length

    @property
    def maxSelect(self):
        return self.field.max_length


################################################################################
#
# group select

@zope.interface.implementer_only(interfaces.IGroupSelectWidget)
class GroupSelectWidget(SelectWidget):
    """Select widget with optgroup support"""

    def appendSubTerms(self, groupName, items, subTerms, count):
        """Append collected sub terms as optgroup subItems"""
        subItems = []
        for subTerm in subTerms:
            id = '%s-%i' % (self.id, count)
            content = zope.i18n.translate(subTerm.title,
                context=self.request, default=subTerm.title)
            subItems.append({
                'id': id,
                'value': subTerm.token,
                'content': content,
                'selected': self.isSelected(subTerm)})
        items.append({
            'isGroup': True,
            'content': groupName,
            'subItems': subItems,
            })

    @property
    def items(self):
        if self.terms is None:
            # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'isGroup': False,
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })

        # setup optgroup and option items
        groupName = None
        subTerms = []
        for count, term in enumerate(self.terms):
            if term.isGroup:
                if groupName is not None and subTerms:
                    self.appendSubTerms(groupName, items, subTerms, count)
                     # set empty subTerms list
                    subTerms = []
                # set as next groupName
                groupName = zope.i18n.translate(term.title,
                    context=self.request, default=term.title)
            else:
                # collect sub item terms
                subTerms.append(term)

        # render the last collected sub terms with the latest groupName
        if groupName is not None:
            self.appendSubTerms(groupName, items, subTerms, count)

        return items


class GroupSelectDropDownWidget(SelectDropDownWidgetMixin, GroupSelectWidget):
    """Select widget with optgroup support"""

    klass = u'select-dropdown-control form-control'
    css = u'select-dropdown'


################################################################################
#
# html select
# https://github.com/jsmodules/ddslick

# NOTE: this requires the mCustomScrollbar javascript
#       http://manos.malihu.gr/jquery-custom-content-scroller/
DDSLICK_SCROLLBAR_JAVASCRIPT = """
    $('#%(id)s .dd-options').mCustomScrollbar({
        alwaysShowScrollbar: 0,
        scrollInertia: 100,
        mouseWheel: {
            enable: true,
            preventDefault: true
        },
        theme: 'dark-3',
        scrollButtons:{
            enable: true
        }
    });
"""

DDSLICK_JAVASCRIPT = """<script type="text/javascript">
$(document).ready(function() {
    $('#%(id)s').ddslick({
        width: "%(width)s",
        background: "%(background)s",
        selectText: "%(label)s",
        showSelectedHTML: false
    });%(mCustomScrollbar)s
});
</script>
"""

@zope.interface.implementer_only(interfaces.IDDSlickSelectWidget)
class DDSlickSelectWidget(SelectWidgteBase):
    """DDSlick select widget

    Title, text and description must get translated during vocbaulary setup.
    We don't provide term translation based in ITitledTokenizedTerm.
    """

    klass = u'ddslick-control form-control'
    css = u'ddslick'
    width = "100%"
    background = "#FFFFFF"
    showScrollbar = False

    def addItem(self, idx, term, items, ignored, prefix=''):
        selected = self.isSelected(term)
        if selected and term.token in ignored:
            ignored.remove(term.token)
        id = '%s-%s%i' % (self.id, prefix, idx)
        items.append({
            'id': id,
            'value': term.token,
            'img': getattr(term, 'img', None),
            'text': getattr(term, 'text', None),
            'description': getattr(term, 'description', None),
            'content': term.title,
            'selected': selected,
            })

    @property
    def items(self):
        if self.terms is None:  # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'img': None,
                'text': message,
                'description': None,
                'selected': self.value == []
                })

        ignored = set(self.value)

        for idx, term in enumerate(self.terms):
            self.addItem(idx, term, items, ignored)

        if ignored:
            # some values are not displayed, probably they went away from the vocabulary
            for idx, token in enumerate(sorted(ignored)):
                try:
                    term = self.terms.getTermByToken(token)
                except LookupError:
                    # just in case the term really went away
                    continue
                self.addItem(idx, term, items, ignored, prefix='missing-')
        return items

    @property
    def javascript(self):
        if self.showScrollbar:
            mCustomScrollbar = DDSLICK_SCROLLBAR_JAVASCRIPT % {
                'id': self.id,
            }
        else:
            mCustomScrollbar = ''
        return DDSLICK_JAVASCRIPT % {
            'id': self.id,
            'label': self.label,
            'width': self.width,
            'background': self.background,
            'mCustomScrollbar': mCustomScrollbar,
            }




# adapter
@zope.component.adapter(zope.schema.interfaces.IChoice, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def ChoiceWidgetDispatcher(field, request):
    """Dispatch widget for IChoice based also on its source."""
    return zope.component.getMultiAdapter((field, field.vocabulary, request),
                                          z3c.form.interfaces.IFieldWidget)


@zope.component.adapter(zope.schema.interfaces.IChoice,
                        zope.interface.Interface, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def SelectFieldWidget(field, source, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, SelectWidget(request))


@zope.component.adapter(
    zope.schema.interfaces.IUnorderedCollection, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def CollectionSelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, MultiSelectWidget(request))


@zope.component.adapter(
    zope.schema.interfaces.IUnorderedCollection,
    zope.schema.interfaces.IChoice, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def CollectionChoiceSelectFieldWidget(field, value_type, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, SelectWidget(request))


# get
def getSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, SelectWidget(request))


def getMultiSelectWidget(field, request):
    """IFieldWidget factory for MultiSelectWidget."""
    return z3c.form.widget.FieldWidget(field, MultiSelectWidget(request))


def getSelectDropDownWidget(field, request):
    """IFieldWidget factory for SelectDropDownWidget."""
    return z3c.form.widget.FieldWidget(field, SelectDropDownWidget(request))


def getMultiSelectDropDownWidget(field, request):
    """IFieldWidget factory for MultiSelectDropDownWidget."""
    return z3c.form.widget.FieldWidget(field, MultiSelectDropDownWidget(request))


def getGroupSelectWidget(field, request):
    """IFieldWidget factory for GroupSelectWidget."""
    return z3c.form.widget.FieldWidget(field, GroupSelectWidget(request))


def getDDSlickSelectWidget(field, request):
    """IFieldWidget factory for DDSlickSelectWidget."""
    return z3c.form.widget.FieldWidget(field, DDSlickSelectWidget(request))


def getDDSlickScrollbarSelectWidget(field, request):
    """IFieldWidget factory for DDSlickSelectWidget."""
    widget = z3c.form.widget.FieldWidget(field, DDSlickSelectWidget(request))
    widget.showScrollbar = True
    return widget