#!/usr/bin/python

import requests
import json
def check(osver,pkgs):
  url = 'http://127.0.0.1:5000'
  head= {"Accept":"applicaiton/json",
          "Content-type": "application/json"}
  res = {"osver":osver,"packages":pkgs}
  data = json.dumps(res)
  print data
  ret = requests.put(url, headers=head, data=data)
  print ret.status_code
  return json.loads(ret.text)

osver = "alpine:v3.6"
pkgs = {
  'musl':'1.1.16-r9',
  'expat':'2.2.0-r0',
  'busybox':'1.26.2-r5',
}
print ("======================%s===================" % (osver,))
print check(osver, pkgs)

osver = "alpine:v3.6"
pkgs = {
  'musl':'1.1.16-r9',
  'expat':'2.2.0-r0',
  'busybox':'1.26.2-r5',
}
print ("======================%s===================" % (osver,))
print check(osver, pkgs)


osver = "ubuntu:16.04"
pkgs = {
  'systemd':'229-4ubuntu17',
  'rsync':'3.1.1-3ubuntu1',
}
print ("======================%s===================" % (osver,))
print check(osver, pkgs)

osver ="centos:7"
pkgs = {
  'glibc':'2.17-157.el7_3.2',
  'glibc-common':'2.17-157.el7_3.2',
}
print ("======================%s===================" % (osver,))
print check(osver, pkgs)


osver="debian:8"
pkgs = {
    'libx11':'1.6.2-3',
    'libxml2':'2.9.1+dfsg1-5+deb8u4',
    'wget':'1.16-1',
}
print ("======================%s===================" % (osver,))
print check(osver, pkgs)


