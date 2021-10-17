import os
import time
import random

import _thread

import txaio
txaio.use_twisted()

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from autobahn.util import utcnow
from autobahn.wamp.types import RegisterOptions
from autobahn.twisted.wamp import ApplicationSession

from twisted.internet.threads import deferToThread


def do_compute(call_no, delay):
    started = utcnow()
    process_id = os.getpid()
    thread_id = _thread.get_ident()

    # yes, we do the evil blocking thing here!
    # this is to simulate CPU intensive stuff
    time.sleep(delay)

    ended = utcnow()

    result = {
        'call_no': call_no,
        'started': started,
        'ended': ended,
        'process': process_id,
        'thread': thread_id
    }
    return result


class ComputeKernel(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        self._max_concurrency = self.config.extra['concurrency']
        self._current_concurrency = 0
        self._invocations_served = 0

        # adjust the background thread pool size
        reactor.suggestThreadPoolSize(self._max_concurrency)

        yield self.register(self.compute,
                            'com.example.compute',
                            options=RegisterOptions(invoke='roundrobin',
                                                    concurrency=self._max_concurrency))

        self.log.info('ComputeKernel ready with concurrency {}!'.format(self._max_concurrency))

    @inlineCallbacks
    def compute(self, call_no, delay):
        self._invocations_served += 1
        self._current_concurrency += 1
        self.log.info('starting compute() on background thread (current concurrency {current_concurrency} of max {max_concurrency}) ..', current_concurrency=self._current_concurrency, max_concurrency=self._max_concurrency)

        # now run our compute kernel on a background thread from the default Twisted reactor thread pool ..
        res = yield deferToThread(do_compute, call_no, delay)

        self._current_concurrency -= 1
        self.log.info('compute() ended from background thread ({invocations} invocations, current concurrency {current_concurrency} of max {max_concurrency})', invocations=self._invocations_served, current_concurrency=self._current_concurrency, max_concurrency=self._max_concurrency)

        returnValue(res)
