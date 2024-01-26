# -*- coding: utf-8 -*-
#
# gdb-frontend is a easy, flexible and extensionable gui debugger
#
# https://github.com/rohanrhu/gdb-frontend
# https://oguzhaneroglu.com/projects/gdb-frontend/
#
# Licensed under GNU/GPLv3
# Copyright (C) 2019, Oğuzhan Eroğlu (https://oguzhaneroglu.com/) <rohanrhu2@gmail.com>

# Example GDBFrontend Plugin

from ... import plugin
from ...api import globalvars

import importlib
import json


gdb = importlib.import_module("gdb")

class HelloPlugin(plugin.GDBFrontendPlugin):
    def __init__(self):
        plugin.GDBFrontendPlugin.__init__(self)

    def loaded(self):
        gdb.events.new_objfile.connect(self.gdb_on_new_objfile)

    def unloaded(self):
        gdb.events.new_objfile.disconnect(self.gdb_on_new_objfile)

    def gdb_on_new_objfile(self, event):
        print("[HELLO] GDB Event: new_objfile:", event)
    
    def event(self, client, event, message):
        print("[HELLO] GDBFrontend Event Client#%d: %s: %s" % (client.client_id, event, message))

        for _client in globalvars.httpServer.ws_clients:
            _client.wsSend(json.dumps({
                "event": "hello",
                "reply_to": event
            }))