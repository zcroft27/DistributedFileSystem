import ipaddress, socket, requests, json
from flask import Flask, request, jsonify
from enum import Enum
import random
import time

app = Flask(__name__)

nodeIPs = set()

class Role(Enum):
    LEADER = 1
    FOLLOWER = 2
    CANDIDATE = 3

class ServerNode:
    def __init__(self, node_id, bootstrap_ip: ipaddress.IPv4Address) -> None:
        hostname = socket.gethostname()
        self.ip = socket.gethostbyname(hostname)
        self.node_id = node_id
        self.bootstrap_ip = bootstrap_ip
        self.network_ips = set()
        self.joined = False
        self.join_network()
        self.role = Role.FOLLOWER
        self.term = 0
        self.vote_count = 0
        self.leader_id = None
        self.log = []  # A simple list as the log
        self.current_leader = None
    
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

    def reset_election_timer(self):
        self.election_timeout = random.uniform(1.5, 3.0)
        self.last_heartbeat = time.time()

    def check_timeout(self):
        if time.time() - self.last_heartbeat >= self.election_timeout:
            self.start_election()

    def start_election(self):
        self.role = Role.CANDIDATE
        self.term += 1
        self.vote_count = 1  # Vote for self
        self.send_vote_request()

    def send_vote_request(self):
        for peer in self.peers:
            # TODO: Send to each peer via HTTP
            pass

    def receive_vote(self, sender_id, term):
        if term > self.term:
            self.term = term
            self.role = Role.FOLLOWER
        self.vote_count += 1

    def become_leader(self):
        self.role = Role.LEADER
        self.leader_id = self.node_id
        self.send_heartbeat()

    def send_heartbeat(self):
            # Simulate sending heartbeats to all followers
            pass

    def append_log_entry(self, entry):
        if self.role == Role.LEADER:
            self.log.append(entry)
            self.replicate_log()
        else:
            # Not the leader, return an error
            raise ValueError("Not the leader!")
            pass

    def replicate_log(self):
        if not self.joined:
            raise ValueError("Not joined to a network to propagate to.")

        for address in self.network_ips:
            if address == self.ip:
                continue
            url = f"http://{address}:5001/propagate"
            data = {
                "type": "propagate",
                "log" : self.log
            }

            try:
                response = requests.post(url, json=data)
                
                if response.status_code == 200:
                    print("Succeeded!")
                else:
                    print("Failed! Code: {status_code}")
            except requests.exceptions.RequestException as e:
                print("error during request: ", e)
        pass

    def receive_log(self, entry):
        if self.role == Role.FOLLOWER:
            self.log.extend(entry)      

    def _write(self, file_name, data):
        """Adds/writes to a file without propagating.
            Not for external use."""
        # open the file in append mode.
        f = open(file_name, "a")
        f.write(data)
        f.close()