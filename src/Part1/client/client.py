import sys
import json
from sys import argv
import random
import http.client

if __name__ == "__main__":
	if (len(argv) >= 2 and len(argv) <= 4):
		if (len(argv) == 2):
			host = '127.0.0.1'
			port = 4000 
			p = float(argv[1])
		elif (len(argv) == 3):
			host = '127.0.0.1'
			port = int(argv[1])
			p = float(argv[2])
		else:
			host = argv[1]
			port = int(argv[2])
			p = float(argv[3])
		
		print ("Client establishing server connection at host: " + host + " , port: " + str(port))
		conn = http.client.HTTPConnection(host, port)
		stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
		trade_types = ["buy", "sell"]

		while (True):
			name = stock_names[random.randint(0, 3)]
			prob = random.random()
			if (prob <= p):
				# Send Lookup request
				print ("Sending Lookup request..")
				url = "/stocks/" + name
				conn.request("GET", url)						
				response = conn.getresponse()
				data = response.read()
				print("response.status, response.reason, response.version : ")
				print(response.status, response.reason, response.version)
			else:
				# Send Trade request
				print ("Sending Trade request..")
				url = "/orders"
				type = trade_types[random.randint(0, 1)]
				body_json = {"name": name, "quantity": 1, "type": type}
				json_str = json.dumps(body_json)
				body = json_str.encode('utf-8')	
				headers = {"Content-type": "application/json", "Content-Length": str(len(body))}		
				conn.request("POST", url, body, headers)
				response = conn.getresponse()
				data = response.read()
				print("response.status, response.reason, response.version : ")
				print(response.status, response.reason, response.version)
				print("data: ")
				print(data)
		# Close the HTTP connection
		conn.close()
	else:
		print ("Invalid arguments")
		print ("To connect with server on a given host and port enter command: \"python3 client.py <host> <port> <p>\"")
		print ("To connect with server at localhost on a given port enter command: \"python3 client.py <port> <p>\"")
		print ("To connect with server at localhost and default port 4000 enter command: \"python3 client.py <p>\"")
		print ("p should be in range[0, 1]")
	
