# clair-generic-scan-server

Clair Generic Scan Server (HTTP)


# Run
```
docker run -d --name=scan-server \
   -p 5000:5000 \
   -e "DB_IP=pgsql" -e "DB_PW=asdf" \
   --link pgsql:pgsql \
   ziozzang/clair-generic-scan-server
```

# API

check test.py

you can run test in server.

```
# docker exec -it scan-server python test.py
```

# Build

```
docker build -t ziozzang/clair-generic-scan-server .
docker run -it --rm  -p 5000:5000 --link pgsql:pgsql ziozzang/clair-generic-scan-server

```
