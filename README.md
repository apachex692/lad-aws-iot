# Learning and Development: AWS IoT Core Provisioning & MQTT3 Pub/Sub Test over MTLS

A library to automate just-in-time provisioning of IoT Things (devices) and testing the publish/subscribe capabilities of the system.

- **Author:** Sakthi Santhosh
- **Created on:** 12/10/2023

## Pre-requisites

- AWS Account
- AWS IAM User Credentials Stored to `~/aws/`
- `python3` and `pip` Installed


## Getting Started

- Run the following in your shell to set-up a virtual environment in the project directory and install the required packages.

```
chmod +x ./scripts/starts.sh
./start.sh
```

- Run the following file to provision a IoT Thing and download certificates on your device. Make sure to replace `<thing-name>` with the name of your choice.

```
python3 -c "from lib.provisioner import Thing; Thing(\"<thing-name>\").jit_provision()"
```

## Testing

- To test, run the python script avaibale at `./samples/pubsub_test.py`. Ensure to replace the following block of code with your own values available at line 68.

```
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint="<endpoint>",
    port=8883,
    cert_filepath="<path>/certificate.pem.crt",
    pri_key_filepath="<path>/private.pem.key",
    ca_filepath="<path>/root-ca1.pem",
    on_connection_interrupted=on_connection_interrupted,
    on_connection_resumed=on_connection_resumed,
    client_id="<thing>/<custom_id>",
    clean_session=False,
    keep_alive_secs=30,
    http_proxy_options=None,
    on_connection_success=on_connection_success,
    on_connection_failure=on_connection_failure,
    on_connection_closed=on_connection_closed
)
```
