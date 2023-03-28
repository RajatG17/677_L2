# Instructions to run 

## PART 1:

1. Run the catalog service in the services/ folder:

```shell
python3 catalogService.py
```

2. Run the order service in the services/ folder with the environment variable "CATALOG_HOST" set as "0.0.0.0":

```shell
CATALOG_HOST="0.0.0.0" python3 orderService.py
```

3. Run the front-end service in the front-end/ fodler with the environment variable "CATALOG_HOST"="0.0.0.0" and ORDER_HOST="0.0.0.0"

```shell
CATALOG_HOST="0.0.0.0" ORDER_HOST="0.0.0.0" python3 front-end-http-server.py
```

4. Run client in the client/ folder:

```shell
python3 client.py 0.4
```

Note:
The client takes host and port of the server as command line arguments:
python3 client.py <host> <port> <p>

In order to connect a client on the local machine to a remote host say "128.119.243.147", run:

```shell
python3 client.py "128.119.243.147" 4000 0.4
```

## PART 2:

### Build and run all the services using Dockerfile:

Run "build.sh" to build docker images based on the Dockerfile of all the three services: order, catalog and front-end

```shell
sh build.sh
```

1. Run catalog container using the catalog service image built using Dockerfile:

```shell
docker run -it --name catalog-container --volume `pwd`/src/Part1/data:/root-dir/data catalog-image
```

2. Run order container using the order service image built using Dockerfile:

```shell
docker run -it --name order-container --env CATALOG_HOST="172.17.0.2" --env CATALOG_PORT=6000 --volume `pwd`/src/Part1/data:/root-dir/data order-image
```

Note: 

<CATALOG_HOST> is the IPAddress of the docker container running the catalog service - This can be obtained by using docker inspect <container> command

3. Run front-end container using the front-end service front-end service built using Dockerfile:

```shell
docker run -it --name frontend-container --env CATALOG_HOST="172.17.0.2" --env CATALOG_PORT=6000 --env ORDER_HOST="172.17.0.3" --env ORDER_PORT=6001 -p 4000:4000 frontend-image
```

Note:
<CATALOG_HOST> is the IPAddress of the docker container running the catalog service - This can be obtained by using docker inspect <container> command.
<ORDER_HOST> is the IPAddress of the docker container running the order service - This can be obtained by using docker inspect <container> command.

4. Run client:

Obtain IPAddress of the docker container running Front-end service - This can be obtained by using docker inspect <container> command

If Linux machine, pass the Front-end service IPAddress, port and p(probability)

In Mac, use the localhost IP using port forwarding since Docker Desktop is used:

```shell
python3 client.py "127.0.0.1" 4000 0.4
``` 

### Run all the services using Docker compose: 

1. Bring up all the services:

```shell
docker-compose up
```

2. Run client:

Obtain IPAddress of the docker container running Front-end service - This can be obtained by using docker inspect <container> command

If Linux machine, pass the Front-end service IPAddress, port and p(probability)

In Mac, use the localhost IP using port forwarding since Docker Desktop is used:

```shell
python3 client.py "127.0.0.1" 4000 0.4
```

3. Tear down all the services:
```shell
docker-compose down
```

