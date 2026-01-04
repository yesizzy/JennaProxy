import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

import asyncio
import json
import os
import psutil
import ssl
import subprocess
import sys
import win32api
import winreg
import signal
from typing import Dict, Any

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from mitmproxy import certs, http, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.tools.web.master import WebMaster
from modifications import cloudstorage, contentpages, images, matchmaking, mcp, motd, xmpp
from utils import cosmetics

debugMode = "-debug" in sys.argv
shutdownEvent = asyncio.Event()

def setProxySettings(proxyServer: str, enableProxy: int):
    try:
        regPath = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, regPath, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxyServer)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, enableProxy)
    except:
        pass

def killProcessByName(processName: str):
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            if processName.lower() in proc.info["name"].lower():
                try:
                    proc.kill()
                except:
                    pass
    except:
        pass

def onExit(signalType=None):
    setProxySettings("", 0)
    processNames = [
        "FortniteClient-Win64-Shipping_EAC_EOS.exe",
        "FortniteClient-Win64-Shipping.exe",
        "FortniteLauncher.exe",
        "EpicGamesLauncher.exe",
    ]
    for name in processNames:
        killProcessByName(name)
    if signalType is not None:
        shutdownEvent.set()
        return True

class JennaProxy:
    def __init__(self, athenaItems, commonCoreItems):
        self.athenaItems = athenaItems
        self.commonCoreItems = commonCoreItems
        self.athena = {}
        self.athenaStats = {}
        self.profileRevision = 1
        self.seasonNum = 0

    def request(self, flow: http.HTTPFlow):
        images.request(self, flow)

    def response(self, flow: http.HTTPFlow):
        cloudstorage.response(self, flow)
        contentpages.response(self, flow)
        matchmaking.response(self, flow)
        mcp.response(self, flow)
        motd.response(self, flow)
    
    def websocket_message(self, flow: http.HTTPFlow):
        xmpp.websocket_message(self, flow)

def isCertificateInstalled() -> bool:
    try:
        caCert = certs.CertStore.from_store(
            path=os.path.expanduser("~/.mitmproxy/"),
            basename="mitmproxy",
            key_size=2048,
        ).default_ca
        if not caCert:
            return False
        mitmFingerprint = caCert.fingerprint()
        for certDer, _, _ in ssl.enum_certificates("ROOT"):
            certObj = x509.load_der_x509_certificate(certDer)
            if certObj.fingerprint(hashes.SHA256()) == mitmFingerprint:
                return True
        return False
    except:
        return False

async def installCertificate():
    certPath = os.path.expanduser("~/.mitmproxy/mitmproxy-ca-cert.cer")
    attempts = 0
    while not isCertificateInstalled() and attempts < 5:
        try:
            subprocess.run(
                ["certutil.exe", "-f", "-addstore", "Root", certPath],
                check=True,
                capture_output=True,
            )
            break
        except:
            attempts += 1
            await asyncio.sleep(1)

async def runMitmproxy(proxy: JennaProxy):
    opts = options.Options(listen_host="127.0.0.1", listen_port=1942)
    master = WebMaster(opts, with_termlog=True) if debugMode else DumpMaster(opts)
    if debugMode:
        master.options.web_open_browser = True
    
    master.addons.add(proxy)
    
    setProxySettings("127.0.0.1:1942", 1)
    await master.run()

async def runProxy():
    athena, commonCore = cosmetics.fetchAthenaCosmetics()
    proxyInstance = JennaProxy(athena, commonCore)

    if hasattr(signal, "SIGINT"):
        signal.signal(signal.SIGINT, lambda s, f: shutdownEvent.set())
    if hasattr(win32api, "SetConsoleCtrlHandler"):
        win32api.SetConsoleCtrlHandler(onExit, True)

    killProcessByName("EpicGamesLauncher.exe")
    await installCertificate()
    asyncio.create_task(runMitmproxy(proxyInstance))
    os.system("start com.epicgames.launcher://apps/Fortnite?action=launch")
    await shutdownEvent.wait()
    onExit()

if __name__ == "__main__":
    try:
        asyncio.run(runProxy())
    except KeyboardInterrupt:
        pass