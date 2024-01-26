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
from . import plugin
from . import util
from . import websocket
from . import terminal_daemon
from .api import debug
from .api import collabration
from .api import flags
from .api import globalvars

import importlib
import json
import time
import traceback


config.init()

gdb = importlib.import_module("gdb")

globalvars.init()
plugin.init()
collabration.init()

class GDBFrontendDebugEventsHandler:
    cont_time = False
    
    def __init__(self):
        self.connectGDBEvents()
    
    def connectGDBEvents(self):
        gdb.events.new_objfile.connect(self.gdb_on_new_objfile)
        gdb.events.clear_objfiles.connect(self.gdb_on_clear_objfiles)
        gdb.events.breakpoint_created.connect(self.gdb_on_breakpoint_created)
        gdb.events.breakpoint_modified.connect(self.gdb_on_breakpoint_modified)
        gdb.events.breakpoint_deleted.connect(self.gdb_on_breakpoint_deleted)
        gdb.events.stop.connect(self.gdb_on_stop)
        gdb.events.new_thread.connect(self.gdb_on_new_thread)
        gdb.events.cont.connect(self.gdb_on_cont)
        gdb.events.exited.connect(self.gdb_on_exited)
        gdb.events.inferior_deleted.connect(self.gdb_on_inferior_deleted)
        gdb.events.new_inferior.connect(self.gdb_on_new_inferior)

    def disconnectGDBEvents(self):
        gdb.events.new_objfile.disconnect(self.gdb_on_new_objfile)
        gdb.events.clear_objfiles.disconnect(self.gdb_on_clear_objfiles)
        gdb.events.breakpoint_created.disconnect(self.gdb_on_breakpoint_created)
        gdb.events.breakpoint_modified.disconnect(self.gdb_on_breakpoint_modified)
        gdb.events.breakpoint_deleted.disconnect(self.gdb_on_breakpoint_deleted)
        gdb.events.stop.disconnect(self.gdb_on_stop)
        gdb.events.new_thread.disconnect(self.gdb_on_new_thread)
        gdb.events.cont.disconnect(self.gdb_on_cont)
        gdb.events.exited.disconnect(self.gdb_on_exited)
        gdb.events.inferior_deleted.disconnect(self.gdb_on_inferior_deleted)
        gdb.events.new_inferior.disconnect(self.gdb_on_new_inferior)

    def gdb_on_new_objfile(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_new_objfile()")

        globalvars.inferior_run_times[gdb.selected_inferior().num] = int(time.time())

        def _mt():
            self.gdb_on_new_objfile__mT(event)
        
        gdb.post_event(_mt)

    def gdb_on_new_objfile__mT(self, event):
        pass

    def gdb_on_clear_objfiles(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_clear_objfiles()")

        if globalvars.dont_emit_until_stop_or_exit: return

        gdb.post_event(self.gdb_on_clear_objfiles__mT)

    def gdb_on_clear_objfiles__mT(self):
        pass

    def gdb_on_breakpoint_created(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_breakpoint_created()")

        gdb.post_event(self.gdb_on_breakpoint_created__mT)

    def gdb_on_breakpoint_created__mT(self):
        interrupted = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_ADD)

    def gdb_on_breakpoint_modified(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_breakpoint_modified()")

        gdb.post_event(self.gdb_on_breakpoint_modified__mT)

    def gdb_on_breakpoint_modified__mT(self):
        interrupted = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_MOD)
        interrupted = interrupted or globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_SET)

    def gdb_on_breakpoint_deleted(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_breakpoint_deleted()")

        if globalvars.dont_emit_until_stop_or_exit: return
        
        gdb.post_event(self.gdb_on_breakpoint_deleted__mT)

    def gdb_on_breakpoint_deleted__mT(self):
        interrupted = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_DEL)

    def gdb_on_stop(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_stop()")

        globalvars.debugFlags.set(flags.AtomicDebugFlags.IS_RUNNING, False)

        globalvars.dont_emit_until_stop_or_exit = False
        globalvars.step_time = time.time() * 1000 - self.cont_time
        
        gdb.post_event(self.gdb_on_stop__mT)

    def gdb_on_stop__mT(self):
        interrupted_for_thread_safety = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_THREAD_SAFETY)
        interrupted_for_terminate = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_TERMINATE)
        interrupted_for_signal = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_SIGNAL)
        interrupted_for_breakpoint_add = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_ADD)
        interrupted_for_breakpoint_del = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_DEL)
        interrupted_for_breakpoint_mod = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_MOD)
        interrupted_for_breakpoint_set = globalvars.debugFlags.get(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_SET)

        if interrupted_for_thread_safety:
            globalvars.debugFlags.set(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_THREAD_SAFETY, False)

            util.verbose("GDBFrontendDebugEventsHandler", "Continuing for interrupt: THREAD_SAFETY.")
            
            try:
                gdb.execute("c")
            except Exception as e:
                print("[Error] (GDBFrontendSocket.gdb_on_stop__mT)", e)
        elif interrupted_for_terminate:
            util.verbose("GDBFrontendDebugEventsHandler", "Terminating for interrupt: TERMINATE.")

            globalvars.debugFlags.set(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_TERMINATE, False)
            
            try:
                gdb.execute("kill")
            except Exception as e:
                print("[Error] (GDBFrontendSocket.gdb_on_stop__mT)", e)
        elif interrupted_for_signal:
            try:
                util.verbose("GDBFrontendDebugEventsHandler", "Continuing for interrupt: SIGNAL.")
                gdb.execute("c")
            except Exception as e:
                print("[Error] (GDBFrontendSocket().gdb_on_stop__mT)", e)
        elif interrupted_for_breakpoint_add:
            util.verbose("GDBFrontendDebugEventsHandler", "Continuing for interrupt: BREAKPOINT_ADD.")

            globalvars.debugFlags.set(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_ADD, False)

            if "address" in interrupted_for_breakpoint_add:
                bp = debug.Breakpoint(
                    address = interrupted_for_breakpoint_add["address"]
                )
            else:
                bp = debug.Breakpoint(
                    source = interrupted_for_breakpoint_add["file"],
                    line = interrupted_for_breakpoint_add["line"]
                )

            try:
                gdb.execute("c")
            except Exception as e:
                print("[Error] (GDBFrontendSocket().gdb_on_stop__mT)", e)
        elif interrupted_for_breakpoint_del:
            util.verbose("GDBFrontendDebugEventsHandler", "Continuing for interrupt: BREAKPOINT_DEL.")

            interrupted_for_breakpoint_del.delete()

            globalvars.debugFlags.set(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_DEL, False)

            try:
                gdb.execute("c")
            except Exception as e:
                print("[Error] (GDBFrontendSocket().gdb_on_stop__mT)", e)
        elif interrupted_for_breakpoint_mod:
            util.verbose("GDBFrontendDebugEventsHandler", "Continuing for interrupt: BREAKPOINT_MOD.")

            globalvars.debugFlags.set(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_MOD, False)

            interrupted_for_breakpoint_mod["breakpoint"].condition = interrupted_for_breakpoint_mod["condition"]

            try:
                gdb.execute("c")
            except Exception as e:
                print("[Error] (GDBFrontendSocket().gdb_on_stop__mT)", e)
        elif interrupted_for_breakpoint_set:
            util.verbose("GDBFrontendDebugEventsHandler", "Continuing for interrupt: BREAKPOINT_SET.")

            globalvars.debugFlags.set(flags.AtomicDebugFlags.IS_INTERRUPTED_FOR_BREAKPOINT_SET, False)

            interrupted_for_breakpoint_set["breakpoint"].enabled = interrupted_for_breakpoint_set["is_enabled"]

            try:
                gdb.execute("c")
            except Exception as e:
                print("[Error] (GDBFrontendSocket().gdb_on_stop__mT)", e)

    def gdb_on_new_thread(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_new_thread()")

        def _mt():
            self.gdb_on_new_thread__mT(event)

        gdb.post_event(_mt)

    def gdb_on_new_thread__mT(self, event):
        inferior_thread = event.inferior_thread
        
        if isinstance(inferior_thread, gdb.InferiorThread):
            globalvars.inferior_run_times[event.inferior_thread.inferior.num] = int(time.time())
        elif isinstance(inferior_thread, gdb.Inferior):
            globalvars.inferior_run_times[event.inferior_thread.num] = int(time.time())

    def gdb_on_cont(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_cont()")

        globalvars.debugFlags.set(flags.AtomicDebugFlags.IS_RUNNING, True)

        self.cont_time = time.time() * 1000
        
        if globalvars.dont_emit_until_stop_or_exit: return
        
        gdb.post_event(self.gdb_on_cont__mT)

    def gdb_on_cont__mT(self):
        pass

    def gdb_on_exited(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_exited()")

        globalvars.debugFlags.set(flags.AtomicDebugFlags.IS_RUNNING, False)

        globalvars.dont_emit_until_stop_or_exit = False
        globalvars.step_time = False

        def _mt():
            self.gdb_on_exited__mT(event)
        
        gdb.post_event(_mt)

    def gdb_on_exited__mT(self, event):
        response = {}

        try:
            del globalvars.inferior_run_times[event.inferior.num]
        except Exception as e:
            util.verbose("GDBFrontendDebugEventsHandler",  e, traceback.format_exc())

        globalvars.debugFlags.set(flags.AtomicDebugFlags.SELECTED_FRAMES, {})

    def gdb_on_new_inferior(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_new_inferior()")

        globalvars.inferior_run_times[event.inferior.num] = int(time.time())

        if globalvars.dont_emit_until_stop_or_exit: return

        def _mt():
            self.gdb_on_new_inferior__mT(event)
        
        gdb.post_event(_mt)

    def gdb_on_new_inferior__mT(self, event):
        pass

    def gdb_on_inferior_deleted(self, event):
        util.verbose("GDBFrontendDebugEventsHandler", "gdb_on_inferior_deleted()")

        def _mt():
            self.gdb_on_inferior_deleted__mT(event)
        
        gdb.post_event(_mt)
        
    def gdb_on_inferior_deleted__mT(self, event):
        response = {}

        del globalvars.inferior_run_times[event.inferior.num]

        if globalvars.dont_emit_until_stop_or_exit: return