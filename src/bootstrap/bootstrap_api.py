import json, requests
from flask import Flask, request, jsonify


app = Flask(__name__)

node_IPs = set()

@app.route('/join', methods=['POST'])
def join_network():
    client_ip = request.remote_addr
    data = request.get_json()
    node_id = data.get("node_id")
    if node_id is None:
        return {"error" : "node_id is required"}, 400
    print(f"Node {node_id} wants to join the network.")
    
    node_IPs.add(client_ip)

    # Update ALL nodes--including the requester node--of real IP list.
    send_updated_ips()
    # Respond with a list of known IP addresses of ALL nodes--including the IP of the requester node.
    # It is the responsibility of the server node to exclude its own IP when propagating changes.
    response = {
        "type": "join_response",
        "ip_addresses": list(node_IPs)
    }

    return jsonify(response)

def send_updated_ips():
    for address in node_IPs:
            url = f"http://{address}:5001/update-ips"
            data = {
                "type": "update",
                "ip_addresses" : list(node_IPs)
            }

            try:
                response = requests.put(url, json=data)
                
                if response.status_code == 200:
                    print("Succeeded!")
                else:
                    print("Failed! Code: {status_code}")
            except requests.exceptions.RequestException as e:
                print("error during request: ", e)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
