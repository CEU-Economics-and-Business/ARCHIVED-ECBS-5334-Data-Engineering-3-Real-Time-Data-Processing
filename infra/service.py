import os, sys

from flask import *
import sqlite3

from utils import *

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'my super secret key'

from functools import wraps
from flask import request, Response


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config['auth_user'] and password == app.config['auth_pass']


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@requires_auth
def show_streams():
    db = get_db()
    cur = db.execute("SELECT c.*, s.*, substr(arn, instr(arn, '/') + 1) as stream_name \
                      FROM streams s INNER JOIN credentials c USING (access_key) ORDER BY name, arn")
    entries = cur.fetchall()
    return render_template('show_streams.html', entries=entries)


@app.route('/c', methods=['GET'])
@requires_auth
def show_credentials():
    db = get_db()
    cur = db.execute('select * FROM credentials ORDER BY name')
    entries = cur.fetchall()
    return render_template('show_credentials.html', entries=entries)


@app.route('/c', methods=['POST'])
@requires_auth
def add_credential():
    db = get_db()

    if request.form['name'].strip() == "":
        return printr("Please fill in the name")

    if request.form['access_key'].strip() == "":
        return printr("Please fill in the access_key")

    if request.form['secret_key'].strip() == "":
        return printr("Please fill in the access_key")

    db.execute('insert into credentials (name, access_key, secret_key) values (?, ?, ?)',
               [request.form['name'], request.form['access_key'].strip(),  request.form['secret_key'].strip()])

    db.commit()
    flash('New credential was successfully added')
    return redirect(url_for('show_credentials'))


@app.route('/start')
@requires_auth
def start_stream():
    arn = request.args.get('arn')
    stream = get_stream(arn)
    if stream is None:
        flash("Can't find stream: " + arn)
    else:
        start_stream_aws(stream)
        flash('Starting stream ' + stream_name(arn))

    return redirect(url_for('show_streams'))


@app.route('/stop')
@requires_auth
def stop_stream():
    arn = request.args.get('arn')
    stream = get_stream(arn)
    if stream is None:
        flash("Can't find stream: " + arn)
    else:
        stop_stream_aws(stream)
        flash('Stopping stream' + stream_name(arn))

    return redirect(url_for('show_streams'))


@app.route('/extend_expiry')
@requires_auth
def extend_expiry():
    arn = request.args.get('arn')
    s = get_stream(arn)
    if s is None:
        flash("Can't find stream: " + arn)
    else:
        s["expiry_time"] = new_expiry_time()
        get_db().execute(
            'UPDATE streams SET expiry_time = ? WHERE arn = ?',
            [s['expiry_time'], s['arn']])
        get_db().commit()

        flash('Expiry time extended for {}/{}'.format(s['name'], stream_name(arn)))

    return redirect(url_for('show_streams'))


################

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(os.path.join(app.root_path, 'app.db'),
                         detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_stream(arn):
    db = get_db()
    cur = db.execute('SELECT c.*, s.* FROM streams s INNER JOIN credentials c USING (access_key) WHERE arn= ?', [arn])
    stream = cur.fetchall()
    if stream is None or len(stream) == 0:
        return None
    return row_dict(stream[0])


def printr(s):
    h = """<pre>""" + s + """</pre><br><br><a href="javascript:history.back()">Go Back</a>"""
    return Response(h, mimetype='text/html')


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: {} [port] [http auth username] [http auth password]".format(sys.argv[0]))
        sys.exit(1)

    app.config['auth_user'] = sys.argv[2]
    app.config['auth_pass'] = sys.argv[3]
    app.debug = True
    app.run(host='0.0.0.0', port=int(sys.argv[1]))
