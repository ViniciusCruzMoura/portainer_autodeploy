import flask
import portainer

app = flask.Flask(__name__)

@app.route("/portainer/deploy/webhook/<action>/<stack_name>", methods = ['POST'])
def hello_world(action, stack_name):
    if action is None or action == "":
        return flask.jsonify({"mensagem": "FALHA", "detalhe": None})
    if stack_name is None or stack_name == "":
        return flask.jsonify({"mensagem": "FALHA", "detalhe": None})
    if portainer.main(["portainer.py", action, stack_name]) == 1:
        return flask.jsonify({"mensagem": "FALHA", "detalhe": None})
    return flask.jsonify({"mensagem": "SUCESSO", "detalhe": None})
