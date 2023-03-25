import sys
import json
from sys import argv
import random
import http.client

if __name__ == "__main__":
	conn = http.client.HTTPConnection("localhost", 4000)
	stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
	trade_types = ["buy", "sell"]

	if len(argv) == 2:
		p = float(argv[1])
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
				print("response.status, response.reason : ")
				print(response.status, response.reason)
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
				print("response.status, response.reason : ")
				print(response.status, response.reason)
				print("data: ")
				print(data)
	else:
		print("Invalid command-line arguments, enter p in range[0, 1]")
	
	# Close the HTTP connection
	conn.close()
