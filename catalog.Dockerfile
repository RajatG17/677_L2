FROM python

RUN pip install --upgrade pip
RUN pip install grpcio grpcio-tools protobuf readerwriterlock pandas

WORKDIR /root-dir

COPY $PWD/src/Part1/services/catalogService.py services/catalogService.py
COPY $PWD/src/Part1/proto proto

WORKDIR /root-dir/services

ENV CATALOG_HOST='0.0.0.0'
ENV CATALOG_PORT=6000
ENV MAX_WORKER_THRESHOLD_CATALOG=3

ENTRYPOINT 'python3' 'catalogService.py' $CATALOG_HOST $CATALOG_PORT
