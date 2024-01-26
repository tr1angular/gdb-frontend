# -*- coding: utf-8 -*-
#
# gdb-frontend is a easy, flexible and extensionable gui debugger
#
# https://github.com/rohanrhu/gdb-frontend
# https://oguzhaneroglu.com/projects/gdb-frontend/
#
# Licensed under GNU/GPLv3
# Copyright (C) 2019, Oğuzhan Eroğlu (https://oguzhaneroglu.com/) <rohanrhu2@gmail.com>

import threading

class AtomicDebugFlags():
    """
    Atomic debug flags for debugging behaviours.
    """

    """
    Flag for checking if the process is running without needing thread-safe GDB API calls.
    ! Usable with non-stop mode is off!
    """
    IS_RUNNING = 9

    """
    Atomic flag for selected frames.
    It is a need due to a GDB bug.
    This bug causes forgetting selected frames
    once switching between threads.
    """
    SELECTED_FRAMES = 1

    """
    Special-puroose interrupt flags.
    These flags provide information about reason last interrupt.
    These special-purpose interrupts will go to run immediately by GDBFrontend
    after their special behaviours.
    """

    """
    Flag for breakpoint adding during process runtime.
    With this approach, breakpoints can be added while process is running
    and application will stop immediately when it comes on the breakpoint.
    """
    IS_INTERRUPTED_FOR_BREAKPOINT_ADD = 2
    IS_INTERRUPTED_FOR_BREAKPOINT_SET = 5
    IS_INTERRUPTED_FOR_BREAKPOINT_DEL = 6
    IS_INTERRUPTED_FOR_BREAKPOINT_MOD = 7

    """
    Flag for interrupt for sending posix SIGKILL to process.
    """
    IS_INTERRUPTED_FOR_TERMINATE = 3

    """
    Flag for posix-signal sending to process.
    """
    IS_INTERRUPTED_FOR_SIGNAL = 4
    
    """
    Flag for interrupting to provide thread-safety and avoid main-thread blockings.
    """
    IS_INTERRUPTED_FOR_THREAD_SAFETY = 8

    def __init__(self, num=0):
        self.lock = threading.Lock()
        
        self.flags = {}
        self.initFlags()

    def initFlags(self):
        self.flags[__class__.IS_RUNNING] = False
        self.flags[__class__.IS_INTERRUPTED_FOR_THREAD_SAFETY] = False
        self.flags[__class__.IS_INTERRUPTED_FOR_BREAKPOINT_ADD] = False
        self.flags[__class__.IS_INTERRUPTED_FOR_BREAKPOINT_SET] = False
        self.flags[__class__.IS_INTERRUPTED_FOR_BREAKPOINT_DEL] = False
        self.flags[__class__.IS_INTERRUPTED_FOR_BREAKPOINT_MOD] = False
        self.flags[__class__.IS_INTERRUPTED_FOR_TERMINATE] = False
        self.flags[__class__.IS_INTERRUPTED_FOR_SIGNAL] = False
        self.flags[__class__.SELECTED_FRAMES] = {}

    def incr(self, flag, diff=1):
        self.lock.acquire()
        self.flags[flag] += diff
        self.lock.release()

    def decr(self, flag, diff=1):
        self.lock.acquire()
        self.flags[flag] -= diff
        self.lock.release()

    def set(self, flag, val):
        self.lock.acquire()
        self.flags[flag] = val
        self.lock.release()

    def get(self, flag):
        self.lock.acquire()
        val = self.flags[flag]
        self.lock.release()

        return val