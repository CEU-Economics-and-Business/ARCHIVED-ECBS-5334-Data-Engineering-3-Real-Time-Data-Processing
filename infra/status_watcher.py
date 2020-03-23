import sys, os, signal
import time
from datetime import datetime
import boto3, sqlite3
import subprocess

from utils import *

sqlite_db = None


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect('app.db',
                         detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
                         )
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    global sqlite_db
    if sqlite_db == None:
        sqlite_db = connect_db()
    return sqlite_db


def get_credential(access_key):
    stream_curr = get_db().execute(
        'SELECT * FROM credentials WHERE access_key = ?', [access_key])
    entry = stream_curr.fetchone()
    if entry is None or len(entry) == 0:
        return None
    e_dict = row_dict(entry)
    return e_dict


def get_db_streams():
    stream_curr = get_db().execute(
        'SELECT c.*, s.* FROM streams s INNER JOIN credentials c USING (access_key) ORDER BY name, arn')
    entries = stream_curr.fetchall()
    streams = {}
    for e in entries:
        e_dict = row_dict(e)
        streams[e_dict["arn"]] = e_dict

    return streams


def start_feed(s):
    if not os.path.isfile("/usr/bin/start-aws-kinesis-agent"):
        print("ERROR: Can't find /usr/bin/start-aws-kinesis-agent", file=sys.stderr)
        return None

    feeder_dir = create_feeder_dir(s['arn'])
    config_fn = feeder_dir + "/feeder.json"
    log_fn = feeder_dir + "/feeder.log"
    with open(config_fn, "w") as f:
        f.write(get_feeder_config_str(s))

    proc = subprocess.Popen(
        ["/usr/bin/start-aws-kinesis-agent", "-c", config_fn, "-L", "INFO", "-l", log_fn]
    )
    return proc.pid


def stop_feed(s):
    pid = s['feeder_pid']
    try:
        if pid is None:
            return None
        os.kill(pid, 0) # This raises an exception if pid is not running
        os.kill(s['feeder_pid'], signal.SIGTERM)
        return pid
    except OSError:
        return None
    finally:
        remove_feeder_dir(s['arn'])


def elog(s):
    print(s, file=sys.stderr)

