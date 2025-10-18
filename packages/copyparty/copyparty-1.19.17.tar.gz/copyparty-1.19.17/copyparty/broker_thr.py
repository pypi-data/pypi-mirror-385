# coding: utf-8
from __future__ import print_function, unicode_literals

import os
import threading

from .__init__ import TYPE_CHECKING
from .broker_util import BrokerCli, ExceptionalQueue, NotExQueue
from .httpsrv import HttpSrv
from .util import HMaccas

if TYPE_CHECKING:
    from .svchub import SvcHub

class BrokerThr(BrokerCli):
    """external api; behaves like BrokerMP but using plain threads"""

    def __init__(self, hub )  :
        super(BrokerThr, self).__init__()

        self.hub = hub
        self.log = hub.log
        self.args = hub.args
        self.asrv = hub.asrv

        self.mutex = threading.Lock()
        self.num_workers = 1

        # instantiate all services here (TODO: inheritance?)
        self.iphash = HMaccas(os.path.join(self.args.E.cfg, "iphash"), 8)
        self.httpsrv = HttpSrv(self, None)
        self.reload = self.noop
        self.reload_sessions = self.noop

    def shutdown(self)  :
        # self.log("broker", "shutting down")
        self.httpsrv.shutdown()

    def noop(self)  :
        pass

    def ask(self, dest , *args )   :

        # new ipc invoking managed service in hub
        obj = self.hub
        for node in dest.split("."):
            obj = getattr(obj, node)

        return NotExQueue(obj(*args))  # type: ignore

    def say(self, dest , *args )  :
        if dest == "httpsrv.listen":
            self.httpsrv.listen(args[0], 1)
            return

        if dest == "httpsrv.set_netdevs":
            self.httpsrv.set_netdevs(args[0])
            return

        # new ipc invoking managed service in hub
        obj = self.hub
        for node in dest.split("."):
            obj = getattr(obj, node)

        obj(*args)  # type: ignore
