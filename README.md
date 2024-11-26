## ML_MULTIPLATFORM

### Build & run containers
```bash
docker build -t myimage:latest .
docker run --name mycontainer -p 80:80 myimage
```

#### How to build and run via docker-compose
```bash
docker-compose up --build
```
