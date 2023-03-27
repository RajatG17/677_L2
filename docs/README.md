# Instructions to run 

## PART 2:

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

