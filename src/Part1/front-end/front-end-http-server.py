import os
import sys
sys.path.append("..")

import http.server
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
import grpc
from proto import service_rpc_pb2_grpc as pb2_grpc
from proto import service_rpc_pb2 as pb2 
from urllib.parse import urlparse
import json
from sys import argv
import threading
import os

class MyHTTPHandlerClass(http.server.BaseHTTPRequestHandler):
	protocol_version = 'HTTP/1.1'

	def handle_one_request(self):
		super(MyHTTPHandlerClass, self).handle_one_request()
		print ("cur_thread: " + threading.current_thread().name)
		print ("client address_string: " + str(self.client_address))

	# Method to encode a JSON string into bytes 
	def convert_json_string(self, json_str):
		response = json_str.encode('utf-8')
		return response

	# Method to write and send response and HTTP headers
	def create_and_send_response(self, status_code, content_type, content_length, response):
		self.send_response(status_code)
		self.send_header("Content-type", content_type)
		self.send_header("Content-Length", content_length)
		self.end_headers()
		self.wfile.write(response)

	def do_GET(self):
		# create channel for communicating with catalog service
		try:
			catalog_host = os.getenv("CATALOG_HOST", "catalog")
			catalog_port = int(os.getenv("CATALOG_PORT", 6000)) 
			self.catalog_channel = grpc.insecure_channel(f"{catalog_host}:{catalog_port}")
		except:
			print("Error establishing a channel with catalog service")

		get_path = str(self.path)
		parsed_path = get_path.split("/")

		# Check if the URL for the GET method is invalid - It should be of the format : "/stocks/<stock_name>"
		if (len(parsed_path) != 3 or parsed_path[0] != "" or parsed_path[1] != "stocks"):
			print ("URL for HTTP GET request is invalid - It should be of the format : ") 
			print("\"/stocks/<stock_name>\"")
			# If the GET request was not successful, return JSON reply with a top-level error object
			json_str = json.dumps({"error": {"code": 404, "message": "stock not found"}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(404, "application/json", str(len(response)), response)
			return
		
		# Obtain the stockname from the parsed URL/path
		stockname = parsed_path[2]

		# make lookup call to catalog service
		catalogService = pb2_grpc.CatalogStub(self.catalog_channel)
		result = catalogService.lookup(pb2.lookupRequestMessage(stockname=stockname))
		print("Response received from the back-end Catalog service:")
		print(result)
		
		if result.error == pb2.NO_ERROR:
			#Return JSON reply with a top-level data object 
			stockname = result.stockname
			price = result.price
			quantity = result.quantity
			json_str = json.dumps({"data": {"name": stockname, "price": price, "quantity": quantity}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(200, "application/json", str(len(response)), response)
		else:
			#If the GET request was not successful, return JSON reply with a top-level error object
			json_str = json.dumps({"error": {"code": 404, "message": "stock not found"}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(404, "application/json", str(len(response)), response) 

	def do_POST(self):
		# create channel for communicating with order service
		try:
			order_host = os.getenv("ORDER_HOST", "order")
			order_port = int(os.getenv("ORDER_PORT", 6001))
			self.order_channel = grpc.insecure_channel(f"{order_host}:{order_port}")
		except:
			print("Error establishing a channel with order service")

		 # Check if the URL for the POST method is invalid - It should be of the format : "/orders"
		if self.path != "/orders":
			print ("URL for HTTP POST request is invalid - It should be of the format : ")
			print("\"/orders\"")
			#If the POST request was not successful, return JSON reply with a top-level error object
			json_str = json.dumps({"error": {"code": 400, "message": "stock could not be traded"}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(400, "application/json", str(len(response)), response)
			return
	
		# Read the JSON object attached by the client to the POST request
		length = int(self.headers["Content-Length"])
		request = json.loads(self.rfile.read(length).decode('utf-8'))

		if (self.headers["Content-type"] != "application/json" or "name" not in request or "quantity" not in request or "type" not in request):
			print ("Invalid POST request - JSON object should contain the keys \"name\", \"quantity\" and \"type\"")
			#If the POST request was not successful, return JSON reply with a top-level error object
			json_str = json.dumps({"error": {"code": 400, "message": "stock could not be traded"}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(400, "application/json", str(len(response)), response)
			return

		# Populate the order information from the recived JSON object
		stockname = request["name"]
		quantity = request["quantity"]
		type = request["type"]
		
		# make trade call to order service
		orderService = pb2_grpc.OrderStub(self.order_channel)
		result = orderService.trade(pb2.tradeRequestMessage(stockname=stockname, quantity=quantity, type=type))
		print("Response received from the back-end Order service:")
		print(result)

		# If the trade request was succesful from the order service, send the JSON object containing the Transaction number
		if result.error == pb2.NO_ERROR:
			#Return JSON reply with a top-level data object
			transaction_number = result.transaction_number
			json_str = json.dumps({"data": {"transaction_number": transaction_number}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(200, "application/json", str(len(response)), response)
		else:
			#If the POST request was not successful, return JSON reply with a top-level error object
			json_str = json.dumps({"error": {"code": 400, "message": "stock could not be traded"}})
			response = self.convert_json_string(json_str) 
			self.create_and_send_response(400, "application/json", str(len(response)), response)

if __name__ == "__main__":

	frontend_host = os.getenv("FRONTEND_HOST", "0.0.0.0")
	frontend_port = int(os.getenv("FRONTEND_PORT", 4000))
	print("Running Front-End Service on host: " + frontend_host + " , port:" + str(frontend_port))
	http_server = ThreadingHTTPServer((frontend_host, frontend_port), MyHTTPHandlerClass)
	http_server.serve_forever()
