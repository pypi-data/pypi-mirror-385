###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH
# All Rights Reserved.
#
###############################################################################
"""Buttons
$Id: btn.py 5211 2025-04-06 22:31:46Z rodrigo.ristow $
"""
from __future__ import absolute_import

import j01.dialog.btn
import j01.jsonrpc.btn


###############################################################################
#
# decorators

handler = j01.jsonrpc.btn.handler
buttonAndHandler = j01.jsonrpc.btn.buttonAndHandler


###############################################################################
#
# buttons, handlers and action

Buttons = j01.jsonrpc.btn.Buttons
Handlers = j01.jsonrpc.btn.Handlers
ButtonAction = j01.jsonrpc.btn.ButtonAction


###############################################################################
#
# browser buttons

Button = j01.jsonrpc.btn.Button
CloseButton = j01.jsonrpc.btn.CloseButton


###############################################################################
#
# jsonrpc buttons

JSButton = j01.jsonrpc.btn.JSButton
JSONRPCButton = j01.jsonrpc.btn.JSONRPCButton
JSONRPCClickButton = j01.jsonrpc.btn.JSONRPCClickButton
JSONRPCContentButton = j01.jsonrpc.btn.JSONRPCContentButton
JSONRPCIconClickButton = j01.jsonrpc.btn.JSONRPCIconClickButton
JSONRPCSingleIconClickButton = j01.jsonrpc.btn.JSONRPCSingleIconClickButton


###############################################################################
#
# dialog buttons

DialogButton = j01.dialog.btn.DialogButton
ShowDialogButton = j01.dialog.btn.ShowDialogButton
DialogContentButton = j01.dialog.btn.DialogContentButton
DialogCloseButton = j01.dialog.btn.DialogCloseButton