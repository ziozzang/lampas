#!/usr/bin/python
fname = "/tmp/packages"

import os
import re
import json
import requests
import sys
import pprint

def get_ostype():
  osid=""
  osrel=""
  ospkg=""
  for i in open("/etc/os-release").readlines():
    j = i.strip().split("=",1)
    if len(j) <2:
      continue
    j[1] = j[1].replace('"','')
    if j[0] == "ID":
      if j[1] == "centos" or j[1] == "rhel":
        osid = "centos"
        ospkg = "rpm"
      elif j[1] == "ubuntu":
        osid = "ubuntu"
        ospkg = "apt"
      elif j[1] == "debian":
        osid = "debian"
        ospkg = "apt"
      elif j[1] == "alpine":
        osid = "alpine"
        ospkg = "apk"
    elif j[0] == "VERSION_ID":
      osrel = j[1]
  # Alpine's format is alpine:v3.7
  if osid == "alpine":
    t = osrel.split(".")
    osver = "%s:v%s.%s" % (osid, t[0], t[1])
  else:
    osver = "%s:%s" % (osid,osrel)
  return osver, ospkg

def pkg_rpm():
  os.system('rpm -qa --qf "%%{NAME} %%{VERSION}-%%{RELEASE}\n" > %s' % fname)
  pkgs = {}
  for i in open(fname).readlines():
    j = i.split()
    if j is None:
      print i
      continue
    pkgs[j[0]] = j[1] #.rsplit(".el",1)[0] # no strip tails
  return pkgs

def pkg_apt():
  os.system("apt list --installed 2> /dev/null > %s" % fname)
  pkgs = {}
  for i in open(fname).readlines():
    j = i.split()
    if len(j)<4:
      continue
    pname = j[0].split("/")[0]
    ver = j[1]
    pkgs[pname] = ver
  return pkgs

def pkg_apk():
  os.system("apk info -vv > %s" % fname)
  m = re.compile("([a-z]{1}[\w\-\_\+]*?)-([0-9]{1}[\w\-\.\_]*)\s\-\s(.*)")
  pkgs = {}
  for i in open(fname).readlines():
    j = m.match(i.strip())
    if j is None:
      print i
      continue
    j = j.groups()
    print j
    pkgs[j[0]] = j[1]
  return pkgs

def gen_request():
  res = {}
  pkg = None
  ostype, ospkg = get_ostype()
  if ospkg == "rpm":
    pkg = pkg_rpm()
  elif ospkg == "apt":
    pkg = pkg_apt()
  elif ospkg == "apk":
    pkg = pkg_apk()
  res["osver"] = ostype
  res["packages"] = pkg
  return res


def check(url, req):
  head= {"Accept":"applicaiton/json",
          "Content-type": "application/json"}
  ret = requests.put(url, headers=head, data=json.dumps(req))
  print ret.status_code
  return json.loads(ret.text)

if __name__ == '__main__':
  if len(sys.argv) <2:
    print """%s server_host\nex) %s http://127.0.0.1:5000""" % (sys.argv[0],sys.argv[0],)
  else:
    res = check(sys.argv[1], gen_request())
    print ">> ", res["osver"]
    for i in res["result"]:
      print "========================================================="
      pp = pprint.PrettyPrinter(indent=2)
      pp.pprint(i)

