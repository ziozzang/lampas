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
  assert(ret.status_code == 200)
  return json.loads(ret.text)

osver = "alpine:v3.6"
pkgs = {
  'musl':'1.1.16-r9',
  'expat':'2.2.0-r0',
  'busybox':'1.26.2-r5',
}
print ("======================%s===================" % (osver,))
r = check(osver, pkgs)
r1 = len(r['result'])
print r1

osver = "alpine:v3.6"
pkgs = {
  'musl':'',
  'expat':'',
  'busybox':'',
}
print ("======================%s===================" % (osver,))
r = check(osver, pkgs)
r2 = len(r['result'])
print r2
assert(r1 <= r2)

osver = "ubuntu:16.04"
pkgs = {
  'systemd':'229-4ubuntu17',
  'rsync':'3.1.1-3ubuntu1',
}
print ("======================%s===================" % (osver,))
r = check(osver, pkgs)
print len(r['result'])

osver ="centos:7"
pkgs = {
  'glibc':'2.17-157.el7_3.2',
  'glibc-common':'2.17-157.el7_3.2',
}
print ("======================%s===================" % (osver,))
r = check(osver, pkgs)
print len(r['result'])


osver="debian:8"
pkgs = {
    'libx11':'1.6.2-3',
    'libxml2':'2.9.1+dfsg1-5+deb8u4',
    'wget':'1.16-1',
}
print ("======================%s===================" % (osver,))
r = check(osver, pkgs)
r1 = len(r['result'])
print r1

# Ask Dummy version
osver="debian:8"
pkgs = {
    'libx11':'',
    'libxml2':'',
    'wget':'',
}
print ("======================%s===================" % (osver,))
r = check(osver, pkgs)
r2 = len(r['result'])
print r2
assert (r1 <= r2)

