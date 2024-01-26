# -*- coding: utf-8 -*-
#
# gdb-frontend is a easy, flexible and extensionable gui debugger
#
# https://github.com/rohanrhu/gdb-frontend
# https://oguzhaneroglu.com/projects/gdb-frontend/
#
# Licensed under GNU/GPLv3
# Copyright (C) 2019, Oğuzhan Eroğlu (https://oguzhaneroglu.com/) <rohanrhu2@gmail.com>

from .... import util
from ....api import debug

import json
import urllib
import importlib

gdb = importlib.import_module("gdb")


def run(request, params):
    if params is None: params = {}

    url_path = urllib.parse.urlparse(request.path)
    qs_params = urllib.parse.parse_qs(url_path.query)

    result_json = {}
    result_json["ok"] = True

    def response():
        nonlocal request
        nonlocal params
        nonlocal result_json

        request.send_response(200)
        request.send_header("Content-Type", "application/json; charset=utf-8")
        request.end_headers()
        request.wfile.write(json.dumps(result_json).encode())

    if qs_params["number"] is None:
        result_json["ok"] = False
        response()
    
    if "condition" not in qs_params or qs_params["condition"] is None:
        condition = ""
    else:
        condition = qs_params["condition"][0]

    debug.setBreakpointCondition(debug.getBreakpoint(qs_params["number"][0]), condition)

    response()