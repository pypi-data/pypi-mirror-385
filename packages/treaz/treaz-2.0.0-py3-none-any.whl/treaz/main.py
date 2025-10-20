#!/usr/bin/env python3
from __future__ import annotations
import socket
import re
import datetime
import os
import platform
import subprocess
import shutil
from typing import Optional, Dict, Any
import time


# ─────────────────────────────────────────────────────────────
#  Treaz — System & Network Reconnaissance Tool
#  Copyright (c) 2025 ERVULN
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is provided on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ─────────────────────────────────────────────────────────────


try:
    import requests
except:
    requests = None


LOGO = [
"⠀⠀⢀⣴⣶⣿⣿⣷⡶⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⢶⣿⣿⣿⣿⣶⣄",
"⠀⢠⡿⠿⠿⠿⢿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⣿⡿⠿⠿⠿⠿⣦",
"⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣿⡿⠆⠀⠀⠀⠀⠰⣿⣿⠿⠋⠁",
"⠀⠀⠀⠀⣀⣤⡤⠤⢤⣀⡈⢿⡄⠀⠀⠀⠀⢠⡟⢁⣠⡤⠤⠤⢤⣀",
"⠐⢄⣀⣼⢿⣾⣿⣿⣿⣷⣿⣆⠁⡆⠀⠀⢰⠈⢸⣿⣾⣿⣿⣿⣷⡮⣧⣀⡠⠂",
"⠰⠛⠉⠙⠛⠶⠶⠏⠷⠛⠋⠁⢠⡇⠀⠀⢸⡄⠈⠛⠛⠿⠹⠿⠶⠚⠋⠉⠛⠆",
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⡇⠀⠀⢸⣷⡀",
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⢻⠇⠀⠀⠘⡟⠳⡄",
"⠰⣄⡀⠀⠀⣀⣠⡤⠞⠫⠁⠀⢸⠀⠀⠀⠀⡇⠀⠘⠄⠳⢤⣀⣀⠀⠀⣀⣠",
"⠀⢻⣏⢻⣯⡉⠀⠀⠀⠀⠀⠒⢎⣓⠶⠶⣞⡱⠒⠀⠀⠀⠀⠀⢉⣽⡟⣹⡟",
"⠀⠀⢻⣆⠹⣿⣆⣀⣀⣀⣀⣴⣿⣿⠟⠻⣿⣿⣦⣀⣀⣀⣀⣰⣿⠟⣰⡟",
"⠀⠀⠀⠻⣧⡘⠻⠿⠿⠿⠿⣿⣿⣃⣀⣀⣙⣿⣿⠿⠿⠿⠿⠟⢃⣴⠟",
"⠀⠀⠀⠀⠙⣮⠐⠤⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠁⠀⠀⠀⠤⠊⡵⠋",
"⠀⠀⠀⠀⠀⠈⠳⡀⠀⠀⠀⠀⠀⠲⣶⣶⠖⠀⠀⠀⠀⠀⢀⠜⠁",
"⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⢀⣿⣿⡀⠀⠀⠀⠀⠀⠁",
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡇",
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⠃",
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡿",
]


import re

# --- Remove color codes for clean length calculation ---
def strip_ansi(s):
    return re.sub(r"\033\[[0-9;]*m", "", s)

# --- Create cyber blue → cyan gradient text ---
def gradient_text(text, start=27, end=51):
    out = ""
    steps = max(len(text) - 1, 1)
    for i, ch in enumerate(text):
        color = int(start + (end - start) * i / steps)
        out += f"\033[38;5;{color}m{ch}"
    return out + "\033[0m"

# colorize logo with gradient
def colorize_logo(logo_lines):
    """ this motherfucking bleow code apply the same cyber gradient (blue → cyan → aqua) to each ASCII logo line."""
    colored = []
    for line in logo_lines:
        colored.append(gradient_text(line, 27, 51))  # same gradient as labels
    return colored

