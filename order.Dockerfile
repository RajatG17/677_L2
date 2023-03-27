FROM python

RUN pip install --upgrade pip
RUN pip install grpcio grpcio-tools protobuf readerwriterlock

WORKDIR /root-dir

COPY $PWD/src/Part1/services/orderService.py services/orderService.py
COPY $PWD/src/Part1/proto proto

WORKDIR /root-dir/services

ENV ORDER_HOST='0.0.0.0'
ENV ORDER_PORT=6001
ENV MAX_WORKER_THRESHOLD_ORDER=3

ENTRYPOINT 'python3' 'orderService.py' $ORDER_HOST $ORDER_PORT
