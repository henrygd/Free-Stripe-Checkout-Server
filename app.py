from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import sql_stripe
import re

app = Flask(__name__)


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
    public, secret = request.form['publickey'], request.form['secretkey']
    if goodpub.match(public) and goodsec.match(secret):
        keys = (public, secret)
        try:
            sql_stripe.addkeys(keys)
            result = "<span style='background:#4EB053'>Your keys have been \
                added! Try verifying below.</span>"
        except:
            result = "<span style='background:#DF4F4F'>Error: At least one \
                these keys already exists. Please see the note above.</span>"
        return jsonify(result=result)
    else:
        return jsonify(result="<span style='background:#DF4F4F'>Error: Please \
            make sure your keys are properly formatted and in the correct \
            fields.</span>")


@app.route('/getkey')
def getkey():
    if re.compile("^pk_(test|live)_[a-zA-Z0-9]{24}$").match(request.args.get('a')):
        pubkey = (request.args.get('a'),)
        conn = sqlite3.connect('stripekeys.db')
        c = conn.cursor()
        c.execute('SELECT secret FROM keys WHERE public=?;', pubkey)
        try:
            seckey = c.fetchone()[0][0:18] + '*' * 14
            result = "<span style='background:#4EB053'>%s</span>" % (seckey)
        except:
            result = "<span style='background:#DF4F4F'>Key not found</span>"
        c.close()
        conn.close()
        return jsonify(result=result)
    else:
        return jsonify(result="<span style='background:#DF4F4F'>Invalid \
            format</span>")


@app.route('/charge', methods=['GET', 'POST'])
def stripecharge():
    if request.method == 'GET':
        return redirect(url_for('stripeserver'))
    else:
        publickey = (request.form['publicKey'],)
        conn = sqlite3.connect('stripekeys.db')
        c = conn.cursor()
        c.execute('SELECT secret FROM keys WHERE public=?;', publickey)
        try:
            seckey = c.fetchone()[0]
            sql_stripe.charge(
                seckey=seckey,
                token=request.form['stripeToken'],
                amount=request.form['amount'],
                description=request.form['description']
            )
        except:
            pass