# It is the fucking  Format label and value with gradient colors ---
def format_label_value(label, value, width=18):
    label_color = gradient_text(label.ljust(width), 27, 39)  #  cheesy dark to light blue
    value_color = gradient_text(value, 45, 51)               # fucking cyan to aqua
    return f"{label_color}{value_color}"

# it will Print each info line beside the ASCII logo ---
def print_line_with_logo(text, logo=""):
    target_col = 70
    padding = " " * max(target_col - len(strip_ansi(text)), 0)
    print(f"{text}{padding}{logo}")




# psutil is optional in any caseeeeeeeee
try:
    import psutil
except Exception:
    psutil = None


# Memory code begins ( RAM & ROM )
def get_memory_info() -> Dict[str, Any]:

    def _fmt(n):
        # format bytes to human-friendly
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024.0:
                return f"{n:.1f} {unit}"
            n /= 1024.0
        return f"{n:.1f} PB"

    if psutil:
        vm = psutil.virtual_memory()
        return {
            "total": _fmt(vm.total),
            "available": _fmt(vm.available),
            "used": _fmt(vm.used),
            "percent": f"{vm.percent}%",
            "raw": vm,
        }
    # fallback: try platform-specific (limited)
    try:
        if platform.system() == "Linux":
            with open("/proc/meminfo", "r") as f:
                mem = f.read()
            m_total = re.search(r"MemTotal:\s+(\d+)\s+kB", mem)
            m_free = re.search(r"MemAvailable:\s+(\d+)\s+kB", mem)
            if m_total:
                total = int(m_total.group(1)) * 1024
                available = int(m_free.group(1)) * 1024 if m_free else 0
                used = total - available
                percent = round(100 * used / total, 1) if total else 0
                return {
                    "total": _fmt(total),
                    "available": _fmt(available),
                    "used": _fmt(used),
                    "percent": f"{percent}%",
                }
    except Exception:
        pass
    return {"error": "psutil not installed and no fallback available"}


# cpu info code ........................................
def get_cpu_info() -> Dict[str, Any]:

    info: Dict[str, Any] = {}
    try:
        info["platform"] = platform.platform()
        info["processor"] = platform.processor() or ""
        if psutil:
            info["logical_cores"] = psutil.cpu_count(logical=True)
            info["physical_cores"] = psutil.cpu_count(logical=False)
            try:
                freq = psutil.cpu_freq()
                if freq:
                    info["frequency_mhz"] = getattr(freq, "current", None) or getattr(freq, "max", None)
            except Exception:
                pass
            try:
                info["load_percent_1m"], info["load_percent_5m"], info["load_percent_15m"] = (
                    round(x, 1) for x in (psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0.0, 0.0, 0.0))
                )
            except Exception:
                pass
        # platform-specific extra
        sys = platform.system()
        if sys == "Linux":
            try:
                out = subprocess.check_output(["lscpu"], universal_newlines=True, stderr=subprocess.DEVNULL)
                m = re.search(r"Model name:\s*(.+)", out)
                if m:
                    info["model"] = m.group(1).strip()
            except Exception:
                pass
        elif sys == "Darwin":
            try:
                out = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], universal_newlines=True)
                if out:
                    info["model"] = out.strip()
            except Exception:
                pass
        elif sys == "Windows":
            try:
                out = subprocess.check_output(["wmic", "cpu", "get", "Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed"], universal_newlines=True, stderr=subprocess.DEVNULL)
                lines = [l.strip() for l in out.splitlines() if l.strip()]
                if len(lines) >= 2:
                    # messy parse; deliver raw output
                    info["wmic_raw"] = lines
            except Exception:
                pass
    except Exception as e:
        info["error"] = str(e)
    return info


