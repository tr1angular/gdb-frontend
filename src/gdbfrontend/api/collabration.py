# -*- coding: utf-8 -*-
#
# gdb-frontend is a easy, flexible and extensionable gui debugger
#
# https://github.com/rohanrhu/gdb-frontend
# https://oguzhaneroglu.com/projects/gdb-frontend/
#
# Licensed under GNU/GPLv3
# Copyright (C) 2019, Oğuzhan Eroğlu (https://oguzhaneroglu.com/) <rohanrhu2@gmail.com>

"""
GDBFrontend Enhanced Collabration API
"""

from .. import config
from .. import settings
from .. import util
from ..api import debug
from ..api import flags
from ..api import globalvars

import importlib
import json
import threading


gdb = importlib.import_module("gdb")

globalvars.init()
settings.init()

state = globalvars.collabration_state

lock = False

def init():
    global lock
    lock = threading.Lock()

    global state

def access(function):
    global lock
    global state

    lock.acquire()
    function()
    lock.release()

def checkClientWindowResolutions():
    """
    Checks window sizes of all client browsers and
    returns true or false as they are same or not.
    """

    global state
    
    res = globalvars.httpServer.ws_clients[0].screen_resolution
    
    for client in globalvars.httpServer.ws_clients[1:]:
        if \
            abs(res[0] - client.screen_resolution[0]) > settings.ENHANCED_COLLABRATION_RESOLUTION_TRESHOLD \
            or \
            abs(res[1] - client.screen_resolution[1]) > settings.ENHANCED_COLLABRATION_RESOLUTION_TRESHOLD \
        :
            return False
    
    return True

@debug.threadSafe(no_interrupt=True)
def enableEnhancedCollabration():
    """
    Enables enhanced collabration features
    that synchronize all clients.
    """

    global state

    globalvars.is_enhanced_collabration = True
    
    for client in globalvars.httpServer.ws_clients:
        client.wsSend("{\"event\": \"enhanced_collabration_enabled\"}")
    
    return True

@debug.threadSafe(no_interrupt=True)
def disableEnhancedCollabration():
    """
    Disables enhanced collabration features
    that synchronize all clients.
    """

    global state

    globalvars.is_enhanced_collabration = False

    globalvars.collabration_state["draw"]["path_color"] = 0
    globalvars.collabration_state["draw"]["paths"] = []
    
    for client in globalvars.httpServer.ws_clients:
        client.wsSend("{\"event\": \"enhanced_collabration_disabled\"}")
    
    return True

def setState(new_state, client_id=0):
    """
    Sets the state of collabrative things
    and sends new sate to all clients.
    """

    global state

    util.verbose("api.collabration.setState()", new_state)

    state["editor"]["file"] = new_state["editor"]["file"]
    state["editor"]["open_files"] = new_state["editor"]["open_files"]
    
    client = globalvars.httpServer.getClientById(client_id)
    client.screen_resolution = new_state["resolution"]
    
    sendState(from_client=client_id)

def setState__scroll(scroll_position, client_id=0):
    """
    Sets the scroll position of current editor
    and sends new sate to all clients.
    """

    global state

    util.verbose("api.collabration.setState__scroll()", scroll_position)

    state["editor"]["scroll_position"] = scroll_position

    sendState__scroll(from_client=client_id)

def setState__cursor(cursor_position, client_id=0):
    """
    Sets the cursor position of current editor
    and sends new sate to all clients.
    """

    global state

    util.verbose("api.collabration.setState__cursor()", cursor_position)

    state["editor"]["cursor_position"] = cursor_position

    sendState__cursor(from_client=client_id)

def setState__watches(watches, client_id=0):
    """
    Sets the watches state
    and sends new sate to all clients.
    """

    global state

    util.verbose("api.collabration.setState__watches()", watches)

    state["watches"] = watches

    sendState__watches(from_client=client_id)

def setState__draw_path(path, client_id=0):
    """
    Adds the path to drawing paths
    and sends new sate to all clients.
    """

    global state

    util.verbose("api.collabration.setState__draw_path()", path)

    state["draw"]["paths"].append(path)

    state["draw"]["path_color"] = (state["draw"]["path_color"] + 1) % 10

    sendState__draw_path(from_client=client_id)

def setState__draw_clear(client_id=0):
    """
    Clears drawing paths
    and sends new sate to all clients.
    """

    global state

    util.verbose("api.collabration.setState__draw_clear()")

    state["draw"]["path_color"] = 0
    state["draw"]["paths"] = []

    sendState__draw_clear(from_client=client_id)

