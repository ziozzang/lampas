//=================================================================
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
    "regexp"
)
import "io/ioutil"
import "fmt"
import "strings"
import "github.com/Jeffail/gabs"
import "github.com/go-ini/ini"

func main() {
  //=================================================================
  // Detect OS from /etc/os-release
  var os_str string = ""
  var pkg_type string = ""
  cfg, err := ini.LoadSources(ini.LoadOptions{AllowBooleanKeys: true}, "/etc/os-release")
  os_id := strings.ToLower(cfg.Section("").Key("ID").String())
  os_ver := cfg.Section("").Key("VERSION_ID").String()

  if (os_id == "rhel") { //Force set to centos
    os_id = "centos"
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

  if (os_id == "alpine") {
    vc := strings.Split(os_ver, ".")
    os_str = fmt.Sprintf("%+v:v%+v.%+v", os_id, vc[0], vc[1])
  } else if (os_id == "centos") {
    vc := strings.Split(os_ver, ".")
    os_str = fmt.Sprintf("%+v:%+v", os_id, vc[0])
  } else {
    os_str = fmt.Sprintf("%+v:%+v", os_id, os_ver)
  }


  fmt.Println(os_str, pkg_type)

  if (len(os.Args) == 1) {
    fmt.Println("No Arguments Supplied.")
    fmt.Println(" Example)")
    fmt.Printf(" $ %s http://127.0.0.1:5000\n", os.Args[0])
    os.Exit(3)
  }

  jobj := gabs.New()
  jobj.Set(os_str, "osver")

  //=================================================================
  // Parsing Installed Packages and its version
  if (pkg_type == "apt") {
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
  } else if (pkg_type == "rpm") {
    cmd := exec.Command("sh","-c", "rpm -qa --qf \"%{NAME} %{VERSION}-%{RELEASE}\\n\" > /tmp/packages")
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

      jobj.Set(fields[1], "packages", fields[0])
      fmt.Printf(">> %s: %s\n", fields[0], fields[1])
    }

    if err := scanner.Err(); err != nil {
      log.Fatal(err)
    }

  } else if (pkg_type == "apk") {
    cmd := exec.Command("sh","-c", "apk info -vv 2>/dev/null > /tmp/packages")
    cmd.Start()
    cmd.Wait()

    file, err := os.Open("/tmp/packages")
    if err != nil {
      log.Fatal(err)
    }
    defer file.Close()

    scanner := bufio.NewScanner(file)
    re := regexp.MustCompile(`([a-z]{1}[\.\w\-\_\+]*?)-([0-9]{1}[\w\-\.\_]*)`)
    for scanner.Scan() {
      line := scanner.Text()
      fields := strings.Split(line, " - ")
      if (len(fields) < 2) {
        continue
      }

      //fmt.Printf("> %s\n>> %q\n", fields[0], re.FindAllStringSubmatch(fields[0], -1)[0])
      pkgs := re.FindAllStringSubmatch(fields[0], -1)[0]
      p_ver := fmt.Sprintf("%+v", pkgs[2])
      p_name :=  fmt.Sprintf("%+v", pkgs[1])
      jobj.Set(p_ver, "packages", p_name)
      fmt.Printf(">> %s: %s\n", p_name, p_ver)
    }

    if err := scanner.Err(); err != nil {
      log.Fatal(err)
    }
  } else {
    fmt.Println(">>> Not Support Linux Distro. <<<")
    os.Exit(3)
  }

  cmd := exec.Command("sh","-c", "rm -f /tmp/packages")
  cmd.Start()
  cmd.Wait()

  fmt.Println(jobj.StringIndent("", "  "))

  //=================================================================
  // Request Result to Server
  rbody := bytes.NewBufferString(jobj.String())
  resp, err := http.Post(os.Args[1], "application/json", rbody)
  if err != nil {
    panic(err)
  }

  defer resp.Body.Close()

  // If ignore flag supplied, only High "severity" && "fixedin" Exist will shown.
  ignore_result := 0
  if (len(os.Args) > 2) {
    if (os.Args[2] == "ignore") {
      ignore_result = 1
    }
  }

  policy := 0 // Total policy violated count
  respBody, err := ioutil.ReadAll(resp.Body)
  if err == nil {
    jres, err := gabs.ParseJSON(respBody)
    if err != nil {
      panic(err)
    }
    fmt.Println("OS VER:",jres.Path("osver").String())
    children, _ := jres.S("result").Children()
    for _, child := range children {
      children2, _ := child.ChildrenMap()
      show := false
      if (ignore_result == 0) {
        show = true
      }
      if (strings.ToLower(children2["severity"].String()) == "high" &&
          len(children2["fixedin"].String()) > 0) { //Policy Checking.
        policy += 1
        show = true
      }
      if (show) {
        fmt.Println("=================================")
        for key, child2 := range children2 {
          if (key =="metadata") { // Skip metadata field.
            continue
          }
          fmt.Printf("> %s: %s\n", key, child2.Data().(string))
        }
      }
    }
  }
  fmt.Println("=================================")
  fmt.Printf(">> Total Security Policy violation : %d\n", policy)

}
