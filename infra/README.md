# training-feed-kinesis
Manage Multiple Kinesis agents associated with multiple accounts and feed them with synthesized bank transaction data

## Installation

* Launch a [Kinesis Agent compatible instance](https://docs.aws.amazon.com/streams/latest/dev/writing-with-agents.html#prereqs).
* Clone this repo and `cd` into it.
* `source setup-aws.sh`
* `virtualenv venv -p python3`
* `. venv/bin/activate`
* `pip install -r requirements.txt`
* `sqlite3 app.db < dbschema.sql`
* Start `generate_transactions.py > /tmp/transactions.log`. This is generating the card transaction data.
* Start `status_watcher.py`. This component will keep the db up-to-date and manage the streams with AWS.
* Start the web UI `service.py`. 

