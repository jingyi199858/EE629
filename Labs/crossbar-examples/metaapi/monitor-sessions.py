import os
import sys
from pprint import pprint

import txaio

import argparse

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationRunner
from autobahn.twisted.wamp import ApplicationSession


class ClientSession(ApplicationSession):

   def onConnect(self):
      print('Client session connected.')
      self.join(self.config.realm)

   @inlineCallbacks
   def onJoin(self, details):
      print('Client session joined: {}'.format(details))

      def print_session(session_details):
         service_name = "???"
         peer = "???"
         if session_details:
            if 'authextra' in session_details and session_details['authextra']:
               service_name = session_details['authextra'].get('service_name', "???")
            if 'transport' in session_details and session_details['transport']:
               peer = session_details['transport'].get('peer', "???")
         print('service_name={} peer={}'.format(service_name.ljust(40), peer.ljust(20)))

      sessions = yield self.call('wamp.session.list')
      for session_id in sessions:
         try:
            session_info = yield self.call('wamp.session.get', session_id)
            print_session(session_info)
         except:
            pass

      def on_session_join(session_details):
         print("WAMP session has joined:")
         if session_details:
            print_session(session_details)

      yield self.subscribe(on_session_join, 'wamp.session.on_join')

      def on_session_leave(session_id):
         print("WAMP session has left: {}".format(session_id))

      yield self.subscribe(on_session_leave, 'wamp.session.on_leave')


if __name__ == '__main__':

   parser = argparse.ArgumentParser()
   parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output.')
   parser.add_argument('--url', dest='url', type=str, default='ws://192.168.40.121:8080/ws', help='The router URL (default: "ws://localhost:8080/ws").')
   parser.add_argument('--realm', dest='realm', type=str, default='realm1', help='The realm to join (default: "realm1").')

   args = parser.parse_args()

   if args.debug:
      txaio.start_logging(level='debug')
   else:
      txaio.start_logging(level='info')

   runner = ApplicationRunner(url=args.url, realm=args.realm)
   runner.run(ClientSession, auto_reconnect=True)
