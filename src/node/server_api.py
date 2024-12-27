from flask import Flask, request, jsonify
from server_node import ServerNode

app = Flask(__name__)

# Simulate the network IPs of other ServerNodes
network_ips = set()

node_id = 1
node_ip = "127.0.0.1"  
bootstrap_ip = "192.168.1.1"  
server_node = ServerNode(node_id, node_ip, bootstrap_ip)

@app.route("/propagate", methods=["POST"])
def propagate():
    try:
        # Get the JSON data from the incoming request
        data = request.json
        type = data.get("type")
        if type != "propagate":
            return jsonify({"status": "failure", "message": "Must be of type propagate"})
        
        data = request.json
        file_name = data.get("file_name")
        file_data = data.get("file_data")

        if not file_name or not file_data:
            return jsonify({"status": "failure", "message": "Missing file name or file data"}), 400

        server_node._write(file_name, file_data)

        return jsonify({"status": "success", "message": "Network updated", "ips": list(network_ips)})

    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # ServerNode on port 5001
