FROM python

RUN pip install --upgrade pip
RUN pip install grpcio grpcio-tools protobuf

WORKDIR /root-dir

COPY $PWD/src/Part1/front-end front-end
COPY $PWD/src/Part1/proto proto

WORKDIR /root-dir/front-end

ENV FRONTEND_HOST='0.0.0.0'
ENV FRONTEND_PORT=4000

ENTRYPOINT 'python3' 'front-end-http-server.py' $FRONTEND_HOST $FRONTEND_PORT
