# -*- coding: utf-8 -*-
#
# gdb-frontend is a easy, flexible and extensionable gui debugger
#
# https://github.com/rohanrhu/gdb-frontend
# https://oguzhaneroglu.com/projects/gdb-frontend/
#
# Licensed under GNU/GPLv3
# Copyright (C) 2019, Oğuzhan Eroğlu (https://oguzhaneroglu.com/) <rohanrhu2@gmail.com>

from ....api import debug

import json
import urllib


def run(request, params):
    if params is None: params = {}

    url_path = urllib.parse.urlparse(request.path)
    qs_params = urllib.parse.parse_qs(url_path.query)

    result_json = {}
    result_json["ok"] = True

    if qs_params.get("variable") is None:
        result_json["ok"] = False

    if result_json["ok"]:
        if "tree" in qs_params.keys():
            result_json["expression"] = debug.getVariableByExpression(qs_params["expression"][0], no_error=True).serializable()
        else:
            result_json["variable"] = debug.getVariableByExpression(qs_params["variable"][0], no_error=True).serializable()

    request.send_response(200)
    request.send_header("Content-Type", "application/json; charset=utf-8")
    request.end_headers()
    request.wfile.write(json.dumps(result_json).encode())