# gPU info code ------------------
def get_gpu_info() -> Dict[str, Any]:
 
    info: Dict[str, Any] = {"gpus": []}
    sys = platform.system()
    try:
        # nvidia-smi (NVIDIA GPU)
        if shutil.which("nvidia-smi"):
            try:
                out = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], universal_newlines=True)
                for line in out.splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    if parts:
                        info["gpus"].append({"name": parts[0], "memory": parts[1] if len(parts) > 1 else None, "driver": parts[2] if len(parts) > 2 else None})
                return info
            except Exception:
                pass
        # macOS: system_profiler
        if sys == "Darwin":
            try:
                out = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], universal_newlines=True, stderr=subprocess.DEVNULL)
                # crude parsing
                blocks = out.split("\n\n")
                for b in blocks:
                    if "Chipset Model" in b or "Graphics" in b or "Vendor" in b:
                        name_m = re.search(r"(Chipset Model|Model):\s*(.+)", b)
                        vram_m = re.search(r"VRAM.*:\s*(.+)", b)
                        if name_m:
                            info["gpus"].append({"name": name_m.group(2).strip(), "vram": vram_m.group(1).strip() if vram_m else None})
                return info
            except Exception:
                pass
        # Linux fallback: lspci -nnk | grep -i vga -A 2
        if sys == "Linux" and shutil.which("lspci"):
            try:
                out = subprocess.check_output(["lspci", "-nnk"], universal_newlines=True, stderr=subprocess.DEVNULL)
                for line in out.splitlines():
                    if re.search(r"VGA|3D controller", line, re.I):
                        # e.g. "01:00.0 VGA compatible controller: NVIDIA Corporation ... "
                        gpuname = line.split(":", 2)[-1].strip()
                        info["gpus"].append({"name": gpuname})
                return info
            except Exception:
                pass
    except Exception:
        pass
    if not info["gpus"]:
        info["note"] = "Bruh GPU info found (requires nvidia-smi, system_profiler, or lspci)"
    return info


# Storage cdode start 
# ----------------------------
def get_storage_info() -> Dict[str, Any]:
    def _fmt(n):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024.0:
                return f"{n:.1f} {unit}"
            n /= 1024.0
        return f"{n:.1f} PB"

    info: Dict[str, Any] = {"total": None, "used": None, "free": None, "partitions": []}
    try:
        if psutil:
            total = used = free = 0
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    info["partitions"].append({
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total": _fmt(usage.total),
                        "used": _fmt(usage.used),
                        "free": _fmt(usage.free),
                        "percent": f"{usage.percent}%",
                    })
                    total += usage.total
                    used += usage.used
                    free += usage.free
                except Exception:
                    continue
            info["total"] = _fmt(total)
            info["used"] = _fmt(used)
            info["free"] = _fmt(free)
            return info
        # fallback: use shutil.disk_usage on root
        total, used, free = shutil.disk_usage("/")
        info["total"] = _fmt(total)
        info["used"] = _fmt(used)
        info["free"] = _fmt(free)
    except Exception as e:
        info["error"] = str(e)
    return info


#VPN code start from here ---------------------------- ( but it did not work well / malai code lekhna jhau vho tei vayera) 
def get_vpn_status() -> Dict[str, Any]:

    status = {"vpn_interfaces": [], "default_route_if": None, "note": None}
    try:
        # detect interfaces that look like VPN
        nic_names = []
        if psutil:
            nic_names = list(psutil.net_if_addrs().keys())
        else:
            # fallback: parse 'ip link' or 'ifconfig'
            try:
                out = subprocess.check_output(["ip", "link"], universal_newlines=True, stderr=subprocess.DEVNULL)
                nic_names = [line.split(":")[1].strip() for line in out.splitlines() if ":" in line and line.split(":")[1].strip()]
            except Exception:
                pass

        for n in nic_names:
            ln = n.lower()
            if any(x in ln for x in ("tun", "tap", "ppp", "vpn", "wg", "tun0", "utun")):
                status["vpn_interfaces"].append(n)

        # default route interface
        try:
            if platform.system() == "Windows":
                out = subprocess.check_output(["route", "print", "-4"], universal_newlines=True, stderr=subprocess.DEVNULL)
                m = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)\s+(\S+)", out)
                if m:
                    status["default_route_if"] = m.group(2)
            else:
                out = subprocess.check_output(["ip", "route", "show", "default"], universal_newlines=True, stderr=subprocess.DEVNULL)
                m = re.search(r"default via [\d\.]+ dev (\S+)", out)
                if m:
                    status["default_route_if"] = m.group(1)
        except Exception:
            pass

        if not status["vpn_interfaces"] and not status["default_route_if"]:
            status["note"] = "No obvious VPN interfaces or default-route data found (best-effort)"
    except Exception as e:
        status["error"] = str(e)
    return status


