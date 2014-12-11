from flask import Flask, render_template, request, jsonify, redirect, \
    url_for, current_app
from functools import wraps
import sqlite3
import sql_stripe
import re

app = Flask(__name__)


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/stripeserver')
def stripeserver():
    return render_template('stripeserver.html')


@app.route('/addkey', methods=['POST'])
def addkey():
    goodpub = re.compile("^pk_(test|live)_[a-zA-Z0-9]{24}$")
    goodsec = re.compile("^sk_(test|live)_[a-zA-Z0-9]{24}$")
    public, secret = request.form['publishablekey'], request.form['secretkey']
    if goodpub.match(public) and goodsec.match(secret):
        keys = (public, secret)
        try:
            sql_stripe.addkeys(keys)
            return jsonify(result="success")
        except:
            return jsonify(result="error1")
    else:
        return jsonify(result="error2")


@app.route('/getkey')
def getkey():
    if re.compile("^pk_(test|live)_[a-zA-Z0-9]{24}$").match(request.args.get('a')):
        pubkey = (request.args.get('a'),)
        conn = sqlite3.connect('stripekeys.db')
        c = conn.cursor()
        c.execute('SELECT secret FROM keys WHERE public=?;', pubkey)
        try:
            seckey = c.fetchone()[0][0:18] + '*' * 14
            result = "%s" % (seckey)
        except:
            result = "error1"
        c.close()
        conn.close()
        return jsonify(result=result)
    else:
        return jsonify(result="error2")


@app.route('/charge')
@jsonp
def stripecharge():
        publickey = (request.args.get('publishableKey'),)
        conn = sqlite3.connect('stripekeys.db')
        c = conn.cursor()
        c.execute('SELECT secret FROM keys WHERE public=?;', publickey)
        try:
            seckey = c.fetchone()[0]
            result = sql_stripe.charge(
                seckey=seckey,
                token=request.args.get('stripeToken'),
                amount=request.args.get('amount'),
                description=request.args.get('description')
            )
            if result == "Thank you!":
                return jsonify(result=result)
            else:
                return jsonify(error=result)
        except:
            return jsonify(error={'message': 'Stripe key pair not found. '
                                  'Please verify on henrygd.me/stripeserver'})