@debug.threadSafe(no_interrupt=True)
def sendState(from_client=0):
    """
    Sends collabration state to all clients.
    """

    global state

    if config.VERBOSE:
        message = {}
        message["event"] = "enhanced_collabration_state"
        message["state"] = state
        message["from_client"] = from_client
        message["state"]["is_resolutions_equal"] = checkClientWindowResolutions()
        
        util.verbose("api.collabration.sendState()", message)

    for client in globalvars.httpServer.ws_clients:
        message = {}
        message["event"] = "enhanced_collabration_state"
        message["state"] = state
        message["from_client"] = from_client
        message["state"]["is_resolutions_equal"] = checkClientWindowResolutions()
        message["is_from_me"] = (from_client == client.client_id)
        message_json = json.dumps(message)

        client.wsSend(message_json)
    
    return True

def sendState__scroll(from_client=0):
    """
    Sends collabration state of scroll position to all clients.
    """

    global state

    if config.VERBOSE:
        message = {}
        message["event"] = "enhanced_collabration_state__scroll"
        message["scroll_position"] = state["editor"]["scroll_position"]
        
        util.verbose("api.collabration.sendState__scroll()", message)

    for client in globalvars.httpServer.ws_clients:
        message = {}
        message["event"] = "enhanced_collabration_state__scroll"
        message["scroll_position"] = state["editor"]["scroll_position"]
        message["is_from_me"] = (from_client == client.client_id)
        message_json = json.dumps(message)

        client.wsSend(message_json)
    
    return True

def sendState__cursor(from_client=0):
    """
    Sends collabration state of cursor position to all clients.
    """

    global state


    if config.VERBOSE:
        message = {}
        message["event"] = "enhanced_collabration_state__cursor"
        message["cursor_position"] = state["editor"]["cursor_position"]
        
        util.verbose("api.collabration.sendState__cursor()", message)

    for client in globalvars.httpServer.ws_clients:
        message = {}
        message["event"] = "enhanced_collabration_state__cursor"
        message["cursor_position"] = state["editor"]["cursor_position"]
        message["is_from_me"] = (from_client == client.client_id)
        message_json = json.dumps(message)

        client.wsSend(message_json)
    
    return True

def sendState__watches(from_client=0):
    """
    Sends collabration state of watches to all clients.
    """

    global state

    if config.VERBOSE:
        message = {}
        message["event"] = "enhanced_collabration_state__watches"
        message["watches"] = state["watches"]
        
        util.verbose("api.collabration.sendState__watches()", message)

    for client in globalvars.httpServer.ws_clients:
        message = {}
        message["event"] = "enhanced_collabration_state__watches"
        message["watches"] = state["watches"]
        message["is_from_me"] = (from_client == client.client_id)
        message_json = json.dumps(message)

        client.wsSend(message_json)
    
    return True

def sendState__draw_path(from_client=0):
    """
    Sends the drawing path to all clients.
    """

    global state

    if config.VERBOSE:
        message = {}
        message["event"] = "enhanced_collabration_state__draw_path"
        message["path"] = state["draw"]["paths"][-1]
        message["draw"] = {}
        message["draw"]["path_color"] = state["draw"]["path_color"]
        
        util.verbose("api.collabration.sendState__draw_path()", message)

    for client in globalvars.httpServer.ws_clients:
        message = {}
        message["event"] = "enhanced_collabration_state__draw_path"
        message["path"] = state["draw"]["paths"][-1]
        message["is_from_me"] = (from_client == client.client_id)
        message["draw"] = {}
        message["draw"]["path_color"] = state["draw"]["path_color"]
        message_json = json.dumps(message)

        client.wsSend(message_json)
    
    return True

def sendState__draw_clear(from_client=0):
    """
    Sends the clear drawings signal to all clients.
    """

    global state

    if config.VERBOSE:
        message = {}
        message["event"] = "enhanced_collabration_state__draw_clear"
        
        util.verbose("api.collabration.sendState__draw_path()", message)

    for client in globalvars.httpServer.ws_clients:
        message = {}
        message["event"] = "enhanced_collabration_state__draw_clear"
        message["is_from_me"] = (from_client == client.client_id)
        message_json = json.dumps(message)

        client.wsSend(message_json)
    
    return True