from vallaipallam.tokens import *
import os,sys,time,platform,psutil,subprocess,ctypes,socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from vallaipallam.agenticai import ai

class NetworkObject(Token):
    os_type = platform.system()
    service_port_map = {
    # Core services
    "ssh": "22",
    "http": "80",
    "https": "443",
    "ftp": "21",
    "dns": "53",
    "smtp": "25",
    "pop3": "110",
    "imap": "143",

    # Databases
    "mysql": "3306",
    "postgresql": "5432",
    "mongodb": "27017",
    "redis": "6379",

    # Dev / cloud services
    "docker": "2375",
    "kubernetes": "6443",
    "elastic": "9200",     # Elasticsearch
    "kibana": "5601",
    "jenkins": "8080"
}

    # ---------- psutil direct mapping (fast; no eval) ----------
    base_commands = {
        'SHOW_INTERFACE_ADDRESSES': psutil.net_if_addrs,                     # dict[str, list[snicaddr]]
        'SHOW_INTERFACE_STATUS': psutil.net_if_stats,                       # dict[str, snicstats]
        'SHOW_ACTIVE_CONNECTIONS': psutil.net_connections,                 # list[sconn]
        'SHOW_NETWORK_IO': psutil.net_io_counters,                 # scounters
        'SHOW_NETWORK_IO_PER_INTERFACE': lambda: psutil.net_io_counters(pernic=True)  # dict[str, scounters]
    }

    # ---------- English → Tamil keywords (stable & explicit) ----------

    def __init__(self, value):
        super().__init__("NET", value)

    # ===================== subprocess helper =====================
    @staticmethod
    def _run(cmd, check=False, text=True, capture=True):
        return subprocess.run(
            cmd,
            check=check,
            text=text,
            capture_output=capture
        )

    # ===================== admin / elevation =====================
    def run_as_admin(self):
        try:
            if self.os_type == "Windows":
                if ctypes.windll.shell32.IsUserAnAdmin():
                    return True
                # relaunch elevated
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit(0)
            else:
                # On Linux/macOS just return whether we are root
                return os.geteuid() == 0
        except Exception:
            return False

    # ===================== OS actions =====================
    def _toggle_iface(self, iface, enable: bool):
        if self.os_type == 'Windows':
            return self._run(["netsh", "interface", "set", "interface", iface,
                              "admin=enabled" if enable else "admin=disabled"])
        else:
            # Linux
            return self._run(["ip", "link", "set", iface, "up" if enable else "down"])

    def _set_dhcp(self, iface):
        if self.os_type == "Windows":
            return self._run(["netsh", "interface", "ip", "set", "address",
                              f"name={iface}", "dhcp"])
        else:
            # Kill any old leases quickly, then request
            self._run(["dhclient", "-r", iface])
            return self._run(["dhclient", iface])

    def _set_ip(self, iface, ip, gw, mask):
        if self.os_type == "Windows":
            # mask must be dotted decimal here
            return self._run([
                "netsh", "interface", "ip", "set", "address",
                f"name={iface}", "static", ip, mask, gw
            ])
        else:
            # Linux: mask can be CIDR (e.g. 24)
            # Flush → add ip/mask → default route
            r1 = self._run(["ip", "addr", "flush", "dev", iface])
            r2 = self._run(["ip", "addr", "add", f"{ip}/{mask}", "dev", iface])
            r3 = self._run(["ip", "route", "replace", "default", "via", gw])
            # Return the last result; non-zero in any step treated as failure by caller
            return r3 if (r1.returncode == 0 and r2.returncode == 0) else r2

    # ===================== Wi-Fi helpers =====================
    def _active_wifi_connection(self):
        """Linux: return active Wi-Fi connection name via nmcli (or None)."""
        res = self._run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show", "--active"])
        if res.returncode != 0:
            return None
        for line in res.stdout.splitlines():
            if not line:
                continue
            name, ctype = (line.split(":", 1) + [""])[:2]
            if ctype.strip() == "wifi":
                return name.strip()
        return None

    def disconnect_wifi(self):
        if self.os_type == "Windows":
            r = self._run(["netsh", "wlan", "disconnect"])
            return 1 if r.returncode == 0 else 0
        else:
            # Prefer disconnecting the active Wi-Fi connection only
            name = self._active_wifi_connection()
            if name:
                r = self._run(["nmcli", "connection", "down", name])
                return 1 if r.returncode == 0 else 0
            # Fallback: turn off Wi-Fi radio
            r = self._run(["nmcli", "radio", "wifi", "off"])
            return 1 if r.returncode == 0 else 0

    def connect_wifi(self, ssid, password):
        try:
            if self.os_type == "Windows":
                profile = f"""<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
  <name>{ssid}</name>
  <SSIDConfig><SSID><name>{ssid}</name></SSID></SSIDConfig>
  <connectionType>ESS</connectionType>
  <connectionMode>manual</connectionMode>
  <MSM><security>
    <authEncryption>
      <authentication>WPA2PSK</authentication>
      <encryption>AES</encryption>
      <useOneX>false</useOneX>
    </authEncryption>
    <sharedKey>
      <keyType>passPhrase</keyType>
      <protected>false</protected>
      <keyMaterial>{password}</keyMaterial>
    </sharedKey>
  </security></MSM>
</WLANProfile>"""
                pf = "wifi_profile.xml"
                with open(pf, "w", encoding="utf-8") as f:
                    f.write(profile)
                self._run(["netsh", "wlan", "add", "profile", f"filename={pf}"], capture=True)
                res = self._run(["netsh", "wlan", "connect", f"name={ssid}"], capture=True)
                try:
                    os.remove(pf)
                except Exception:
                    pass
                return 1 if "completed successfully" in res.stdout else 0
            else:
                # Linux / NetworkManager
                res = self._run(["nmcli", "dev", "wifi", "connect", ssid, "password", password])
                ok = ("successfully" in res.stdout.lower()) or (res.returncode == 0)
                return 1 if ok else 0
        except Exception:
            return 0

    def list_wifi(self):
        wifi_list = []
        if self.os_type == "Windows":
            res = self._run(["netsh", "wlan", "show", "networks", "mode=bssid"])
            ssid = None
            for line in res.stdout.splitlines():
                s = line.strip()
                if s.startswith("SSID "):
                    # "SSID 1 : Name"
                    parts = s.split(":", 1)
                    ssid = parts[1].strip() if len(parts) == 2 else ""
                    wifi_list.append({"SSID": ssid})
                elif "Signal" in s and ssid:
                    wifi_list[-1]["Signal"] = s.split(":", 1)[1].strip()
                elif "Authentication" in s and ssid:
                    wifi_list[-1]["Security"] = s.split(":", 1)[1].strip()
        elif self.os_type=="Linux":
            res = self._run(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi"])
            for line in res.stdout.splitlines():
                parts = line.split(":")
                if len(parts) >= 3 and parts[0].strip():
                    wifi_list.append({
                        "SSID": parts[0].strip(),
                        "Signal": (parts[1].strip() + "%") if parts[1].strip() else "",
                        "Security": parts[2].strip() or "Open"
                    })

        if not wifi_list:
            return "⚠️ No Wi-Fi networks found."

        out = []
        out.append("Available Wi-Fi Networks")
        out.append("-" * 54)
        out.append(f"{'No.':<4} {'SSID':<28} {'Signal':<10} {'Security':<10}")
        out.append("-" * 54)
        for i, w in enumerate(wifi_list, 1):
            out.append(f"{i:<4} {w.get('SSID','')[:28]:<28} {w.get('Signal',''):<10} {w.get('Security',''):<10}")
        return "\n".join(out)
    #========================troubleshooting==============================

    def ping_test(self,host: str) -> str:
        system = platform.system()

        if system == "Windows":
            cmd = ["ping", "-n", "1", host]   # 1 echo request
        else:
            cmd = ["ping", "-c", "1", host]   # Linux/macOS

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            output = res.stdout
            if res.returncode != 0:
                return f"Ping Test to {host}\n" \
                    f"{'-'*40}\n" \
                    f"Status   : ❌ Unreachable\n"

            # Extract RTT
            rtt = "N/A"
            for line in output.splitlines():
                if "time=" in line:
                    # Example: "time=24.3 ms"
                    rtt = line.split("time=")[-1].split()[0] + " ms"
                    break

            return f"Ping Test to {host}\n" \
                f"{'-'*40}\n" \
                f"Status   : ✅ Reachable\n" \
                f"RTT      : {rtt}\n" \
                f"Packets  : Sent=1, Received=1, Lost=0\n"

        except Exception as e:
            return f"Ping Test to {host}\n" \
                f"{'-'*40}\n" \
                f"Status   : Error\n" \
                f"Reason   : {str(e)}\n"
        
    def traceroute(self, host: str) -> str: 
        """Cross-platform traceroute with safe timeout & error handling"""
        system = platform.system()
        cmd = ["tracert", "-d", host] if system == "Windows" else ["traceroute", "-n", host]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode != 0 and not res.stdout:
                return (
                    f"Traceroute to {host}\n"
                    f"{'-'*40}\n"
                    f"Status   : ❌ Failed\n"
                    f"Reason   : {res.stderr.strip() or 'Unknown error'}\n"
                )

            lines = res.stdout.strip().splitlines()
            formatted_hops = []
            hop_num = 1
            for line in lines:
                if "Tracing" in line or "over a maximum" in line: continue
                if "traceroute to" in line.lower(): continue
                if not line.strip(): continue
                formatted_hops.append(f"Hop {hop_num:02d} → {line.strip()}")
                hop_num += 1

            if not formatted_hops:
                return (
                    f"Traceroute to {host}\n"
                    f"{'-'*40}\n"
                    f"Status   : ❌ Timed Out\n"
                    f"Note     : Target may be unreachable or blocked by firewall.\n"
                )

            return (
                f"Traceroute to {host}\n"
                f"{'-'*40}\n" +
                "\n".join(formatted_hops)
            )

        except subprocess.TimeoutExpired:
            return (
                f"Traceroute to {host}\n"
                f"{'-'*40}\n"
                f"Status   : ❌ Timed Out\n"
                f"Note     : Try increasing timeout or check firewall settings.\n"
            )

        except Exception as e:
            return (
                f"Traceroute to {host}\n"
                f"{'-'*40}\n"
                f"Status   : Error\n"
                f"Reason   : {str(e)}\n"
            )

    def dns_lookup(self,host: str) -> str:
        """Resolve domain name to IP address with error handling & formatting"""
        try:
            # gethostbyname_ex returns (hostname, aliaslist, ipaddrlist)
            official_name, aliases, ip_list = socket.gethostbyname_ex(host)

            result = [f"🔎 DNS Lookup for {host}", "-" * 40]
            result.append(f"Official Name : {official_name}")

            if aliases:
                result.append("Aliases       : " + ", ".join(aliases))
            else:
                result.append("Aliases       : None")

            if ip_list:
                result.append("IP Addresses  : " + ", ".join(ip_list))
            else:
                result.append("IP Addresses  : None")

            return "\n".join(result)

        except socket.gaierror as e:
            # DNS resolution error (e.g., domain doesn’t exist or no internet)
            return (
                f"🔎 DNS Lookup for {host}\n"
                f"{'-'*40}\n"
                f"Status   : ❌ Failed\n"
                f"Reason   : {str(e)}\n"
            )

        except Exception as e:
            # Catch other unexpected errors
            return (
                f"🔎 DNS Lookup for {host}\n"
                f"{'-'*40}\n"
                f"Status   : ❌ Error\n"
                f"Reason   : {str(e)}\n"
            )     

    def show_gateway(self):
        start_time = time.time()
        system=self.os_type.lower()
        try:
            if system == "windows":
                cmd = ["route", "print"]
            elif system == "linux":
                cmd = ["ip", "route"]
            else:
                return "❌ Unsupported OS"

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            output = result.stdout.strip()

            if not output:
                return "❌ No routing information found."

            formatted_output = []
            formatted_output.append("🌐 Routing Table".center(60, "-"))

            if system == "windows":
                lines = output.splitlines()
                # extract the IPv4 routing table
                if "IPv4 Route Table" in output:
                    idx = lines.index("IPv4 Route Table")
                    lines = lines[idx+2:]  # skip header lines

                headers = ["Network Destination", "Netmask", "Gateway", "Interface", "Metric"]
                formatted_output.append(" | ".join(f"{h:<20}" for h in headers))
                formatted_output.append("-" * 90)

                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5 and parts[0][0].isdigit():
                        row = [parts[0], parts[1], parts[2], parts[3], parts[4]]
                        formatted_output.append(" | ".join(f"{col:<20}" for col in row))

            elif system == "linux":
                headers = ["Destination", "Gateway", "Device", "Options"]
                formatted_output.append(" | ".join(f"{h:<20}" for h in headers))
                formatted_output.append("-" * 90)

                for line in output.splitlines():
                    parts = line.split()
                    if "via" in parts:
                        dst = parts[0]
                        gw = parts[2]
                        dev = parts[4] if "dev" in parts else "?"
                        formatted_output.append(f"{dst:<20} | {gw:<20} | {dev:<20} | via")
                    elif "dev" in parts:
                        dst = parts[0]
                        gw = "-"
                        dev = parts[2]
                        formatted_output.append(f"{dst:<20} | {gw:<20} | {dev:<20} | direct")

            execution_time = time.time() - start_time
            formatted_output.append("-" * 60)
            formatted_output.append(f"🟢 Execution Time: {execution_time:.3f} seconds")
            return "\n".join(formatted_output)

        except subprocess.TimeoutExpired:
            return "⏳ Command timed out after 20 seconds."
        except Exception as e:
            return f"⚠️ Error: {str(e)}"
        

    def latency_test(self,target, count=4, timeout=20):
        """
        Test network latency to a given host using ping.
        Works on Windows and Linux (no external modules required).
        """

        start_time = time.time()
        system = self.os_type.lower()

        try:
            if system == "windows":
                cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), target]
            elif system == "linux":
                cmd = ["ping", "-c", str(count), "-W", str(timeout), target]
            else:
                return "❌ Unsupported OS"

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
            output = result.stdout.strip()

            if not output:
                return f"❌ No response from {target}"

            # Format output
            lines = output.splitlines()
            formatted = []
            formatted.append(f"🌐 Latency Test to {target}")
            formatted.append("-" * 50)

            if system == "windows":
                sent, received, lost = 0, 0, 0
                avg, min_, max_ = None, None, None

                for line in lines:
                    if "Packets:" in line:
                        parts = line.split(",")
                        sent = int(parts[0].split("=")[1])
                        received = int(parts[1].split("=")[1])
                        lost = int(parts[2].split("=")[1].split()[0])
                    if "Average =" in line:
                        parts = line.split(",")
                        min_ = parts[0].split("=")[1].strip()
                        max_ = parts[1].split("=")[1].strip()
                        avg = parts[2].split("=")[1].strip()

                if avg:
                    formatted.append(f"Average Latency   : {avg}")
                    formatted.append(f"Min Latency       : {min_}")
                    formatted.append(f"Max Latency       : {max_}")
                    formatted.append(f"Packets Sent      : {sent}")
                    formatted.append(f"Packets Received  : {received}")
                    formatted.append(f"Packet Loss       : {lost}%")
                    formatted.append("-" * 50)
                    formatted.append("🟢 Status : Good Connection" if lost == 0 else "⚠️ Status : Packet Loss Detected")

            elif system == "linux":
                stats_line = [line for line in lines if "rtt min/avg/max/mdev" in line]
                packet_line = [line for line in lines if "packets transmitted" in line]

                if packet_line:
                    parts = packet_line[0].split(",")
                    sent = int(parts[0].split()[0])
                    received = int(parts[1].split()[0])
                    loss = parts[2].strip()
                    formatted.append(f"Packets Sent      : {sent}")
                    formatted.append(f"Packets Received  : {received}")
                    formatted.append(f"Packet Loss       : {loss}")

                if stats_line:
                    stats = stats_line[0].split("=")[1].split("/")
                    min_, avg, max_ = stats[0], stats[1], stats[2]
                    formatted.append(f"Average Latency   : {avg} ms")
                    formatted.append(f"Min Latency       : {min_} ms")
                    formatted.append(f"Max Latency       : {max_} ms")

                formatted.append("-" * 50)
                formatted.append("🟢 Status : Good Connection" if "0% packet loss" in output else "⚠️ Status : Packet Loss Detected")

            execution_time = time.time() - start_time
            formatted.append(f"⏱️ Execution Time: {execution_time:.3f} seconds")

            return "\n".join(formatted)

        except subprocess.TimeoutExpired:
            return f"⏳ Error: Request timed out after {timeout} seconds."
        except Exception as e:
            return f"⚠️ Error: {str(e)}"
    #=======================Allow/disable services=========================

    def allow_service(self,service_name: str):
        os_type = self.os_type
        print("\n===============================")
        print(f" ✅ ALLOW SERVICE ({service_name}) (சேவை_அனுமதி)")
        print("===============================")
        print(f"🖥️  Detected OS : {os_type}\n")

        port = self.service_port_map.get(service_name.lower())

        if not port:
            print(f"❌ Unknown service: {service_name}")
            print("➡️ Please provide a valid service name (e.g., ssh, http, mysql).")
            return

        try:
            if os_type == "Windows":
                cmd = ["netsh", "advfirewall", "firewall", "add", "rule",
                    f"name=Allow_{service_name}", "dir=in", "action=allow", f"protocol=TCP", f"localport={port}"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                print("🟢 Beginner View: Service allowed successfully ✅")
                print("\n📊 Professional View:")
                print(result.stdout.strip() or f"Rule added to allow {service_name} on port {port}")

            elif os_type == "Linux":
                try:
                    cmd = ["sudo", "ufw", "allow", str(port)]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    print("🟢 Beginner View: Service allowed successfully ✅")
                    print("\n📊 Professional View:")
                    print(result.stdout.strip() or f"ufw rule added to allow {service_name} on port {port}")
                except subprocess.CalledProcessError:
                    cmd = ["sudo", "iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "ACCEPT"]
                    subprocess.run(cmd, capture_output=True, text=True, check=True)
                    print("🟢 Beginner View: Service allowed successfully ✅")
                    print("\n📊 Professional View:")
                    print(f"iptables rule added to allow {service_name} on port {port}")

            else:
                print("🔴 Unsupported OS: This command works only on Windows and Linux.")

        except subprocess.CalledProcessError as e:
            print("❌ Error while allowing service!")
            print("📊 Details:", e.stderr.strip() if e.stderr else str(e))

        except FileNotFoundError:
            print("❌ Firewall tool not found (ufw/iptables/netsh missing).")
            print("➡️ Please install or configure manually.")

        except Exception as e:
            print("⚠️ Unexpected Error:", str(e))

    def block_service(self,service_name: str):
        os_type = platform.system()
        print("\n===============================")
        print(f" ⛔ BLOCK SERVICE ({service_name}) (சேவை_தடு)")
        print("===============================")
        print(f"🖥️  Detected OS : {os_type}\n")

        port = self.service_port_map.get(service_name.lower())

        if not port:
            print(f"❌ Unknown service: {service_name}")
            print("➡️ Please provide a valid service name (e.g., ssh, http, mysql).")
            return

        try:
            if os_type == "Windows":
                cmd = ["netsh", "advfirewall", "firewall", "add", "rule",
                    f"name=Block_{service_name}", "dir=in", "action=block", f"protocol=TCP", f"localport={port}"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                print("🟢 Beginner View: Service blocked successfully ✅")
                print("\n📊 Professional View:")
                print(result.stdout.strip() or f"Rule added to block {service_name} on port {port}")

            elif os_type == "Linux":
                try:
                    cmd = ["sudo", "ufw", "deny", str(port)]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    print("🟢 Beginner View: Service blocked successfully ✅")
                    print("\n📊 Professional View:")
                    print(result.stdout.strip() or f"ufw rule added to block {service_name} on port {port}")
                except subprocess.CalledProcessError:
                    cmd = ["sudo", "iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "DROP"]
                    subprocess.run(cmd, capture_output=True, text=True, check=True)
                    print("🟢 Beginner View: Service blocked successfully ✅")
                    print("\n📊 Professional View:")
                    print(f"iptables rule added to block {service_name} on port {port}")

            else:
                print("🔴 Unsupported OS: This command works only on Windows and Linux.")

        except subprocess.CalledProcessError as e:
            print("❌ Error while blocking service!")
            print("📊 Details:", e.stderr.strip() if e.stderr else str(e))

        except FileNotFoundError:
            print("❌ Firewall tool not found (ufw/iptables/netsh missing).")
            print("➡️ Please install or configure manually.")

        except Exception as e:
            print("⚠️ Unexpected Error:", str(e))


    #====================== PORT SCAN FUNCTIONS ===================


    def _parse_ports(self,port_spec):
        """
        Accepts:
        "22" -> [22]
        "20-25" -> [20,21,22,23,24,25]
        "22,80,443" -> [22,80,443]
        "20-22,80" -> [20,21,22,80]
        Raises ValueError for bad input.
        """
        ports = set()
        parts = port_spec.split(",")
        for p in parts:
            p = p.strip()
            if "-" in p:
                a, b = p.split("-", 1)
                a = int(a.strip()); b = int(b.strip())
                if a < 1 or b > 65535 or a > b:
                    raise ValueError(f"Invalid port range: {p}")
                ports.update(range(a, b+1))
            else:
                v = int(p)
                if v < 1 or v > 65535:
                    raise ValueError(f"Invalid port number: {p}")
                ports.add(v)
        return sorted(ports)


    def _scan_port(self,addr, port, timeout):
        """
        Try TCP connect to (addr, port) with timeout.
        Returns (port, state, duration_seconds)
        state: "open", "closed", "filtered", "error_resolve", "error_network", "error_other"
        """
        start = time.perf_counter()
        try:
            # socket.create_connection wraps connect and handles name resolution if needed
            with socket.create_connection((addr, port), timeout=timeout):
                dur = time.perf_counter() - start
                return (port, "open", dur)
        except socket.timeout:
            dur = time.perf_counter() - start
            return (port, "filtered", dur)   # likely filtered or unreachable (no reply)
        except ConnectionRefusedError:
            dur = time.perf_counter() - start
            return (port, "closed", dur)
        except OSError as e:
            dur = time.perf_counter() - start
            msg = str(e).lower()
            if "name or service not known" in msg or "nodename nor servname provided" in msg:
                return (port, "error_resolve", dur)
            if "network is unreachable" in msg or "no route to host" in msg:
                return (port, "error_network", dur)
            return (port, "error_other", dur)


    def port_scan(self,host, port_spec, timeout=1.0, workers=100):
        """
        Scan TCP ports on host according to port_spec (single, range or comma list).
        Returns a formatted string (human readable + informative).
        """
        # Resolve host first
        start_all = time.perf_counter()
        try:
            resolved = socket.gethostbyname_ex(host)
            canonical_name, aliases, ip_list = resolved[0], resolved[1], resolved[2]
            ip_display = ", ".join(ip_list) if ip_list else "N/A"
        except socket.gaierror as e:
            return (
                f"Port Scan: {host} ({port_spec})\n"
                + "-" * 60 + "\n"
                + "Status   : ❌ Host name resolution failed\n"
                + f"Reason   : {e}\n"
                + "Note     : Check DNS or the hostname/IP provided.\n"
            )

        # parse ports
        try:
            ports = self._parse_ports(port_spec)
        except ValueError as e:
            return f"Port Scan: Invalid port specification: {e}"

        total_ports = len(ports)
        header_lines = []
        header_lines.append(f"Port Scan: {host}  ({ip_display})")
        header_lines.append("-" * 60)
        header_lines.append(f"Ports    : {port_spec} -> {total_ports} port(s)")
        header_lines.append(f"Timeout  : {timeout}s  Parallel threads: {min(workers, total_ports)}")
        header_lines.append("")

        # Limit workers sensibly
        max_workers = min(workers, total_ports, 500)
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(self._scan_port, ip_list[0], p, timeout): p for p in ports}
            for fut in as_completed(futures):
                p = futures[fut]
                try:
                    res = fut.result()
                except Exception:
                    results.append((p, "error_other", 0.0))
                else:
                    results.append(res)

        # Sort results by port
        results.sort(key=lambda x: x[0])

        # Produce summary counts
        counts = {"open":0, "closed":0, "filtered":0, "error_resolve":0, "error_network":0, "error_other":0}
        for _, state, _ in results:
            if state in counts:
                counts[state] += 1
            else:
                counts["error_other"] += 1

        # Build table lines
        lines = header_lines.copy()
        lines.append(f"{'Port':>6}  {'State':<12}  {'RTT(ms)':>8}  {'Service':<12}")
        lines.append("-"*60)
        for port, state, dur in results:
            rtt_ms = f"{dur*1000:.1f}" if dur and dur > 0 else "-"
            # Try to map common port -> service
            service = "-"
            try:
                service = socket.getservbyport(port, "tcp")
            except Exception:
                service = "-"
            state_mark = {"open":"✅ open", "closed":"✖ closed", "filtered":"⚠ filtered",
                        "error_resolve":"! DNS", "error_network":"! network", "error_other":"! err"}.get(state, state)
            lines.append(f"{port:6d}  {state_mark:<12}  {rtt_ms:>8}  {service:<12}")

        # Summary
        elapsed = time.perf_counter() - start_all
        lines.append("-"*60)
        lines.append(f"Summary: Open={counts['open']}, Closed={counts['closed']}, Filtered={counts['filtered']}, Errors={counts['error_resolve']+counts['error_network']+counts['error_other']}")
        lines.append(f"Elapsed: {elapsed:.2f}s")

        # Recommendations (helpful for diagnosis)
        if counts["open"] == 0 and counts["filtered"] > 0:
            lines.append("Note: Ports appear filtered (firewall may be dropping packets).")
        if counts["open"] == 0 and counts["closed"] > 0 and counts["filtered"] == 0:
            lines.append("Note: Host reachable but no listening services on the scanned ports.")
        if counts["error_network"] > 0:
            lines.append("Warning: network unreachable for one or more ports (check routing/firewall).")

        return "\n".join(lines)
    

    def allow_port(self, port):
        """
        துறைமுகம்_அனுமதி (ALLOW_PORT)
        Opens a TCP port in the firewall (Windows & Linux).
        Consistent Beginner + Professional output format.
        """
        os_type = self.os_type
        print("\n===============================")
        print(f" 🔓 ALLOW PORT {port} (துறைமுகம்_அனுமதி)")
        print("===============================")
        print(f"🖥️  Detected OS : {os_type}\n")

        try:
            # ---------------- Windows ----------------
            if os_type == "Windows":
                rule_name = f"Allow Port {port}"
                # Check if rule with this name exists
                try:
                    chk = subprocess.run(
                        ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"],
                        capture_output=True, text=True
                    )
                except FileNotFoundError:
                    print("❌ 'netsh' not found on this system.")
                    return

                chk_out = (chk.stdout or "") + (chk.stderr or "")
                if "no rules match" not in chk_out.lower() and chk_out.strip():
                    # Rule exists
                    print(f"🟡 Beginner View: Port {port} already has an allow rule (no change).")
                    print("\n📊 Professional View:")
                    print(chk_out.strip())
                    return

                # Add the rule
                add = subprocess.run([
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    f"name={rule_name}", "dir=in", "action=allow",
                    "protocol=TCP", f"localport={port}"
                ], capture_output=True, text=True)

                if add.returncode == 0:
                    print(f"🟢 Beginner View: Port {port} is now OPEN ✅")
                    print("\n📊 Professional View:")
                    print(add.stdout.strip() or "Rule added successfully.")
                else:
                    print(f"❌ Failed to add rule for port {port}.")
                    print("\n📊 Professional View:")
                    print(add.stderr.strip() or add.stdout.strip() or f"Return code: {add.returncode}")

            # ---------------- Linux ----------------
            elif os_type == "Linux":
                # Try UFW first
                use_iptables = False
                try:
                    status = subprocess.run(["sudo", "ufw", "status", "numbered"],
                                            capture_output=True, text=True)
                    out = (status.stdout or "") + (status.stderr or "")
                    if f"{port}/tcp" in out and "allow" in out.lower():
                        print(f"🟡 Beginner View: Port {port} already allowed (ufw).")
                        print("\n📊 Professional View:")
                        print(out.strip())
                        return
                    # Not found → add
                    add = subprocess.run(["sudo", "ufw", "allow", f"{port}/tcp"],
                                        capture_output=True, text=True)
                    if add.returncode == 0:
                        print(f"🟢 Beginner View: Port {port} is now OPEN ✅")
                        print("\n📊 Professional View:")
                        print(add.stdout.strip() or add.stderr.strip() or "ufw rule added.")
                        return
                    # If ufw exists but failed for some reason, we'll fallback to iptables
                    use_iptables = True
                except FileNotFoundError:
                    use_iptables = True

                # iptables fallback
                if use_iptables:
                    # Check if iptables already has rule
                    chk = subprocess.run(
                        ["sudo", "iptables", "-C", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "ACCEPT"],
                        capture_output=True, text=True
                    )
                    if chk.returncode == 0:
                        print(f"🟡 Beginner View: Port {port} already allowed (iptables).")
                        print("\n📊 Professional View:")
                        print("iptables rule exists (INPUT ACCEPT).")
                        return

                    # Add iptables rule
                    add = subprocess.run(
                        ["sudo", "iptables", "-I", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "ACCEPT"],
                        capture_output=True, text=True
                    )
                    if add.returncode == 0:
                        print(f"🟢 Beginner View: Port {port} is now OPEN ✅")
                        print("\n📊 Professional View:")
                        print(f"iptables rule inserted: ACCEPT tcp dport {port}")
                    else:
                        print(f"❌ Failed to add iptables rule for port {port}.")
                        print("\n📊 Professional View:")
                        print(add.stderr.strip() or add.stdout.strip() or f"Return code: {add.returncode}")

            # ---------------- Unsupported OS ----------------
            else:
                print("🔴 Unsupported OS: This command works only on Windows and Linux.")

        except PermissionError:
            print("❌ Permission denied: run as Administrator (Windows) or use sudo (Linux).")

        except FileNotFoundError as e:
            print("❌ Required tool not found:", str(e))
            print("➡️ Install ufw/iptables (Linux) or ensure netsh is available (Windows).")

        except Exception as e:
            print("⚠️ Unexpected Error:", str(e))



    def block_port(self, port):
        """
        துறைமுகம்_தடு (BLOCK_PORT)
        Blocks a TCP port in the firewall (Windows & Linux).
        Consistent Beginner + Professional output format.
        """
        # Validate port
       
        os_type = self.os_type
        print("\n===============================")
        print(f" 🔒 BLOCK PORT {port} (துறைமுகம்_தடு)")
        print("===============================")
        print(f"🖥️  Detected OS : {os_type}\n")

        try:
            # ---------------- Windows ----------------
            if os_type == "Windows":
                rule_name = f"Block Port {port}"
                # Check existing rule
                try:
                    chk = subprocess.run(
                        ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"],
                        capture_output=True, text=True
                    )
                except FileNotFoundError:
                    print("❌ 'netsh' not found on this system.")
                    return

                chk_out = (chk.stdout or "") + (chk.stderr or "")
                if "no rules match" not in chk_out.lower() and chk_out.strip():
                    print(f"🟡 Beginner View: Port {port} already has a block rule (no change).")
                    print("\n📊 Professional View:")
                    print(chk_out.strip())
                    return

                # Add block rule
                add = subprocess.run([
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    f"name={rule_name}", "dir=in", "action=block",
                    "protocol=TCP", f"localport={port}"
                ], capture_output=True, text=True)

                if add.returncode == 0:
                    print(f"🟢 Beginner View: Port {port} is now BLOCKED 🚫")
                    print("\n📊 Professional View:")
                    print(add.stdout.strip() or "Rule added successfully.")
                else:
                    print(f"❌ Failed to add block rule for port {port}.")
                    print("\n📊 Professional View:")
                    print(add.stderr.strip() or add.stdout.strip() or f"Return code: {add.returncode}")

            # ---------------- Linux ----------------
            elif os_type == "Linux":
                use_iptables = False
                try:
                    status = subprocess.run(["sudo", "ufw", "status", "numbered"],
                                            capture_output=True, text=True)
                    out = (status.stdout or "") + (status.stderr or "")
                    if f"{port}/tcp" in out and ("deny" in out.lower() or "blocked" in out.lower()):
                        print(f"🟡 Beginner View: Port {port} already blocked (ufw).")
                        print("\n📊 Professional View:")
                        print(out.strip())
                        return

                    add = subprocess.run(["sudo", "ufw", "deny", f"{port}/tcp"],
                                        capture_output=True, text=True)
                    if add.returncode == 0:
                        print(f"🟢 Beginner View: Port {port} is now BLOCKED 🚫")
                        print("\n📊 Professional View:")
                        print(add.stdout.strip() or add.stderr.strip() or "ufw rule added.")
                        return
                    use_iptables = True
                except FileNotFoundError:
                    use_iptables = True

                # iptables fallback
                if use_iptables:
                    chk = subprocess.run(
                        ["sudo", "iptables", "-C", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "DROP"],
                        capture_output=True, text=True
                    )
                    if chk.returncode == 0:
                        print(f"🟡 Beginner View: Port {port} already blocked (iptables).")
                        print("\n📊 Professional View:")
                        print("iptables rule exists (INPUT DROP).")
                        return

                    add = subprocess.run(
                        ["sudo", "iptables", "-I", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "DROP"],
                        capture_output=True, text=True
                    )
                    if add.returncode == 0:
                        print(f"🟢 Beginner View: Port {port} is now BLOCKED 🚫")
                        print("\n📊 Professional View:")
                        print(f"iptables rule inserted: DROP tcp dport {port}")
                    else:
                        print(f"❌ Failed to add iptables DROP rule for port {port}.")
                        print("\n📊 Professional View:")
                        print(add.stderr.strip() or add.stdout.strip() or f"Return code: {add.returncode}")

            # ---------------- Unsupported OS ----------------
            else:
                print("🔴 Unsupported OS: This command works only on Windows and Linux.")

        except PermissionError:
            print("❌ Permission denied: run as Administrator (Windows) or use sudo (Linux).")

        except FileNotFoundError as e:
            print("❌ Required tool not found:", str(e))
            print("➡️ Install ufw/iptables (Linux) or ensure netsh is available (Windows).")

        except Exception as e:
            print("⚠️ Unexpected Error:", str(e))

   #======================= firewall enable and disable =================

    def enable_firewall(self):
        os_type = self.os_type
        print("\n===============================")
        print(" 🔐 ENABLE FIREWALL (தடுப்பு_செயல்படுத்து)")
        print("===============================")
        print(f"🖥️  Detected OS : {os_type}\n")

        try:
            if os_type == "Windows":
                cmd = ["netsh", "advfirewall", "set", "allprofiles", "state", "on"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # Beginner output
                print("🟢 Beginner View: Firewall is now ENABLED ✅")
                
                # Professional output
                print("\n📊 Professional View:")
                if result.returncode == 0:
                    print(result.stdout.strip() or "Firewall enabled successfully.")
                else:
                    print("⚠️ Firewall command executed with issues:", result.stderr.strip())

            elif os_type == "Linux":
                try:
                    # Force enable UFW without interactive prompt
                    cmd = ["sudo", "ufw", "--force", "enable"]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    print("🟢 Beginner View: Firewall is now ENABLED ✅")
                    print("\n📊 Professional View:")
                    if result.returncode == 0:
                        print(result.stdout.strip() or result.stderr.strip() or "Firewall enabled successfully.")
                    else:
                        print("⚠️ UFW execution issue:", result.stderr.strip())

                except FileNotFoundError:
                    # fallback to iptables if ufw not found
                    cmds = [
                        ["sudo", "iptables", "-P", "INPUT", "DROP"],
                        ["sudo", "iptables", "-P", "OUTPUT", "ACCEPT"],
                        ["sudo", "iptables", "-P", "FORWARD", "DROP"],
                    ]
                    for cmd in cmds:
                        subprocess.run(cmd, capture_output=True, text=True)

                    print("🟢 Beginner View: Firewall is now ENABLED ✅")
                    print("\n📊 Professional View:")
                    print("iptables policy set: DROP incoming, ACCEPT outgoing.")

            else:
                print("🔴 Unsupported OS: This command works only on Windows and Linux.")

        except Exception as e:
            print("⚠️ Unexpected Error:", str(e))


    def disable_firewall(self):
        os_type = self.os_type
        print("\n===============================")
        print(" 🔓 DISABLE FIREWALL (தடுப்பு_நிறுத்து)")
        print("===============================")
        print(f"🖥️  Detected OS : {os_type}\n")

        try:
            if os_type == "Windows":
                cmd = ["netsh", "advfirewall", "set", "allprofiles", "state", "off"]
                result = subprocess.run(cmd, capture_output=True, text=True)

                # Beginner output
                print("🟢 Beginner View: Firewall is now DISABLED ❌")

                # Professional output
                print("\n📊 Professional View:")
                if result.returncode == 0:
                    print(result.stdout.strip() or "Firewall disabled successfully.")
                else:
                    print("⚠️ Firewall command executed with issues:", result.stderr.strip())

            elif os_type == "Linux":
                try:
                    # Force disable UFW without interactive prompt
                    cmd = ["sudo", "ufw", "--force", "disable"]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    print("🟢 Beginner View: Firewall is now DISABLED ❌")
                    print("\n📊 Professional View:")
                    if result.returncode == 0:
                        print(result.stdout.strip() or result.stderr.strip() or "Firewall disabled successfully.")
                    else:
                        print("⚠️ UFW execution issue:", result.stderr.strip())

                except FileNotFoundError:
                    # fallback to iptables flush if ufw not found
                    cmds = [
                        ["sudo", "iptables", "-F"],
                        ["sudo", "iptables", "-P", "INPUT", "ACCEPT"],
                        ["sudo", "iptables", "-P", "OUTPUT", "ACCEPT"],
                        ["sudo", "iptables", "-P", "FORWARD", "ACCEPT"],
                    ]
                    for cmd in cmds:
                        subprocess.run(cmd, capture_output=True, text=True)

                    print("🟢 Beginner View: Firewall is now DISABLED ❌")
                    print("\n📊 Professional View:")
                    print("iptables policy reset: ACCEPT all traffic (INPUT/OUTPUT/FORWARD).")

            else:
                print("🔴 Unsupported OS: This command works only on Windows and Linux.")

        except Exception as e:
            print("⚠️ Unexpected Error:", str(e))
    #==========================firewall rules
    def list_firewall_rules(self):
        os_type = self.os_type
        print("\n===================================")
        print(" 📜 FIREWALL RULES (துறைமுகம்_விதிகள்)")
        print("===================================")
        print(f"🖥️  Detected OS : {os_type}\n")

        try:
            if os_type == "Windows":
                cmd = ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)

                print("🟢 Beginner View: Below are your active firewall rules 👇")
                print("\n📊 Professional View (Raw netsh output):\n")
                print(result.stdout.strip() or "No firewall rules found.")

            elif os_type == "Linux":
                try:
                    cmd = ["sudo", "ufw", "status", "numbered"]
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

                    print("🟢 Beginner View: Below are your active firewall rules 👇")
                    print("\n📊 Professional View (UFW output):\n")
                    print(result.stdout.strip() or "No firewall rules found.")

                except subprocess.CalledProcessError:
                    # fallback → iptables
                    cmd = ["sudo", "iptables", "-L", "-n", "-v"]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    print("🟢 Beginner View: Firewall rules listed successfully 👇")
                    print("\n📊 Professional View (iptables output):\n")
                    print(result.stdout.strip() or "No iptables rules found.")

            else:
                print("🔴 Unsupported OS: This command works only on Windows and Linux.")

        except subprocess.CalledProcessError as e:
            print("❌ Error while listing firewall rules!")
            print("📊 Details:", e.stderr.strip() if e.stderr else str(e))

        except FileNotFoundError:
            print("❌ Firewall tool not found (ufw/iptables/netsh missing).")
            print("➡️ Please install or configure manually.")

        except Exception as e:
            print("⚠️ Unexpected Error:", str(e))


    # ===================== formatters (pretty, fast) =====================
    def _fmt_if_addrs(self, data: dict):
        lines = ["Interface Addresses", "-" * 60]
        if not data:
            lines.append("(none)")
            return "\n".join(lines)
        fam_map = {
            socket.AF_INET:  "IPv4",
            socket.AF_INET6: "IPv6",
            getattr(socket, "AF_LINK", 0): "MAC"
        }
        for iface, addrs in data.items():
            lines.append(f"\n[{iface}]")
            if not addrs:
                lines.append("  (no addresses)")
                continue
            for a in addrs:
                fam = fam_map.get(getattr(a, "family", None), str(getattr(a, "family", "")))
                addr = getattr(a, "address", "")
                mask = getattr(a, "netmask", "")
                bcast = getattr(a, "broadcast", "")
                ptp = getattr(a, "ptp", "")
                lines.append(f"  {fam:<4}  addr={addr}  mask={mask}  bcast={bcast}  ptp={ptp}")
        return "\n".join(lines)

    def _fmt_if_stats(self, data: dict):
        lines = ["Interface Status", "-" * 60, f"{'Iface':<18} {'Up':<4} {'Speed(Mbps)':<12} {'Duplex':<8} {'MTU':<6}"]
        for iface, st in data.items():
            up = "Yes" if getattr(st, "isup", False) else "No"
            sp = getattr(st, "speed", 0)
            dp = getattr(st, "duplex", 0)
            # Map duplex code to text if available
            dup_map = {0: "?", 1: "Full", 2: "Half"}
            dup = dup_map.get(dp, str(dp))
            mtu = getattr(st, "mtu", 0)
            lines.append(f"{iface:<18} {up:<4} {sp:<12} {dup:<8} {mtu:<6}")
        return "\n".join(lines)

    def _fmt_connections(self, conns, limit=50):
        lines = ["Active Connections", "-" * 90,
                 f"{'Proto':<6} {'Local Address':<25} {'Remote Address':<25} {'State':<13} {'PID':<6}"]
        cnt = 0
        for c in conns:
            if cnt >= limit: break
            proto = "tcp" if getattr(c, "type", 0) == socket.SOCK_STREAM else ("udp" if getattr(c, "type", 0) == socket.SOCK_DGRAM else str(getattr(c, "type", "")))
            la = getattr(c, "laddr", None)
            ra = getattr(c, "raddr", None)
            ltxt = f"{la.ip}:{la.port}" if la else ""
            rtxt = f"{ra.ip}:{ra.port}" if ra else ""
            state = getattr(c, "status", "")
            pid = getattr(c, "pid", "")
            lines.append(f"{proto:<6} {ltxt:<25} {rtxt:<25} {state:<13} {str(pid):<6}")
            cnt += 1
        lines.append(f"-- showing {cnt} of {len(conns)} --")
        return "\n".join(lines)

    def _fmt_io_global(self, io):
        # scounters(bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout)
        fields = getattr(io, "_fields", [])
        return "\n".join([f"{f}: {getattr(io, f)}" for f in fields]) if fields else str(io)

    def _fmt_io_pernic(self, d):
        lines = ["Per-Interface IO", "-" * 60, f"{'Iface':<16} {'Sent(bytes)':>12} {'Recv(bytes)':>12} {'Pkt-S':>8} {'Pkt-R':>8} {'ErrIn':>6} {'ErrOut':>6} {'DropIn':>6} {'DropOut':>7}"]
        for iface, io in d.items():
            lines.append(f"{iface:<16} {getattr(io,'bytes_sent',0):>12} {getattr(io,'bytes_recv',0):>12} "
                         f"{getattr(io,'packets_sent',0):>8} {getattr(io,'packets_recv',0):>8} "
                         f"{getattr(io,'errin',0):>6} {getattr(io,'errout',0):>6} "
                         f"{getattr(io,'dropin',0):>6} {getattr(io,'dropout',0):>7}")
        return "\n".join(lines)

    # ===================== utilities =====================
    def speed(self, iface):
        per = psutil.net_io_counters(pernic=True)
        if iface not in per:
            # fallback: first NIC
            if not per:
                return 0.0
            iface = next(iter(per.keys()))
        old = per[iface].bytes_recv
        time.sleep(1)
        new = psutil.net_io_counters(pernic=True)[iface].bytes_recv
        return (new - old) / 1024.0  # KB/s

    # ===================== main dispatcher =====================
    def execute_command(self, line_no, args=None):
       
        cmd = self.value.strip()

        try:
            # ---- direct psutil commands (pretty formatted) ----
            if cmd == 'SHOW_INTERFACE_ADDRESSES':
                return String(self._fmt_if_addrs(self.base_commands[cmd]()))
            elif cmd == 'SHOW_INTERFACE_STATUS':
                return String(self._fmt_if_stats(self.base_commands[cmd]()))
            elif cmd == 'SHOW_ACTIVE_CONNECTIONS':
                return String(self._fmt_connections(self.base_commands[cmd]()))
            elif cmd == 'SHOW_NETWORK_IO':
                return String(self._fmt_io_global(self.base_commands[cmd]()))
            elif cmd == 'SHOW_NETWORK_IO_PER_INTERFACE' :
                return String(self._fmt_io_pernic(self.base_commands[cmd]()))
            #================Firewall able and disable==============
            elif cmd == 'ENABLE_FIREWALL':
                return self.enable_firewall()
            elif cmd == 'DISABLE_FIREWALL':
                return self.disable_firewall()
            # ---- special actions ----
            elif cmd == 'RUN_AS_ADMIN':
                return Boolean(1.0 if self.run_as_admin() else 0.0)
            elif cmd == 'SHOW_NETWORK_SPEED':
                # args: [TOKEN, ifaceToken]
                iface = args[1].value if args and len(args) > 1 else ""
                return Number(self.speed(iface))
            elif cmd == 'ENABLE_INTERFACE':
                iface = args[1].value
                return Boolean(1.0 if self._toggle_iface(iface, True).returncode == 0 else 0.0)
            elif cmd == 'DISABLE_INTERFACE':
                iface = args[1].value
                return Boolean(1.0 if self._toggle_iface(iface, False).returncode == 0 else 0.0)
            elif cmd == 'SET_DHCP':
                iface = args[1].value
                return Boolean(1.0 if self._set_dhcp(iface).returncode == 0 else 0.0)
            elif cmd == 'SET_IP':
                # args: [TOKEN, [ifaceTok, ipTok, gwTok, maskTok]]
                iface = args[1][0].value
                ip    = args[1][1].value
                gw    = args[1][2].value if hasattr(args[1][2],'value') else args[1][2]
                mask  = args[1][3].value
                return Boolean(1.0 if self._set_ip(iface, ip, gw, mask).returncode == 0 else 0.0)
            elif cmd == 'LIST_WIFI':
                return String(self.list_wifi())
            elif cmd == 'CONNECT_WIFI':
                # args: [TOKEN, [ssidTok, passTok]]
                ssid = args[1][0].value
                password = args[1][1].value
                return Boolean(1.0 if self.connect_wifi(ssid, password) == 1 else 0.0)
            elif cmd == 'DISCONNECT_WIFI':
                return Boolean(1.0 if self.disconnect_wifi() == 1 else 0.0)
            elif cmd == "PING":
                return String(self.ping_test(args[1][0].value))
            elif cmd == "TRACEROUTE":
                return String(self.traceroute(args[1][0].value))
            elif cmd == 'DNS_LOOKUP':
                return String(self.dns_lookup(args[1][0].value))
            elif cmd == 'PORT_SCAN':
                host=args[1][0].value
                port_spec=args[1][1].value
                return String(self.port_scan(host,port_spec))
            elif cmd == 'SHOW_GATEWAY':
                return String(self.show_gateway())
            elif cmd == 'LATENCY_TEST':
                return String(self.latency_test(args[1][0].value))
            elif cmd == 'ALLOW_PORT':
                return self.allow_port(int(args[1][0].value))
            elif cmd == 'BLOCK_PORT':
                return self.block_port(int(args[1][0].value))
            elif cmd == 'LIST_FIREWALL_RULES':
                return self.list_firewall_rules()
            elif cmd == 'ALLOW_SERVICE':
                return self.allow_service(args[1][0].value)
            elif cmd=='BLOCK_SERVICE':
                return self.block_service(args[1][0].value)
            elif cmd=="ACTIVATE_AGENT_VALLAI":
                return ai.main(args[1][0].value,args[1][1].value)


            # Unknown command
            return Error(f"Unknown network command: {cmd}", line_no, cmd)

        except Exception as e:
            return Error(str(e), line_no, e)
