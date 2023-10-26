#!/usr/bin/env bash
#
# Author: Sakthi Santhosh
# Created on: 10/10/2023
set -e

mkdir -p $PWD/.aws/iot/certs/

if [ ! -d ./venv/ ]; then
    virtualenv -q ./venv/ && source ./venv/bin/activate
fi

if [ ! -d ./awsiot-sdk/ ]; then
  git clone --recursive https://github.com/aws/aws-iot-device-sdk-python-v2.git ./awsiotsdk
fi

if ! python3 -c "import awsiot" &> /dev/null; then
  python3 -m pip install ./awsiot-sdk/
  result=$?
  if [ $result -ne 0 ]; then
    printf "Error: Failed to install AWS IoT SDK.\n"
    exit $result
  fi
fi

pip3 install boto3
pip3 freeze > ./requirements.txt

rm -r -f ./awsiot-sdk/