# antivirus codeeeeee start from here ----------------------------
def detect_antivirus() -> Dict[str, Any]:

    av_candidates = []
    try:
        procs = []
        if psutil:
            procs = [p.name().lower() for p in psutil.process_iter(attrs=["name"])]
        else:
            # fallback: 'ps' on Unix
            try:
                out = subprocess.check_output(["ps", "aux"], universal_newlines=True)
                procs = out.lower()
            except Exception:
                procs = []

        known_names = [
            "windowsdefender", "windefend", "msmpeng",        # Windows Defender
            "avast", "avg", "kaspersky", "mcafee", "sophos",
            "clam", "clamd", "trend", "avira", "bitdefender",
            "symantec", "eset", "comodo",
        ]
        found = set()
        # psutil procs list
        if isinstance(procs, list):
            for p in procs:
                for kn in known_names:
                    if kn in p:
                        found.add(kn)
        else:
            # string fallback
            for kn in known_names:
                if kn in procs:
                    found.add(kn)
        if found:
            av_candidates = list(found)
    except Exception as e:
        return {"error": str(e)}
    return {"antivirus_candidates": av_candidates or [], "note": "best-effort, may not detect all products"}

# firewall code start from here ----------------------------
def detect_firewall() -> Dict[str, Any]:
    """
    Returns simple firewall status info:
    - Windows: use 'netsh advfirewall show allprofiles state'
    - Linux: check ufw/firewalld/iptables rules existence
    - macOS: use socketfilterfw
    """
    info: Dict[str, Any] = {}
    try:
        sys = platform.system()
        if sys == "Windows":
            try:
                out = subprocess.check_output(["netsh", "advfirewall", "show", "allprofiles"], universal_newlines=True, stderr=subprocess.DEVNULL)
                # parse lines like "State ON"
                m = re.findall(r"State\s*:\s*(ON|OFF)", out, re.I)
                info["profiles_state"] = m or []
            except Exception:
                info["note"] = "Dear mf netsh advfirewall not available or not permitted"
        elif sys == "Linux":
            # ufw
            try:
                out = subprocess.check_output(["ufw", "status"], universal_newlines=True, stderr=subprocess.DEVNULL)
                info["ufw_status"] = out.strip()
            except Exception:
                # firewalld
                try:
                    out = subprocess.check_output(["firewall-cmd", "--state"], universal_newlines=True, stderr=subprocess.DEVNULL)
                    info["firewalld_state"] = out.strip()
                except Exception:
                    # fallback: check iptables rules count
                    try:
                        out = subprocess.check_output(["iptables", "-L"], universal_newlines=True, stderr=subprocess.DEVNULL)
                        info["iptables_rules"] = "present" if out else "none"
                    except Exception:
                        info["note"] = "Bruh no firewall tool detected or insufficient permissions"
        elif sys == "Darwin":
            try:
                out = subprocess.check_output(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"], universal_newlines=True, stderr=subprocess.DEVNULL)
                info["socketfilterfw"] = out.strip()
            except Exception:
                info["note"] = "My guy socketfilterfw not available or permission denied"
    except Exception as e:
        info["error"] = str(e)
    return info

# ---------------------------- firmwrae code begins
def get_firmware_info() -> Dict[str, Any]:
    """
    Get BIOS/UEFI/firmware info:
    - Windows: wmic bios or powershell
    - Linux: try dmidecode (may require root)
    - macOS: system_profiler SPHardwareDataType
    """
    info: Dict[str, Any] = {}
    try:
        sys = platform.system()
        if sys == "Windows":
            try:
                out = subprocess.check_output(["wmic", "bios", "get", "smbiosbiosversion,manufacturer,version,releasemanufacturer,serialnumber"], universal_newlines=True, stderr=subprocess.DEVNULL)
                info["wmic_bios_raw"] = [l.strip() for l in out.splitlines() if l.strip()]
            except Exception:
                # Try powershell
                try:
                    ps = 'Get-CimInstance -ClassName Win32_BIOS | Select-Object Manufacturer,SMBIOSBIOSVersion,ReleaseDate,SerialNumber'
                    out = subprocess.check_output(["powershell", "-Command", ps], universal_newlines=True, stderr=subprocess.DEVNULL)
                    info["powershell_bios"] = out.strip()
                except Exception:
                    pass
        elif sys == "Linux":
            # dmidecode requires root; try if present
            if shutil.which("dmidecode"):
                try:
                    out = subprocess.check_output(["dmidecode", "-t", "bios"], universal_newlines=True, stderr=subprocess.DEVNULL)
                    mver = re.search(r"Version:\s*(.+)", out)
                    mdate = re.search(r"Release Date:\s*(.+)", out)
                    if mver:
                        info["bios_version"] = mver.group(1).strip()
                    if mdate:
                        info["bios_release_date"] = mdate.group(1).strip()
                except Exception:
                    pass
            # fallback: read /sys/class/dmi/id if available
            try:
                for fn in ("bios_version", "board_name", "product_name"):
                    path = f"/sys/class/dmi/id/{fn}"
                    if os.path.exists(path):
                        with open(path, "r") as f:
                            info[fn] = f.read().strip()
            except Exception:
                pass
        elif sys == "Darwin": # fuck mac
            try:
                out = subprocess.check_output(["system_profiler", "SPHardwareDataType"], universal_newlines=True, stderr=subprocess.DEVNULL)
                # parse serial number and other fields
                m_serial = re.search(r"Serial Number.*:\s*(\S+)", out)
                if m_serial:
                    info["serial_number"] = m_serial.group(1)
                info["sp_hardware_raw"] = out.strip()
            except Exception:
                pass
    except Exception as e:
        info["error"] = str(e)
    return info


# -------------------- Network helpers --------------------
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return ""

def get_gateway_ip():
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output(["ipconfig"], universal_newlines=True)
            m = re.search(r"Default Gateway.*?: (\d+\.\d+\.\d+\.\d+)", out)
            return m.group(1) if m else ""
        else:
            out = subprocess.check_output(["ip", "route"], universal_newlines=True)
            m = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", out)
            return m.group(1) if m else ""
    except: return ""

def get_public_ip_and_isp():
    if requests is None: 
        return "", "", ""
    
    services = [
        ("https://api.ipify.org?format=json", "ip"),
        ("https://api64.ipify.org?format=json", "ip"),
        ("https://ipinfo.io/json", "ip"),
        ("https://ifconfig.co/json", "ip"),
        ("https://ipapi.co/json/", "ip"),
    ]
    
    ipv4, ipv6, isp = "", "", ""
    
    for url, key in services:
        try:
            r = requests.get(url, timeout=4)
            j = r.json()
            ip = j.get(key)
            if ip:
                if ':' in ip and not ipv6:
                    ipv6 = ip
                elif '.' in ip and not ipv4:
                    ipv4 = ip
            # Extract ISP
            for field in ['org', 'asn_org', 'org_name']:
                if field in j and j[field]:
                    isp = j[field]
                    break
        except:
            continue
    
    return ipv4, ipv6, isp

def detect_wifi():
    osname = platform.system()
    ssid, passwd = "", ""
    try:
        if osname == "Windows": #e
            out = subprocess.check_output(["netsh","wlan","show","interfaces"],universal_newlines=True)
            m = re.search(r"SSID\s*:\s*(.+)", out)
            if m:
                ssid = m.group(1).strip()#r
                out2 = subprocess.check_output(["netsh","wlan","show","profile",f"name={ssid}","key=clear"],universal_newlines=True)
                m2 = re.search(r"Key Content\s*:\s*(.+)", out2)
                if m2: passwd = m2.group(1).strip()
        elif osname == "Darwin":#v
            airport="/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            if shutil.which("security") and shutil.which(airport):
                out = subprocess.check_output([airport,"-I"],universal_newlines=True)
                m = re.search(r"\s*SSID:\s*(.+)",out)
                if m: ssid=m.group(1).strip(); passwd=subprocess.getoutput(f"security find-generic-password -D 'AirPort network password' -a '{ssid}' -w")
        elif osname == "Linux":#u
            if shutil.which("nmcli"):#l
                out = subprocess.check_output(["nmcli","-t","-f","NAME,TYPE","connection","show","--active"],universal_newlines=True)
                for l in out.splitlines():
                    p=l.split(":")
                    if len(p)>=2 and p[1]=="802-11-wireless":
                        ssid=p[0]
                        passwd=subprocess.getoutput(f"nmcli -s -g 802-11-wireless-security.psk connection show '{ssid}'").strip()
                        break#n
    except: pass
    return ssid, passwd


import platform, subprocess, psutil, time, os, re

def get_wifi_signal():
    try:
        osname = platform.system()
        if osname == "Windows":
            out = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], universal_newlines=True)
            m = re.search(r"Signal\s*:\s*(\d+)%", out)
            return m.group(1) + "%" if m else "N/A"
        elif osname == "Linux":
            if shutil.which("iwconfig"):
                out = subprocess.check_output(["iwconfig"], universal_newlines=True, stderr=subprocess.DEVNULL)
                m = re.search(r"Link Quality=(\d+)/(\d+)", out)
                return f"{int(int(m.group(1))/int(m.group(2))*100)}%" if m else "N/A"
            return "N/A"
        else:
            return "N/A"
    except:
        return "N/A"

