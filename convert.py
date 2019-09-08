from __future__ import unicode_literals
from contextlib import redirect_stdout
from youtube_dl import YoutubeDL
from flask import Flask
from flask import redirect
from flask import request
from flask import escape
from flask import g
from io import StringIO
import urllib.parse as urlparse
import sqlite3
import time
import os

DATABASE = './url-list.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CHANGEME'

if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('CREATE TABLE urls (title TEXT NOT NULL, url TEXT NOT NULL);')
    conn.commit()
    conn.close()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET'])
def index():
    song = escape(request.args['s'])

    conn = get_db()
    cur = conn.cursor()
    res = cur.execute('SELECT url FROM urls WHERE title = "{}";'.format(song)).fetchone()
    
    if res:
        redirurl = res[0]
        parsed = urlparse.urlparse(redirurl)
        expiretime = int(urlparse.parse_qs(parsed.query)['expire'][0])
        curtime = int(time.time())
        
        if expiretime < curtime:
            cur.execute('DELETE FROM urls WHERE title = "{}";'.format(song))
            conn.commit()
        else:
            conn.close()
            return redirect(redirurl.strip('\n'))

    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'forceurl': True,
        'format': 'bestaudio',
        'default_search': 'ytsearch1',
    }

    try:
        with StringIO() as buf, redirect_stdout(buf):
            with YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(song)
                songurl = buf.getvalue()
        
        cur.execute('INSERT INTO urls VALUES("{}", "{}");'.format(song, songurl.strip('\n')))
        conn.commit()
        conn.close()
        
        return redirect(songurl.strip('\n'))
    except:
        return 'Not found'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
