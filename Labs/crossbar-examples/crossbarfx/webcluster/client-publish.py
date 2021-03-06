import os
import sys
import binascii
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.wamp.types import PublishOptions

TRANSPORT, SERIALIZER = sys.argv[1].split('-')
if TRANSPORT not in ['websocket', 'rawsocket']:
    raise Exception('invalid TRANSPORT "{}"'.format(TRANSPORT))
if SERIALIZER not in ['cbor', 'msgpack', 'json', 'ubjson']:
    raise Exception('invalid TRANSPORT "{}"'.format(TRANSPORT))

AUTHENTICATION = {
    'ticket': {
        'authid': 'user2',
        'ticket': 'secret2'
    }
}

if TRANSPORT == 'websocket':
    comp = Component(
        transports=[
            {
                "type": "websocket",
                "url": "ws://localhost:8080/ws",
                "endpoint": {
                    "type": "tcp",
                    "host": "localhost",
                    "port": 8080,
                },
                "serializers": [SERIALIZER],
            },
        ],
        realm="myrealm1",
        # authentication=AUTHENTICATION
    )
elif TRANSPORT == 'rawsocket':
    comp = Component(
        transports=[
            {
                "type": "rawsocket",
                "url": "rs://localhost:8080",
                "endpoint": {
                    "type": "tcp",
                    "host": "localhost",
                    "port": 8080,
                },
                "serializer": SERIALIZER,
            },
        ],
        realm="myrealm1",
        # authentication=AUTHENTICATION
    )

@comp.on_join
@inlineCallbacks
def _(session, details):
    print("joined: {}".format(details))
    topic_name = u"com.example.mytopic1"
    pid = os.getpid()
    counter = 0

    while session.is_connected():
        print("pid {} publish {} to '{}'".format(pid, counter, topic_name))
        data = os.urandom(10)
        session.publish(
            topic_name, pid, counter, foo='0x'+binascii.b2a_hex(data).decode(), baz=data,
            options=PublishOptions(exclude_me=False),
        )
        counter += 1
        yield sleep(1)

if __name__ == "__main__":
    run([comp], log_level='info')
