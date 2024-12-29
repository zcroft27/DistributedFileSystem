import ipaddress, socket, requests, json
from flask import Flask, request, jsonify

app = Flask(__name__)

nodeIPs = set()




class ServerNode:
    def __init__(self, node_id, bootstrap_ip: ipaddress.IPv4Address) -> None:
        hostname = socket.gethostname()
        self.ip = socket.gethostbyname(hostname)
        self.node_id = node_id
        self.bootstrap_ip = bootstrap_ip
        self.network_ips = set()
        self.joined = False
        self.join_network()
    
    def join_network(self):
        data = {
            "node_id": str(self.node_id),
            "action": "join"
        }
        url = f"http://{self.bootstrap_ip}:5000/join"

        try:
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                print("Succeeded!")
                joined_ips = response.json().get("ips", [])
                self.network_ips.update(joined_ips)
                self.joined = True
            else:
                print("Failed!")
        except requests.exceptions.RequestException as e:
            print("error during request: ", e)


    def _propagate(self, file_name, file_data):
        if not self.joined:
            raise ValueError("Not joined to a network to propagate to.")

        for address in self.network_ips:
            if address == self.ip:
                continue
            url = f"http://{address}:5001/propagate"
            data = {
                "type": "propagate",
                "file_name": file_name,
                "file_data": file_data
            }

            try:
                response = requests.post(url, json=data)
                
                if response.status_code == 200:
                    print("Succeeded!")
                else:
                    print("Failed! Code: {status_code}")
            except requests.exceptions.RequestException as e:
                print("error during request: ", e)
                

    def _write(self, file_name, data):
        """Adds/writes to a file without propagating.
            Not for external use."""
        # open the file in append mode.
        f = open(file_name, "a")
        f.write(data)
        f.close()

    def add_file(self, file_name, data):
        """Adds/writes to a file without propagating.
            For external writing."""
        self._write(file_name, data)
        self._propagate(file_name, data)