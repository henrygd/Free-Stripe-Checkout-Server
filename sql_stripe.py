import sqlite3
import stripe


def init_db():
    confirm = raw_input('THIS WILL DELETE YOUR DB IF IT EXISTS. Are you sure  you want to continue? (y/n)')
    if confirm == 'y' or confirm == 'Y':
        print 'Creating db...'
        with sqlite3.connect("stripekeys.db") as connection:
            c = connection.cursor()
            c.execute("DROP TABLE IF EXISTS keys")
            c.execute("CREATE TABLE keys(public TEXT UNIQUE, secret TEXT UNIQUE)")
    else:
        print 'Exiting without making changes...'


def addkeys(newpost):
    with sqlite3.connect("stripekeys.db") as connection:
        c = connection.cursor()
        c.execute('INSERT INTO keys VALUES(?, ?)', (newpost))


def charge(seckey, token, amount, description):
    stripe.api_key = seckey
    # Create the charge on Stripe's servers - this will charge the user's card
    try:
        stripe.Charge.create(
            amount=amount,
            currency="usd",
            card=token,
            description=description
        )
        return "Thank you!"
    except stripe.error.CardError, e:
        # Since it's a decline, stripe.error.CardError will be caught
        return e.json_body['error']
    except stripe.error.InvalidRequestError, e:
        return e.json_body['error']
    except stripe.error.AuthenticationError, e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        return e.json_body['error']
    except stripe.error.APIConnectionError, e:
        # Network communication with Stripe failed
        return e.json_body['error']
    except stripe.error.StripeError, e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        return e.json_body['error']
    except Exception, e:
        # Something else happened, completely unrelated to Stripe
        return {"message": "Unknown error"}