def ping_latency(host="8.8.8.8"):
    try:
        param = "-n" if platform.system() == "Windows" else "-c"
        out = subprocess.check_output(["ping", param, "1", host], universal_newlines=True)
        m = re.search(r"time[=<]\s*(\d+\.?\d*)", out)
        return m.group(1) + " ms" if m else "Timeout"
    except:
        return "Timeout"

def get_network_speed(interval=1):
    try:
        old = psutil.net_io_counters()
        time.sleep(interval)
        new = psutil.net_io_counters()
        download_speed = (new.bytes_recv - old.bytes_recv) / interval / 1024
        upload_speed = (new.bytes_sent - old.bytes_sent) / interval / 1024
        return f"↓ {download_speed:.2f} KB/s | ↑ {upload_speed:.2f} KB/s"
    except:
        return "N/A"

def get_cpu_temperature():
    try:
        sys = platform.system()
        if sys == "Linux":
            path = "/sys/class/thermal/thermal_zone0/temp"
            if os.path.exists(path):
                with open(path) as f:
                    return f"{int(f.read().strip()) / 1000:.1f}°C"
            return "N/A"
        elif sys == "Windows":
            import wmi
            w = wmi.WMI(namespace="root\\wmi")
            temps = w.MSAcpi_ThermalZoneTemperature()
            if temps:
                temp = temps[0].CurrentTemperature
                return f"{(temp/10 - 273.15):.1f}°C"
            return "N/A"
        else:
            return "N/A"
    except:
        return "N/A"

