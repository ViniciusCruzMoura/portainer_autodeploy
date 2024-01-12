import flask
import portainer

# Start webhook server
# command:
#   flask --app server run --host=0.0.0.0 --port=5000

app = flask.Flask(__name__)

@app.route("/portainer/deploy/webhook/<action>/<stack_name>", methods = ['POST'])
def webhook(action, stack_name):
    if action is None or action == "":
        return flask.jsonify({"mensagem": "FALHA", "detalhe": None})
    if stack_name is None or stack_name == "":
        return flask.jsonify({"mensagem": "FALHA", "detalhe": None})
    if portainer.main(["portainer.py", action, stack_name]) == 1:
        return flask.jsonify({"mensagem": "FALHA", "detalhe": None})
    return flask.jsonify({"mensagem": "SUCESSO", "detalhe": None})
