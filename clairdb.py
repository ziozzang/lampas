##################################################
#
# Code by Jioh L. Jung <ziozzang@gmail.com>
#
##################################################

from distutils.version import LooseVersion
import json
import psycopg2

def conn_db(DB_IP,DB_PORT,DB_ID,DB_PW):
  if type(DB_PORT) == type(0):
  	DB_PORT = str(DB_PORT)
  conn = psycopg2.connect("host='%s' port='%s' user='%s' password='%s'" % (DB_IP, DB_PORT, DB_ID, DB_PW))
  return conn

def check(conn, osver, pkgs):
  cur = conn.cursor()
  cur.execute("select * from namespace where name='%s'" % (osver,))
  oskey = cur.fetchone()[0]
  res = {}
  res["result"] = []
  res["osver"] = osver
  for i in pkgs:
    cur.execute("""
      select *
        from vulnerability as v, vulnerability_affected_feature as f
        where f.vulnerability_id = v.id and
              v.namespace_id = %d and
              f.feature_name ='%s'
       """ % (oskey, i))
    
    # Fetch Each Packages from database.
    for j in cur.fetchall():
      # Table name mapping
      cn = [desc[0] for desc in cur.description] # Table name

      # Version string extraction
      av = j[cn.index("affected_version")] # Affected Version
      fv = j[cn.index("fixedin")] # Fixed version
      pv = pkgs[i] # Reported(Installed) version
      #- Strip 1:2.3.4 version string type
      av1 = av.split(":",1)
      if len(av1) > 1 and av1[0].isdigit():
        av = av1[1]
      fv1 = fv.split(":",1)
      if len(fv1) > 1 and fv1[0].isdigit():
        fv = fv1[1]
      pv1 = pv.split(":",1)
      if len(pv1) > 1 and pv1[0].isdigit():
        pv = pv1[1]
      
      # Checking Affected.
      #- Reset flag
      v1 = False
      v2 = False

      #- Check issue is native bugs.
      if av == "#MAXV#": # if MAXV is set ==> All Version.
        if fv == "": # No Fix release yet.
          v2 = True
        elif LooseVersion(pv) < LooseVersion(fv): # Current Version not Fixed
          v2 = True
      else: # Affected specific version range
        if LooseVersion(av) < LooseVersion(pv): # Maybe fixed? (not important issue)
          v1 = True
        if LooseVersion(pv) < LooseVersion(fv): # Affected.
          v2 = True

      if v2: # Affected
        print "%s %s - %s / %s / %s (%s): %s/%s" % \
          (v1,v2,av,pkgs[i],fv, i,j[cn.index("name")],j[cn.index("severity")])
        d = {}
        d["affected_version"] = av
        if av == "#MAXV#":
          d["affected_version"] = "#ALL_VERSION#"
        d["fixedin"] = fv
        d["requested_version"] = pv
        d["pkg_name"] = i
        d["cve_name"] = j[cn.index("name")]
        d["severity"] = j[cn.index("severity")]
        d["description"] = j[cn.index("description")]
        d["link"] = j[cn.index("link")]
        d["metadata"] = json.loads(str(j[cn.index("metadata")]))
        res["result"].append(d)
  cur.close()
  return res

