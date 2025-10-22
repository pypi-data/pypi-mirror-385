###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Widgets
$Id: __init__.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import

# checkbox
from j01.form.widget.checkbox import getCheckBoxWidget
from j01.form.widget.checkbox import getCheckBoxInlineWidget

from j01.form.widget.checkbox import getSingleCheckBoxWidget
from j01.form.widget.checkbox import getSingleCheckBoxInlineWidget

from j01.form.widget.checkbox import getCheckBoxPickerWidget
from j01.form.widget.checkbox import getCheckBoxInlinePickerWidget

from j01.form.widget.checkbox import getSingleCheckBoxPickerWidget
from j01.form.widget.checkbox import getSingleCheckBoxInlinePickerWidget

# dictionary
from j01.form.widget.dictionary import getDictKeyValueWidget
from j01.form.widget.dictionary import getProxyWidget

# file
from j01.form.widget.file import getFileWidget

# multi
from j01.form.widget.multi import getMultiFieldWidget

# password
from j01.form.widget.password import getPasswordWidget
from j01.form.widget.password import getPasswordConfirmationWidget

# radio
from j01.form.widget.radio import getRadioWidget
from j01.form.widget.radio import getRadioInlineWidget
from j01.form.widget.radio import getRadioPickerWidget
from j01.form.widget.radio import getRadioInlinePickerWidget

# select
from j01.form.widget.select import getSelectWidget
from j01.form.widget.select import getMultiSelectWidget
from j01.form.widget.select import getSelectDropDownWidget
from j01.form.widget.select import getMultiSelectDropDownWidget
from j01.form.widget.select import getGroupSelectWidget
from j01.form.widget.select import getDDSlickSelectWidget
from j01.form.widget.select import getDDSlickScrollbarSelectWidget

# text and html5 variants
from j01.form.widget.text import getTextWidget
from j01.form.widget.text import getEMailWidget
from j01.form.widget.text import getDateWidget
from j01.form.widget.text import getDatetimeWidget
from j01.form.widget.text import getDatetimeLocalWidget
from j01.form.widget.text import getTimeWidget
from j01.form.widget.text import getWeekWidget
from j01.form.widget.text import getMonthWidget
from j01.form.widget.text import getColorWidget
from j01.form.widget.text import getSearchWidget
from j01.form.widget.text import getURLWidget
from j01.form.widget.text import getNumberWidget
from j01.form.widget.text import getTelWidget

# textlines
from j01.form.widget.textlines import getTextLinesWidget

# textarea
from j01.form.widget.textarea import getTextAreaWidget

# j01.datepicker
try:
    # available if j01.datepicker package is available
    from j01.form.widget.datepicker import getDatePickerWidget
    from j01.form.widget.datepicker import getStartDatePickerWidget
    from j01.form.widget.datepicker import getEndDatePickerWidget
except ImportError:
    pass

# j01.datepickerzebra
try:
    # available if j01.datepickerzebra package is available
    from j01.form.widget.datepickerzebra import getZebraDatePickerWidget
    from j01.form.widget.datepickerzebra import getStartZebraDatePickerWidget
    from j01.form.widget.datepickerzebra import getEndZebraDatePickerWidget
    from j01.form.widget.datepickerzebra import getZebraDateTimePickerWidget
except ImportError:
    pass

# j01.datetimepicker
try:
    # available if j01.datetimepicker package is available
    from j01.form.widget.datetimepicker import getDateTimePickerWidget
except ImportError:
    pass

# j01.rater
try:
    # available if j01.rater package is available
    from j01.form.widget.rater import getFiveStarRatingWidget
    from j01.form.widget.rater import getFiveHalfStarRatingWidget
    from j01.form.widget.rater import getFiveHalfStarFullRatingWidget
except ImportError:
    pass

# j01.select2
try:
    # available if j01.select2 package is available
    from j01.form.widget.select2 import getSelect2Widget
    from j01.form.widget.select2 import getPromptSelect2Widget
    from j01.form.widget.select2 import getSingleSelect2Widget
    from j01.form.widget.select2 import getPromptSingleSelect2Widget
    from j01.form.widget.select2 import getSingleTagSelect2Widget
    from j01.form.widget.select2 import setUpSingleTagSelect2Widget
    from j01.form.widget.select2 import getTagListSelect2Widget
    from j01.form.widget.select2 import setUpTagListSelect2Widget
    from j01.form.widget.select2 import getLiveListSelect2Widget
    from j01.form.widget.select2 import getLiveTagSelect2Widget
except ImportError:
    pass

# m01.gmap
try:
    # available if m01.gmap package is available
    from j01.form.widget.gmap import getGMapWidget
    from j01.form.widget.gmap import getGeoPointGMapWidget
except ImportError:
    pass

# j01.selectordered
try:
    from j01.form.widget.selectordered import getOrderedSelectWidget
except ImportError:
    pass
