# Author: Sakthi Santhosh
# Created on: 10/10/2023
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
from random import random
from sys import exit
from threading import Event
from time import sleep
from json import dumps

message_count = 10
received_count = 0
received_all_event = Event()

def on_connection_interrupted(connection, error, **kwargs):
    print("Error: Connection interrupted: {}".format(error))


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Info: Connection resumed.\n  return_code: {}\n  session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Info: Session did not persist. Resubscribing to existing topics...")

        resubscribe_future, _ = connection.resubscribe_existing_topics()

        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()

    print("Info: Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results["topics"]:
        if qos is None:
            exit("Error: Server rejected resubscribe to topic: {}".format(topic))


def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Info: Received message from topic \"{}\": {}".format(topic, payload))

    global message_count, received_count

    received_count += 1

    if received_count == message_count:
        received_all_event.set()

def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Info: Connection successful.\n  return_code: {}\n  session_present: {}".format(callback_data.return_code, callback_data.session_present))

def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailuredata)
    print("Error: Connection failed with code: {}".format(callback_data.error))

def on_connection_closed(connection, callback_data):
    print("Info: Connection closed.")

if __name__ == "__main__":
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint="a2udp0nfk450zx-ats.iot.ap-south-1.amazonaws.com",
        port=8883,
        cert_filepath="/home/pi/.aws/iot/certs/test-thing00/certificate.pem.crt",
        pri_key_filepath="/home/pi/.aws/iot/certs/test-thing00/private.pem.key",
        ca_filepath="/home/pi/.aws/iot/certs/root-ca1.pem",
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id="test-thing00/rpi-testing",
        clean_session=False,
        keep_alive_secs=30,
        http_proxy_options=None,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed
    )

    connect_future = mqtt_connection.connect()

    connect_future.result()
    print("Info: Connected with the MQTT broker.")

    message_topic = "test-thing00/rpi-testing/test"

    print("Info: Subscribing to topic \"{}\"...".format(message_topic))

    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=message_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received
    )
    subscribe_result = subscribe_future.result()

    print("Info: Subscribed with {}.".format(str(subscribe_result["qos"])))

    publish_count = 1

    while publish_count <= message_count:
        message = {
            "entropy": random(),
            "counter": publish_count
        }

        print("Info: Publishing message to topic \"{}\": {}".format(message_topic, message))

        message_json = dumps(message)

        mqtt_connection.publish(
            topic=message_topic,
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        sleep(1)

        publish_count += 1

    if message_count != 0 and not received_all_event.is_set():
        print("Info: Waiting for all messages to be received...")

    received_all_event.wait()
    print("Info: {} message(s) received.".format(received_count))
    print("Info: Disconnecting...")

    disconnect_future = mqtt_connection.disconnect()

    disconnect_future.result()
