import pandas as pd
import grpc
import sys
sys.path.append("..")
from concurrent import futures
from proto import service_rpc_pb2_grpc as pb2_grpc
from proto import service_rpc_pb2 as pb2
from threading import Lock


# Maximum worker threshold for threadpool (default valuw is 3)
MAX_WORKER_THRESHOLD = 3


# Catalog service server class to carry out lookup and trade operations with backend(file)
class CatalogService(pb2_grpc.CatalogServicer):

    def __init__(self) -> None:
        # load data
        self.data_file = pd.read_csv("stock_data.csv")
        try:
            self.order_channel = grpc.insecure_channel("[::]:6001")
        except:
            print("Error creating a channel to order service")

    def lookup(self, request, context):
        try:
            print("Inside lookup method")
            stockname = request.stockname
            # acquire read lock

            # get stock details from data
            name = stockname
            price =  self.data_file[stockname][0]
            quantity = self.data_file[stockname][1]

            # release read lock
            print(name, price, quantity)
   
            return pb2.lookupResponseMessage(error=0, stockname=name, price=price, quantity=int(quantity))
        except :
            return pb2.lookupResponseMessage(error=1)
        
    def buy_or_sell_stock(self, request, context):
            stockname = request.stockname
            quantity = int(request.quantity)
            order_type = request.type

            print("Inside catalog service's buy or sell method")

            if order_type.lower() == "buy":
                try:
                    # acquire write lock
                    #
                    # reduce quantity of stock volume (in server's data)    
                    self.data_file[stockname][1] -= quantity
                    # presist data

                    # release lock
                    # 
                    print("try buying stock")
                    print(f"Buy request successful for {quantity} stocks of {stockname} for $ {(quantity*self.data_file[stockname][0])}.") 
                    return pb2.orderResponseMessage(error=0)
                except:
                    print(f"Error occured processing request for buying {quantity} {stockname} stocks")
                    return pb2.orderResponseMessage(error=1)
            elif order_type.lower() == "sell":
                try:
                    # acquire write lock
                
                    # reduce quantity of stock volume (in server's data)   
                    print("try selling stock")
                    self.data_file[stockname][1] += quantity
                    # persist data

                    # release lock
                    # 
                    print(f"Sell request successful for {quantity} stocks of {stockname} for $ {(quantity*self.data_file[stockname][0])}.") 
                    return pb2.orderResponseMessage(error=0)
                except:
                    print(f"Error occured processing request for selling {quantity} {stockname} stocks")
                    return pb2.orderResponseMessage(error=1)
                
def serve(port=6000, max_workers=MAX_WORKER_THRESHOLD):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    pb2_grpc.add_CatalogServicer_to_server(CatalogService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()

    server.wait_for_termination()



if __name__=="__main__":
    if len(sys.argv) > 1:
        MAX_WORKER_THRESHOLD = sys.argv[1]

    serve()