if __name__ == '__main__':
    print("Status updater started")
    db = get_db()

    FIRST_RUN = True
    while True:
        cur = db.execute('select * FROM credentials ORDER BY name')
        db_credentials = map(row_dict, cur.fetchall())

        db_streams = get_db_streams()
        changed_streams = {}
        aws_arns = {}

        for e in db_credentials:
            try:
                client = boto3.client(
                    'kinesis',
                    aws_access_key_id=e["access_key"],
                    aws_secret_access_key=e["secret_key"],
                    region_name='eu-west-1'
                )

                streams_dict = client.list_streams()
            except Exception as error:
                elog("Exception: " + str(error) + str(e))
                continue

            stream_names = streams_dict["StreamNames"]

            for s in stream_names:
                stream_description = client.describe_stream_summary(StreamName=s)
                time.sleep(0.1)
                print(stream_description)
                aws_status = stream_description['StreamDescriptionSummary']['StreamStatus']
                arn = stream_description['StreamDescriptionSummary']['StreamARN']
                aws_arns[arn] = True

                # If this stream isn't in the DB, add it.
                if arn not in db_streams:
                    credential = get_credential(e['access_key'])
                    db_streams[arn] = {
                        'arn': arn,
                        'access_key': e['access_key'],
                        'status': 'STOPPED',
                        'expiry_time': new_expiry_time(),
                        'state_change': datetime.now(),
                        'secret_key': credential['secret_key'],
                        'name': credential['name'],
                        'feeder_pid': None
                    }
                    changed_streams[arn] = db_streams[arn]

                db_stream = db_streams[arn]
                old_db_status = db_stream['status']
                if db_stream['status'] == 'STARTING':
                    if aws_status == 'CREATING':
                        pass
                    elif aws_status == 'ACTIVE':
                        pid = start_feed(db_stream)
                        db_stream['feeder_pid'] = pid
                        db_stream['status'] = 'RUNNING'
                        changed_streams[arn] = db_stream
                    elif aws_status == 'DELETING':
                        stop_feed(db_stream)
                        db_stream['feeder_pid'] = None
                        db_stream['status'] = 'STOPPED'
                        changed_streams[arn] = db_stream
                    elif aws_status == 'UPDATING':
                        pass
                    else:
                        print('Unexpected statce change. ARN: {}, AWS status: {}, DB Status: {}'.format(
                            arn, aws_status, db_stream['status']),
                            file=sys.stderr)

                elif db_stream['status'] == 'RUNNING':
                    if aws_status == 'CREATING':
                        db_stream['status'] = 'STARTING'
                        changed_streams[arn] = db_stream
                    elif aws_status == "ACTIVE":
                        # If the status server got just fired up and there is a stream in RUNNING state,
                        # Recreate the feeder
                        if FIRST_RUN:
                            pid = start_feed(db_stream)
                            db_stream['feeder_pid'] = pid
                            db_stream['status'] = 'RUNNING'
                            changed_streams[arn] = db_stream
                        pass
                    elif aws_status == "DELETING":
                        stop_feed(db_stream)
                        db_stream['feeder_pid'] = None
                        db_stream['status'] = 'STOPPED'
                        changed_streams[arn] = db_stream
                    elif aws_status == 'UPDATING':
                        pass
                    else:
                        print('Unexpected statce change. ARN: {}, AWS status: {}, DB Status: {}'.format(
                            arn, aws_status, db_stream['status']),
                            file=sys.stderr)

                elif db_stream['status'] == 'STOPPED':
                    if aws_status == 'CREATING':
                        db_stream['status'] = 'STARTING'
                        changed_streams[arn] = db_stream
                    elif aws_status == "ACTIVE":
                        pid = start_feed(db_stream)
                        db_stream['feeder_pid'] = pid
                        db_stream['status'] = 'RUNNING'
                        changed_streams[arn] = db_stream
                    elif aws_status == "DELETING":
                        pass
                    elif aws_status == 'UPDATING':
                        pass
                    else:
                        print('Unexpected statce change. ARN: {}, AWS status: {}, DB Status: {}'.format(
                            arn, aws_status, db_stream['status']),
                            file=sys.stderr)

                if arn in changed_streams:
                    print("{}/{}: AWS:{} OLD:{} NEW:{}".format(db_stream['name'], arn, aws_status, old_db_status,
                                                               changed_streams[arn]['status']))

        # Stop streams that got removed from AWS manually.
        for arn in db_streams:
            db_stream = db_streams[arn]
            if (db_stream['status'] != 'STOPPED') and (arn not in aws_arns):
                stop_feed(db_streams[arn])
                db_stream['feeder_pid'] = None
                db_stream['status'] = 'STOPPED'
                changed_streams[arn] = db_stream
                print("{}/{}: {} -> {}".format(db_stream['name'], arn, "N/A", changed_streams[arn]['status']))

        # Update DB
        for arn in changed_streams:
            s = changed_streams[arn]
            db.execute('REPLACE INTO STREAMS \
                        (arn, access_key, status, state_change, expiry_time, feeder_pid) \
                        values (?, ?, ?, ?, ?, ?)',
                       [s['arn'], s['access_key'], s['status'], datetime.now(), new_expiry_time(), s['feeder_pid']])

        db.commit()

        streams = get_db_streams()
        for (arn, s) in iter(streams.items()):
            expiry_time = s["expiry_time"]
            if s['status'] != 'STOPPED' and expiry_time < datetime.now():
                print("{}/{}: {} -> {} (exp time: {})".format(s['name'], arn, s['status'], 'EXPIRED', s['expiry_time']))
                stop_stream_aws(s)

        # Sleep for a second at the end of each iteration
        # So we don't exceed the AWS API rate limit
        time.sleep(1)
        FIRST_RUN=False
