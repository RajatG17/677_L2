import grpc
import sys
sys.path.append("..")
from concurrent import futures
from proto import service_rpc_pb2_grpc as pb2_grpc
from proto import service_rpc_pb2 as pb2 

MAX_WORKER_THRESHOLD = 3
#unique trtansaction for every order
transaction_number = 0


class OrderService(pb2_grpc.OrderServicer):
    def __init__(self):
        self.transaction_logs = open("transaction_log.txt ", "a")
        # create a grpc channel
        

    def trade(self, request, context):
        global transaction_number
        try:

            try:
                self.channel = grpc.insecure_channel("[::]:6000")
            except:
                print("Error establishing a grpc channel")
            # get stockname, quantity and transaction type (buy/sell)  
            stockname = request.stockname
            quantity= request.quantity
            order_type = request.type
            print("inside order service")
            print(type(quantity))

            catalogService = pb2_grpc.CatalogStub(self.channel)
            # make lookup call to catalog service
            with self.channel:
                result = catalogService.lookup(pb2.lookupRequestMessage(stockname=stockname))
                print(result)
            
                # first check if stockname provides is valid and has enough quantity
                if result and int(result.quantity) >= quantity:
                    # call buy method of catalog service to decrement stock from data
                    status = None
                    # make grpc call to catalog service to cary out trade operation 
                    
                    status = catalogService.buy_or_sell_stock(pb2.orderRequestMessage(stockname=stockname, quantity=quantity, type=order_type))
                    print(status.error)
                    if not status.error:
                        transaction_number  += 1
                        self.transaction_logs.write(f"{transaction_number} - {stockname}  {quantity} {order_type}, \n")
                        return pb2.tradeResponseMessage(error=0, transaction_number=transaction_number)
                    else:
                        return pb2.tradeResponseMessage(error=1)           
        except:
            return pb2.tradeResponseMessage(error=1)


def serve(port=6001, max_workers = MAX_WORKER_THRESHOLD):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    pb2_grpc.add_OrderServicer_to_server(OrderService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()             
    
if __name__=="__main__":
    if len(sys.argv) > 1:
        MAX_WORKER_THRESHOLD = sys.argv[1]

    serve()
        
