docker build -f catalog.Dockerfile . -t catalog-image
docker build -f order.Dockerfile . -t order-image
docker build -f frontend.Dockerfile . -t frontend-image
