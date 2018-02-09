# clair-generic-scan-server

Clair Generic Scan Server (HTTP)

* You can scan any linux system not only docker but also bare-metal.
* Clair use newest distro's NVD/CVE database.

* Support Linux Distro.
    * Ubuntu / Debian
    * Centos / Redhat / Oracle
    * Alpine

* [Clair](https://github.com/coreos/clair/) is opensource project by CoreOS(Acquired by RedHat)

# Author
* Jioh L. Jung <ziozzang@gmail.com>: [linkedin.com/in/ziozzang](https://linkedin.com/in/ziozzang)

# Requirements
* Clair DB format is 2.0.1 (on Clair Public Release)
* not working with VMWare Harbor or other 3rd party's clair release.


# Run

* Run with docker-compose.
```
cd compose
docker-compose up -d

# wait for DB updating is complated.
# 10-30 min
docker exec -it search-server python /opt/test.py

```

* You can test on bare-metal using with cli client.
    * prerequisit: python & requests module
```
cd cli
python scanner.py http://127.0.0.1:5000
```

* Environments Parameters
    * not yet documented


# API

not yet documented.

# Build

```
docker build -t ziozzang/clair-generic-scan-server .
docker run -it --rm  -p 5000:5000 --link pgsql:pgsql ziozzang/clair-generic-scan-server

```

# Known Issue
* welcome any pull requests.


* if no database updated, server return 500.
* no error processing
* no web ui.

# TO-Do

* Documents
* API

# License
* BSD.
* You can use any purpose.




