import os
import string
import random
import sqlite3
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, request, redirect, jsonify, render_template, g
import validators

app = Flask(__name__)
app.config['DATABASE'] = os.environ.get('DATABASE_PATH', 'urls.db')
app.config['BASE_URL'] = os.environ.get('BASE_URL', 'http://localhost:5000')

CHARS = string.ascii_letters + string.digits
SHORT_URL_LENGTH = 6


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0
        )
    ''')
    db.commit()


def generate_short_code(length=SHORT_URL_LENGTH):
    return ''.join(random.choices(CHARS, k=length))


def get_unique_short_code():
    db = get_db()
    while True:
        code = generate_short_code()
        existing = db.execute(
            'SELECT id FROM urls WHERE short_code = ?', (code,)
        ).fetchone()
        if not existing:
            return code


def normalize_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


@app.route('/')
def index():
    return render_template('index.html', base_url=app.config['BASE_URL'])


@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    original_url = normalize_url(data['url'].strip())
    
    if not validators.url(original_url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    custom_code = data.get('custom_code', '').strip()
    
    db = get_db()
    
    if custom_code:
        if len(custom_code) < 3 or len(custom_code) > 20:
            return jsonify({'error': 'Custom code must be 3-20 characters'}), 400
        if not custom_code.isalnum():
            return jsonify({'error': 'Custom code must be alphanumeric'}), 400
        
        existing = db.execute(
            'SELECT id FROM urls WHERE short_code = ?', (custom_code,)
        ).fetchone()
        if existing:
            return jsonify({'error': 'Custom code already in use'}), 409
        short_code = custom_code
    else:
        existing = db.execute(
            'SELECT short_code FROM urls WHERE original_url = ?', (original_url,)
        ).fetchone()
        if existing:
            short_url = f"{app.config['BASE_URL']}/{existing['short_code']}"
            return jsonify({
                'short_url': short_url,
                'short_code': existing['short_code'],
                'original_url': original_url,
                'is_existing': True
            })
        short_code = get_unique_short_code()
    
    db.execute(
        'INSERT INTO urls (short_code, original_url) VALUES (?, ?)',
        (short_code, original_url)
    )
    db.commit()
    
    short_url = f"{app.config['BASE_URL']}/{short_code}"
    
    return jsonify({
        'short_url': short_url,
        'short_code': short_code,
        'original_url': original_url,
        'is_existing': False
    }), 201


@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    db = get_db()
    url_data = db.execute(
        'SELECT * FROM urls WHERE short_code = ?', (short_code,)
    ).fetchone()
    
    if not url_data:
        return jsonify({'error': 'Short URL not found'}), 404
    
    return jsonify({
        'short_code': url_data['short_code'],
        'original_url': url_data['original_url'],
        'created_at': url_data['created_at'],
        'clicks': url_data['clicks']
    })


@app.route('/api/urls')
def list_urls():
    db = get_db()
    urls = db.execute(
        'SELECT * FROM urls ORDER BY created_at DESC LIMIT 50'
    ).fetchall()
    
    return jsonify([{
        'short_code': url['short_code'],
        'short_url': f"{app.config['BASE_URL']}/{url['short_code']}",
        'original_url': url['original_url'],
        'created_at': url['created_at'],
        'clicks': url['clicks']
    } for url in urls])


@app.route('/<short_code>')
def redirect_to_url(short_code):
    db = get_db()
    url_data = db.execute(
        'SELECT * FROM urls WHERE short_code = ?', (short_code,)
    ).fetchone()
    
    if not url_data:
        return render_template('404.html'), 404
    
    db.execute(
        'UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?',
        (short_code,)
    )
    db.commit()
    
    return redirect(url_data['original_url'], code=302)


with app.app_context():
    init_db()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
