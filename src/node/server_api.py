from flask import Flask
from flask import  request, jsonify
from server_node import ServerNode
import uuid

app = Flask(__name__)

# Simulate the network IPs of other ServerNodes
network_ips = set()

node_id = uuid.uuid4()
bootstrap_ip = "192.168.86.52" # Desktop PC
server_node = ServerNode(node_id, bootstrap_ip)

@app.route("/propagate", methods=["POST"])
def receive_propagate():
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

@app.route("/write", methods=["POST"])
def write():
    try:
        data = request.json
        type = data.get("type")
        if type != "write":
            return jsonify({"status": "failure", "message": "Must be of type write"}), 400
        
        data = request.json
        file_name = data.get("file_name")
        file_data = data.get("file_data")

        if not file_name or not file_data:
            return jsonify({"status": "failure", "message": "Missing file name or file data"}), 400

        # This function writes the file to this node AND propagates it to the known nodes.
        # TOOD: Make the write have the state 'appended' before 'committed' based on majority response.
        server_node.add_file(file_name, file_data)

        return jsonify({"status": "success", "message": "Written data", "data": file_data})

    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 400

@app.route("/update-ips", methods=["PUT"])
def update_IPs():
    try:
        data = request.json
        type = data.get("type")
        if type != "update":
           return jsonify({"status": "failure", "message": "Must be of type update"}), 400

        new_IPs = data.get("ip_addresses")
        if not new_IPs:
           return jsonify({"status": "failure", "message": "Missing new IP adddresses"}), 400
 
        server_node.network_ips = set(new_IPs)
        return jsonify({"status": "success", "message": "Updated IPs", "IPs": new_IPs})

    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # ServerNode on port 5001
