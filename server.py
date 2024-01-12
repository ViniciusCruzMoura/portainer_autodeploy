import flask
import portainer

# Start webhook server
# command:
#   flask --app server run --host=0.0.0.0 --port=5000

app = flask.Flask(__name__)

@app.route("/portainer/deploy/webhook/<action>/<stack_name>", methods = ['POST'])
def webhook(action, stack_name):
    if portainer.main(["portainer.py", action, stack_name]) == 1:
        return flask.Response(status=500)
    return flask.Response(status=200)

def disable_print():
    import sys, os
    sys.stdout = open(os.devnull, 'w')

def activate_print():
    import sys
    sys.stdout = sys.__stdout__
