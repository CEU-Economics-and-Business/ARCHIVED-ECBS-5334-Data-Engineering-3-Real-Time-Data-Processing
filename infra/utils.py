import os
from datetime import datetime, timedelta

import boto3
import shutil
import random


def generate_ibans(num, countries, reset_seed=True):
    if reset_seed:
        random.seed(273)
    # There is a problem here: using random + yield
    # But it's ok for this app.
    for i in range(0, num):
        country = countries[random.randint(0, len(countries) - 1)]
        iban = country + \
               str(random.randint(0,99)).zfill(2) + \
               " " + \
               str(random.randint(0, 9999)).zfill(4) + \
               " " + \
               str(random.randint(0, 9999)).zfill(4) + \
               " " + \
               str(random.randint(0, 9999)).zfill(4) + \
               " " + \
               str(random.randint(0, 9999)).zfill(4)
        yield iban


def stream_name(arn):
    try:
        return arn.split("/")[-1]
    except e:
        return 'INVALID ARN AT NAME EXTRACTION: ' + arn


def start_stream_aws(s):
    client = boto3.client(
        'kinesis',
        aws_access_key_id=s["access_key"],
        aws_secret_access_key=s["secret_key"],
        region_name='eu-west-1'
    )

    name = stream_name(s['arn'])

    client.create_stream(
        StreamName=name,
        ShardCount=1
    )


def stop_stream_aws(s):
    client = boto3.client(
        'kinesis',
        aws_access_key_id=s["access_key"],
        aws_secret_access_key=s["secret_key"],
        region_name='eu-west-1'
    )

    name = stream_name(s['arn'])

    client.delete_stream(
        StreamName=name
    )


def row_dict(row):
    return dict(zip(row.keys(), row))


def new_expiry_time():
    return datetime.now() + timedelta(hours=7.5)
    #return datetime.now() + timedelta(seconds=5)


def encode_arn(arn):
    return arn.replace("/","--SLASH--")


def decode_arn(enc_arn):
    return enc_arn.replace("--SLASH--", "/")


def get_feeder_dir(arn):
    return os.path.dirname(os.path.realpath(__file__)) + "/feeder-config/" + encode_arn(arn)


def create_feeder_dir(arn):
    directory = get_feeder_dir(arn)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def remove_feeder_dir(arn):
    config_dir = os.path.dirname(os.path.realpath(__file__)) + "/feeder-config/" + encode_arn(arn)
    if os.path.isdir(config_dir):
        shutil.rmtree(config_dir)
    return config_dir


def get_feeder_config_str(s):
    return """{{
  "cloudwatch.emitMetrics": true,
  "kinesis.endpoint": "https://kinesis.eu-west-1.amazonaws.com",
  "firehose.endpoint": "https://firehose.eu-west-1.amazonaws.com",
  "awsAccessKeyId":"{}",
  "awsSecretAccessKey":"{}",
  "checkpointFile": "{}",
  "flows": [
    {{
      "filePattern": "/tmp/transactions.log*",
      "kinesisStream": "{}",
      "partitionKeyOption": "RANDOM",
      "maxBufferAgeMillis": 1000,
      "maxBufferSizeRecords": 500,
      "initialPosition": "END_OF_FILE"
    }}
  ]
}}
""".format(s["access_key"], s["secret_key"], get_feeder_dir(s['arn']) + "/checkpoint", stream_name(s["arn"]))
