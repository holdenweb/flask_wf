from flask import Flask
app = Flask(__name__)
import twilio.twiml

@app.route("/")
def hello():
    import sys
    resp = twilio.twiml.Response()
    resp.dial("+15714846266")
    return str(resp)
    return "Hello World!"

if __name__ == "__main__":
    app.run()
