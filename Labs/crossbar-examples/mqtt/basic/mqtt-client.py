#
# Example MQTT client using paho-mqtt
#

import os
import time
import struct
import binascii

import paho.mqtt.client as paho

# binary payload format we use in this example:
# unsigned short + signed int + 8 bytes (all big endian)
FORMAT = '>Hl8s'

# topic we publish and subscribe to
TOPIC = 'mqtt/test/mytopic1'

pid = os.getpid()
print('MQTT client starting with PID {}..'.format(pid))

client = paho.Client()

# called when the client has connected to the MQTT broker (or when the client reconnects
# upon a lost connection)
def on_connect(client, userdata, flags, rc):
    print('on_connect({}, {}, {}, {})'.format(client, userdata, flags, rc))

    # subscribe to a topic, this will fire on_message() upon receiving events
    client.subscribe(TOPIC, qos=0)

# called when a message has been received on a topic that the client subscribes to.
def on_message(client, userdata, msg):
    pid, seq, ran = struct.unpack(FORMAT, msg.payload)
    print('event received on topic {}: pid={}, seq={}, ran={}'.format(msg.topic, pid, seq, binascii.b2a_hex(ran)))

client.on_connect = on_connect
client.on_message = on_message

# connect to the universal transport we configured in Crossbar.io
client.connect('localhost', port=8080)

# connect to the dedicated MQTT transport we configured in Crossbar.io
# client.connect('localhost', port=1883)

# start the network loop in a background thread
# see: https://pypi.python.org/pypi/paho-mqtt#network-loop
client.loop_start()

# publish once a second forever ..
seq = 1
while True:
    payload = struct.pack(FORMAT, pid, seq, os.urandom(8))

    result, mid = client.publish(TOPIC, payload, qos=0, retain=True)
    print('event published: result={}, mid={}'.format(result, mid))

    seq += 1
    time.sleep(1)
