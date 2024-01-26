# -*- coding: utf-8 -*-
#
# gdb-frontend is a easy, flexible and extensionable gui debugger
#
# https://github.com/rohanrhu/gdb-frontend
# https://oguzhaneroglu.com/projects/gdb-frontend/
#
# Licensed under GNU/GPLv3
# Copyright (C) 2019, Oğuzhan Eroğlu (https://oguzhaneroglu.com/) <rohanrhu2@gmail.com>

from . import config
from . import commands
from . import plugin
from . import util
from . import urls
from . import settings
from . import http_server
from . import http_handler
from . import websocket
from . import debug_events
from .api import globalvars
from .api import url

import threading
import importlib
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python-libs"))
sys.path.insert(0, config.PLUGINS_DIR)


gdb = importlib.import_module("gdb")

try: gdb.execute("set confirm off")
except gdb.error as e: util.verbose(e)
try: gdb.execute("set non-stop off")
except gdb.error as e: util.verbose(e)
try: gdb.execute("set pagination off")
except gdb.error as e: util.verbose(e)

gdb.execute("shell tmux set-option status off")
gdb.execute("shell tmux set-option mouse on")

globalvars.init()
settings.init()
plugin.init()
plugin.loadAll()

globalvars.debugHandler = debug_events.GDBFrontendDebugEventsHandler()

all_urls = urls.urls

for _plugin_name, _plugin in plugin.plugins.items():
    for _url_name, _url in _plugin.urls.items():
        all_urls.prepend(_url_name, _url)

http_handler.url = url.URL(all_urls)

globalvars.httpServer = http_server.GDBFrontendHTTPServer(
    (config.BIND_ADDRESS, config.HTTP_PORT),
    http_handler.RequestHandler
)

thread = threading.Thread(target=globalvars.httpServer.serve_forever)
thread.setDaemon(True)
thread.start()

config.HTTP_PORT = globalvars.httpServer.server_port

if config.MMAP_PATH:
    import mmap
    import ctypes
    
    fd = os.open(config.MMAP_PATH, os.O_RDWR)
    mmapBuff = mmap.mmap(fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_WRITE)

    http_port = ctypes.c_uint16.from_buffer(mmapBuff, 0)
    
    http_port.value = globalvars.httpServer.server_port