# Copyright (c) 2006-2014 Sippy Software, Inc. All rights reserved.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import ctypes, os, platform
import ctypes.util

CLOCK_REALTIME = 0
CLOCK_MONOTONIC = 4 # see <linux/time.h> / <include/time.h>
if platform.system() == 'FreeBSD':
    # FreeBSD-specific
    CLOCK_UPTIME = 5
    CLOCK_UPTIME_PRECISE = 7
    CLOCK_UPTIME_FAST = 8
    CLOCK_MONOTONIC_PRECISE = 11
    CLOCK_MONOTONIC_FAST = 12
elif platform.system() == 'Linux':
    # Linux-specific
    CLOCK_BOOTTIME = 7

class timespec32(ctypes.Structure):
    _fields_ = [
        ('tv_sec', ctypes.c_long),
        ('tv_nsec', ctypes.c_long)
    ]

class timespec64(ctypes.Structure):
    _fields_ = [
        ('tv_sec', ctypes.c_longlong),
        ('tv_nsec', ctypes.c_long)
    ]

def find_lib(libname, paths):
    spaths = ['%s/lib%s.so' % (path, libname) for path in paths]
    for path in spaths:
        if os.path.islink(path):
            libcname = os.readlink(path)
            return (libcname)
        elif os.path.isfile(path):
            for line in open(path, 'r').readlines():
                parts = line.split(' ')
                if parts[0] != 'GROUP':
                    continue
                libcname = parts[2]
                return (libcname)
    return ctypes.util.find_library(libname)

def find_symbol(symname, lnames, paths):
    for lname in lnames:
        lib = find_lib(lname, paths)
        if lib == None:
            continue
        try:
            llib = ctypes.CDLL(lib, use_errno = True)
            return llib.__getitem__(symname)
        except:
            continue
    raise Exception('Bah, %s cannot be found in libs %s in the paths %s' % (symname, lnames, paths))

clock_gettime = find_symbol('clock_gettime', ('c', 'rt'), ('/usr/lib', '/lib'))
for tstype in timespec64, timespec32:
    clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(tstype)]
    t = tstype()
    if clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(t)) != 0 or t.tv_nsec == 0:
        continue
    ns1 = t.tv_nsec
    if clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(t)) != 0 or t.tv_nsec == 0:
        continue
    if ns1 != t.tv_nsec:
        timespec = tstype
        break
else:
    raise Exception('Cannot deduce format of the struct timespec')

clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

def clock_getitime(type):
    t = timespec()
    if clock_gettime(type, ctypes.pointer(t)) != 0:
        errno_ = ctypes.get_errno()
        raise OSError(errno_, os.strerror(errno_))
    return (t.tv_sec, t.tv_nsec)

def clock_getntime(type):
    ts = clock_getitime(type)
    return (ts[0] * 10**9 + ts[1])

def clock_getdtime(type):
    ts = clock_getitime(type)
    return float(ts[0]) + float(ts[1] * 1e-09)

if __name__ == "__main__":
    print('%.10f' % (clock_getdtime(CLOCK_REALTIME),))
    print('%.10f' % (clock_getdtime(CLOCK_REALTIME) - clock_getdtime(CLOCK_MONOTONIC),))
    if platform.system() == 'FreeBSD':
        print('%.10f' % (clock_getdtime(CLOCK_REALTIME) - clock_getdtime(CLOCK_UPTIME),))
        print('%.10f' % (clock_getdtime(CLOCK_REALTIME) - clock_getdtime(CLOCK_UPTIME_PRECISE),))
        print('%.10f' % (clock_getdtime(CLOCK_REALTIME) - clock_getdtime(CLOCK_UPTIME_FAST),))
        print('%.10f' % (clock_getdtime(CLOCK_REALTIME) - clock_getdtime(CLOCK_MONOTONIC_PRECISE),))
        print('%.10f' % (clock_getdtime(CLOCK_REALTIME) - clock_getdtime(CLOCK_MONOTONIC_FAST),))