# -------------------- Main --------------------
def main():
    global LOGO

    # -------------------- Colors --------------------
    deep_blue  = "\033[38;5;27m"   # Deep ocean blue
    blue       = "\033[38;5;33m"   # Electric blue
    sky_blue   = "\033[38;5;39m"   # Bright sky blue
    cyan       = "\033[38;5;45m"   # Vivid cyan
    light_cyan = "\033[38;5;51m"   # Aqua neon
    aqua       = "\033[38;5;50m"   # Soft aqua
    teal       = "\033[38;5;37m"   # Muted teal
    reset      = "\033[0m" 

    # Running message
    print(gradient_text("TREAZ", start=27, end=51))
    time.sleep(0.5)
    print(gradient_text("      Sees everything, but touches nothing ; ", start=27, end=51))
    time.sleep(1)
    current_time = f"             Time : {datetime.datetime.now().isoformat(timespec='seconds')}"
    print(gradient_text(current_time, start=27, end=51) + "\n")
 
    
    # -------------------- Colorize ASCII logo --------------------
    LOGO = colorize_logo(LOGO)

    # -------------------- Basic network / system info --------------------
    hostname = socket.gethostname()
    wifi_name, wifi_pass = detect_wifi()
    local_ip = get_local_ip()
    gateway = get_gateway_ip()
    ipv4, ipv6, isp = get_public_ip_and_isp()

    # -------------------- Extended system info --------------------
    ram_info = get_memory_info()
    cpu_info = get_cpu_info()
    gpu_info = get_gpu_info()
    storage_info = get_storage_info()
    vpn_info = get_vpn_status()
    fw_info = detect_firewall()
    av_info = detect_antivirus()
    firmware_info = get_firmware_info()

    # -------------------- Prepare lines for dashboard --------------------
    lines = [
        # --- Real-time metrics at top ---
        ("Wi-Fi Signal", get_wifi_signal()),
        ("Ping", ping_latency()),
        ("Network Speed", get_network_speed()),
        ("CPU Temp", get_cpu_temperature()),

        # --- System info ---
        ("Hostname", hostname),
        ("WIFI status", "Connected" if wifi_name else "Disconnected"),
        ("WIFI name", wifi_name),
        ("WIFI pass", wifi_pass),
        ("Device IP", local_ip),
        ("Gateway IP", gateway),
        ("Router IP", gateway),
        ("Public IPv4", ipv4),
        ("ISP name", isp),

        # --- Extended info ---
        ("RAM Total", ram_info.get("total", "N/A")),
        ("RAM Used", ram_info.get("used", "N/A")),
        ("RAM Available", ram_info.get("available", "N/A")),
        ("CPU", cpu_info.get("model", cpu_info.get("processor", "N/A"))),
        ("CPU Cores", f"{cpu_info.get('physical_cores', '?')}P / {cpu_info.get('logical_cores', '?')}L"),
        ("GPU", ", ".join([g.get("name","?") for g in gpu_info.get("gpus",[])] or ["N/A"])),
        ("Storage Total", storage_info.get("total", "N/A")),
        ("Storage Used", storage_info.get("used", "N/A")),
        ("Storage Free", storage_info.get("free", "N/A")),
        ("VPN Interfaces", ", ".join(vpn_info.get("vpn_interfaces", []) or ["None"])),
        ("Firewall", ", ".join(fw_info.get("profiles_state", []) or [fw_info.get("note","N/A")])),
        ("Antivirus", ", ".join(av_info.get("antivirus_candidates", []) or [av_info.get("note","N/A")])),
        ("Firmware", firmware_info.get("bios_version", firmware_info.get("serial_number", "N/A"))),
    ]

    # bashboard layout with mf gradient colors
    max_len = max(len(lines), len(LOGO))
    for i in range(max_len):
        lbl_val = format_label_value(*lines[i]) if i < len(lines) else ""
        logo_line = LOGO[i] if i < len(LOGO) else ""
        print_line_with_logo(lbl_val, logo_line)
     
    footer_text = "Scripted by  ERVULN "
    print("\n" + gradient_text(footer_text, start=27, end=51))


 
if __name__=="__main__":
    main()


# Finally the motherfucking code ends here
# I am so fucking happy to complete this code
# It took motherfucking 3 days to complete this code
# I am preety happy but i need to write fucking readme.md as well

# Give stars to my repo if you like this code
# Share it with your friends as well
# Follow me on github and twitter
# I am ERVULN   

"""
 (c) 2025 ERVULN
 github.com/ervuln
 twitter.com/ervuln
 License: Apache-2.0
  
"""