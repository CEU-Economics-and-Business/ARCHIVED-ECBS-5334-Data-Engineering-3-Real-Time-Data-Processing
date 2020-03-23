source venv/bin/activate
python generate_transactions.py | tee -a /tmp/transactions.log
cat start-generator.sh
exec bash

