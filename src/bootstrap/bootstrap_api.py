import json
from flask import Flask, request, jsonify


app = Flask(__name__)

nodeIPs = set()

@app.route('/join', methods=['POST'])
def join_network():
    data = request.get_json()
    node_id = data.get("node_id")
    if node_id is None:
        return {"error" : "node_id is required"}, 400
    print(f"Node {node_id} wants to join the network.")
    
    # Respond with a list of known IP addresses of other nodes
    response = {
        "type": "join_response",
        "ip_addresses": nodeIPs
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
