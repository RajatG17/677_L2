import sys
sys.path.append("..")

import grpc
import os
from concurrent import futures
from proto import service_rpc_pb2_grpc as pb2_grpc
from proto import service_rpc_pb2 as pb2 
from readerwriterlock import rwlock

MAX_WORKER_THRESHOLD = 3
#unique trtansaction for every order
transaction_number = 0

# os.environ["ORDER_HOST"] = "localhost"
# os.environ["CATALOG_HOST"] = "localhost"

# get last transaction number from log file if it exists
with open("../data/transaction_logs.txt", "r") as file:
    try:
        last_line = file.readlines()[-1]
        if last_line:
            last_line_word = int(last_line.split(" ")[0]) if last_line else 0
            transaction_number = last_line_word
    except:        
        pass

class OrderService(pb2_grpc.OrderServicer):
    def __init__(self):
        # create lock instance
        self.lock = rwlock.RWLockRead()
        try:
            # create channel for communicating with catalog service
            catalog_hostname = os.getenv('CATALOG_HOST', 'catalog')
            catalog_port = os.getenv('CATALOG_PORT', 6000)
            self.channel = grpc.insecure_channel(f"{catalog_hostname}:{catalog_port}")
        except:
            print("Error establishing a channel with catalog service")

    def trade(self, request, context):
        global transaction_number

        try:
            # get stockname, quantity and order type (buy/sell)  
            stockname = request.stockname
            quantity= request.quantity
            order_type = request.type

            # return error order type is invalid (other than buy/sell)
            if order_type.lower() not in ["buy", "sell"]:
                return pb2.tradeResponseMessage(error=pb2.INVALID_REQUEST)

            catalogService = pb2_grpc.CatalogStub(self.channel)
            
            # make lookup call to catalog service
            result = catalogService.lookup(pb2.lookupRequestMessage(stockname=stockname))
            # print(result)

            # return error if stockname is not in stocks catalog
            if result.error == pb2.INVALID_STOCKNAME:
                return pb2.tradeResponseMessage(error=pb2.INVALID_STOCKNAME)
            # return error if available quantity to buy is less than requested quantity
            if (order_type.lower() == "buy" and result.quantity < quantity):
                return pb2.tradeResponseMessage(error=pb2.INSUFFICIENT_QUANTITY)
            
            # check if stockname provided is valid & if request type is buy, there is enough stock available to buy
            if result.error == pb2.NO_ERROR and ((order_type.lower() == "buy" and int(result.quantity) >= quantity) or (order_type.lower() == "sell")):
                # make grpc call to catalog service to cary out trade operation 
                status = catalogService.buy_or_sell_stock(pb2.orderRequestMessage(stockname=stockname, quantity=quantity, type=order_type))
                # print(status.error)
                # If no error proceed with generating transaction number and logging the transaction
                if status.error == pb2.NO_ERROR:
                    with self.lock.gen_wlock() as wlock:
                        transaction_number  += 1
                        # open log file and append the latest transaction to it
                        with open("../data/transaction_logs.txt", "a") as transaction_logs:
                            transaction_str = str(f"{transaction_number} - Stockname: {stockname}  Quantity: {quantity} Order: {order_type}, \n")
                            transaction_logs.write(transaction_str)
                        # send appropriate error code (for no error) and transaction number back to front end server
                        return pb2.tradeResponseMessage(error=pb2.NO_ERROR, transaction_number=transaction_number)
                # else forward the error to front end server to send appropriate response to client
                else:
                    return pb2.tradeResponseMessage(error=status.error) 
            else:
                return pb2.tradeResponseMessage(error=pb2.INTERNAL_ERROR)
        except:
            return pb2.tradeResponseMessage(error=pb2.INTERNAL_ERROR)


def serve(host="[::]", port=6001, max_workers = MAX_WORKER_THRESHOLD):
    print(MAX_WORKER_THRESHOLD)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    pb2_grpc.add_OrderServicer_to_server(OrderService(), server)
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    server.wait_for_termination()             
    
if __name__=="__main__":

    if len(sys.argv) >= 2 :
        MAX_WORKER_THRESHOLD = int(sys.argv[1])

    host = os.getenv("ORDER_HOST", "order")
    port = os.getenv("ORDER_PORT", 6001)
    
    serve(host, port)
        
