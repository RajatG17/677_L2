import sys
sys.path.append("..")

import pandas as pd
import grpc
from concurrent import futures
from proto import service_rpc_pb2_grpc as pb2_grpc
from proto import service_rpc_pb2 as pb2
from readerwriterlock import rwlock

# Maximum worker threshold for threadpool (default valuw is 3)
MAX_WORKER_THRESHOLD = 3


# Catalog service server class to carry out lookup and trade operations with backend(file)
class CatalogService(pb2_grpc.CatalogServicer):

    def __init__(self) -> None:
        self.lock = rwlock.RWLockRead()
        # load data
        self.data_file = pd.read_csv("./data/stock_data.csv")
        try:
            self.order_channel = grpc.insecure_channel("[::]:6001")
        except:
            print("Error creating a channel to order service")

    def lookup(self, request, context):
        try:
            print("Inside lookup method")
            stockname = request.stockname
            # acquire read lock
            read_lock = self.lock.gen_rlock()

            if stockname in self.data_file.keys():
                # get stock details from data
                with read_lock:
                    name = stockname
                    price =  self.data_file[stockname][0]
                    quantity = self.data_file[stockname][1]
                print(name, price, quantity)

                return pb2.lookupResponseMessage(error=pb2.NO_ERROR, stockname=name, price=price, quantity=int(quantity))
            else:
                # return stockname with approperiate error to indicate invalid stockname 
                return pb2.lookupResponseMessage(error=pb2.INVALID_STOCKNAME)
        except :
            return pb2.lookupResponseMessage(error=pb2.INTERNAL_ERROR)
        
    def buy_or_sell_stock(self, request, context):
            stockname = request.stockname
            quantity = int(request.quantity)
            order_type = request.type

            print("Inside catalog service's buy or sell method")

            # acquire write lock
            write_lock = self.lock.gen_wlock()

            if order_type.lower() == "buy":
                try:
                    # reduce quantity of stock volume (in server's data)   
                    with write_lock: 
                        self.data_file[stockname][1] -= quantity
                        print(self.data_file[stockname][1], stockname)
                        # presist data
                        try:
                            self.data_file.to_csv('./data/stock_data.csv', sep=",", index=False)
                            print("persisted data !!")
                        except:
                            print("Error writing data to file")
                    print("try buying stock")
                    print(f"Buy request successful for {quantity} stocks of {stockname} for $ {(quantity*self.data_file[stockname][0])}.") 
                    return pb2.orderResponseMessage(error=pb2.NO_ERROR)
                except:
                    print(f"Error occured processing request for buying {quantity} {stockname} stocks")
                    return pb2.orderResponseMessage(error=pb2.INTERNAL_ERROR)
            elif order_type.lower() == "sell":
                try:
                    # reduce quantity of stock volume (in server's data)   
                    print("try selling stock")
                    with write_lock:
                        self.data_file[stockname][1] += quantity
                        # persist data
                        try:
                            self.data_file.to_csv('./data/stock_data.csv', sep=",", index=False)
                            print("persisted data !!")
                        except:
                            print("Error persisting data")
                     
                    print(f"Sell request successful for {quantity} stocks of {stockname} for $ {(quantity*self.data_file[stockname][0])}.") 
                    return pb2.orderResponseMessage(error=pb2.NO_ERROR)
                except:
                    print(f"Error occured processing request for selling {quantity} {stockname} stocks")
                    return pb2.orderResponseMessage(error=pb2.INTERNAL_ERROR)
                
def serve(port=6000, max_workers=MAX_WORKER_THRESHOLD):
    print(MAX_WORKER_THRESHOLD)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    pb2_grpc.add_CatalogServicer_to_server(CatalogService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()

    server.wait_for_termination()



if __name__=="__main__":
    if len(sys.argv) > 1:
        MAX_WORKER_THRESHOLD = sys.argv[1]

    serve()


