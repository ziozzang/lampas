// Code by Jioh L. Jung <ziozzang@gmail.com>
// This code is test purpose only.
package main

import (
    "net/http"
    "bytes"
    "bufio"
    "log"
    "os"
    "os/exec"
)
import "io/ioutil"
import "fmt"
import "strings"
import "github.com/Jeffail/gabs"
import "github.com/go-ini/ini"

func main() {
  // Detect OS from /etc/os-release
  var os_str string = ""
  var pkg_type string = ""
  cfg, err := ini.LoadSources(ini.LoadOptions{AllowBooleanKeys: true}, "/etc/os-release")
  os_id := strings.ToLower(cfg.Section("").Key("ID").String())
  os_ver := cfg.Section("").Key("VERSION_ID").String()
  if (os_id == "redhat") { //Force set to centos
    os_id = "centos"
  }
  if (os_id == "alpine") {
    vc := strings.Split(os_ver, ".")
    os_str = fmt.Sprintf("%+v:v%+v.%+v", os_id, vc[0], vc[1])
  } else {
    os_str = fmt.Sprintf("%+v:%+v", os_id, os_ver)
  }

  switch os_id {
    case "centos", "oracle":
      pkg_type = "rpm"
    case "ubuntu", "debian":
      pkg_type = "apt"
    case "alpine":
      pkg_type = "apk"
    default:
      defer fmt.Println("Unknown System!")
      os.Exit(3)
  }

  fmt.Println(os_str, pkg_type)

  if (len(os.Args) == 1) {
    fmt.Println("No Arguments Supplied.")
    fmt.Println(" Example)")
    fmt.Printf(" $ %s http://127.0.0.1:5000\n", os.Args[0])
    os.Exit(3)
  }
  if (pkg_type  != "apt") {
    fmt.Println("Current version only works with Apt Package system. / Ubuntu & Debian Only")
    os.Exit(3)
  }


  jobj := gabs.New()
  jobj.Set(os_str, "osver")
  //-------------
  // TODO: Need more work (Centos / RedHat /Alpine...)
  cmd := exec.Command("sh","-c", "apt list --installed 2>/dev/null > /tmp/packages")
  cmd.Start()
  cmd.Wait()

  file, err := os.Open("/tmp/packages")
  if err != nil {
    log.Fatal(err)
  }
  defer file.Close()

  scanner := bufio.NewScanner(file)
  for scanner.Scan() {
    line := scanner.Text()
    fields := strings.Split(line, " ")
    if (len(fields) < 2) {
      continue
    }

    pkgs := strings.Split(fields[0], "/")
    p_ver := fmt.Sprintf("%+v", fields[1])
    p_name :=  fmt.Sprintf("%+v", pkgs[0])
    jobj.Set(p_ver, "packages", p_name)
    fmt.Printf(">> %s: %s\n", p_name, p_ver)
  }

  if err := scanner.Err(); err != nil {
    log.Fatal(err)
  }

  fmt.Println(jobj.StringIndent("", "  "))

  rbody := bytes.NewBufferString(jobj.String())
  resp, err := http.Post(os.Args[1], "application/json", rbody)
  if err != nil {
    panic(err)
  }

  defer resp.Body.Close()

  respBody, err := ioutil.ReadAll(resp.Body)
  if err == nil {
    //Just Print : No Processing
    str := string(respBody)
    println(str)
  }

}
