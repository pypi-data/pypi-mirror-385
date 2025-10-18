# Copyright (c) 2003-2005 Maxim Sobolev. All rights reserved.
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

from random import random
from hashlib import md5
from time import time
from sippy.SipGenericHF import SipGenericHF
from sippy.SipConf import SipConf
from sippy.ESipHeaderCSV import ESipHeaderCSV

class SipVia(SipGenericHF):
    hf_names = ('via', 'v')

    sipver = 'SIP/2.0'
    transport = 'UDP'
    hostname = None
    port = None
    params = None

    def __init__(self, body = None, cself = None):
        if body is not None and body.find(',') > -1:
            raise ESipHeaderCSV(None, body.split(','))
        SipGenericHF.__init__(self, body)
        if body is not None:
            assert cself is None
            return
        if cself is not None:
            self.parsed, self.sipver, self.transport, self.hostname, self.port, \
              self.params = cself.parsed, cself.sipver, cself.transport, \
              cself.hostname, cself.port, cself.params.copy()
            return
        self.parsed = True
        self.params = {'rport':None}
        self.hostname = SipConf.my_address
        self.port = SipConf.my_port
        self.transport = SipConf.my_transport

    def parse(self):
        self.params = {}
        parts, hostname = self.body.split(None, 1)
        self.sipver, self.transport = (p:=parts.rsplit('/', 1))[0].rstrip(), p[1].lstrip()
        hcomps = [x.strip() for x in hostname.split(';')]
        for param in hcomps[1:]:
            sparam = param.split('=', 1)
            if len(sparam) == 1:
                val = None
            else:
                val = sparam[1]
            self.params[sparam[0]] = val
        if hcomps[0].startswith('['):
            hcomps = hcomps[0].split(']', 1)
            self.hostname = hcomps[0] + ']'
            hcomps = hcomps[1].split(':', 1)
        else:
            hcomps = hcomps[0].split(':', 1)
            self.hostname = hcomps[0]
        if len(hcomps) == 2:
            try:
                self.port = int(hcomps[1])
            except Exception as e:
                # XXX: some bad-ass devices send us port number twice
                # While not allowed by the RFC, deal with it
                portparts = hcomps[1].split(':', 1)
                if len(portparts) != 2 or portparts[0] != portparts[1]:
                    raise e
                self.port = int(portparts[0])
        else:
            self.port = None
        self.parsed = True

    def __str__(self):
        return self.localStr()

    def localStr(self, local_addr = None):
        if not self.parsed:
            return self.body
        if local_addr is not None:
            (local_addr, local_port), local_transport = local_addr
        else:
            local_addr = local_port = local_transport = None
        if 'my' in dir(self.transport):
            transport = str(self.transport) if local_transport is None \
                                            else local_transport
            transport = transport.upper()
            if transport == 'WS': transport = 'WSS'
        else:
            transport = self.transport
        sipver = f'{self.sipver}/{transport}'
        if local_addr != None and 'my' in dir(self.hostname):
            s = sipver + ' ' + local_addr
        else:
            s = sipver + ' ' + str(self.hostname)
        if self.port != None:
            if local_port != None and 'my' in dir(self.port):
                if SipConf.port_needed(local_port, self.transport, local_transport):
                    s += ':' + str(local_port)
            else:
                s += ':' + str(self.port)
        for key, val in self.params.items():
            s += ';' + key
            if val != None:
                s += '=' + val
        return s

    def getCopy(self):
        if not self.parsed:
            return SipVia(self.body)
        return SipVia(cself=self)

    def genBranch(self):
        salt = str((random() * 1000000000) + time())
        self.params['branch'] = 'z9hG4bK' + md5(salt.encode()).hexdigest()

    def getBranch(self):
        return self.params.get('branch', None)

    def setParam(self, name, value = None):
        self.params[name] = value

    def getAddr(self):
        if self.port == '':
            return (self.hostname, SipConf.default_port)
        else:
            return (self.hostname, self.port)

    def getTAddr(self):
        rport = self.params.get('rport', None)
        if rport != None:
            rport = int(rport)
            if rport <= 0:
                rport = None
        if rport == None:
            rport = self.getAddr()[1]
            if rport == None:
                rport = SipConf.default_port
        return (self.params.get('received', self.getAddr()[0]), rport)

    def getCanName(self, name, compact = False):
        if compact:
            return 'v'
        return 'Via'

def _unit_test():
    via1 = 'SIP/2.0/UDP 203.193.xx.xx;branch=z9hG4bK2dd1.1102f3e2.0'
    v = SipVia(via1)
    v.parse()
    if via1 != str(v):
        return (False, 1)
    if v.getTAddr() != ('203.193.xx.xx', 5060):
        return (False, 2)
    return (True, None)
