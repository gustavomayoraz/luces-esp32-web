# -*- coding: utf-8 -*-
"""
Subir a Apps Script - sube Codigo.gs y Pagina.html a script.google.com
y publica una version nueva SIN cambiar la URL (/exec).

Usa clasp (herramienta oficial de Google). La cuenta de Gmail se autoriza
una sola vez por el navegador (OAuth): la contrasena nunca pasa por este programa.
"""
import codecs
import hashlib
import math
import time
import traceback
import json
import os
import urllib.request
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unicodedata
import zipfile
import tkinter as tk
import webbrowser
from tkinter import filedialog, scrolledtext, ttk

# ---------- Carteles propios: siempre aparecen en el medio de la ventana del programa ----------
_PRINCIPAL = [None]   # ventana principal (la completa App)


def _dialogo(titulo, texto, botones, icono="ℹ️", parent=None, defecto=0, cancelar=None):
    """Cartel modal centrado sobre el programa. Devuelve el indice del boton tocado (o 'cancelar' si lo cierran)."""
    padre = parent or _PRINCIPAL[0]
    if padre is None:
        return cancelar
    d = tk.Toplevel(padre)
    d.title(titulo)
    d.configure(bg="#f8f9fa")
    d.resizable(False, False)
    try:
        d.transient(padre.winfo_toplevel())
    except tk.TclError:
        pass
    res = [cancelar]
    cuerpo = tk.Frame(d, bg="#f8f9fa")
    cuerpo.pack(padx=20, pady=(16, 8))
    tk.Label(cuerpo, text=icono, font=("Segoe UI Emoji", 24), bg="#f8f9fa").pack(side="left", anchor="n", padx=(0, 14))
    tk.Label(cuerpo, text=texto, font=("Segoe UI", 10), bg="#f8f9fa", fg="#2c3e50", justify="left",
             wraplength=440, anchor="w").pack(side="left")
    fb = tk.Frame(d, bg="#f8f9fa")
    fb.pack(pady=(4, 14))

    def elegir(i):
        res[0] = i
        d.destroy()
    botones_w = []
    for i, t in enumerate(botones):
        b = tk.Button(fb, text=t, width=12, command=lambda i=i: elegir(i), font=("Segoe UI", 9, "bold" if i == defecto else "normal"))
        b.pack(side="left", padx=5)
        botones_w.append(b)
    d.bind("<Return>", lambda e: elegir(defecto))
    d.bind("<Escape>", lambda e: elegir(cancelar) if cancelar is not None else None)
    d.protocol("WM_DELETE_WINDOW", lambda: elegir(cancelar))
    d.withdraw()
    d.update_idletasks()
    w, h = d.winfo_reqwidth(), d.winfo_reqheight()
    try:
        top = padre.winfo_toplevel()
        px, py, pw, ph = top.winfo_rootx(), top.winfo_rooty(), top.winfo_width(), top.winfo_height()
    except tk.TclError:
        px, py, pw, ph = 0, 0, d.winfo_screenwidth(), d.winfo_screenheight()
    x = max(0, min(px + (pw - w) // 2, d.winfo_screenwidth() - w))
    y = max(0, min(py + (ph - h) // 2, d.winfo_screenheight() - h))
    d.geometry(f"+{x}+{y}")
    d.deiconify()
    d.lift()
    d.grab_set()
    botones_w[defecto].focus_set()
    d.wait_window()
    return res[0]


# ---------- Icono del programa (embebido, se usa en las ventanas y en la barra de tareas) ----------
_ICONO_B64 = """
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
"""


def poner_icono(ventana):
    """Pone el icono en la ventana y en todas las que se abran desde ella. Si algo falla, sigue sin icono."""
    try:
        import base64, zlib
        ruta = os.path.join(tempfile.gettempdir(), "subir_apps_script_icono.ico")
        if not os.path.isfile(ruta):
            with open(ruta, "wb") as f:
                f.write(zlib.decompress(base64.b64decode("".join(_ICONO_B64.split()))))
        ventana.iconbitmap(default=ruta)
    except Exception:
        pass


try:
    if os.name == "nt":      # para que la barra de tareas muestre el icono propio y no el de Python
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Gustavo.SubirAppsScript")
except Exception:
    pass


class _Cuadros:
    """Mismo uso que tkinter.messagebox, pero los carteles salen centrados sobre el programa."""
    @staticmethod
    def showinfo(titulo, texto, parent=None, **kw):
        _dialogo(titulo, texto, ["Aceptar"], "ℹ️", parent, cancelar=0)
        return "ok"

    @staticmethod
    def showwarning(titulo, texto, parent=None, **kw):
        _dialogo(titulo, texto, ["Aceptar"], "⚠️", parent, cancelar=0)
        return "ok"

    @staticmethod
    def showerror(titulo, texto, parent=None, **kw):
        _dialogo(titulo, texto, ["Aceptar"], "❌", parent, cancelar=0)
        return "ok"

    @staticmethod
    def askyesno(titulo, texto, parent=None, **kw):
        return _dialogo(titulo, texto, ["Sí", "No"], "❓", parent, cancelar=1) == 0

    @staticmethod
    def askyesnocancel(titulo, texto, parent=None, **kw):
        r = _dialogo(titulo, texto, ["Sí", "No", "Cancelar"], "❓", parent, cancelar=2)
        return True if r == 0 else False if r == 1 else None

    @staticmethod
    def askretrycancel(titulo, texto, parent=None, **kw):
        return _dialogo(titulo, texto, ["Reintentar", "Cancelar"], "⚠️", parent, cancelar=1) == 0


messagebox = _Cuadros()

CREAR_SIN_VENTANA = 0x08000000 if os.name == "nt" else 0
ARCHIVOS = ["Codigo.gs", "Pagina.html"]
ARCHIVO_INO = "luces_esp32_google_lcd.ino"
FQBN = "esp32:esp32:esp32"       # ESP32 Dev Module
URL_ESP32 = "https://espressif.github.io/arduino-esp32/package_esp32_index.json"
URL_CLI = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip"
LIBRERIAS = ["LiquidCrystal I2C"]
NUCLEO_PROBADO = "3.3.12"       # version del soporte ESP32 con la que se probo el sketch

if getattr(sys, "frozen", False):
    # Como .exe: todo (configuración, dependencias, proyectos y registro) va dentro de UNA carpeta «Luces_ESP32»
    # junto al .exe, así no quedan archivos sueltos en el escritorio ni donde lo pongas.
    _dir_exe = os.path.dirname(os.path.abspath(sys.executable))
    DIR_APP = _dir_exe if os.path.basename(_dir_exe).lower() == "luces_esp32" else os.path.join(_dir_exe, "Luces_ESP32")
    try:
        os.makedirs(DIR_APP, exist_ok=True)
    except OSError:
        DIR_APP = _dir_exe
else:
    DIR_APP = os.path.dirname(os.path.abspath(sys.argv[0]))
RUTA_CONFIG = os.path.join(DIR_APP, "config_subir_script.json")

# Posición física de los pines, vista desde arriba con el USB ABAJO (de arriba hacia abajo).
# Número = GPIO configurable; texto = pin fijo / alimentación / no utilizable.
LCD_SDA, LCD_SCL = 21, 22
PLACAS = {
    "ESP32 de 30 pines": (
        ["EN", 36, 39, 34, 35, 32, 33, 25, 26, 27, 14, "GPIO12 · arranque, no usar", 13, "GND", "VIN"],
        [23, "GPIO22 · LCD SCL", "TX0 · GPIO1", "RX0 · GPIO3", "GPIO21 · LCD SDA", 19, 18, 5, 17, 16, 4, 2, 15, "GND", "3V3"]),
    "ESP32 de 38 pines": (
        ["3V3", "EN", 36, 39, 34, 35, 32, 33, 25, 26, 27, 14, "GPIO12 · arranque, no usar", "GND", 13,
         "GPIO9 · flash", "GPIO10 · flash", "GPIO11 · flash", "5V"],
        ["GND", 23, "GPIO22 · LCD SCL", "TX0 · GPIO1", "RX0 · GPIO3", "GPIO21 · LCD SDA", "GND", 19, 18, 5, 17, 16, 4,
         "GPIO0 · botón BOOT", 2, 15, "GPIO8 · flash", "GPIO7 · flash", "GPIO6 · flash"]),
}
PLACAS["ESP32-S3 DevKitC-1 (44 pines)"] = (
    ["3V3", "3V3", "RST", 4, 5, 6, 7, 15, 16, 17, 18, "GPIO8 · LCD SDA", "GPIO3 · arranque", "GPIO46 · arranque",
     "GPIO9 · LCD SCL", 10, 11, 12, 13, 14, "5V", "GND"],
    ["GND", "TX0 · GPIO43", "RX0 · GPIO44", 1, 2, 42, 41, 40, 39, "GPIO38 · LED RGB (v1.1)", "GPIO37 · PSRAM",
     "GPIO36 · PSRAM", "GPIO35 · PSRAM", "GPIO0 · botón BOOT", "GPIO45 · arranque", "GPIO48 · LED RGB (v1.0)", 47, 21,
     "GPIO20 · USB", "GPIO19 · USB", "GND", "GND"])
PLACAS["ESP32-C3 SuperMini (16 pines)"] = (        # dibujada con el USB abajo (en la placa real el USB-C está arriba)
    [0, 1, "GPIO2 · arranque", 3, "GPIO4 · LCD SDA", "3V3", "GND", "5V"],
    [21, 20, 10, "GPIO9 · botón BOOT", "GPIO8 · LED azul / arranque", 7, 6, "GPIO5 · LCD SCL"])
PLACAS["ESP32-C6 DevKitC-1 (32 pines)"] = (
    ["3V3", "RST", "GPIO4 · arranque", "GPIO5 · arranque", "GPIO6 · LCD SDA", "GPIO7 · LCD SCL", 0, 1,
     "GPIO8 · LED RGB / arranque", 10, 11, 2, 3, "5V", "GND", "NC"],
    ["GND", "TX0 · GPIO16", "RX0 · GPIO17", "GPIO15 · arranque", 23, 22, 21, 20, 19, 18, "GPIO9 · botón BOOT", "GND",
     "GPIO13 · USB", "GPIO12 · USB", "GND", "NC"])
PLACA_DEFECTO = "ESP32 de 30 pines"

# Datos de cada placa (solo chips con WiFi: ESP32, S3, C3, C6). pines = GPIO que se pueden configurar; analog = pines ADC1
# (los únicos que andan bien con el WiFi prendido); usb = cómo se mira el dibujo; los def_* son la configuración inicial.
_NOTAS_CLASICO = {2: "LED azul de la placa", 15: "cuidado al arrancar", 34: "solo entrada", 35: "solo entrada",
                  36: "SUP/VP solo entrada", 39: "SUN/VN solo entrada"}
_CLASICO = dict(chip="ESP32", fqbn="esp32:esp32:esp32", sda=21, scl=22, boot=0, led=2,
                pines=[16, 17, 18, 19, 23, 25, 26, 27, 2, 4, 5, 13, 14, 32, 33, 34, 35, 36, 39, 15],
                solo={34, 35, 36, 39}, analog=[32, 33, 34, 35, 36, 39], notas=_NOTAS_CLASICO,
                def_sal=(16, 17, 18, 19, 23, 25, 26, 27), def_ent=(4, 5, 13, 14, 32, 33, 34, 35), def_bot=15,
                usb="con el USB abajo",
                fijos="GPIO0 = botón BOOT de la placa (siempre funciona como botón) · GPIO21 y 22 = pantalla LCD",
                aviso="")
BOARDS = {
    "ESP32 de 30 pines": dict(_CLASICO),
    "ESP32 de 38 pines": dict(_CLASICO),
    "ESP32-S3 DevKitC-1 (44 pines)": dict(
        chip="ESP32-S3", fqbn="esp32:esp32:esp32s3:CDCOnBoot=cdc", sda=8, scl=9, boot=0, led=None,
        pines=[1, 2, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21, 39, 40, 41, 42, 47],
        solo=set(), analog=[1, 2, 4, 5, 6, 7, 10], notas={},
        def_sal=(15, 16, 17, 18, 39, 40, 41, 42), def_ent=(10, 11, 12, 13, 14, 47), def_bot=21,
        usb="con los USB abajo",
        fijos="GPIO0 = botón BOOT · GPIO8 y 9 = pantalla LCD · GPIO19 y 20 = USB · GPIO35 a 37 = PSRAM · GPIO38 y 48 = LED RGB",
        aviso="Para grabar por cable usá el puerto USB marcado «USB» (o «COM»). Si no entra en modo grabación, mantené pulsado BOOT y apretá RST."),
    "ESP32-C3 SuperMini (16 pines)": dict(
        chip="ESP32-C3", fqbn="esp32:esp32:esp32c3:CDCOnBoot=cdc", sda=4, scl=5, boot=9, led=None,
        pines=[0, 1, 3, 6, 7, 10, 20, 21],
        solo=set(), analog=[0, 1, 3], notas={},
        def_sal=(6, 7, 10), def_ent=(20, 21), def_bot=None,
        usb="con el USB abajo",
        fijos="GPIO9 = botón BOOT · GPIO4 y 5 = pantalla LCD · GPIO8 = LED azul (lógica invertida, no se usa) · GPIO2 y 8 = arranque",
        aviso="Placa pequeña: quedan pocos pines libres. Confirmá la posición con lo impreso en tu placa. "
              "Si no entra en modo grabación, mantené pulsado BOOT y conectá el USB."),
    "ESP32-C6 DevKitC-1 (32 pines)": dict(
        chip="ESP32-C6", fqbn="esp32:esp32:esp32c6:CDCOnBoot=cdc", sda=6, scl=7, boot=9, led=None,
        pines=[0, 1, 2, 3, 10, 11, 18, 19, 20, 21, 22, 23],
        solo=set(), analog=[0, 1, 2, 3], notas={},
        def_sal=(18, 19, 20, 21, 22, 23), def_ent=(10, 11), def_bot=None,
        usb="con los USB abajo",
        fijos="GPIO9 = botón BOOT · GPIO6 y 7 = pantalla LCD · GPIO12 y 13 = USB · GPIO8 = LED RGB · GPIO4, 5, 8, 9 y 15 = arranque",
        aviso="Para grabar por cable usá el puerto marcado «USB». Si no entra en modo grabación, mantené pulsado BOOT y apretá RST."),
}
_PERFIL_S2 = dict(
    chip="ESP32-S2", fqbn="esp32:esp32:esp32s2", sda=8, scl=9, boot=0, led=None,
    pines=[1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21, 38, 39, 40, 41, 42],
    solo=set(), analog=[1, 2, 3, 4, 5, 6, 7, 10], notas={},
    def_sal=(11, 12, 13, 14, 15, 16, 17, 18), def_ent=(21, 38, 39, 40, 41, 42), def_bot=None,
    usb="", fijos="GPIO0 = botón BOOT · GPIO8 y 9 = pantalla LCD · GPIO19 y 20 = USB · GPIO26 a 37 = memoria flash/PSRAM · GPIO43 y 44 = UART0 · GPIO45 y 46 = arranque",
    aviso="")
# Datos por tipo de chip (solo los que tienen WiFi) para las placas genéricas que lista el Arduino IDE
PERFILES_CHIP = {"esp32": BOARDS["ESP32 de 30 pines"], "esp32s2": _PERFIL_S2,
                 "esp32s3": BOARDS["ESP32-S3 DevKitC-1 (44 pines)"], "esp32c3": BOARDS["ESP32-C3 SuperMini (16 pines)"],
                 "esp32c6": BOARDS["ESP32-C6 DevKitC-1 (32 pines)"]}
CHIP_USB_NATIVO = {"esp32s2", "esp32s3", "esp32c3", "esp32c6"}


def archivo_boards_txt():
    base = os.path.join(DEPS_ARDUINO, "data", "packages", "esp32", "hardware", "esp32")
    try:
        for v in sorted(os.listdir(base), reverse=True):
            p = os.path.join(base, v, "boards.txt")
            if os.path.isfile(p):
                return p
    except OSError:
        pass
    return None


def leer_placas_core():
    """Lista de placas del soporte ESP32 instalado (las mismas del Arduino IDE) que tienen WiFi:
    [{'id', 'nombre', 'mcu', 'fqbn'}]. Sin internet: lee boards.txt de Dependencias_Ofline."""
    ruta = archivo_boards_txt()
    if not ruta:
        return []
    nombres, mcus, cdc = {}, {}, set()
    try:
        with open(ruta, "r", encoding="utf-8", errors="replace") as f:
            for linea in f:
                m = re.match(r"^([A-Za-z0-9_\-]+)\.(name|build\.mcu)=(.*)$", linea.strip())
                if m:
                    (nombres if m.group(2) == "name" else mcus)[m.group(1)] = m.group(3).strip()
                elif ".menu.CDCOnBoot.cdc=" in linea:
                    cdc.add(linea.split(".menu.", 1)[0].strip())
    except OSError:
        return []
    out = []
    for i, nombre in nombres.items():
        mcu = mcus.get(i, "")
        if mcu not in PERFILES_CHIP:
            continue
        fqbn = f"esp32:esp32:{i}" + (":CDCOnBoot=cdc" if (mcu in CHIP_USB_NATIVO and i in cdc) else "")
        out.append({"id": i, "nombre": nombre, "mcu": mcu, "fqbn": fqbn})
    out.sort(key=lambda x: x["nombre"].lower())
    return out


# Dibujos físicos conocidos de cada chip (USB siempre abajo). Para el resto: «Ordenado por GPIO».
FORMATO_GPIO = "Ordenado por GPIO (sin dibujo real)"
LAYOUTS = {
    "esp32": {"ESP32 de 30 pines": PLACAS["ESP32 de 30 pines"], "ESP32 de 38 pines": PLACAS["ESP32 de 38 pines"]},
    "esp32s3": {"DevKitC-1 (44 pines)": PLACAS["ESP32-S3 DevKitC-1 (44 pines)"]},
    "esp32c3": {"SuperMini (16 pines)": PLACAS["ESP32-C3 SuperMini (16 pines)"],
                "DevKitM-1 (30 pines)": (
                    ["GND", "3V3", "3V3", "GPIO2 · arranque", 3, "GND", "RST", "GND", 0, 1, 10, "GND", "5V", "5V", "GND"],
                    ["GND", 21, 20, "GND", "GPIO9 · botón BOOT", "GPIO8 · LED RGB / arranque", "GND", 7, 6,
                     "GPIO5 · LCD SCL", "GPIO4 · LCD SDA", "GND", "GPIO18 · USB", "GPIO19 · USB", "GND"])},
    "esp32c6": {"DevKitC-1 (32 pines)": PLACAS["ESP32-C6 DevKitC-1 (32 pines)"]},
}


def formatos_de(mcu):
    return list(LAYOUTS.get(mcu, {}).keys()) + [FORMATO_GPIO]


def registrar_placa(nombre, fqbn, mcu, formato=None):
    """Agrega a la lista una placa genérica del Arduino IDE usando los datos de su chip y el dibujo físico elegido."""
    perfil = PERFILES_CHIP.get(mcu)
    if not perfil:
        return False
    b = dict(perfil)
    b["fqbn"] = fqbn
    b["generica"] = True
    b["mcu"] = mcu
    disp = LAYOUTS.get(mcu, {})
    if formato not in disp and formato != FORMATO_GPIO:
        formato = next(iter(disp), FORMATO_GPIO)
    b["formato"] = formato
    b["aviso"] = (f"Placa genérica del Arduino IDE ({perfil['chip']}): se usan los pines típicos de ese chip. "
                  "Elegí en «Formato» el dibujo que más se parezca a tu placa y revisá que el pin exista y esté libre.")
    permitidos = list(perfil["pines"])
    if mcu == "esp32" and re.search(r"wrover|pico-?d4|pico-?v3|pico-?32", nombre, re.I):
        permitidos = [p for p in permitidos if p not in (16, 17)]       # memoria PSRAM / flash interna
        b["fijos"] = b["fijos"] + " · GPIO16 y 17 = memoria interna de este módulo"
    if formato == FORMATO_GPIO:
        b["usb"] = "ordenados por número de GPIO (la posición física depende de tu placa)"
        b["lados"] = ("GPIO (parte 1)", "GPIO (parte 2)")
        b["sin_dibujo"] = True
        pines = sorted(permitidos)
        mitad = (len(pines) + 1) // 2
        lay = (pines[:mitad], pines[mitad:])
    else:
        b["usb"] = "con el USB abajo"
        izq, der = disp[formato]
        # solo se puede configurar un número si ese pin sirve en este chip y módulo; el resto se muestra como fijo
        conv = lambda lista: [x if (not isinstance(x, int) or x in permitidos) else f"GPIO{x} · no disponible" for x in lista]
        lay = (conv(izq), conv(der))
        pines = [x for x in lay[0] + lay[1] if isinstance(x, int)]
    b["pines"] = [p for p in permitidos if p in pines]
    PLACAS[nombre] = lay
    BOARDS[nombre] = b
    return True

NOMBRES_RAPIDOS_R = [""] + [f"R{i}" for i in range(1, 17)]
NOMBRES_RAPIDOS_E = [""] + [f"E{i}" for i in range(1, 17)]

CONFIG_DEFECTO = {
    "placas_extra": {},
    "carpeta": r"C:\Users\Gustavo\Desktop\Todo lo Mio\Proyectos Python 2026\luces_esp32_google_lcd",
    "script_id": "",
    "deployment_id": "",
    "clave": "",
    "wifi_ssid": "",
    "wifi_pass": "",
    "ap_ssid": "luces1",
    "ap_pass": "",
    "rele_bajo": "ALTO",
    "puerto": "",
    "nombre_script": "",
    "pines": None,
    "perfiles": {},
    "sensores": [],
    "reglas": [],
    "codigo_extra": {},
    "librerias_extra": [],
    "librerias_zip": [],
    "hechos": {},
    "cuenta": "",
    "placa": "ESP32 de 30 pines",
}


def cstr(v):
    """Texto seguro para ponerlo entre comillas en C++ / JavaScript."""
    return v.replace("\\", "\\\\").replace('"', '\\"')


def reemplazar_const(texto, patron, valor):
    """Cambia el valor entre comillas de una linea 'patron "valor"'. Devuelve (texto, cantidad)."""
    rx = re.compile(r'(' + patron + r'\s*=\s*)"(?:[^"\\]|\\.)*"')
    return rx.subn(lambda m: m.group(1) + '"' + cstr(valor) + '"', texto)

MANIFIESTO = {
    "timeZone": "America/Argentina/Buenos_Aires",
    "exceptionLogging": "STACKDRIVER",
    "runtimeVersion": "V8",
    "webapp": {"access": "ANYONE_ANONYMOUS", "executeAs": "USER_DEPLOYING"},
}


def asegurar_path():
    """Agrega al PATH del programa las carpetas de Node y de npm (por si se instalaron recien)."""
    extra = [r"C:\Program Files\nodejs", os.path.join(os.environ.get("APPDATA", ""), "npm")]
    partes = os.environ.get("PATH", "").split(os.pathsep)
    for e in extra:
        if e and os.path.isdir(e) and e not in partes:
            os.environ["PATH"] = e + os.pathsep + os.environ["PATH"]


asegurar_path()


# ---------- Dependencias_Ofline: todo lo que se descarga se guarda junto al programa ----------
# Primera vez: el programa baja Node.js portátil, clasp, arduino-cli, el soporte ESP32 y las librerías y los deja en
# esta carpeta. Las próximas veces los busca ahí (sin internet). Se puede copiar la carpeta entera a otra PC.
DEPS = os.path.join(DIR_APP, "Dependencias_Ofline")
DEPS_NODE = os.path.join(DEPS, "node")
DEPS_CLASP = os.path.join(DEPS, "clasp")
DEPS_NPM = os.path.join(DEPS, "npm_cache")
DEPS_CLI = os.path.join(DEPS, "arduino-cli")
DEPS_ARDUINO = os.path.join(DEPS, "arduino")
AVISOS_DEPS = []                 # avisos para mostrar en el registro cuando abre el programa
_ARDUINO_ENV_LISTO = [False]


def node_en_deps():
    return os.path.isfile(os.path.join(DEPS_NODE, "node.exe"))


def clasp_en_deps():
    return os.path.isfile(os.path.join(DEPS_CLASP, "clasp.cmd"))


def cli_en_deps():
    return os.path.isfile(os.path.join(DEPS_CLI, "arduino-cli.exe"))


def _es_junction(p):
    try:
        return os.path.isjunction(p) or os.path.islink(p)
    except Exception:
        return False


def _quitar_enlace(p):
    """Borra SOLO el acceso (junction/enlace), nunca el contenido al que apunta."""
    try:
        os.rmdir(p)
    except OSError:
        subprocess.run(["cmd", "/c", "rmdir", p], capture_output=True, creationflags=CREAR_SIN_VENTANA)


def _ruta_corta(base):
    """El compilador del ESP32 falla con rutas de más de ~260 caracteres, pero arduino-cli tampoco funciona si su carpeta
    de datos (o una carpeta padre) es un acceso directo tipo junction. Por eso, si la ruta es larga, los datos REALES viven
    en una carpeta corta (por ejemplo C:\\ESP32_ab12cd) y Dependencias_Ofline\\arduino queda como acceso que apunta a ella
    (se ve y se usa igual desde el programa)."""
    if os.name != "nt" or len(base) <= 60:
        return base
    try:
        import hashlib
        h = hashlib.md5(os.path.normcase(os.path.abspath(base)).encode("utf-8")).hexdigest()[:6]
        corto = os.path.join(os.environ.get("SystemDrive", "C:") + os.sep, "ESP32_" + h)
        if _es_junction(corto):                       # esquema viejo (corto -> largo): no sirve, se invierte
            _quitar_enlace(corto)
        if not os.path.lexists(corto):
            if os.path.isdir(base) and not _es_junction(base):
                try:
                    os.rename(base, corto)            # mismo disco: instantáneo
                except OSError:
                    shutil.move(base, corto)
            else:
                os.makedirs(corto, exist_ok=True)
        for sub in ("data", "downloads", "user"):
            os.makedirs(os.path.join(corto, sub), exist_ok=True)
        if os.path.lexists(base) and _es_junction(base) and \
                os.path.normcase(os.path.realpath(base)) != os.path.normcase(os.path.realpath(corto)):
            _quitar_enlace(base)
        if not os.path.lexists(base):
            subprocess.run(["cmd", "/c", "mklink", "/J", base, corto], capture_output=True, text=True,
                           creationflags=CREAR_SIN_VENTANA)
        if os.path.isdir(os.path.join(corto, "data")):
            return corto
    except Exception as e:
        AVISOS_DEPS.append(f"⚠️ No pude preparar la carpeta corta para el ESP32: {e}")
    AVISOS_DEPS.append("⚠️ La carpeta del programa tiene una ruta muy larga y no pude crear un acceso corto: si la compilación "
                       "falla por «path too long», mové el programa a una carpeta con ruta corta (por ejemplo C:\\Luces).")
    return base


def preparar_entorno_deps():
    """Pone Dependencias_Ofline primero en el PATH y hace que arduino-cli guarde sus datos ahí."""
    try:
        os.makedirs(DEPS, exist_ok=True)
        partes = os.environ.get("PATH", "").split(os.pathsep)
        for d in (DEPS_CLASP, DEPS_NODE):          # node queda primero
            if os.path.isdir(d) and (not partes or partes[0] != d):
                os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
                partes = os.environ["PATH"].split(os.pathsep)
        if not _ARDUINO_ENV_LISTO[0]:
            for sub in ("data", "downloads", "user"):
                os.makedirs(os.path.join(DEPS_ARDUINO, sub), exist_ok=True)
            pk = os.path.join(DEPS_ARDUINO, "data", "packages")
            if os.path.islink(pk) and not os.path.exists(pk):      # enlace roto que hace fallar a arduino-cli
                try:
                    os.rmdir(pk)
                except OSError:
                    try:
                        os.unlink(pk)
                    except OSError:
                        pass
            base = _ruta_corta(DEPS_ARDUINO)
            os.environ["ARDUINO_DIRECTORIES_DATA"] = os.path.join(base, "data")
            os.environ["ARDUINO_DIRECTORIES_DOWNLOADS"] = os.path.join(base, "downloads")
            os.environ["ARDUINO_DIRECTORIES_USER"] = os.path.join(base, "user")
            _ARDUINO_ENV_LISTO[0] = True
    except OSError as e:
        AVISOS_DEPS.append(f"⚠️ No pude preparar la carpeta Dependencias_Ofline: {e}")


preparar_entorno_deps()


def descargar_node_portatil(log=None):
    """Baja Node.js LTS en versión portátil (zip) a Dependencias_Ofline\\node. Devuelve True si quedó listo."""
    if os.name != "nt":
        return False
    decir = log or (lambda t: None)
    try:
        with urllib.request.urlopen("https://nodejs.org/dist/index.json", timeout=30) as r:
            lista = json.loads(r.read().decode("utf-8"))
        ver = next(x["version"] for x in lista if x.get("lts"))
        url = f"https://nodejs.org/dist/{ver}/node-{ver}-win-x64.zip"
        zpath = os.path.join(tempfile.gettempdir(), "node-portatil.zip")
        tmp = os.path.join(tempfile.gettempdir(), "node_portatil_tmp")
        decir("Descargando " + url)
        urllib.request.urlretrieve(url, zpath)
        shutil.rmtree(tmp, ignore_errors=True)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)
        interior = next(os.path.join(tmp, n) for n in os.listdir(tmp) if os.path.isdir(os.path.join(tmp, n)))
        shutil.rmtree(DEPS_NODE, ignore_errors=True)
        os.makedirs(DEPS, exist_ok=True)
        shutil.move(interior, DEPS_NODE)
        shutil.rmtree(tmp, ignore_errors=True)
        try:
            os.remove(zpath)
        except OSError:
            pass
        preparar_entorno_deps()
        return node_en_deps()
    except Exception as e:
        decir(f"No se pudo bajar Node.js portátil: {e}")
        return False


def comando_instalar_clasp():
    """npm instala clasp dentro de Dependencias_Ofline (con su propia caché, para poder reinstalar sin internet)."""
    return (f'npm install -g @google/clasp --prefix "{DEPS_CLASP}" --cache "{DEPS_NPM}" --no-fund --no-audit')


# ---------- Pines del ESP32 ----------
# Orden de la lista = orden de las salidas / entradas en el sketch y en la pagina.
PIN_LISTA = list(_CLASICO["pines"])
SOLO_ENTRADA = set(_CLASICO["solo"])      # sin resistencia interna y no pueden ser salida
NOTAS_PIN = dict(_NOTAS_CLASICO)
LED_DEF = 2                                # pin del LED de la placa por defecto (None si la placa no tiene uno usable)
PIN_BOOT = 0
DEF_SAL, DEF_ENT, DEF_BOT = _CLASICO["def_sal"], _CLASICO["def_ent"], _CLASICO["def_bot"]


RES_ETIQ = {"PULLUP": "Pull-up", "PULLDOWN": "Pull-down", "NINGUNA": "Ninguna"}
RES_CLAVE = {v: k for k, v in RES_ETIQ.items()}


def nivel_salida(pines, pin):
    """Nivel que ACTIVA el rele de una salida: 'BAJO' o 'ALTO' (cada salida el suyo; GPIO2/LED siempre ALTO)."""
    if LED_DEF is not None and pin == LED_DEF:
        return "ALTO"
    return "BAJO" if (pines.get(str(pin)) or {}).get("alarma") == "BAJO" else "ALTO"


def resistencia_de(pines, pin):
    """Resistencia interna de una entrada: PULLUP (por defecto), PULLDOWN o NINGUNA. 34/35/36/39 no tienen."""
    if pin in SOLO_ENTRADA:
        return "NINGUNA"
    r = (pines.get(str(pin)) or {}).get("resistencia")
    return r if r in RES_ETIQ else "PULLUP"


def opciones_pin(pin):
    if pin in SOLO_ENTRADA:
        return ["—", "ENT", "SEN"]
    if LED_DEF is not None and pin == LED_DEF:
        return ["—", "SAL", "LED"]       # LED = indicador de conexion (parpadea cada 3 s)
    return ["—", "SAL", "ENT", "BOT", "SEN", "LED"]      # LED = indicador de conexión (uno solo). SEN = pin reservado para un sensor (ver «Sensores y reglas»)


def pines_defecto():
    p = {}
    for pin in PIN_LISTA:
        tipo = "LED" if (LED_DEF is not None and pin == LED_DEF) else \
               "SAL" if pin in DEF_SAL else \
               "ENT" if pin in DEF_ENT else \
               "BOT" if (DEF_BOT is not None and pin == DEF_BOT) else "—"
        p[str(pin)] = {"tipo": tipo, "nombre": "", "alarma": "ALTO", "resistencia": "PULLDOWN"}
    return p


def carpeta_de_proyecto(nombre):
    """Carpeta junto al programa con el nombre del script (como App.Path + nombre)."""
    limpio = re.sub(r'[<>:"/\\|?*]', "_", nombre).strip(" .")
    return os.path.join(DIR_APP, limpio) if limpio else ""


def texto_sensores(cfg):
    """Seccion de sensores y reglas para 'Pines ESP32.txt'."""
    try:
        lecturas = armar_sensores(cfg)
    except ValueError as ex:
        return ["", "SENSORES", "⚠ " + str(ex)]
    L = []
    if cfg.get("sensores"):
        L += ["", "SENSORES"]
        for x in cfg["sensores"]:
            L.append(f"{x.get('nombre')}= GPIO {x.get('pin')}  {TIPOS_SENSOR.get(x.get('tipo'), x.get('tipo'))}")
            L.extend("    " + ln for ln in CABLEADO.get(x.get("tipo"), "").split("\n") if ln)
    if cfg.get("reglas"):
        L += ["", "REGLAS AUTOMATICAS"]
        for r in cfg["reglas"]:
            acc = "prende" if r.get("prender", True) else "apaga"
            dur = f", vuelve sola a los {r['duracion']} s" if int(_num(r.get("duracion"))) > 0 else ", y al revés cuando deja de cumplirse"
            L.append(f"{r.get('nombre')}: si {r.get('sensor')} {'<' if r.get('op') == '<' else '>'} {r.get('umbral')} "
                     f"(margen {r.get('histeresis')}, espera {r.get('retardo')} s) → {acc} {r.get('salida')}{dur}")
    return L


def texto_pines(pines, nivel_rele, placa="", cfg=None):
    """Texto de 'Pines ESP32.txt': a que GPIO va cada salida, entrada y boton."""
    salidas, entradas, botones = armar_pines(pines)[:3]
    posiciones = {}
    if placa in PLACAS and not BOARDS.get(placa, {}).get("sin_dibujo"):
        for lado, lista in zip(("izquierdo", "derecho"), PLACAS[placa]):
            for fila, item in enumerate(lista, start=1):
                if isinstance(item, int):
                    posiciones[item] = f"lado {lado}, fila {fila} desde arriba"

    alias = {36: "rotulado SUP/VP en algunas placas", 39: "rotulado SUN/VN en algunas placas"}

    def donde(pin):
        extra = f", {alias[pin]}" if pin in alias else ""
        return f"  [{posiciones[pin]}{extra}]" if pin in posiciones else ""
    L = ["PINES DEL ESP32 - como cablear", ""]
    if placa in PLACAS:
        _b = BOARDS.get(placa, _CLASICO)
        L += [f"Placa: {placa} ({'pines ' if _b.get('sin_dibujo') else 'vista desde arriba, '}{_b['usb']})"]
    L += [f"LCD I2C: SDA = GPIO{LCD_SDA}, SCL = GPIO{LCD_SCL}",
          "", "SALIDAS (reles)"]
    for pin, nombre, corto in salidas:
        m = re.fullmatch(r"Rele_(\d+)", nombre)
        act = "" if (LED_DEF is not None and pin == LED_DEF) else f" (se activa con nivel {nivel_salida(pines, pin)})"
        L.append(f"{('R' + m.group(1)) if m else nombre}= GPIO {pin} SAL{act}{donde(pin)}")
    if entradas:
        L += ["", "ENTRADAS (sensores)"]
        for pin, nombre, nivel in entradas:
            m = re.fullmatch(r"Entrada_(\d+)", nombre)
            res = resistencia_de(pines, pin)
            txt_res = ("sin resistencia interna: poné una externa de 10 kΩ" if pin in SOLO_ENTRADA
                       else {"PULLUP": "pull-up interno", "PULLDOWN": "pull-down interno", "NINGUNA": "sin resistencia interna"}[res])
            L.append(f"{('E' + m.group(1)) if m else nombre}= GPIO {pin} ENT (alarma con nivel {'BAJO' if nivel == 'LOW' else 'ALTO'}, {txt_res}){donde(pin)}")
    if led_estado(pines):
        L += ["", "LED DE LA PLACA", f"LED= GPIO {led_pin(pines)} (LED de la placa): indica la conexion con Google, se enciende 200 ms cada 3 segundos"]
    botones = botones if isinstance(botones, (list, tuple)) else [botones]
    botones = [b for b in botones if b not in (None, -1)]
    if botones:
        L += ["", "BOTON de cambio de red"]
        for b in botones:
            L.append(f"BOT= GPIO {b} BOT{donde(b)}")
    if cfg:
        L += texto_sensores(cfg)
    return "\r\n".join(L) + "\r\n"


def sin_tildes(txt):
    return unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("ascii")


def led_pin(pines):
    """Número de pin del LED indicador de conexión (None si no hay). Por defecto GPIO2, pero según la placa el LED
    azul está en otro pin: se puede poner el tipo LED en cualquier pin que no sea solo-entrada."""
    for k, d in sorted((pines or {}).items(), key=lambda x: int(x[0])):
        if (d or {}).get("tipo") == "LED":
            return int(k)
    return None


def led_estado(pines):
    """True si hay un pin usado como LED indicador de conexion."""
    return led_pin(pines) is not None


def armar_pines(pines):
    """Devuelve (salidas, entradas, boton). Lanza ValueError si hay algo mal."""
    salidas, entradas, botones = [], [], []
    if sum(1 for d in (pines or {}).values() if (d or {}).get("tipo") == "LED") > 1:
        raise ValueError("Solo puede haber un pin tipo LED (el indicador de conexión).")
    r = e = 0
    usados = set()
    # numeros ya elegidos a mano (R1, E3...) para que el nombre automatico no los repita
    res_r, res_e = set(), set()
    for pin in PIN_LISTA:
        d0 = pines.get(str(pin), {})
        n0 = (d0.get("nombre") or "").strip()
        m0 = re.fullmatch(r"(?:R|Rele_)(\d+)", n0, re.I) if d0.get("tipo") == "SAL" else \
            re.fullmatch(r"(?:E|Entrada_)(\d+)", n0, re.I) if d0.get("tipo") == "ENT" else None
        if m0:
            (res_r if d0.get("tipo") == "SAL" else res_e).add(int(m0.group(1)))
    for pin in PIN_LISTA:
        d = pines.get(str(pin), {})
        tipo = d.get("tipo", "—")
        nombre = (d.get("nombre") or "").strip()
        if tipo not in opciones_pin(pin):
            raise ValueError(f"GPIO {pin}: '{tipo}' no está permitido en ese pin.")
        if tipo in ("SAL", "ENT") and nombre and not re.fullmatch(r"[\w ]{1,16}", nombre):
            raise ValueError(f"GPIO {pin}: el nombre solo puede tener letras, números, espacios y _ (máximo 16).")
        if tipo == "SAL":
            if nombre:
                corto = (sin_tildes(nombre).replace(" ", "") or "S")[:3]
            elif LED_DEF is not None and pin == LED_DEF:
                nombre, corto = "LED_placa", "LED"
            else:
                r += 1
                while r in res_r:
                    r += 1
                nombre, corto = f"Rele_{r}", f"R{r}"
            if LED_DEF is not None and pin == LED_DEF and "led" not in nombre.lower():
                # GPIO2 enciende el LED azul de la placa: se avisa en el nombre (R9 -> "R9 LED")
                nombre = f"{nombre} LED"[:16]
            salidas.append((pin, nombre, corto))
        elif tipo == "ENT":
            if not nombre:
                e += 1
                while e in res_e:
                    e += 1
            entradas.append((pin, nombre or f"Entrada_{e}", "LOW" if d.get("alarma") == "BAJO" else "HIGH"))
        elif tipo == "BOT":
            botones.append(pin)
        # tipo "LED" (solo GPIO2): no es salida de la pagina, la placa lo usa como indicador de conexion
    if not salidas:
        raise ValueError("Tiene que haber al menos una salida (SAL).")
    # Orden de la web y del sketch: por numero del nombre (R1, R2... / E1, E2...); los nombres sin numero
    # (por ejemplo LED_placa) quedan al final, en el orden de los pines.
    def _orden(nombre):
        m = re.search(r"\d+", nombre)
        return (0, int(m.group())) if m else (1, 0)
    salidas.sort(key=lambda x: _orden(x[1]))
    entradas.sort(key=lambda x: _orden(x[1]))
    if len(botones) > 1:
        raise ValueError("Solo se puede usar un botón externo (BOT). El BOOT de la placa ya funciona siempre.")
    nombres = [n.lower() for _, n, *_ in salidas] + [n.lower() for _, n, _ in entradas]
    if len(set(nombres)) != len(nombres):
        raise ValueError("Hay nombres repetidos.")
    return salidas, entradas, (botones[0] if botones else -1)


def resumen_pines(pines):
    try:
        s, e, b = armar_pines(pines)
    except ValueError as ex:
        return "⚠ " + str(ex)
    return (f"{len(s)} salidas · {len(e)} entradas · botón externo: {'GPIO ' + str(b) if b >= 0 else 'ninguno'}"
            + (" · LED de conexión" if led_estado(pines) else ""))



# ---------- Sensores y reglas automaticas ----------
PINES_ANALOGICOS = [32, 33, 34, 35, 36, 39]          # ADC1: los unicos que andan con el WiFi prendido
PINES_DIGITALES = [4, 5, 13, 14, 15, 16, 17, 18, 19, 23, 25, 26, 27, 32, 33]   # entrada y salida (DS18B20, DHT)
PINES_SOLO_LEER = [4, 5, 13, 14, 15, 16, 17, 18, 19, 23, 25, 26, 27, 32, 33, 34, 35, 36, 39]   # PIR


def usar_placa(nombre):
    """Pone en marcha los datos de la placa elegida (pines válidos, I2C del LCD, código de compilación...).
    Devuelve el nombre de placa realmente usado."""
    global FQBN, LCD_SDA, LCD_SCL, PIN_LISTA, SOLO_ENTRADA, NOTAS_PIN, LED_DEF, PIN_BOOT, DEF_SAL, DEF_ENT, DEF_BOT
    global PINES_ANALOGICOS, PINES_DIGITALES, PINES_SOLO_LEER
    if nombre not in BOARDS:
        nombre = PLACA_DEFECTO
    b = BOARDS[nombre]
    FQBN = b["fqbn"]
    LCD_SDA, LCD_SCL = b["sda"], b["scl"]
    PIN_LISTA = list(b["pines"])
    SOLO_ENTRADA = set(b["solo"])
    NOTAS_PIN = dict(b["notas"])
    LED_DEF = b["led"]
    PIN_BOOT = b["boot"]
    DEF_SAL, DEF_ENT, DEF_BOT = b["def_sal"], b["def_ent"], b["def_bot"]
    libres = [p for p in PIN_LISTA if p != LED_DEF]
    PINES_ANALOGICOS = [p for p in b["analog"] if p in PIN_LISTA]
    PINES_DIGITALES = [p for p in libres if p not in SOLO_ENTRADA]
    PINES_SOLO_LEER = list(libres)
    return nombre


usar_placa(PLACA_DEFECTO)
TIPOS_SENSOR = {
    "LDR": "LDR · luz (analógico)",
    "PRES": "Presión 0–5 V (bomba de agua)",
    "ANA": "Analógico genérico (0–3,3 V)",
    "PIR": "Movimiento PIR (HC-SR501)",
    "DS18B20": "Temperatura DS18B20 (sonda)",
    "DHT22": "Temperatura y humedad DHT22",
    "DHT11": "Temperatura y humedad DHT11",
}
ETQ_A_TIPO = {v: k for k, v in TIPOS_SENSOR.items()}
LIBS_SENSOR = {"DS18B20": ["OneWire", "DallasTemperature"],
               "DHT22": ["DHT sensor library", "Adafruit Unified Sensor"],
               "DHT11": ["DHT sensor library", "Adafruit Unified Sensor"]}
CABLEADO = {
    "LDR": "Cableado: 3,3 V → LDR → pin; del mismo pin una resistencia de 10 kΩ a GND. Con un módulo LDR de 4 pines usá la salida AO.\n"
           "Más luz = valor más alto. Si en tu montaje sube al revés (típico en módulos), tildá «Invertir».",
    "PRES": "Cableado: el transductor lleva 5 V, GND y señal. ¡La señal NO puede pasar de 3,3 V al ESP32!\n"
            "Poné un divisor de tensión: señal → 10 kΩ → pin; pin → 20 kΩ → GND  (divisor = 1,5). Con 10k/10k el divisor es 2.",
    "ANA": "Cableado: la señal va al pin (máximo 3,3 V; si es más, usá un divisor y poné su factor).",
    "PIR": "Cableado: VCC → 5 V, GND → GND, OUT → pin. Da movimiento (1) o no (0). Esperá ~1 minuto al encender.",
    "DS18B20": "Cableado: rojo → 3,3 V, negro → GND, amarillo → pin y una resistencia de 4,7 kΩ entre el pin y 3,3 V.",
    "DHT22": "Cableado: VCC → 3,3 V, GND → GND, DATA → pin (los módulos de 3 patas ya traen la resistencia). Da temperatura y humedad.",
    "DHT11": "Cableado: VCC → 3,3 V, GND → GND, DATA → pin. Da temperatura y humedad (menos preciso que el DHT22).",
}
UNIDADES_PRESION = ["bar", "psi", "kPa", "MPa", "kg/cm²"]


def sensor_defecto(tipo):
    d = {"tipo": tipo, "nombre": "", "pin": 0, "invertir": False, "factor": 1.0, "v0": 0.0, "v1": 3.3,
         "u0": 0.0, "u1": 100.0, "unidad": "", "dec": 1, "amin": "", "amax": ""}
    if tipo == "LDR":
        d.update(unidad="%", dec=0, nombre="Luz")
    elif tipo == "PRES":
        d.update(factor=1.5, v0=0.5, v1=4.5, u1=12.0, unidad="bar", dec=2, nombre="Presion")
    elif tipo == "ANA":
        d.update(nombre="Analogico")
    elif tipo == "PIR":
        d.update(nombre="Movimiento", dec=0)
    elif tipo == "DS18B20":
        d.update(nombre="Temperatura", unidad="°C")
    elif tipo in ("DHT22", "DHT11"):
        d.update(nombre="Ambiente")
    return d


def _num(v, defecto=0.0):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return defecto


def pines_posibles_sensor(tipo, pines, sensores, propio=None):
    """Pines que se pueden usar para un sensor: libres en la pantalla de pines y no usados por otro sensor."""
    base = PINES_ANALOGICOS if tipo in ("LDR", "PRES", "ANA") else PINES_SOLO_LEER if tipo == "PIR" else PINES_DIGITALES
    ocupados = {int(x["pin"]) for x in sensores if x is not propio and str(x.get("pin", "")).lstrip("-").isdigit()}
    return [p for p in base if (pines.get(str(p)) or {}).get("tipo", "—") in ("—", "SEN") and p not in ocupados]


def armar_sensores(cfg):
    """Devuelve (lista de sensores para el sketch, nombres de las lecturas). Lanza ValueError si hay algo mal.
    Cada lectura es un dict con lo que va al .ino; un DHT da dos lecturas (temperatura y humedad)."""
    pines = cfg.get("pines") or {}
    lecturas, vistos, pines_usados = [], set(), {}
    for x in cfg.get("sensores") or []:
        tipo = x.get("tipo")
        if tipo not in TIPOS_SENSOR:
            raise ValueError(f"Sensor con tipo desconocido: {tipo}")
        nombre = (x.get("nombre") or "").strip()
        if not re.fullmatch(r"[\w ]{1,16}", nombre):
            raise ValueError(f"Sensor «{nombre}»: el nombre solo puede tener letras, números, espacios y _ (máximo 16).")
        try:
            pin = int(x.get("pin"))
        except (TypeError, ValueError):
            raise ValueError(f"Sensor «{nombre}»: falta elegir el pin.")
        base = PINES_ANALOGICOS if tipo in ("LDR", "PRES", "ANA") else PINES_SOLO_LEER if tipo == "PIR" else PINES_DIGITALES
        if pin not in base:
            raise ValueError(f"Sensor «{nombre}»: el GPIO {pin} no sirve para este tipo de sensor.")
        if (pines.get(str(pin)) or {}).get("tipo", "—") not in ("—", "SEN"):
            raise ValueError(f"Sensor «{nombre}»: el GPIO {pin} está usado como salida, entrada o botón en «Pines». "
                             f"Elegí otro pin para el sensor o poné ese pin en SEN.")
        if pin in pines_usados:
            raise ValueError(f"Sensor «{nombre}»: el GPIO {pin} ya lo usa «{pines_usados[pin]}».")
        pines_usados[pin] = nombre
        amin = x.get("amin", "")
        amax = x.get("amax", "")
        vmin = _num(amin, None) if str(amin).strip() != "" else None
        vmax = _num(amax, None) if str(amax).strip() != "" else None
        if vmin is not None and vmax is not None and vmin >= vmax:
            raise ValueError(f"Sensor «{nombre}»: el aviso mínimo tiene que ser menor que el máximo.")
        if tipo in ("DHT22", "DHT11"):
            for suf, t, clase, uni, dec in ((" Temp", "T", "t", "°C", 1), (" Hum", "U", "h", "%", 0)):
                lecturas.append({"nombre": nombre + suf, "unidad": uni, "tipo": t, "clase": clase, "pin": pin,
                                 "modelo": 11 if tipo == "DHT11" else 22, "factor": 1, "v0": 0, "v1": 1, "u0": 0, "u1": 1,
                                 "dec": dec, "amin": vmin if t == "T" else None, "amax": vmax if t == "T" else None})
            continue
        e = {"nombre": nombre, "pin": pin, "modelo": 0, "factor": 1, "v0": 0, "v1": 1, "u0": 0, "u1": 1,
             "dec": int(_num(x.get("dec"), 1)), "amin": vmin, "amax": vmax}
        if tipo == "PIR":
            e.update(tipo="P", clase="m", unidad="", dec=0, amin=None, amax=None)
        elif tipo == "DS18B20":
            e.update(tipo="D", clase="t", unidad="°C", dec=1)
        else:
            f, v0, v1 = _num(x.get("factor"), 1.0), _num(x.get("v0"), 0.0), _num(x.get("v1"), 3.3)
            u0, u1 = _num(x.get("u0"), 0.0), _num(x.get("u1"), 100.0)
            if f <= 0 or f > 20:
                raise ValueError(f"Sensor «{nombre}»: el divisor tiene que estar entre 0 y 20.")
            if v1 == v0:
                raise ValueError(f"Sensor «{nombre}»: las dos tensiones no pueden ser iguales.")
            if tipo == "LDR":
                u0, u1 = (100.0, 0.0) if x.get("invertir") else (0.0, 100.0)
                v0, v1, f = 0.0, 3.3, 1.0
            if v1 * f > 3.3 + 0.001 and tipo != "LDR":
                pass          # la tension del sensor puede ser mayor: lo que importa es que el pin reciba menos de 3,3 V
            e.update(tipo="A", clase="l" if tipo == "LDR" else "p" if tipo == "PRES" else "a",
                     unidad=(x.get("unidad") or "").strip()[:8], factor=f, v0=v0, v1=v1, u0=u0, u1=u1,
                     dec=max(0, min(4, e["dec"])))
        lecturas.append(e)
    nombres = [l["nombre"].lower() for l in lecturas]
    if len(set(nombres)) != len(nombres):
        raise ValueError("Hay sensores con el mismo nombre.")
    if len(lecturas) > 16:
        raise ValueError("Máximo 16 lecturas de sensores por placa.")
    return lecturas


def armar_reglas(cfg, lecturas, salidas):
    """Devuelve la lista de reglas con los indices que usa el sketch. Lanza ValueError si hay algo mal."""
    sensores = [l["nombre"] for l in lecturas]
    outs = [n for _p, n, _c in salidas]
    reglas, vistos = [], set()
    for r in cfg.get("reglas") or []:
        nombre = (r.get("nombre") or "").strip()
        if not re.fullmatch(r"[\w ]{1,16}", nombre):
            raise ValueError(f"Regla «{nombre}»: el nombre solo puede tener letras, números, espacios y _ (máximo 16).")
        if nombre.lower() in vistos:
            raise ValueError(f"Hay dos reglas con el nombre «{nombre}».")
        vistos.add(nombre.lower())
        if r.get("sensor") not in sensores:
            raise ValueError(f"Regla «{nombre}»: el sensor «{r.get('sensor')}» ya no existe.")
        if r.get("salida") not in outs:
            raise ValueError(f"Regla «{nombre}»: la salida «{r.get('salida')}» ya no existe.")
        reglas.append({"nombre": nombre, "sensor": sensores.index(r["sensor"]), "op": "<" if r.get("op") == "<" else ">",
                       "umbral": _num(r.get("umbral")), "histeresis": max(0.0, _num(r.get("histeresis"))),
                       "salida": outs.index(r["salida"]), "prender": bool(r.get("prender", True)),
                       "retardo": max(0, int(_num(r.get("retardo")))), "duracion": max(0, int(_num(r.get("duracion"))))})
    if len(reglas) > 16:
        raise ValueError("Máximo 16 reglas por placa.")
    return reglas


def libs_de_sensores(sensores):
    lib = []
    for x in sensores or []:
        for l in LIBS_SENSOR.get(x.get("tipo"), []):
            if l not in lib:
                lib.append(l)
    return lib


DEPS_ZIPS = os.path.join(DEPS, "librerias_zip")      # copia de las librerias que se instalaron desde un ZIP


def carpeta_libs():
    """Carpeta donde arduino-cli guarda las librerias (dentro de Dependencias_Ofline)."""
    return os.path.join(os.environ.get("ARDUINO_DIRECTORIES_USER") or os.path.join(os.path.expanduser("~"), "Documents", "Arduino"), "libraries")


def cabeceras_libreria(nombre):
    """Archivos .h que hay que incluir para usar una libreria instalada (los lee de la propia libreria)."""
    base = os.path.join(carpeta_libs(), nombre.replace(" ", "_"))
    if not os.path.isdir(base):
        return []
    try:
        with open(os.path.join(base, "library.properties"), encoding="utf-8", errors="replace") as f:
            for ln in f:
                if ln.lower().startswith("includes="):
                    hs = [h.strip() for h in ln.split("=", 1)[1].split(",") if h.strip().lower().endswith(".h")]
                    if hs:
                        return hs[:4]
    except OSError:
        pass
    for sub in ("src", ""):
        d = os.path.join(base, sub) if sub else base
        try:
            hs = sorted(h for h in os.listdir(d) if h.lower().endswith(".h"))
        except OSError:
            continue
        if hs:
            clave = re.sub(r"[^a-z0-9]", "", nombre.lower())
            for h in hs:
                if re.sub(r"[^a-z0-9]", "", h[:-2].lower()) == clave:
                    return [h]
            return hs[:2]
    return []


def restaurar_zips(cfg, cli, log=None):
    """Reinstala (sin internet) las librerias que vinieron de un ZIP y faltan en la carpeta de Arduino."""
    for z in cfg.get("librerias_zip") or []:
        arch = os.path.join(DEPS_ZIPS, z.get("zip", ""))
        if not os.path.isfile(arch) or os.path.isdir(os.path.join(carpeta_libs(), z.get("nombre", "?").replace(" ", "_"))):
            continue
        os.environ["ARDUINO_LIBRARY_ENABLE_UNSAFE_INSTALL"] = "true"
        try:
            subprocess.run([cli, "lib", "install", "--zip-path", arch], capture_output=True, timeout=180, creationflags=CREAR_SIN_VENTANA)
            if log:
                log(f"✅ Librería {z.get('nombre')} restaurada desde Dependencias_Ofline\\librerias_zip.")
        except Exception:
            pass


def libs_necesarias(cfg):
    """Librerias que hacen falta: las base, las de los sensores de la placa y las que agregaste a mano."""
    todas = list(LIBRERIAS)
    for l in libs_de_sensores(cfg.get("sensores")) + list(cfg.get("librerias_extra") or []):
        if l not in todas:
            todas.append(l)
    return todas


def resumen_sensores(cfg):
    n, r = len(cfg.get("sensores") or []), len(cfg.get("reglas") or [])
    if not n and not r:
        return "sin sensores"
    return f"{n} sensor{'es' if n != 1 else ''} · {r} regla{'s' if r != 1 else ''}"


def _f(v):
    """Numero para el .ino (float de C)."""
    if v is None:
        return "NAN"
    t = repr(round(float(v), 4))
    return t[:-2] if t.endswith(".0") else t


def bloques_sensores(cfg, salidas):
    """Texto de los bloques que van en el .ino: defines, datos, funciones propias e includes propios."""
    lecturas = armar_sensores(cfg)
    reglas = armar_reglas(cfg, lecturas, salidas)
    defs = []
    tipos = {x.get("tipo") for x in cfg.get("sensores") or []}
    if "DS18B20" in tipos:
        defs.append("#define USA_DS18B20")
    if tipos & {"DHT22", "DHT11"}:
        defs.append("#define USA_DHT")
    if lecturas:
        lin = [f'  {{"{cstr(l["nombre"])}", "{cstr(l["unidad"])}", \'{l["tipo"]}\', \'{l["clase"]}\', {l["pin"]}, {l["modelo"]}, '
               f'{_f(l["factor"])}, {_f(l["v0"])}, {_f(l["v1"])}, {_f(l["u0"])}, {_f(l["u1"])}, {l["dec"]}, '
               f'{_f(l["amin"])}, {_f(l["amax"])}}},' for l in lecturas]
    else:
        lin = ['  {"-", "", \'A\', \'a\', 36, 0, 1, 0, 3.3, 0, 100, 0, NAN, NAN},   // sin sensores (no se usa)']
    datos = [f"const int N_SENSORES = {len(lecturas)};", "Sensor sensores[] = {"] + lin + ["};",
             f"const int N_REGLAS = {len(reglas)};", "Regla reglas[] = {"]
    if reglas:
        for g in reglas:
            datos.append(f'  {{"{cstr(g["nombre"])}", {g["sensor"]}, \'{g["op"]}\', {_f(g["umbral"])}, {_f(g["histeresis"])}, '
                         f'{g["salida"]}, {"true" if g["prender"] else "false"}, {g["retardo"]}, {g["duracion"]}}},')
    else:
        datos.append('  {"-", 0, \'>\', 0, 0, 0, true, 0, 0},   // sin reglas (no se usa)')
    datos.append("};")
    ex = cfg.get("codigo_extra") or {}
    funcs = []
    if (ex.get("globales") or "").strip():
        funcs.append(ex["globales"].rstrip())
    funcs += ["void extraSetup() {", (ex.get("setup") or "").rstrip(), "}",
              "void extraLoop() {", (ex.get("loop") or "").rstrip(), "}"]
    return ("\n".join(defs), "\n".join(datos), "\n".join(f for f in funcs), (ex.get("includes") or "").strip())


def poner_bloque(t, marca, texto):
    """Reemplaza lo que hay entre // MARCA_INICIO y // MARCA_FIN."""
    patron = re.compile(r"(// " + marca + r"_INICIO[^\n]*\n).*?(// " + marca + r"_FIN)", re.S)
    if not patron.search(t):
        raise RuntimeError("Tu .ino es de una versión vieja (falta la marca " + marca + "). Usá el .ino versión 19.")
    return patron.sub(lambda m: m.group(1) + (texto + "\n" if texto else "") + m.group(2), t, count=1)


def sub1(texto, patron, nuevo, flags=0):
    texto, n = re.subn(patron, lambda m: nuevo(m) if callable(nuevo) else nuevo, texto, count=1, flags=flags)
    if n != 1:
        raise RuntimeError(f"No encontré en el archivo: {patron[:40]}")
    return texto


def generar_ino(t, cfg, url):
    """Aplica contraseña, WiFi, URL, AP y pines al texto del .ino."""
    salidas, entradas, boton = armar_pines(cfg["pines"])
    niveles = [nivel_salida(cfg["pines"], p) for p, _, _ in salidas if p != 2]
    activo_bajo = "true" if niveles and all(n == "BAJO" for n in niveles) else "false"
    ap_pass = cfg.get("ap_pass", "")
    if ap_pass and len(ap_pass) < 8:
        raise ValueError("La clave de la red AP debe tener al menos 8 caracteres (o dejala vacía).")
    for patron, valor in ((r"const\s+char\*\s+WIFI_SSID_INICIAL", cfg["wifi_ssid"]),
                          (r"const\s+char\*\s+WIFI_PASS_INICIAL", cfg["wifi_pass"]),
                          (r"const\s+char\*\s+URL_SCRIPT", url),
                          (r"const\s+char\*\s+CLAVE", cfg["clave"]),
                          (r"const\s+char\*\s+AP_SSID", cfg.get("ap_ssid") or "luces1"),
                          (r"const\s+char\*\s+AP_PASS", ap_pass)):
        t, n = reemplazar_const(t, patron, valor)
        if n != 1:
            raise RuntimeError("Tu .ino es de una versión vieja (falta " + patron.split("*")[-1].strip() + "). Usá el .ino versión 19.")
    t = sub1(t, r"const bool RELE_ACTIVO_EN_BAJO = (true|false);", f"const bool RELE_ACTIVO_EN_BAJO = {activo_bajo};")
    t = sub1(t, r"const bool LED_ESTADO = (true|false);", f"const bool LED_ESTADO = {'true' if led_estado(cfg['pines']) else 'false'};")
    t = sub1(t, r"const int LED_ESTADO_PIN = \d+;", f"const int LED_ESTADO_PIN = {led_pin(cfg['pines']) or 2};")
    b = BOARDS.get(cfg.get("placa"), BOARDS[PLACA_DEFECTO])
    t = sub1(t, r"const int BOTON_PIN = \d+;", f"const int BOTON_PIN = {b['boot']};")
    t = sub1(t, r"const int SDA_PIN = \d+;", f"const int SDA_PIN = {b['sda']};")
    t = sub1(t, r"const int SCL_PIN = \d+;", f"const int SCL_PIN = {b['scl']};")
    lineas = []
    for pin, nombre, corto in salidas:
        nivel = "true" if nivel_salida(cfg["pines"], pin) == "BAJO" else "false"
        lineas.append(f'  {{"{cstr(nombre)}", "{cstr(corto)}", {pin}, {nivel}}},')
    t = sub1(t, r"Luz luces\[\] = \{.*?\n\};", "Luz luces[] = {\n" + "\n".join(lineas) + "\n};", re.S)
    t = sub1(t, r"const int N_LUCES = [^;]*;", f"const int N_LUCES = {len(salidas)};")
    modo_c = {"PULLUP": "INPUT_PULLUP", "PULLDOWN": "INPUT_PULLDOWN", "NINGUNA": "INPUT"}
    lineas = [f'  {{"{cstr(n)}", {p}, {a}, {modo_c[resistencia_de(cfg["pines"], p)]}}},' for p, n, a in entradas] \
        or ['  {"-", 4, HIGH, INPUT_PULLUP},   // sin entradas (no se usa)']
    t = sub1(t, r"Entrada entradas\[\] = \{.*?\n\};", "Entrada entradas[] = {\n" + "\n".join(lineas) + "\n};", re.S)
    t = sub1(t, r"const int N_ENTRADAS = [^;]*;", f"const int N_ENTRADAS = {len(entradas)};")
    t = sub1(t, r"const int BOTON_EXT_PIN = -?\d+;", f"const int BOTON_EXT_PIN = {boton};")
    defs, datos, funcs, incl = bloques_sensores(cfg, salidas)
    t = poner_bloque(t, "SENSORES_DEFINES", defs)
    t = poner_bloque(t, "SENSORES_DATOS", datos)
    t = poner_bloque(t, "EXTRA_FUNCIONES", funcs)
    t = poner_bloque(t, "EXTRA_INCLUDES", incl)
    return t


def generar_gs(t, cfg):
    """Pone la contraseña en Codigo.gs. Los nombres de salidas y entradas ya no van aca: cada ESP32 los manda."""
    if cfg.get("clave"):
        t, n1 = reemplazar_const(t, r"const\s+CLAVE_ESP", cfg["clave"])
        t, n2 = reemplazar_const(t, r"const\s+CLAVE_WEB_INICIAL", cfg["clave"])
        if n1 != 1 or n2 != 1:
            raise RuntimeError("No encontré CLAVE_ESP / CLAVE_WEB_INICIAL en Codigo.gs")
    return t


def buscar_cli():
    """Busca arduino-cli: en el PATH, dentro del Arduino IDE 2.x o la copia que baja este programa."""
    propio = os.path.join(DEPS_CLI, "arduino-cli.exe")
    if os.path.isfile(propio):
        return propio
    c = shutil.which("arduino-cli")
    if c:
        return c
    candidatos = []
    for base in (os.environ.get("LOCALAPPDATA", ""), os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")):
        if base:
            candidatos.append(os.path.join(base, "Programs", "Arduino IDE", "resources", "app", "lib", "backend", "resources", "arduino-cli.exe"))
            candidatos.append(os.path.join(base, "Arduino IDE", "resources", "app", "lib", "backend", "resources", "arduino-cli.exe"))
    candidatos.append(os.path.join(DIR_APP, "arduino-cli", "arduino-cli.exe"))
    for c in candidatos:
        if os.path.isfile(c):
            return c
    return None


def version_nucleo(texto):
    """Version instalada de esp32:esp32 segun 'arduino-cli core list --format json' (o None)."""
    try:
        d = json.loads(texto)
    except Exception:
        return None
    lista = d.get("platforms", d) if isinstance(d, dict) else d
    for p in lista or []:
        if p.get("id") == "esp32:esp32":
            return p.get("installed_version") or p.get("installed")
    return None


def _dns_nombre(d, i):
    """Lee un nombre DNS (con compresion) y devuelve (nombre, posicion siguiente)."""
    partes, saltos, fin = [], 0, None
    while True:
        n = d[i]
        if n == 0:
            i += 1
            break
        if n & 0xC0 == 0xC0:
            if fin is None:
                fin = i + 2
            i = ((n & 0x3F) << 8) | d[i + 1]
            saltos += 1
            if saltos > 20:
                raise ValueError("bucle")
            continue
        partes.append(d[i + 1:i + 1 + n].decode("utf-8", "replace"))
        i += 1 + n
    return ".".join(partes), (fin if fin is not None else i)


def _dns_registros(d):
    """Devuelve la lista de (nombre, tipo, datos_crudos, posicion_datos) de un paquete mDNS."""
    import struct
    qd, an, ns, ar = struct.unpack(">4H", d[4:12])
    i = 12
    for _ in range(qd):
        _, i = _dns_nombre(d, i)
        i += 4
    res = []
    for _ in range(an + ns + ar):
        nombre, i = _dns_nombre(d, i)
        tipo, _cl, _ttl, ln = struct.unpack(">HHIH", d[i:i + 10])
        i += 10
        res.append((nombre, tipo, d[i:i + ln], i))
        i += ln
    return res


PATRON_VPN = re.compile(r"vpn|tap-windows|\btun\b|wintun|wireguard|nordlynx|surfshark|cyberghost|"
                        r"cloudflare warp|hamachi|radmin|zerotier|tailscale|windscribe|mullvad|\bpia\b|fortinet|anyconnect|"
                        r"pulse secure|globalprotect|sstp|l2tp|pptp|virtual private", re.I)


def adaptadores_activos():
    """Lista de adaptadores IPv4 activos [{'ip','nombre','desc','vpn'}] (solo Windows; [] si no se puede leer)."""
    if os.name != "nt":
        return []
    ps = ("Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | ForEach-Object { $a=$_; "
          "Get-NetIPAddress -InterfaceIndex $a.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | "
          "ForEach-Object { [pscustomobject]@{ip=$_.IPAddress;nombre=$a.Name;desc=$a.InterfaceDescription} } } | ConvertTo-Json -Compress")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True,
                           timeout=15, creationflags=0x08000000)
        datos = json.loads(r.stdout) if r.stdout.strip() else []
    except Exception:
        return []
    if isinstance(datos, dict):
        datos = [datos]
    for d in datos:
        d["vpn"] = bool(PATRON_VPN.search(f"{d.get('nombre', '')} {d.get('desc', '')}"))
    return datos


def vpn_activa():
    """Nombres de los adaptadores de VPN activos (lista vacia si no hay o no se pudo saber)."""
    return sorted({d["nombre"] for d in adaptadores_activos() if d["vpn"]})


def buscar_esp32_ota(segundos=3.0):
    """Busca en la red los equipos que anuncian grabacion por WiFi (servicio mDNS _arduino._tcp).
    Devuelve una lista de (nombre, ip) sin repetidos."""
    import select, socket, struct
    consulta = b"\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
    for parte in ("_arduino", "_tcp", "local"):
        consulta += bytes([len(parte)]) + parte.encode()
    consulta += b"\x00" + struct.pack(">HH", 12, 0x8001)      # PTR, con pedido de respuesta directa
    locales = set()
    try:
        for inf in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            locales.add(inf[4][0])
    except OSError:
        pass
    ips_vpn = set()
    try:
        ads = adaptadores_activos()
        ips_vpn = {d["ip"] for d in ads if d["vpn"]}
        locales |= {d["ip"] for d in ads if not d["vpn"]}      # una consulta por cada adaptador real (WiFi/cable)
    except Exception:
        pass
    locales -= ips_vpn                                          # nunca por la VPN
    if not ips_vpn:
        locales.add("0.0.0.0")                                  # sin VPN: tambien la ruta por defecto
    socks = []
    for ip in locales:
        if ip.startswith("127."):
            continue
        try:
            u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            u.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
            if ip != "0.0.0.0":
                u.bind((ip, 0))
                u.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
            u.sendto(consulta, ("224.0.0.251", 5353))
            socks.append(u)
        except OSError:
            pass
    instancias, ips, srv = set(), {}, {}
    t0 = time.time()
    reenviado = False
    while socks and time.time() - t0 < segundos:
        if not reenviado and time.time() - t0 > 1.2:
            reenviado = True
            for u in socks:
                try:
                    u.sendto(consulta, ("224.0.0.251", 5353))
                except OSError:
                    pass
        listos, _, _ = select.select(socks, [], [], 0.3)
        for u in listos:
            try:
                d, (origen, _) = u.recvfrom(2048)
                for nombre, tipo, datos, pos in _dns_registros(d):
                    if tipo == 12:                       # PTR: nombre de la instancia
                        inst, _ = _dns_nombre(d, pos)
                        if "_arduino._tcp" in inst:
                            instancias.add(inst.split("._arduino")[0])
                    elif tipo == 1 and len(datos) == 4:  # A: nombre -> IP
                        ips[nombre.lower()] = socket.inet_ntoa(datos)
                    elif tipo == 33:                     # SRV: instancia -> equipo
                        objetivo, _ = _dns_nombre(d, pos + 6)
                        srv[nombre.split("._arduino")[0]] = objetivo.lower()
                    if tipo == 1 or tipo == 12:
                        ips.setdefault("origen:" + nombre.lower(), origen)
            except Exception:
                continue
    for u in socks:
        try:
            u.close()
        except OSError:
            pass
    res = {}
    for inst in instancias:
        ip = ips.get(srv.get(inst, ""), "") or ips.get(inst.lower() + ".local", "") or ips.get("origen:" + inst.lower() + "._arduino._tcp.local", "")
        if ip:
            res[ip] = inst
    return sorted(((n, ip) for ip, n in res.items()), key=lambda x: x[0].lower())


def matar_arbol(p):
    """Mata un proceso y todos los que lanzo."""
    if not p or p.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(f"taskkill /PID {p.pid} /T /F", shell=True, capture_output=True, creationflags=CREAR_SIN_VENTANA)
        else:
            p.kill()
    except Exception:
        pass


def matar_huerfanos():
    """Cierra los procesos de compilacion/grabacion que hayan quedado de una ejecucion anterior.
    Solo toca los que usan la carpeta de este programa (luces_esp32_build): no molesta al Arduino IDE."""
    if os.name != "nt":
        return
    ps = ("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*luces_esp32_build*' -and "
          "$_.ProcessId -ne $PID } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }")
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, timeout=15,
                       creationflags=CREAR_SIN_VENTANA)
    except Exception:
        pass


def puertos_com():
    """Puertos COM presentes ahora (lee el registro de Windows: instantaneo, sin lanzar programas)."""
    try:
        import winreg
        res = []
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM") as k:
            i = 0
            while True:
                try:
                    nombre, valor, _ = winreg.EnumValue(k, i)
                except OSError:
                    break
                i += 1
                if "bth" not in nombre.lower():     # se ignoran los puertos de Bluetooth
                    res.append(str(valor))
        return sorted(set(res), key=lambda c: int(re.sub(r"\D", "", c) or 0))
    except Exception:
        return None


def parsear_puertos(texto):
    """Lee la salida JSON de 'arduino-cli board list' (formato nuevo y viejo)."""
    try:
        d = json.loads(texto)
    except Exception:
        return []
    lista = d.get("detected_ports", d) if isinstance(d, dict) else d
    out = []
    for it in lista or []:
        p = it.get("port", it)
        dire = p.get("address")
        if dire and dire not in out and not dire.lower().startswith("/dev/ttys"):
            out.append(dire)
    return out


def cargar_config():
    cfg = dict(CONFIG_DEFECTO)
    try:
        with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    for n_, d_ in list((cfg.get("placas_extra") or {}).items()):
        try:
            registrar_placa(n_, d_["fqbn"], d_["mcu"], d_.get("formato"))
        except Exception:
            cfg["placas_extra"].pop(n_, None)
    cfg["placa"] = usar_placa(cfg.get("placa"))
    base = pines_defecto()
    base.update(cfg.get("pines") or {})
    cfg["pines"] = base
    if not cfg.get("led_migrado"):
        # antes el LED azul (GPIO2) era una salida mas; ahora, por defecto, indica la conexion
        for pr in [cfg] + list((cfg.get("perfiles") or {}).values()):
            d2 = (pr.get("pines") or {}).get("2")
            if d2 and d2.get("tipo") == "SAL":
                d2["tipo"] = "LED"
        cfg["led_migrado"] = True
    return cfg


def guardar_config(cfg):
    try:
        with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


class App:
    def __init__(self):
        self.cfg = cargar_config()
        try:
            open(os.path.join(DIR_APP, "registro_programa.txt"), "w", encoding="utf-8").close()
        except Exception:
            pass
        self.cola = queue.Queue()
        self.ocupado = False
        self.proc_actual = None
        self.cancelado = False
        self.cancelado_nombre = False
        self.req_ok = False
        self.login_ok = False

        self.v = tk.Tk()
        poner_icono(self.v)
        _PRINCIPAL[0] = self.v
        self.v.title("☁️ Subir a Apps Script")
        self.v.configure(bg="#f8f9fa")
        self.v.resizable(False, False)

        BG = "#f8f9fa"
        LF = ("Segoe UI", 9, "bold")
        tk.Label(self.v, text="☁️ Subir a Apps Script", font=("Segoe UI", 14, "bold"),
                 bg=BG, fg="#2c3e50").grid(row=0, column=0, columnspan=2, pady=(6, 0))
        tk.Label(self.v, text="Hacé los pasos ① y ②; después usá ⚡ HACER TODO. Cada paso se habilita cuando el anterior terminó.",
                 font=("Segoe UI", 9), bg=BG, fg="#7f8c8d").grid(row=1, column=0, columnspan=2, pady=(0, 2))

        izq = tk.Frame(self.v, bg=BG); izq.grid(row=3, column=0, sticky="n", padx=(12, 6))
        der = tk.Frame(self.v, bg=BG); der.grid(row=3, column=1, sticky="n", padx=(6, 12))

        # ---------- COLUMNA IZQUIERDA ----------
        marco = tk.LabelFrame(izq, text="🔍 Requisitos", bg=BG, font=LF)
        marco.pack(fill="x", pady=2)
        self.lbl_node = self._fila(marco, "Node.js")
        self.lbl_clasp = self._fila(marco, "clasp")
        self.lbl_login = self._fila(marco, "Cuenta de Google")
        tk.Button(marco, text="⚙️ Activar API de Apps Script (1 vez)", command=self.abrir_api,
                  font=("Segoe UI", 8)).pack(anchor="w", padx=6, pady=(2, 3))

        datos = tk.LabelFrame(izq, text="⚙️ Datos del proyecto", bg=BG, font=LF)
        datos.pack(fill="x", pady=2)
        self.var_carpeta = tk.StringVar(value=self.cfg["carpeta"])
        self.var_script = tk.StringVar(value=self.cfg["script_id"])
        self.var_deploy = tk.StringVar(value=self.cfg["deployment_id"])
        self.var_nombre = tk.StringVar(value=self.cfg.get("nombre_script", ""))

        f = tk.Frame(datos, bg=BG); f.pack(fill="x", padx=6, pady=2)
        tk.Label(f, text="Carpeta (auto)", width=14, anchor="w", bg=BG).pack(side="left")
        tk.Entry(f, textvariable=self.var_carpeta, width=21).pack(side="left", padx=2)
        tk.Button(f, text="📂", command=self.elegir_carpeta).pack(side="left")
        f = tk.Frame(datos, bg=BG); f.pack(fill="x", padx=6, pady=2)
        tk.Label(f, text="Nombre del script", width=14, anchor="w", bg=BG).pack(side="left")
        tk.Entry(f, textvariable=self.var_nombre, width=21).pack(side="left", padx=2)
        f = tk.Frame(datos, bg=BG); f.pack(fill="x", padx=6, pady=2)
        tk.Label(f, text="ID script", width=8, anchor="w", bg=BG).pack(side="left")
        tk.Entry(f, textvariable=self.var_script, width=9).pack(side="left", padx=(2, 6))
        tk.Label(f, text="ID publicación", anchor="w", bg=BG).pack(side="left")
        tk.Entry(f, textvariable=self.var_deploy, width=9).pack(side="left", padx=2)
        fg_ = tk.Frame(datos, bg=BG); fg_.pack(fill="x", padx=6, pady=2)
        tk.Button(fg_, text="📝 Abrir en Google", command=self.abrir_en_google).pack(side="left", padx=2)
        tk.Button(fg_, text="📋 Mis scripts", command=lambda: webbrowser.open("https://script.google.com/home")).pack(side="left", padx=2)
        self.b_nuevo = tk.Button(datos, text="🆕 Crear script NUEVO con ese nombre",
                                 command=self.crear_script_nuevo, bg="#16a085", fg="white", font=("Segoe UI", 8, "bold"))
        self.b_nuevo.pack(fill="x", padx=6, pady=(2, 4))

        ef = tk.LabelFrame(izq, text="🌐 Enlace de la web (para el celular)", bg=BG, font=LF)
        ef.pack(fill="x", pady=2)
        fe = tk.Frame(ef, bg=BG); fe.pack(fill="x", padx=6, pady=3)
        self.var_url = tk.StringVar()
        tk.Entry(fe, textvariable=self.var_url, width=22, state="readonly", readonlybackground="#ffffff").pack(side="left", padx=2)
        tk.Button(fe, text="📋 Copiar", command=self.copiar_url).pack(side="left", padx=2)
        tk.Button(fe, text="🌐 Abrir", command=lambda: webbrowser.open(self.var_url.get())).pack(side="left", padx=2)
        self.var_deploy.trace_add("write", lambda *_: self.escribir_enlace(archivo=False))

        # ---------- COLUMNA DERECHA ----------
        seg = tk.LabelFrame(der, text="🔐 Contraseña de la web y WiFi del ESP32", bg=BG, font=LF)
        seg.pack(fill="x", pady=2)
        self.var_clave = tk.StringVar(value=self.cfg.get("clave", ""))
        self.var_ssid = tk.StringVar(value=self.cfg.get("wifi_ssid", ""))
        self.var_wpass = tk.StringVar(value=self.cfg.get("wifi_pass", ""))
        self.var_ver = tk.BooleanVar(value=False)
        self.ent_clave = self._campo(seg, "Contraseña web", self.var_clave, True)
        self.ent_wpass = None
        self._campo(seg, "Nombre del WiFi", self.var_ssid, False)
        self.ent_wpass = self._campo(seg, "Clave del WiFi", self.var_wpass, True)
        self.var_apssid = tk.StringVar(value=self.cfg.get("ap_ssid", "luces1"))
        self.var_appass = tk.StringVar(value=self.cfg.get("ap_pass", ""))
        self._campo(seg, "Red AP (nombre)", self.var_apssid, False)
        self.ent_appass = self._campo(seg, "Red AP (clave)", self.var_appass, True)
        tk.Checkbutton(seg, text="Mostrar contraseñas", variable=self.var_ver, bg=BG,
                       command=self._mostrar).pack(anchor="w", padx=6)
        tk.Label(seg, text="WiFi 2,4 GHz. Clave AP: mín. 8 (vacía = abierta).",
                 font=("Segoe UI", 8), bg=BG, fg="#7f8c8d").pack(anchor="w", padx=6, pady=(0, 2))

        pf = tk.LabelFrame(der, text="🔌 Pines", bg=BG, font=LF)
        pf.pack(fill="x", pady=2)
        tk.Button(pf, text="Configurar salidas, entradas y botón", command=self.abrir_pines,
                  font=("Segoe UI", 9, "bold"), bg="#16a085", fg="white").pack(anchor="w", padx=6, pady=3)
        fsb = tk.Frame(pf, bg=BG); fsb.pack(anchor="w", padx=6, pady=(0, 3))
        tk.Button(fsb, text="📡 Sensores y reglas", command=self.abrir_sensores, font=("Segoe UI", 9, "bold"),
                  bg="#2980b9", fg="white").pack(side="left")
        tk.Button(fsb, text="📚 Librerías", command=self.abrir_librerias, font=("Segoe UI", 9, "bold"),
                  bg="#8e44ad", fg="white").pack(side="left", padx=4)
        self.lbl_pines = tk.Label(pf, text="", bg=BG, fg="#2c3e50",
                                  font=("Segoe UI", 8), wraplength=280, justify="left")
        self.lbl_pines.pack(anchor="w", padx=6, pady=(0, 3))
        self._perfil_activo = None
        if self._nombre_ap() not in (self.cfg.get("perfiles") or {}):
            self._guardar_perfil()             # los pines actuales quedan guardados con el nombre de este ESP32
        self._perfil_activo = self._nombre_ap()
        self.lbl_pines.config(text=self._texto_pines())
        self.var_apssid.trace_add("write", self._al_cambiar_nombre_ap)

        ar = tk.LabelFrame(der, text="🔧 ESP32 (conectalo por USB)", bg=BG, font=LF)
        ar.pack(fill="x", pady=2)
        fa = tk.Frame(ar, bg=BG); fa.pack(fill="x", padx=6, pady=4)
        tk.Label(fa, text="Puerto", bg=BG).pack(side="left")
        self.var_puerto = tk.StringVar(value=self.cfg.get("puerto", ""))
        self.cb_puerto = ttk.Combobox(fa, textvariable=self.var_puerto, width=12)
        self.cb_puerto.pack(side="left", padx=4)
        self.b_puertos = tk.Button(fa, text="🔄 Buscar", command=self.buscar_puertos)
        self.b_puertos.pack(side="left", padx=2)
        self.lbl_puerto = tk.Label(ar, text="", bg=BG, fg="#7f8c8d", font=("Segoe UI", 9))
        self.lbl_puerto.pack(anchor="w", padx=6, pady=(0, 3))
        self._pc_prev = None
        self.var_wifi = tk.BooleanVar(value=bool(self.cfg.get("por_wifi", False)))
        self.var_host = tk.StringVar(value=self.cfg.get("ota_host", ""))
        fw = tk.Frame(ar, bg=BG); fw.pack(fill="x", padx=6, pady=(0, 4))
        tk.Checkbutton(fw, text="📶 Grabar por WiFi", variable=self.var_wifi, bg=BG,
                       command=self._al_tildar_wifi).pack(side="left")
        self.b_comprobar = tk.Button(fw, text="🔎 Buscar", command=self.comprobar_ota)
        self.b_comprobar.pack(side="left", padx=2)
        self.b_renombrar = tk.Button(fw, text="✏️ Renombrar", command=self.renombrar, bg="#f39c12", fg="white",
                                     font=("Segoe UI", 9, "bold"))
        self.b_renombrar.pack(side="left", padx=8)
        fw2 = tk.Frame(ar, bg=BG); fw2.pack(fill="x", padx=6, pady=(0, 4))
        tk.Label(fw2, text="ESP32 destino", bg=BG).pack(side="left")
        self.cb_host = ttk.Combobox(fw2, textvariable=self.var_host, width=26)
        self.cb_host.pack(side="left", padx=4)
        self.cb_host.bind("<<ComboboxSelected>>", self._al_elegir_destino)
        tk.Label(fw2, text="(lista, nombre.local o IP)", bg=BG, fg="#7f8c8d",
                 font=("Segoe UI", 8)).pack(side="left")

        # ---------- PASOS (en una fila, arriba) Y REGISTRO (abajo, a lo ancho) ----------
        pasos = tk.LabelFrame(self.v, text="▶ Pasos", bg=BG, font=LF)
        pasos.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 2))
        bf = ("Segoe UI", 9, "bold")
        ancho = 23
        self.b_instalar = tk.Button(pasos, text="①  Instalar lo que falta", command=self.instalar_clasp,
                                    font=bf, bg="#3498db", fg="white", width=ancho)
        self.b_login = tk.Button(pasos, text="②  Conectar con Google", command=self.conectar,
                                 font=bf, bg="#3498db", fg="white", width=ancho)
        self.b_todo = tk.Button(pasos, text="③  Crear los 3 archivos", command=self.crear_todo,
                                font=bf, bg="#e67e22", fg="white", width=ancho)
        self.b_subir = tk.Button(pasos, text="④  Subir y publicar", command=self.subir,
                                 font=bf, bg="#27ae60", fg="white", width=ancho)
        self.b_cargar = tk.Button(pasos, text="⑤  Preparar y cargar ESP32", command=self.cargar_esp32,
                                  font=bf, bg="#c0392b", fg="white", width=ancho)
        # Los pasos ③ ④ ⑤ sueltos quedan ocultos (los hace el botón «HACER TODO»); siguen existiendo por dentro.
        for b in (self.b_instalar, self.b_login):
            b.pack(side="left", padx=4, pady=4)
        self.b_hacer = tk.Button(pasos, text="⚡  HACER TODO", command=self.hacer_todo,
                                 font=("Segoe UI", 10, "bold"), bg="#2c3e50", fg="white", width=ancho - 6)
        self.b_hacer.pack(side="left", padx=(14, 4), pady=4)
        for _b in (self.b_instalar, self.b_login, self.b_hacer):
            _b.config(disabledforeground="#ecf0f1")      # que el texto se lea aunque el botón esté deshabilitado
        self.b_cancel = tk.Button(pasos, text="⛔  Cancelar", command=self.cancelar_tarea,
                                  font=bf, bg="#95a5a6", fg="white", width=12, state="disabled")
        self.b_cancel.pack(side="left", padx=4, pady=4)
        tk.Button(pasos, text="↺ Reactivar", command=self.reactivar_pasos,
                  font=("Segoe UI", 8)).pack(side="right", padx=6, pady=4)
        self.base_pasos = {b: (b.cget("text"), b.cget("bg")) for b in
                           (self.b_instalar, self.b_login, self.b_todo, self.b_subir, self.b_cargar)}

        fila = tk.Frame(self.v, bg=BG)
        fila.grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(2, 2))
        fila.grid_columnconfigure(0, weight=1)
        self.log = scrolledtext.ScrolledText(fila, width=60, height=8, font=("Consolas", 9),
                                             bg="#1e1e1e", fg="#dcdcdc", state="disabled")
        self.log.tag_configure("verde", foreground="#2ecc71", font=("Consolas", 9, "bold"))
        self.log.grid(row=0, column=0, sticky="ew")

        fbarra = tk.Frame(self.v, bg=self.v.cget("bg"))
        fbarra.grid(row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=2)
        self.lbl_pct = tk.Label(fbarra, text="", width=5, anchor="e", bg=self.v.cget("bg"), font=("Segoe UI", 10, "bold"), fg="#2c3e50")
        self.lbl_pct.pack(side="right")
        self.barra = ttk.Progressbar(fbarra, mode="indeterminate")
        self.barra.pack(side="left", fill="x", expand=True)
        self.prog_activo = False
        self.prog = None
        self.pct_mostrado = 0.0
        self._buf_prog = ""
        self.estado = tk.Label(self.v, text="Listo.", bg=BG, fg="#2c3e50", font=("Segoe UI", 9))
        self.estado.grid(row=6, column=0, columnspan=2, pady=(0, 6))

        def nombre_a_carpeta(*_):
            c = carpeta_de_proyecto(self.var_nombre.get())
            if c:
                self.var_carpeta.set(c)
        self.var_nombre.trace_add("write", nombre_a_carpeta)
        # La carpeta del proyecto siempre va junto al programa (como App.Path + nombre). Si la guardada
        # quedó en otro lado (por ejemplo el escritorio de cuando el programa estaba ahí), se corrige.
        actual = os.path.normcase(os.path.dirname(os.path.normpath(self.var_carpeta.get().strip() or "x")))
        if self.var_nombre.get().strip() and actual != os.path.normcase(os.path.normpath(DIR_APP)):
            nombre_a_carpeta()
        # Configuracion que ya tiene script y publicacion pero no anotó el nombre del script creado (copiada o de
        # una version anterior): se toma el nombre actual, asi «Crear script NUEVO» no queda activo sin motivo.
        h0 = self.cfg.setdefault("hechos", {})
        if (self.var_nombre.get().strip() and self.var_script.get().strip() and self.var_deploy.get().strip()
                and "nombre_creado" not in h0):
            h0["nombre_creado"] = self.var_nombre.get().strip()
        for var in (self.var_clave, self.var_ssid, self.var_wpass, self.var_apssid, self.var_appass,
                    self.var_carpeta, self.var_script, self.var_deploy, self.var_nombre):
            var.trace_add("write", lambda *_: self.refrescar_botones())
        self.refrescar_botones()

        self.v.protocol("WM_DELETE_WINDOW", self.cerrar)
        self._bombear()
        self.v.update_idletasks()
        self._centrar_ventana()
        # el contenido cambia de tamaño al llenarse (estados, textos): se vuelve a ajustar un momento después
        for ms in (600, 2000, 5000):
            self.v.after(ms, self._ajustar_ventana)
        threading.Thread(target=matar_huerfanos, daemon=True).start()
        self.verificar()
        self.buscar_puertos()
        self.vigilar_puertos()
        if self.var_wifi.get():
            self.v.after(900, lambda: self.comprobar_ota(silencioso=True))
        self.escribir_enlace()

    # ---------- utilidades de UI ----------
    def _fila(self, padre, nombre):
        f = tk.Frame(padre, bg="#f8f9fa"); f.pack(fill="x", padx=6, pady=1)
        tk.Label(f, text=nombre, width=18, anchor="w", font=("Segoe UI", 9, "bold"), bg="#f8f9fa").pack(side="left")
        lbl = tk.Label(f, text="⏳ Pendiente", anchor="w", bg="#f8f9fa")
        lbl.pack(side="left")
        return lbl

    def _campo(self, padre, texto, var, oculto):
        f = tk.Frame(padre, bg="#f8f9fa"); f.pack(fill="x", padx=6, pady=2)
        tk.Label(f, text=texto, width=14, anchor="w", bg="#f8f9fa").pack(side="left")
        e = tk.Entry(f, textvariable=var, width=22, show="●" if oculto else "")
        e.pack(side="left", padx=2)
        return e

    def _mostrar(self):
        c = "" if self.var_ver.get() else "●"
        self.ent_clave.config(show=c)
        if self.ent_wpass is not None:
            self.ent_wpass.config(show=c)
        if getattr(self, "ent_appass", None) is not None:
            self.ent_appass.config(show=c)

    def _bombear(self):
        """Pasa a la UI lo que llega desde los hilos (unico lugar que toca widgets)."""
        try:
            while True:
                fn = self.cola.get_nowait()
                try:
                    fn()
                except tk.TclError:
                    pass
                except Exception:
                    # un error en una actualizacion de pantalla no debe frenar todas las demas
                    self._a_archivo("ERROR en la pantalla:\n" + traceback.format_exc())
        except queue.Empty:
            pass
        self.v.after(100, self._bombear)

    def ui(self, fn):
        self.cola.put(fn)

    def _a_archivo(self, txt):
        """Copia todo lo que sale en el registro a registro_programa.txt (junto al programa), por si algo se cuelga."""
        try:
            with open(os.path.join(DIR_APP, "registro_programa.txt"), "a", encoding="utf-8", errors="replace") as f:
                f.write(txt if txt.endswith("\n") else txt + "\n")
        except Exception:
            pass

    def escribir(self, txt):
        self._a_archivo(time.strftime("%H:%M:%S ") + txt.rstrip("\n"))
        def f():
            self.log.configure(state="normal")
            self.log.insert("end", txt.rstrip("\n") + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.ui(f)

    def escribir_vivo(self, trozo):
        """Agrega texto al registro tal como llega (sin forzar salto de linea); \\r reescribe la linea actual."""
        self._a_archivo(trozo.replace("\r", "\n").rstrip("\n"))
        def f():
            self.log.configure(state="normal")
            for i, parte in enumerate(trozo.replace("\r\n", "\n").split("\r")):
                if i > 0:
                    self.log.delete("end-1c linestart", "end-1c")
                if not parte:
                    continue
                actual = self.log.get("end-1c linestart", "end-1c")
                if "Connecting" in (actual + parte):
                    # los puntitos de 'Connecting......' van en verde: ahi hay que apretar BOOT
                    for pedazo in re.split(r"(\.+)", parte):
                        if pedazo:
                            self.log.insert("end-1c", pedazo, ("verde",) if set(pedazo) == {"."} else ())
                else:
                    self.log.insert("end-1c", parte)
            self.log.see("end")
            self.log.configure(state="disabled")
        self.ui(f)

    def set_estado(self, txt):
        self.ui(lambda: self.estado.config(text=txt))

    def set_ocupado(self, si):
        def f():
            self.ocupado = si
            if si:
                self.cancelado = False
                self.barra.config(mode="indeterminate")
                self.lbl_pct.config(text="")
                self.barra.start(12)
            elif str(self.barra.cget("mode")) == "indeterminate":
                self.barra.stop()
            self.refrescar_botones()
        self.ui(f)

    # ---------- barra con porcentaje (preparar y cargar) ----------
    def modo_pct(self, si, final=False):
        """Pasa la barra a modo porcentaje (si=True) o la deja (si=False; final=True la deja en 100%)."""
        def f():
            if si:
                self.prog_activo = True
                self.pct_mostrado = 0.0
                self._buf_prog = ""
                self.barra.stop()
                self.barra.config(mode="determinate", maximum=100, value=0)
                self.lbl_pct.config(text="0%")
                self._tick()
            else:
                self.prog_activo = False
                self.prog = None
                if final:
                    self.barra.config(value=100)
                    self.lbl_pct.config(text="100%")
                else:
                    self.barra.config(mode="indeterminate", value=0)
                    self.lbl_pct.config(text="")
        self.ui(f)

    def fase(self, desde, hasta, modo="tiempo", T=60.0, total=1):
        """Define el tramo de la barra (desde..hasta, en %) y como avanza: por tiempo estimado, por paquetes o por subida."""
        self._buf_prog = ""
        self.prog = {"d": desde, "h": hasta, "modo": modo, "T": T, "total": total, "t0": time.time(), "v": 0.0, "fin": False, "paq": set()}

    def fase_fin(self):
        p = self.prog
        if p:
            p.update(modo="fijo", v=1.0, fin=True)

    def _tick(self):
        if not self.prog_activo:
            return
        p = self.prog
        if p:
            if p["modo"] == "tiempo":
                v = 1 - math.exp(-(time.time() - p["t0"]) / p["T"])
            else:
                v = p["v"]
            if not p["fin"]:
                v = min(v, 0.97)
            valor = p["d"] + (p["h"] - p["d"]) * max(v, 0.0)
            self.pct_mostrado = max(self.pct_mostrado, valor)
            self.barra.config(value=self.pct_mostrado)
            self.lbl_pct.config(text=f"{int(self.pct_mostrado)}%")
        self.v.after(200, self._tick)

    def _leer_progreso(self, trozo):
        """Saca el avance real de lo que imprimen arduino-cli / esptool."""
        p = self.prog
        if not p or p["modo"] in ("tiempo", "fijo"):
            return
        self._buf_prog = (self._buf_prog + trozo)[-600:]
        if p["modo"] == "paquetes":
            # cada paquete que aparece nombrado (esp32:xtensa-esp-elf-gcc@..., esp32:esp32s2-libs@...) suma un paso
            for m in re.finditer(r"\b(?:esp32|builtin):[\w\-]+@[\w]+(?:\.[\d]+)*", self._buf_prog):
                p["paq"].add(m.group(0))
            p["v"] = max(p["v"], len(p["paq"]) / float(p["total"]))
        elif p["modo"] == "subida":
            m = None
            for m in re.finditer(r"Writing at 0x([0-9a-fA-F]+)\.*\s*\(\s*(\d+)\s*%\)", self._buf_prog):
                pass
            if m:
                addr, pc = int(m.group(1), 16), int(m.group(2))
                # el programa (desde 0x10000) es casi todo el peso; el cargador y las particiones son chicos
                base, peso = (0.0, 0.03) if addr < 0x8000 else (0.03, 0.02) if addr < 0x10000 else (0.05, 0.95)
                p["v"] = max(p["v"], base + peso * pc / 100.0)

    # ---------- estado de los pasos (se deshabilitan los ya hechos) ----------
    def firma(self, tipo):
        c = self.cfg
        datos = [json.dumps(c.get("pines"), sort_keys=True), str(c.get("rele_bajo")), str(c.get("placa")),
                 self.var_clave.get(), self.var_ssid.get(), self.var_wpass.get(),
                 self.var_apssid.get(), self.var_appass.get(), self.var_carpeta.get().strip(),
                 json.dumps([c.get("sensores"), c.get("reglas"), c.get("codigo_extra")], sort_keys=True)]
        if tipo == "ino":
            datos.append(self.var_deploy.get().strip())
        elif tipo == "gs":
            datos = [datos[2], self.var_script.get().strip(), self.var_deploy.get().strip()]
        datos.append(MARCA_PLANTILLA)      # si cambia la version de las plantillas, los pasos se vuelven a habilitar
        if tipo != "ino":                  # la pagina cambia sin tocar el sketch: ③ y ④ se habilitan, ⑤ no
            datos.append(MARCAS_PLANTILLA["Pagina.html"])
            datos.append(MARCAS_PLANTILLA["Codigo.gs"])     # si cambia el script de Google, ③ y ④ se vuelven a habilitar
        return hashlib.sha1(json.dumps(datos).encode("utf-8")).hexdigest()

    def marcar(self, clave, valor=True):
        self.cfg.setdefault("hechos", {})[clave] = valor
        guardar_config(self.cfg)
        self.refrescar_botones()

    def refrescar_botones(self):
        """Habilita solo lo que falta: lo ya hecho queda gris y deshabilitado hasta que cambies algo."""
        h = self.cfg.get("hechos") or {}
        carpeta = self.var_carpeta.get().strip()
        existen = all(os.path.isfile(os.path.join(carpeta, n)) for n in ("Codigo.gs", "Pagina.html", ARCHIVO_INO))
        req, login = self.req_ok, self.login_ok
        pasos = {
            self.b_instalar: (req, True),
            self.b_login: (login, req),
            self.b_todo: (existen and h.get("archivos") == self.firma("arch"), True),
            self.b_subir: (h.get("subido") == self.firma("gs"), req and login and existen),
            self.b_cargar: (h.get("cargado") == self.firma("ino"), existen),
        }
        for b, (hecho, puede) in pasos.items():
            txt, col = self.base_pasos[b]
            b.config(text=("✅ " + txt) if hecho else txt,
                     bg="#95a5a6" if hecho else col,
                     state="disabled" if (self.ocupado or hecho or not puede) else "normal")
        nombre = self.var_nombre.get().strip()
        ok_nuevo = (not self.ocupado) and req and login and nombre and nombre != h.get("nombre_creado")
        self.b_nuevo.config(state="normal" if ok_nuevo else "disabled", bg="#16a085" if ok_nuevo else "#95a5a6")
        self.b_puertos.config(state="disabled" if self.ocupado else "normal")
        if getattr(self, "b_renombrar", None) is not None:
            self.b_renombrar.config(state="disabled" if self.ocupado else "normal")
        if getattr(self, "b_hacer", None) is not None:
            self.b_hacer.config(state="disabled" if (self.ocupado or not (req and login)) else "normal")
        self.b_cancel.config(state="normal" if self.ocupado else "disabled",
                             bg="#7f8c8d" if self.ocupado else "#95a5a6")

    def _evitar_nombre_repetido(self):
        """Antes de grabar por USB mira si ya hay otro ESP32 con el mismo nombre en la red; si es asi
        propone el siguiente libre (Reles1 -> Reles2 -> Reles3...)."""
        self.cancelado_nombre = False
        self.set_estado("🔎 Comprobando que el nombre no esté repetido en la red...")
        self.v.update_idletasks()
        try:
            usados = [n for n, _ in buscar_esp32_ota(2.5)]
        except Exception:
            usados = []
        self.set_estado("Listo.")
        actual = self.var_apssid.get().strip() or "luces1"
        bajos = {n.lower() for n in usados}
        if actual.lower() not in bajos:
            return
        m = re.match(r"^(.*?)(\d*)$", actual)
        base, num = m.group(1), m.group(2)
        n = int(num) + 1 if num else 2
        while f"{base}{n}".lower() in bajos:
            n += 1
        nuevo = f"{base}{n}"
        texto = (f"Ya hay un ESP32 llamado «{actual}» en la red.\n"
                 f"Si grabás este con el mismo nombre no vas a poder distinguirlos.\n\n"
                 f"En la red hay: {', '.join(sorted(usados))}")
        i = _dialogo("Nombre repetido", texto, [f"Usar «{nuevo}»", f"Dejar «{actual}»", "Cancelar"], "⚠️", cancelar=2)
        if i == 0:
            self.var_apssid.set(nuevo)
            self.guardar()
            self.escribir(f"✏️ Nombre de la red AP cambiado a {nuevo} (ya existía {actual}).")
        elif i != 1:
            self.cancelado_nombre = True

    def _al_tildar_wifi(self):
        if self.var_wifi.get():
            self.comprobar_ota(silencioso=True)

    def comprobar_ota(self, silencioso=False):
        """Busca en la red los ESP32 que aceptan grabacion por WiFi y llena la lista de destinos."""
        if str(self.b_comprobar.cget("state")) == "disabled":
            return
        self.b_comprobar.config(state="disabled", text="🔎 Buscando...")
        self.escribir("🔎 Buscando ESP32 con grabación por WiFi en la red...")

        def tarea():
            try:
                lista = buscar_esp32_ota(3.5)
            except Exception:
                lista = []
            self.ui(lambda: self._resultado_busqueda(lista, silencioso))
        threading.Thread(target=tarea, daemon=True).start()

    def _resultado_busqueda(self, lista, silencioso=False):
        self.b_comprobar.config(state="normal", text="🔎 Buscar")
        etiquetas = [f"{n}  ({ip})" for n, ip in lista]
        self.cb_host.config(values=etiquetas)
        vpn = []
        if not lista:
            try:
                vpn = vpn_activa()
            except Exception:
                vpn = []
        if not lista and vpn:
            self.escribir("🛡️ Detecté una VPN activa (" + ", ".join(vpn) + "): apagala para buscar o grabar por WiFi; manda el tráfico por fuera de tu red de casa.")
            if not silencioso:
                messagebox.showwarning("Buscar ESP32", "No encontré el ESP32 y hay una VPN activa:\n\n   " + "\n   ".join(vpn) +
                                       "\n\nLa VPN desvía el tráfico y el ESP32 (que está en tu red de casa) no se ve.\nApagala, volvé a tocar 🔎 Buscar y listo.")
            return
        if not lista:
            self.escribir("⚠️ No encontré ningún ESP32 con grabación por WiFi. Puede estar apagado, en otra red, o tener un programa viejo (grabalo una vez por USB).")
            if not silencioso:
                messagebox.showwarning("Buscar ESP32", "No encontré ningún ESP32 con grabación por WiFi en esta red.\n\nRevisá que esté encendido, en el mismo WiFi y que ya tenga el programa versión 15 (grabado una vez por USB).")
            return
        for e in etiquetas:
            self.escribir("✅ " + e)
        actual = self.var_host.get().strip()
        if len(lista) == 1:
            era = self.var_host.get().strip()
            self.var_host.set(etiquetas[0])
            if era != etiquetas[0]:      # si es el mismo ESP32 de antes, no se pisa el nombre que estás escribiendo
                self._al_elegir_destino()
            self.escribir(f"📶 Destino: {etiquetas[0]}")
            if not silencioso:
                messagebox.showinfo("Buscar ESP32", f"✅ Encontré 1 ESP32 listo para grabar por WiFi:\n\n{etiquetas[0]}\n\nQuedó elegido.\n\nSi tenés otro y no aparece, ese todavía tiene un programa sin grabación por WiFi: grabalo una vez por USB.")
        else:
            if actual not in etiquetas:
                self.var_host.set("")
            self.escribir(f"📶 Encontré {len(lista)} ESP32: elegí cuál en la lista «ESP32 destino».")
            if not silencioso:
                messagebox.showinfo("Buscar ESP32", f"✅ Encontré {len(lista)} ESP32:\n\n" + "\n".join(etiquetas) + "\n\nElegí a cuál grabar en la lista «ESP32 destino».")
            self.cb_host.focus_set()
            try:
                self.cb_host.event_generate("<Down>")
            except Exception:
                pass

    def _destino_wifi(self):
        """Devuelve la direccion (IP o nombre) elegida en la lista de destinos."""
        t = self.var_host.get().strip()
        m = re.search(r"\((\d{1,3}(?:\.\d{1,3}){3})\)", t)
        if m:
            return m.group(1)
        return t or (self.var_apssid.get().strip() or "luces1") + ".local"

    def cancelar_tarea(self):
        """Corta el comando que esta corriendo (y todos sus procesos hijos)."""
        self.cancelado = True
        self.escribir("⛔ Cancelado por el usuario.")
        self.set_estado("⛔ Cancelando...")
        matar_arbol(self.proc_actual)

    def reactivar_pasos(self):
        self.cfg["hechos"] = {}
        guardar_config(self.cfg)
        self.refrescar_botones()

    def elegir_carpeta(self):
        d = filedialog.askdirectory(initialdir=self.var_carpeta.get() or DIR_APP)
        if d:
            self.var_carpeta.set(os.path.normpath(d))

    def revisar_cuenta(self, cuenta):
        """Si cambió la cuenta de Google, los IDs guardados son de la cuenta anterior: ofrece limpiarlos."""
        vieja = self.cfg.get("cuenta", "")
        if vieja and vieja.lower() != cuenta.lower() and (self.var_script.get().strip() or self.var_deploy.get().strip()):
            if messagebox.askyesno("Cuenta de Google distinta",
                                   f"Ahora estás conectado como:\n   {cuenta}\n\nLos IDs guardados son de la cuenta anterior:\n   {vieja}\n\n"
                                   "Esa cuenta nueva no tiene esos scripts. ¿Borro los IDs para empezar limpio?\n"
                                   "(Después usá el botón 🆕 Crear script NUEVO.)"):
                self.var_script.set("")
                self.var_deploy.set("")
                self.cfg["hechos"] = {}
        self.cfg["cuenta"] = cuenta
        self.guardar()
        self.refrescar_botones()

    def abrir_api(self):
        webbrowser.open("https://script.google.com/home/usersettings")

    def ofrecer_api(self, texto):
        """Si el error es por la API de Apps Script desactivada, ofrece abrir la pagina para activarla."""
        if "enabled the Apps Script API" in (texto or "") or "Apps Script API" in (texto or ""):
            def f():
                if messagebox.askyesno("Falta activar la API de Apps Script",
                                       "En esta cuenta de Google la API de Apps Script está desactivada.\n\n"
                                       "Se abre la página: activá el interruptor, esperá 2 a 5 minutos y repetí el paso.\n\n¿Abrir la página ahora?"):
                    self.abrir_api()
            self.ui(f)

    def abrir_en_google(self):
        sid = self.var_script.get().strip()
        webbrowser.open(f"https://script.google.com/home/projects/{sid}/edit" if sid else "https://script.google.com/home")

    def copiar_url(self):
        self.v.clipboard_clear()
        self.v.clipboard_append(self.var_url.get())
        self.v.update()
        self.set_estado("📋 Enlace copiado: pegalo en el navegador del celular.")

    def escribir_enlace(self, archivo=True):
        """Muestra el enlace en el programa y lo guarda en enlace_luces.txt dentro de la carpeta del proyecto."""
        if not hasattr(self, "var_url"):
            return
        dep = self.var_deploy.get().strip()
        url = f"https://script.google.com/macros/s/{dep}/exec" if dep else ""
        try:
            self.var_url.set(url)
        except tk.TclError:
            return
        carpeta = self.var_carpeta.get().strip()
        if archivo and url and carpeta and os.path.isdir(carpeta):
            try:
                with open(os.path.join(carpeta, "enlace_luces.txt"), "w", encoding="utf-8", newline="") as f:
                    clave = self.var_clave.get()
                    f.write("Enlace de la pagina web de las luces (abrilo en el celular o la PC):\n\n" + url + "\n"
                            + (f"Contraseña: {clave}\n" if clave else "") + "\n")
            except Exception:
                pass

    def guardar(self):
        self.cfg = {"carpeta": self.var_carpeta.get().strip(),
                    "script_id": self.var_script.get().strip(),
                    "deployment_id": self.var_deploy.get().strip(),
                    "clave": self.var_clave.get(),
                    "wifi_ssid": self.var_ssid.get(),
                    "wifi_pass": self.var_wpass.get(),
                    "ap_ssid": self.var_apssid.get().strip() or "luces1",
                    "ap_pass": self.var_appass.get(),
                    "rele_bajo": self.cfg.get("rele_bajo", "ALTO"),
                    "puerto": self.var_puerto.get().strip(),
                    "por_wifi": bool(self.var_wifi.get()),
                    "ota_host": self.var_host.get().strip(),
                    "nombre_script": self.var_nombre.get().strip(),
                    "pines": self.cfg["pines"],
                    "perfiles": self.cfg.get("perfiles") or {},
                    "sensores": self.cfg.get("sensores") or [],
                    "reglas": self.cfg.get("reglas") or [],
                    "codigo_extra": self.cfg.get("codigo_extra") or {},
                    "librerias_extra": self.cfg.get("librerias_extra") or [],
                    "librerias_zip": self.cfg.get("librerias_zip") or [],
                    "led_migrado": True,
                    "hechos": self.cfg.get("hechos") or {},
                    "cuenta": self.cfg.get("cuenta", ""),
                    "placa": self.cfg.get("placa", PLACA_DEFECTO)}
        self._guardar_perfil()
        guardar_config(self.cfg)
        if self.cfg["nombre_script"] and self.cfg["carpeta"] == carpeta_de_proyecto(self.cfg["nombre_script"]):
            try:
                os.makedirs(self.cfg["carpeta"], exist_ok=True)
            except OSError:
                pass
        self.escribir_enlace()
        self.escribir_pines_txt()

    # ---------- pines de cada ESP32 (se guardan con el nombre de su Red AP) ----------
    def _nombre_ap(self):
        return self.var_apssid.get().strip() or "luces1"

    def _guardar_perfil(self):
        """Guarda los pines actuales con el nombre del ESP32 elegido (Red AP)."""
        perf = self.cfg.setdefault("perfiles", {})
        n = self._nombre_ap()
        perf[n] = {"pines": json.loads(json.dumps(self.cfg["pines"])),
                   "rele_bajo": self.cfg.get("rele_bajo", "ALTO"),
                   "sensores": json.loads(json.dumps(self.cfg.get("sensores") or [])),
                   "reglas": json.loads(json.dumps(self.cfg.get("reglas") or [])),
                   "codigo_extra": json.loads(json.dumps(self.cfg.get("codigo_extra") or {})),
                   "placa": self.cfg.get("placa", PLACA_DEFECTO)}
        self._perfil_activo = n

    def _texto_pines(self):
        return (f"Pines de {self._nombre_ap()} ({self.cfg.get('placa', PLACA_DEFECTO)}): " + resumen_pines(self.cfg["pines"])
                + " · " + resumen_sensores(self.cfg))

    def _al_cambiar_nombre_ap(self, *_):
        """Al elegir otro ESP32 (otro nombre de Red AP) se muestran sus pines guardados."""
        n = self._nombre_ap()
        if n == getattr(self, "_perfil_activo", None):
            return
        perf = self.cfg.get("perfiles") or {}
        if n in perf:
            pr = perf[n]
            if pr.get("placa") in BOARDS:
                self.cfg["placa"] = pr["placa"]
            usar_placa(self.cfg.get("placa"))
            base = pines_defecto()
            base.update(pr.get("pines") or {})
            self.cfg["pines"] = base
            self.cfg["rele_bajo"] = pr.get("rele_bajo", "ALTO")
            self.cfg["sensores"] = json.loads(json.dumps(pr.get("sensores") or []))
            self.cfg["reglas"] = json.loads(json.dumps(pr.get("reglas") or []))
            self.cfg["codigo_extra"] = json.loads(json.dumps(pr.get("codigo_extra") or {}))
            if pr.get("placa") in PLACAS:
                self.cfg["placa"] = pr["placa"]
            self._perfil_activo = n
            self.lbl_pines.config(text=self._texto_pines())
            self.escribir(f"🔌 Pines de {n} cargados ({resumen_pines(base)}).")
            self.refrescar_botones()
        else:
            self.lbl_pines.config(text=f"Pines de {n} (nuevo, con la placa y los pines de la pantalla): " + resumen_pines(self.cfg["pines"]))

    def _al_elegir_destino(self, _=None):
        """Al elegir un ESP32 de la lista de destinos, su nombre pasa a «Red AP» y se cargan sus pines."""
        m = re.match(r"^(.*?)\s+\(\d{1,3}(?:\.\d{1,3}){3}\)\s*$", self.var_host.get().strip())
        if m and m.group(1):
            self.var_apssid.set(m.group(1))

    def escribir_pines_txt(self, avisar=False):
        carpeta = self.cfg.get("carpeta", "")
        if not carpeta:
            return
        try:
            os.makedirs(carpeta, exist_ok=True)
            txt = texto_pines(self.cfg["pines"], self.cfg.get("rele_bajo", "ALTO"), self.cfg.get("placa", PLACA_DEFECTO), self.cfg)
            nombre = re.sub(r'[\\/:*?"<>|]', "_", self._nombre_ap())
            archivo = f"Pines ESP32 - {nombre}.txt"
            with open(os.path.join(carpeta, archivo), "w", encoding="utf-8", newline="") as f:
                f.write(f"ESP32: {self._nombre_ap()}\n\n" + txt)
            if avisar:
                self.escribir(f"📄 {archivo} guardado en {carpeta}")
        except Exception as ex:
            self.escribir(f"⚠️ No pude guardar el archivo de pines: {ex}")

    # ---------- comandos ----------
    def ejecutar(self, comando, cwd=None, mostrar=True, timeout=None, latido=None):
        """Corre un comando mostrando la salida en vivo. Devuelve (codigo, texto)."""
        if mostrar:
            self.escribir("> " + comando)
        try:
            p = subprocess.Popen(comando, shell=True, cwd=cwd, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 creationflags=CREAR_SIN_VENTANA)
        except Exception as e:
            self.escribir(f"ERROR: {e}")
            return 1, str(e)
        self.proc_actual = p
        vencio = []
        if timeout:
            def cortar():
                vencio.append(True)
                try:
                    if os.name == "nt":
                        subprocess.run(f"taskkill /PID {p.pid} /T /F", shell=True, capture_output=True, creationflags=CREAR_SIN_VENTANA)
                    else:
                        p.kill()
                except Exception:
                    pass
            temporizador = threading.Timer(timeout, cortar)
            temporizador.daemon = True
            temporizador.start()
        fin_latido = threading.Event()
        if latido:
            def pulso():
                t0 = time.time()
                while not fin_latido.wait(20):
                    seg = int(time.time() - t0)
                    self.escribir(f"⏳ {latido}... lleva {seg // 60}:{seg % 60:02d} (sigue trabajando, no se colgó)")
            threading.Thread(target=pulso, daemon=True).start()
        salida = []
        # Se lee lo que vaya llegando (no linea por linea) para ver al instante los puntitos de
        # 'Connecting......' y poder apretar BOOT a tiempo.
        deco = codecs.getincrementaldecoder("utf-8")(errors="replace")
        fd = p.stdout.fileno()
        ultimo = "\n"
        while True:
            try:
                datos = os.read(fd, 4096)
            except OSError:
                break
            if not datos:
                break
            trozo = deco.decode(datos)
            if not trozo:
                continue
            salida.append(trozo)
            self._leer_progreso(trozo)
            if mostrar:
                self.escribir_vivo(trozo)
                ultimo = trozo[-1]
        p.wait()
        fin_latido.set()
        if timeout:
            temporizador.cancel()
        if vencio and mostrar:
            self.escribir(f"⏱ Se cortó el comando: pasaron {timeout} segundos sin terminar.")
        if mostrar and ultimo not in "\n\r":
            self.escribir_vivo("\n")
        return p.returncode, "".join(salida).replace("\r\n", "\n")

    def verificar(self):
        def tarea():
            node = shutil.which("node")
            clasp = shutil.which("clasp")
            self.ui(lambda: self.lbl_node.config(text="✅ Instalado" if node else "❌ Falta (botón Instalar lo que falta)"))
            self.ui(lambda: self.lbl_clasp.config(text="✅ Instalado" if clasp else "❌ Falta (botón Instalar lo que falta)"))
            logueado = os.path.exists(os.path.join(os.path.expanduser("~"), ".clasprc.json"))
            cuenta = ""
            if logueado and clasp:
                try:
                    r = subprocess.run("clasp show-authorized-user", shell=True, capture_output=True, text=True,
                                       timeout=20, creationflags=0x08000000 if os.name == "nt" else 0)
                    m = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", (r.stdout or "") + (r.stderr or ""))
                    cuenta = m.group(0) if m else ""
                except Exception:
                    cuenta = ""
            if cuenta:
                self.ui(lambda: self.revisar_cuenta(cuenta))
            self.ui(lambda: self.lbl_login.config(text=("✅ Conectada" + (f" ({cuenta})" if cuenta else "")) if logueado else "❌ Sin conectar (botón Conectar)"))
            def flags():
                self.req_ok = bool(node and clasp)
                self.login_ok = bool(logueado)
                self.refrescar_botones()
            self.ui(flags)
            self.set_estado("Listo." if (node and clasp and logueado) else "Faltan pasos: mirá los requisitos.")
        threading.Thread(target=tarea, daemon=True).start()

    def instalar_node(self):
        """Node.js: primero la versión portátil en Dependencias_Ofline; si falla, winget o el instalador oficial."""
        self.set_estado("⬇️ Descargando Node.js portátil a Dependencias_Ofline...")
        if descargar_node_portatil(self.escribir):
            return True
        if shutil.which("winget"):
            self.set_estado("📦 Instalando Node.js con winget (acepta el permiso si Windows lo pide)...")
            cod, _ = self.ejecutar("winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements")
            asegurar_path()
            if shutil.which("node"):
                return True
        try:
            self.set_estado("⬇️ Descargando Node.js desde nodejs.org...")
            with urllib.request.urlopen("https://nodejs.org/dist/index.json", timeout=30) as r:
                lista = json.loads(r.read().decode("utf-8"))
            ver = next(x["version"] for x in lista if x.get("lts"))
            url = f"https://nodejs.org/dist/{ver}/node-{ver}-x64.msi"
            destino = os.path.join(tempfile.gettempdir(), f"node-{ver}-x64.msi")
            self.escribir(f"Descargando {url}")
            urllib.request.urlretrieve(url, destino)
            self.set_estado("📦 Instalando Node.js (acepta el permiso de Windows)...")
            self.ejecutar(f'msiexec /i "{destino}" /passive /norestart')
            try:
                os.remove(destino)
            except Exception:
                pass
        except Exception as e:
            self.escribir(f"ERROR descargando Node.js: {e}")
        asegurar_path()
        return bool(shutil.which("node"))

    def instalar_clasp(self):
        if self.ocupado:
            return

        def tarea():
            self.set_ocupado(True)
            try:
                if not (node_en_deps() or shutil.which("node")):
                    if not self.instalar_node():
                        self.set_estado("❌ No se pudo instalar Node.js (ver registro). Instalalo desde nodejs.org")
                        return
                    self.escribir("✅ Node.js instalado")
                if not (clasp_en_deps() or shutil.which("clasp")):
                    self.set_estado("📦 Instalando clasp en Dependencias_Ofline...")
                    cod, _ = self.ejecutar(comando_instalar_clasp())
                    preparar_entorno_deps()
                    asegurar_path()
                    if cod != 0 or not shutil.which("clasp"):
                        self.set_estado("❌ Error al instalar clasp (mirá el registro)")
                        return
                self.set_estado("✅ Todo instalado. Ahora tocá Conectar con Google.")
            finally:
                self.set_ocupado(False)
                self.verificar()
        threading.Thread(target=tarea, daemon=True).start()

    def conectar(self):
        if self.ocupado:
            return
        if not shutil.which("clasp"):
            messagebox.showwarning("Falta clasp", "Primero tocá Instalar lo que falta.")
            return

        def tarea():
            self.set_ocupado(True)
            self.set_estado("🔑 Se abrió el navegador: elegí tu cuenta y tocá Permitir...")
            cod, salida = self.ejecutar("clasp login")
            if cod == 0:
                self.set_estado("✅ Cuenta conectada")
            else:
                self.set_estado("❌ No se pudo conectar (mirá el registro)")
            self.set_ocupado(False)
            self.verificar()
        threading.Thread(target=tarea, daemon=True).start()

    def clave_valida(self):
        c = self.var_clave.get()
        if len(c) < 4 or " " in c or "&" in c or "#" in c or "+" in c or "%" in c:
            messagebox.showerror("Contraseña", "La contraseña web debe tener al menos 4 caracteres y no puede tener espacios ni los símbolos & # + %\n(el ESP32 la manda dentro de un enlace).")
            return False
        return True

    def abrir_pines(self):
        w = tk.Toplevel(self.v)
        w.withdraw()          # se arma oculta y se muestra ya con el tamaño final (sin el parpadeo de ancho)
        w.title(f"🔌 Pines de {self._nombre_ap()}")
        w.configure(bg="#f8f9fa")
        w.resizable(False, False)
        w.transient(self.v)
        tk.Label(w, text=f"Elegí qué hace cada pin de «{self._nombre_ap()}»", font=("Segoe UI", 12, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(pady=(10, 0))
        tk.Label(w, text="SAL = salida (relé)   ENT = entrada (contacto)   SEN = sensor (LDR, presión...)   LED = luz de la placa que indica la conexión (un solo pin)   BOT = botón de cambio de red   — = sin usar",
                 font=("Segoe UI", 8), bg="#f8f9fa", fg="#7f8c8d").pack()
        fp = tk.Frame(w, bg="#f8f9fa"); fp.pack(pady=(6, 0))
        tk.Label(fp, text="Placa:", bg="#f8f9fa", font=("Segoe UI", 9, "bold")).pack(side="left")
        vplaca = tk.StringVar(value=self.cfg.get("placa", PLACA_DEFECTO) if self.cfg.get("placa") in PLACAS else PLACA_DEFECTO)
        cbplaca = ttk.Combobox(fp, textvariable=vplaca, values=list(PLACAS.keys()), state="readonly", width=30)
        cbplaca.pack(side="left", padx=4)
        _bd = BOARDS.get(vplaca.get(), _CLASICO)
        _vista = ("Pines " + _bd["usb"]) if _bd.get("sin_dibujo") else f"Vista desde arriba, {_bd['usb']}"
        fmt_v = tk.StringVar(value=_bd.get("formato", ""))
        if _bd.get("generica"):
            tk.Label(fp, text="Formato:", bg="#f8f9fa", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(6, 0))
            cbfmt = ttk.Combobox(fp, textvariable=fmt_v, values=formatos_de(_bd["mcu"]), state="readonly", width=24)
            cbfmt.pack(side="left", padx=4)
        tk.Label(fp, text=f"{_vista}. LCD I2C fijo: SDA = GPIO{_bd['sda']}, SCL = GPIO{_bd['scl']}.",
                 bg="#f8f9fa", fg="#7f8c8d", font=("Segoe UI", 8)).pack(side="left", padx=6)
        # los botones van fijos abajo (se empaquetan primero) y la lista de pines se desplaza si no entra en pantalla
        bf = tk.Frame(w, bg="#f8f9fa"); bf.pack(side="bottom", pady=(4, 12))
        zona = tk.Frame(w, bg="#f8f9fa"); zona.pack(side="top", fill="both", expand=True, padx=(12, 0), pady=6)
        lienzo = tk.Canvas(zona, bg="#f8f9fa", highlightthickness=0)
        barra_y = ttk.Scrollbar(zona, orient="vertical", command=lienzo.yview)
        lienzo.configure(yscrollcommand=barra_y.set)
        lienzo.pack(side="left", fill="both", expand=True)
        cuerpo = tk.Frame(lienzo, bg="#f8f9fa")
        lienzo.create_window((0, 0), window=cuerpo, anchor="nw")
        cuerpo.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))

        def _rueda(e):
            if barra_y.winfo_ismapped():
                lienzo.yview_scroll(-1 if e.delta > 0 else 1, "units")
        w.bind("<MouseWheel>", _rueda)
        vars_ = {}
        vres = {}
        widgets = {}
        previos = {}
        agregados = []          # sensores creados desde esta ventana (si se cancela, se quitan)

        def mapa_sensores():
            return {int(x["pin"]): x for x in (self.cfg.get("sensores") or []) if str(x.get("pin", "")).isdigit()}

        def _clave_nombre(n):
            n = (n or "").strip().lower().replace(" ", "")
            m = re.fullmatch(r"(?:r|rele_)(\d+)", n) or re.fullmatch(r"(?:e|entrada_)(\d+)", n)
            return (n[0] + m.group(1)) if m else n

        def siguiente_nombre(letra, pin):
            """Primer R# / E# que no usa otro pin."""
            usados = {_clave_nombre(v[1].get()) for p, v in vars_.items()
                      if p != pin and v[0].get() in ("SAL", "ENT") and v[1].get().strip()}
            i = 1
            while f"{letra.lower()}{i}" in usados:
                i += 1
            return f"{letra}{i}"

        def lista_nombres(pin):
            """Nombres rápidos del combo, sin los que ya usó otro pin (así no se repiten por error)."""
            usados = {_clave_nombre(v[1].get()) for p, v in vars_.items()
                      if p != pin and v[0].get() in ("SAL", "ENT") and v[1].get().strip()}
            base = NOMBRES_RAPIDOS_E if vars_[pin][0].get() == "ENT" else NOMBRES_RAPIDOS_R
            return [n for n in base if n == "" or _clave_nombre(n) not in usados]

        def refrescar_listas(*_):
            for p, (en_, _ca, _cr) in list(widgets.items()):
                try:
                    en_.config(values=lista_nombres(p))
                except tk.TclError:
                    pass

        def reflejar(pin):
            vt, vn, va = vars_[pin]
            t = vt.get()
            if previos[pin] != t:
                va.set("ALTO")            # al cambiar de tipo, el nivel vuelve al valor normal (después se elige a mano)
                actual = vn.get().strip()
                es_auto = (actual == "") or re.fullmatch(r"[REre]\d+", actual) is not None
                if t in ("SAL", "ENT") and es_auto:
                    vn.set(siguiente_nombre("R" if t == "SAL" else "E", pin))     # R1, R2... / E1, E2... (se puede cambiar a mano)
                elif t not in ("SAL", "ENT") and es_auto:
                    vn.set("")
            previos[pin] = t
            if pin in widgets:
                en, ca, cr = widgets[pin]
                if t == "ENT" and pin in SOLO_ENTRADA:
                    vres[pin].set(RES_ETIQ["NINGUNA"])
                try:
                    en.config(values=lista_nombres(pin),
                              state="normal" if t in ("SAL", "ENT") else "disabled")
                    ca.config(state="readonly" if t in ("ENT", "SAL") else "disabled")
                    cr.config(state="readonly" if (t == "ENT" and pin not in SOLO_ENTRADA) else "disabled")
                except tk.TclError:
                    pass

        def auto_res(pin):
            """Al cambiar el nivel de alarma de una entrada, la resistencia se pone al revés
            (alarma ALTO -> pull-down, alarma BAJO -> pull-up). Después se puede cambiar a mano."""
            if vars_[pin][0].get() != "ENT" or pin in SOLO_ENTRADA:
                return
            vres[pin].set(RES_ETIQ["PULLDOWN" if vars_[pin][2].get() == "ALTO" else "PULLUP"])

        def crear_sensor(pin):
            """Se eligió SEN en un pin sin sensor: se abre el formulario del sensor con ese pin."""
            if vars_[pin][0].get() != "SEN" or pin in mapa_sensores():
                return
            n = self._dialogo_sensor(w, None, self.cfg.get("sensores") or [], pin_inicial=pin, pines=leer())
            if n is None:
                vars_[pin][0].set("—")
                return
            self.cfg.setdefault("sensores", []).append(n)
            agregados.append(n)
            np_ = int(n["pin"])
            if np_ != pin:                     # en el formulario eligió otro pin
                vars_[pin][0].set("—")
                if np_ in vars_:
                    vars_[np_][0].set("SEN")
            if np_ in vars_:
                vars_[np_][1].set(n["nombre"])

        def al_elegir_sen(pin):
            if vars_[pin][0].get() == "SEN" and pin not in mapa_sensores():
                w.after(30, lambda: crear_sensor(pin))

        for pin in PIN_LISTA:
            d = self.cfg["pines"].get(str(pin), {})
            sp = mapa_sensores().get(pin)
            tipo0 = "SEN" if sp else ("—" if d.get("tipo") == "SEN" else d.get("tipo", "—"))     # el pin de un sensor figura como SEN
            vt = tk.StringVar(value=tipo0)
            vn = tk.StringVar(value=sp["nombre"] if sp else ("" if tipo0 == "—" else d.get("nombre", "")))
            va = tk.StringVar(value=d.get("alarma", "ALTO"))
            vars_[pin] = (vt, vn, va)
            vres[pin] = tk.StringVar(value=RES_ETIQ[resistencia_de(self.cfg["pines"], pin)])
            previos[pin] = vt.get()
            vt.trace_add("write", lambda *_, pin=pin: reflejar(pin))
            vt.trace_add("write", lambda *_, pin=pin: al_elegir_sen(pin))
            va.trace_add("write", lambda *_, pin=pin: auto_res(pin))
            vn.trace_add("write", refrescar_listas)
            vt.trace_add("write", refrescar_listas)

        def dibujar(*_):
            for hijo in cuerpo.winfo_children():
                hijo.destroy()
            widgets.clear()
            izq, der = PLACAS[vplaca.get()]
            _lados = BOARDS.get(vplaca.get(), {}).get("lados") or ("◀ LADO IZQUIERDO", "LADO DERECHO ▶")
            for col, (titulo, lado) in enumerate(((_lados[0], izq), (_lados[1], der))):
                base = col * 7
                tk.Label(cuerpo, text=titulo, font=("Segoe UI", 9, "bold"), bg="#f8f9fa", fg="#2980b9").grid(row=0, column=base, columnspan=6, pady=(0, 2))
                tk.Label(cuerpo, text="Tipo · Nombre · Nivel · Resistencia", font=("Segoe UI", 7), bg="#f8f9fa", fg="#7f8c8d").grid(row=0, column=base + 3, columnspan=3, sticky="e")
                for fila, item in enumerate(lado, start=1):
                    if not isinstance(item, int):
                        fijo = item.startswith("GPIO") or item[:2] in ("TX", "RX")
                        tk.Label(cuerpo, text=f"  {item}", anchor="w", font=("Segoe UI", 8), bg="#ecf0f1", fg="#7f8c8d" if not fijo else "#c0392b",
                                 width=52).grid(row=fila, column=base, columnspan=6, padx=(0, 10), pady=1, sticky="we")
                        continue
                    pin = item
                    vt, vn, va = vars_[pin]
                    tk.Label(cuerpo, text=f"GPIO {pin}", width=8, anchor="w", font=("Segoe UI", 9, "bold"), bg="#f8f9fa").grid(row=fila, column=base, pady=1)
                    ttk.Combobox(cuerpo, textvariable=vt, values=opciones_pin(pin), width=5, state="readonly").grid(row=fila, column=base + 1, padx=2)
                    en = ttk.Combobox(cuerpo, textvariable=vn, values=NOMBRES_RAPIDOS_R, width=10)
                    en.grid(row=fila, column=base + 2, padx=2)
                    ca = ttk.Combobox(cuerpo, textvariable=va, values=["ALTO", "BAJO"], width=5, state="readonly")
                    ca.grid(row=fila, column=base + 3, padx=2)
                    cr = ttk.Combobox(cuerpo, textvariable=vres[pin], values=list(RES_ETIQ.values()), width=9, state="readonly")
                    cr.grid(row=fila, column=base + 4, padx=2)
                    nota = NOTAS_PIN.get(pin, "")
                    if pin in SOLO_ENTRADA:
                        nota = "solo entrada · 10 kΩ externa"
                    tk.Label(cuerpo, text=nota, width=26, anchor="w", font=("Segoe UI", 7), bg="#f8f9fa",
                             fg="#e67e22").grid(row=fila, column=base + 5, padx=(0, 10))
                    widgets[pin] = (en, ca, cr)
                    reflejar(pin)
            _bdv = BOARDS.get(vplaca.get(), {})
            filas = max(len(izq), len(der))
            if _bdv.get("sin_dibujo"):
                tk.Frame(cuerpo, bg="#f8f9fa", width=14).grid(row=1, column=6, rowspan=filas)
            else:                            # la placa vista desde arriba, con el USB siempre abajo
                pl = tk.Frame(cuerpo, bg="#1e5c3a", width=74, highlightthickness=2, highlightbackground="#0e3a22")
                pl.grid(row=1, column=6, rowspan=filas, sticky="ns", padx=6)
                pl.pack_propagate(False)
                tk.Label(pl, text="((·))\nWiFi", bg="#1e5c3a", fg="#bdc3c7", font=("Segoe UI", 8)).pack(side="top", pady=(8, 2))
                tk.Label(pl, text=_bdv.get("chip", "ESP32"), bg="#2c3e50", fg="white", font=("Segoe UI", 8, "bold"), width=9, pady=6).pack(side="top", pady=4)
                tk.Label(pl, text="⏏ USB", bg="#95a5a6", fg="#2c3e50", font=("Segoe UI", 8, "bold"), width=9, pady=3).pack(side="bottom", pady=(0, 4))
                tk.Label(pl, text="▲ arriba", bg="#1e5c3a", fg="#7fb99a", font=("Segoe UI", 7)).pack(side="top", pady=(30, 0))
            w.update_idletasks()
            if medida:                       # al cambiar de placa, la lista se reajusta (con barra si no entra)
                ajustar_lista()
        medida = []

        def ajustar_lista():
            w.update_idletasks()
            if not medida:
                medida.append(w.winfo_reqheight() - lienzo.winfo_reqheight())     # títulos + botones
            tope = max(300, w.winfo_screenheight() - 120)
            alto = min(cuerpo.winfo_reqheight(), tope - medida[0])
            lienzo.configure(width=cuerpo.winfo_reqwidth(), height=alto)
            if alto < cuerpo.winfo_reqheight():
                if not barra_y.winfo_ismapped():
                    barra_y.pack(side="left", fill="y")
            else:
                barra_y.pack_forget()
            lienzo.yview_moveto(0)
        def cambiar_placa(*_):
            nueva, actual = vplaca.get(), self.cfg.get("placa", PLACA_DEFECTO)
            if nueva == actual:
                return
            bn, ba = BOARDS[nueva], BOARDS.get(actual, _CLASICO)
            if bn["fqbn"] == ba["fqbn"] and bn["pines"] == ba["pines"]:
                self.cfg["placa"] = nueva            # 30 <-> 38 pines: solo cambia el dibujo
                dibujar()
                return
            hay = bool(self.cfg.get("sensores") or self.cfg.get("reglas"))
            msg = (f"Vas a cambiar a «{nueva}» ({bn['chip']}).\n\nLos pines vuelven a los valores por defecto de esa placa"
                   + (" y se quitan los sensores y reglas (usan pines de la placa anterior)." if hay else ".")
                   + "\n\n¿Continuar?")
            if not messagebox.askyesno("Cambiar de placa", msg, parent=w):
                vplaca.set(actual)
                return
            self.cfg["placa"] = usar_placa(nueva)
            self.cfg["pines"] = pines_defecto()
            if hay:
                self.cfg["sensores"], self.cfg["reglas"] = [], []
            self._tras_cambio_config(f"🔧 Placa cambiada a {nueva}: pines por defecto cargados.")
            w.destroy()
            self.abrir_pines()
        cbplaca.bind("<<ComboboxSelected>>", cambiar_placa)

        def cambiar_formato(*_):
            nombre, nuevo = vplaca.get(), fmt_v.get()
            b0 = BOARDS.get(nombre, {})
            if not b0.get("generica") or nuevo == b0.get("formato"):
                return
            antes = list(b0["pines"])
            registrar_placa(nombre, b0["fqbn"], b0["mcu"], nuevo)
            self.cfg.setdefault("placas_extra", {}).setdefault(nombre, {"fqbn": b0["fqbn"], "mcu": b0["mcu"]})["formato"] = nuevo
            if sorted(BOARDS[nombre]["pines"]) != sorted(antes):
                messagebox.showinfo("Formato", "Este dibujo tiene otros pines disponibles: se cargan los valores por defecto.", parent=w)
                self.cfg["placa"] = usar_placa(nombre)
                self.cfg["pines"] = pines_defecto()
                self.cfg["sensores"], self.cfg["reglas"] = [], []
                self._tras_cambio_config(f"🔧 Formato {nuevo}: pines por defecto cargados.")
                w.destroy()
                self.abrir_pines()
                return
            usar_placa(nombre)
            dibujar()
        if _bd.get("generica"):
            cbfmt.bind("<<ComboboxSelected>>", cambiar_formato)

        def buscar_placa():
            """Lista con buscador de todas las placas ESP32 con WiFi del Arduino IDE (se leen de la carpeta, sin internet)."""
            todas = leer_placas_core()
            if not todas:
                messagebox.showinfo("Todas las placas", "Todavía no está instalado el soporte ESP32 en Dependencias_Ofline.\n\n"
                                    "Se baja solo la primera vez que abrís el programa (la ventana de verificación). "
                                    "Cuando termine, volvé a abrir esta ventana.", parent=w)
                return
            d = tk.Toplevel(w)
            d.title("🔍 Todas las placas ESP32 con WiFi")
            d.configure(bg="#f8f9fa")
            d.transient(w)
            d.grab_set()
            tk.Label(d, text="Escribí para buscar (igual que en el Arduino IDE):", bg="#f8f9fa", font=("Segoe UI", 9)).pack(padx=12, pady=(10, 2), anchor="w")
            vb = tk.StringVar()
            ent = tk.Entry(d, textvariable=vb, width=60)
            ent.pack(padx=12, fill="x")
            fl = tk.Frame(d, bg="#f8f9fa")
            fl.pack(padx=12, pady=6, fill="both", expand=True)
            sb = ttk.Scrollbar(fl, orient="vertical")
            lb = tk.Listbox(fl, height=16, width=64, yscrollcommand=sb.set, exportselection=False)
            sb.config(command=lb.yview)
            lb.pack(side="left", fill="both", expand=True)
            sb.pack(side="left", fill="y")
            visibles = []
            lbl_n = tk.Label(d, text="", bg="#f8f9fa", fg="#7f8c8d", font=("Segoe UI", 8))
            lbl_n.pack()

            def filtrar(*_):
                q = vb.get().strip().lower()
                lb.delete(0, "end")
                visibles.clear()
                for x in todas:
                    if not q or q in x["nombre"].lower() or q in x["mcu"] or q in x["id"].lower():
                        visibles.append(x)
                        lb.insert("end", f"{x['nombre']}   ·   {PERFILES_CHIP[x['mcu']]['chip']}")
                lbl_n.config(text=f"{len(visibles)} placas con WiFi (ESP32, S2, S3, C3 y C6)")
            vb.trace_add("write", filtrar)
            filtrar()

            def elegir(*_):
                sel = lb.curselection()
                if not sel:
                    return
                x = visibles[sel[0]]
                nombre = x["nombre"]
                if nombre in BOARDS and BOARDS[nombre]["fqbn"] != x["fqbn"]:
                    nombre = f"{nombre} [{x['id']}]"
                registrar_placa(nombre, x["fqbn"], x["mcu"])
                self.cfg.setdefault("placas_extra", {})[nombre] = {"fqbn": x["fqbn"], "mcu": x["mcu"], "formato": BOARDS[nombre]["formato"]}
                cbplaca.config(values=list(PLACAS.keys()))
                d.destroy()
                vplaca.set(nombre)
                cambiar_placa()
            lb.bind("<Double-Button-1>", elegir)
            bfd = tk.Frame(d, bg="#f8f9fa")
            bfd.pack(pady=(2, 10))
            tk.Button(bfd, text="✅ Usar esta placa", command=elegir, bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=18).pack(side="left", padx=4)
            tk.Button(bfd, text="Cancelar", command=d.destroy, width=10).pack(side="left", padx=4)
            ent.focus_set()
        tk.Button(fp, text="🔍 Todas las placas...", command=buscar_placa, font=("Segoe UI", 8)).pack(side="left", padx=4)
        dibujar()
        tk.Label(w, text="Nombre: elegí R1, R2... / E1, E2... del combo (los que ya usaste no aparecen) o escribí el tuyo; vacío = automático.  Columna ALTO/BAJO: en ENT es el nivel de ALARMA y en SAL el nivel que ACTIVA el relé (elegí uno por cada salida); Resistencia (solo ENT, se pone sola al revés de la alarma: ALTO→Pull-down, BAJO→Pull-up; podés cambiarla): Pull-up = reposo en ALTO (contacto a GND), Pull-down = reposo en BAJO (contacto a 3,3 V), Ninguna = flotante.",
                 font=("Segoe UI", 8), bg="#f8f9fa", fg="#7f8c8d", wraplength=900, justify="center").pack()
        tk.Label(w, text="Fijos (no se pueden usar): " + _bd["fijos"],
                 font=("Segoe UI", 8), bg="#f8f9fa", fg="#7f8c8d", wraplength=900, justify="center").pack()
        if _bd.get("aviso"):
            tk.Label(w, text="ℹ️ " + _bd["aviso"], font=("Segoe UI", 8), bg="#f8f9fa", fg="#2980b9",
                     wraplength=900, justify="center").pack()
        lbl = tk.Label(w, text="", bg="#f8f9fa", fg="#2c3e50", font=("Segoe UI", 9, "bold"))
        lbl.pack(pady=2)

        def leer():
            return {str(p): {"tipo": v[0].get(), "nombre": v[1].get().strip(), "alarma": v[2].get(),
                             "resistencia": RES_CLAVE.get(vres[p].get(), "PULLUP")} for p, v in vars_.items()}

        def actualizar(*_):
            lbl.config(text=resumen_pines(leer()))
        for v in vars_.values():
            for x in v:
                x.trace_add("write", actualizar)
        for x in vres.values():
            x.trace_add("write", actualizar)
        actualizar()

        def aceptar():
            p = leer()
            con_sensor = set(mapa_sensores())
            for k, dd in p.items():
                if dd["tipo"] == "SEN":
                    dd["nombre"] = ""
                    if int(k) not in con_sensor:
                        dd["tipo"] = "—"          # SEN sin sensor cargado: queda libre
            try:
                armar_pines(p)
                armar_sensores(dict(self.cfg, pines=p))        # que ningun pin de sensor quede usado como salida o entrada
            except ValueError as ex:
                messagebox.showerror("Pines", str(ex), parent=w)
                return
            # proteccion: no pisar sin querer los pines de otra placa (suele pasar si se editan antes de elegir el ESP32)
            nombre_ap = self._nombre_ap()
            previo = (self.cfg.get("perfiles") or {}).get(nombre_ap)
            if previo:
                try:
                    s0, e0, _ = armar_pines(previo.get("pines") or {})
                    s1, e1, _ = armar_pines(p)
                    if (len(s0), len(e0)) != (len(s1), len(e1)):
                        if not messagebox.askyesno(
                                "¿Son los pines de esta placa?",
                                f"Estás cambiando los pines de «{nombre_ap}»:\n\n"
                                f"   antes: {len(s0)} salidas y {len(e0)} entradas\n"
                                f"   ahora: {len(s1)} salidas y {len(e1)} entradas\n\n"
                                f"¿Son de «{nombre_ap}»?\nSi son de otra placa, tocá No, cerrá esta ventana y primero elegí el ESP32 en «ESP32 destino» (o escribí su nombre en «Red AP»).",
                                parent=w):
                            return
                except ValueError:
                    pass
            self.cfg["pines"] = p
            niv = [d["alarma"] for k, d in p.items() if d["tipo"] == "SAL" and k != str(LED_DEF)]
            self.cfg["rele_bajo"] = "BAJO" if niv and all(n == "BAJO" for n in niv) else "ALTO"
            self.cfg["placa"] = vplaca.get()
            self.guardar()
            self.lbl_pines.config(text=self._texto_pines())
            self.escribir_pines_txt(avisar=True)
            self.refrescar_botones()
            w.destroy()
        tk.Button(bf, text="✅ Aceptar", command=aceptar, bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=14).pack(side="left", padx=4)
        def valores_defecto():
            for pin, d in pines_defecto().items():
                if int(pin) in vars_ and int(pin) not in mapa_sensores():
                    vars_[int(pin)][0].set(d["tipo"]); vars_[int(pin)][1].set(""); vars_[int(pin)][2].set(d["alarma"]); vres[int(pin)].set(RES_ETIQ["PULLDOWN"])
        tk.Button(bf, text="↺ Valores por defecto", command=valores_defecto, width=18).pack(side="left", padx=4)

        def cancelar():
            for n in agregados:                    # los sensores creados desde esta ventana se descartan
                if n in (self.cfg.get("sensores") or []):
                    self.cfg["sensores"].remove(n)
            w.destroy()
        w.protocol("WM_DELETE_WINDOW", cancelar)
        tk.Button(bf, text="Cancelar", command=cancelar, width=10).pack(side="left", padx=4)
        w.update_idletasks()
        ajustar_lista()
        w.update_idletasks()
        x = self.v.winfo_rootx() + 20
        y = self.v.winfo_rooty() + 20
        # que la ventana quede entera dentro de la pantalla
        x = max(0, min(x, self.v.winfo_screenwidth() - w.winfo_reqwidth() - 10))
        y = max(0, min(y, self.v.winfo_screenheight() - w.winfo_reqheight() - 80))
        w.geometry(f"{w.winfo_reqwidth()}x{w.winfo_reqheight()}+{x}+{y}")
        w.deiconify()
        w.lift()
        w.focus_set()

    # ---------- Sensores, reglas, librerias y codigo propio ----------
    def _tras_cambio_config(self, aviso=None):
        """Despues de tocar sensores / reglas / codigo: guarda, actualiza el resumen y re-habilita los pasos."""
        self.guardar()
        self.lbl_pines.config(text=self._texto_pines())
        self.escribir_pines_txt()
        self.refrescar_botones()
        if aviso:
            self.escribir(aviso)

    def _centrar_sobre(self, w, padre):
        w.update_idletasks()
        x = padre.winfo_rootx() + 30
        y = padre.winfo_rooty() + 30
        x = max(0, min(x, w.winfo_screenwidth() - w.winfo_reqwidth() - 10))
        y = max(0, min(y, w.winfo_screenheight() - w.winfo_reqheight() - 60))
        w.geometry(f"+{x}+{y}")
        w.deiconify()
        w.lift()
        w.focus_set()

    def _dialogo_sensor(self, padre, actual, otros, pin_inicial=None, pines=None):
        """Formulario para crear o editar un sensor. Devuelve el dict o None si se cancela.
        pin_inicial: pin que ya se eligió en la ventana de pines. pines: estado de los pines (si todavía no se guardó)."""
        pines = pines or self.cfg["pines"]
        d = dict(actual) if actual else sensor_defecto("LDR" if (pin_inicial is None or pin_inicial in PINES_ANALOGICOS) else "DS18B20")
        if pin_inicial is not None and not actual:
            d["pin"] = pin_inicial
        w = tk.Toplevel(padre)
        w.withdraw()
        w.title("✏️ Sensor" if actual else "➕ Sensor nuevo")
        w.configure(bg="#f8f9fa")
        w.resizable(False, False)
        w.transient(padre)
        res = {"v": None}
        v_tipo = tk.StringVar(value=TIPOS_SENSOR.get(d["tipo"], TIPOS_SENSOR["LDR"]))
        v_nom = tk.StringVar(value=d.get("nombre", ""))
        v_pin = tk.StringVar(value=str(d.get("pin", "")) if d.get("pin") else "")
        v_amin = tk.StringVar(value=str(d.get("amin", "")))
        v_amax = tk.StringVar(value=str(d.get("amax", "")))
        v_inv = tk.BooleanVar(value=bool(d.get("invertir")))
        v_par = {k: tk.StringVar(value=str(d.get(k, ""))) for k in ("factor", "v0", "v1", "u0", "u1", "unidad", "dec")}
        fuente = ("Segoe UI", 9)
        f = tk.Frame(w, bg="#f8f9fa"); f.pack(padx=14, pady=(12, 4), fill="x")

        def fila(r, texto):
            tk.Label(f, text=texto, bg="#f8f9fa", font=fuente, anchor="w").grid(row=r, column=0, sticky="w", pady=2)
        fila(0, "Tipo de sensor")
        cb_tipo = ttk.Combobox(f, textvariable=v_tipo, values=list(TIPOS_SENSOR.values()), state="readonly", width=34)
        cb_tipo.grid(row=0, column=1, sticky="w", padx=6)
        fila(1, "Nombre")
        tk.Entry(f, textvariable=v_nom, width=20).grid(row=1, column=1, sticky="w", padx=6)
        fila(2, "Pin (GPIO)")
        cb_pin = ttk.Combobox(f, textvariable=v_pin, width=8, state="readonly")
        cb_pin.grid(row=2, column=1, sticky="w", padx=6)
        lbl_pin = tk.Label(f, text="", bg="#f8f9fa", fg="#7f8c8d", font=("Segoe UI", 8), anchor="w", justify="left", wraplength=330)
        lbl_pin.grid(row=3, column=0, columnspan=2, sticky="w")
        fp = tk.Frame(w, bg="#f8f9fa"); fp.pack(padx=14, pady=2, fill="x")
        fa = tk.Frame(w, bg="#f8f9fa"); fa.pack(padx=14, pady=2, fill="x")
        tk.Label(fa, text="Avisar si baja de", bg="#f8f9fa", font=fuente).pack(side="left")
        tk.Entry(fa, textvariable=v_amin, width=7).pack(side="left", padx=4)
        tk.Label(fa, text="o sube de", bg="#f8f9fa", font=fuente).pack(side="left")
        tk.Entry(fa, textvariable=v_amax, width=7).pack(side="left", padx=4)
        tk.Label(fa, text="(vacío = sin aviso)", bg="#f8f9fa", fg="#7f8c8d", font=("Segoe UI", 8)).pack(side="left")
        lbl_cable = tk.Label(w, text="", bg="#fff8e1", fg="#6d4c00", font=("Segoe UI", 8), justify="left", anchor="w",
                             wraplength=420, padx=8, pady=6)
        lbl_cable.pack(padx=14, pady=(6, 2), fill="x")
        lbl_err = tk.Label(w, text="", bg="#f8f9fa", fg="#c0392b", font=("Segoe UI", 9, "bold"), wraplength=420)
        lbl_err.pack()
        estado = {"tipo": d["tipo"]}

        def tipo_actual():
            return ETQ_A_TIPO.get(v_tipo.get(), "LDR")

        def armar_params(*_):
            for h in fp.winfo_children():
                h.destroy()
            t = tipo_actual()
            if t == "LDR":
                tk.Checkbutton(fp, text="Invertir (más luz = menos tensión, típico de los módulos de 4 pines)", variable=v_inv,
                               bg="#f8f9fa", font=fuente).grid(row=0, column=0, columnspan=6, sticky="w")
            elif t in ("PRES", "ANA"):
                filas = ([("Presión máxima del sensor", "u1"), ("Unidad", "unidad")] if t == "PRES"
                         else [("Valor con tensión mínima", "u0"), ("Valor con tensión máxima", "u1"), ("Unidad", "unidad")])
                r = 0
                for txt, k in filas:
                    tk.Label(fp, text=txt, bg="#f8f9fa", font=fuente).grid(row=r, column=0, sticky="w", pady=1)
                    if k == "unidad" and t == "PRES":
                        ttk.Combobox(fp, textvariable=v_par[k], values=UNIDADES_PRESION, width=8).grid(row=r, column=1, sticky="w", padx=6)
                    else:
                        tk.Entry(fp, textvariable=v_par[k], width=9).grid(row=r, column=1, sticky="w", padx=6)
                    r += 1
                for txt, k in (("Tensión mínima del sensor (V)", "v0"), ("Tensión máxima del sensor (V)", "v1"),
                               ("Divisor de tensión (1 = sin divisor)", "factor"), ("Decimales", "dec")):
                    tk.Label(fp, text=txt, bg="#f8f9fa", font=fuente).grid(row=r, column=0, sticky="w", pady=1)
                    tk.Entry(fp, textvariable=v_par[k], width=9).grid(row=r, column=1, sticky="w", padx=6)
                    r += 1
            lbl_cable.config(text=CABLEADO.get(t, ""))
            fa.pack_forget() if t == "PIR" else fa.pack(padx=14, pady=2, fill="x", before=lbl_cable)
            libs = LIBS_SENSOR.get(t)
            if libs:
                lbl_cable.config(text=CABLEADO.get(t, "") + "\nLibrerías (se instalan solas al grabar): " + ", ".join(libs))
            pins = pines_posibles_sensor(t, pines, otros)
            cb_pin.config(values=[str(p) for p in pins])
            if v_pin.get() not in [str(p) for p in pins]:
                v_pin.set(str(pins[0]) if pins else "")
            lbl_pin.config(text="" if pins else "⚠ No hay pines libres para este tipo: en «Configurar salidas, entradas y botón» liberá un pin (—).")
            if t in ("LDR", "PRES", "ANA", "PIR"):
                lbl_pin.config(text=(lbl_pin.cget("text") or "Pines libres que sirven para este sensor (los analógicos son solo los del grupo ADC1)."))

        def al_cambiar_tipo(*_):
            t = tipo_actual()
            if t != estado["tipo"]:
                prev_def = sensor_defecto(estado["tipo"])["nombre"]
                nuevo = sensor_defecto(t)
                if not v_nom.get().strip() or v_nom.get().strip() == prev_def:
                    v_nom.set(nuevo["nombre"])
                for k in v_par:
                    v_par[k].set(str(nuevo.get(k, "")))
                v_inv.set(False)
                estado["tipo"] = t
            armar_params()
        cb_tipo.bind("<<ComboboxSelected>>", al_cambiar_tipo)
        armar_params()

        def aceptar():
            t = tipo_actual()
            nuevo = {"tipo": t, "nombre": v_nom.get().strip(), "pin": v_pin.get(), "invertir": bool(v_inv.get()),
                     "amin": v_amin.get().strip().replace(",", "."), "amax": v_amax.get().strip().replace(",", ".")}
            for k in v_par:
                nuevo[k] = v_par[k].get().strip().replace(",", ".") if k != "unidad" else v_par[k].get().strip()
            try:
                armar_sensores({"pines": pines, "sensores": list(otros) + [nuevo]})
            except ValueError as ex:
                lbl_err.config(text=str(ex))
                return
            res["v"] = nuevo
            w.destroy()
        bf = tk.Frame(w, bg="#f8f9fa"); bf.pack(pady=(4, 12))
        tk.Button(bf, text="✅ Aceptar", command=aceptar, bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=12).pack(side="left", padx=4)
        tk.Button(bf, text="Cancelar", command=w.destroy, width=10).pack(side="left", padx=4)
        self._centrar_sobre(w, padre)
        w.grab_set()
        padre.wait_window(w)
        return res["v"]

    def _dialogo_regla(self, padre, actual, nombres_sensores, nombres_salidas, unidades, otras):
        """Formulario para crear o editar una regla automatica."""
        d = dict(actual) if actual else {"nombre": "", "sensor": nombres_sensores[0], "op": "<", "umbral": "20", "histeresis": "10",
                                         "salida": nombres_salidas[0], "prender": True, "retardo": "30", "duracion": "0"}
        w = tk.Toplevel(padre)
        w.withdraw()
        w.title("✏️ Regla automática" if actual else "➕ Regla automática nueva")
        w.configure(bg="#f8f9fa")
        w.resizable(False, False)
        w.transient(padre)
        res = {"v": None}
        v_nom = tk.StringVar(value=d.get("nombre", ""))
        v_sen = tk.StringVar(value=d.get("sensor", nombres_sensores[0]))
        v_op = tk.StringVar(value="menor que" if d.get("op") == "<" else "mayor que")
        v_um = tk.StringVar(value=str(d.get("umbral", "")))
        v_hi = tk.StringVar(value=str(d.get("histeresis", "")))
        v_sal = tk.StringVar(value=d.get("salida", nombres_salidas[0]))
        v_acc = tk.StringVar(value="Prender" if d.get("prender", True) else "Apagar")
        v_re = tk.StringVar(value=str(d.get("retardo", "")))
        v_du = tk.StringVar(value=str(d.get("duracion", "")))
        fuente = ("Segoe UI", 9)
        f = tk.Frame(w, bg="#f8f9fa"); f.pack(padx=14, pady=(12, 4), fill="x")

        def etq(r, c, t, **kw):
            tk.Label(f, text=t, bg="#f8f9fa", font=fuente, **kw).grid(row=r, column=c, sticky="w", pady=3)
        etq(0, 0, "Nombre de la regla")
        tk.Entry(f, textvariable=v_nom, width=22).grid(row=0, column=1, columnspan=3, sticky="w", padx=6)
        etq(1, 0, "CUANDO el sensor")
        ttk.Combobox(f, textvariable=v_sen, values=nombres_sensores, state="readonly", width=20).grid(row=1, column=1, columnspan=3, sticky="w", padx=6)
        etq(2, 0, "esté")
        ttk.Combobox(f, textvariable=v_op, values=["menor que", "mayor que"], state="readonly", width=10).grid(row=2, column=1, sticky="w", padx=6)
        tk.Entry(f, textvariable=v_um, width=8).grid(row=2, column=2, sticky="w")
        lbl_un = tk.Label(f, text="", bg="#f8f9fa", fg="#7f8c8d", font=fuente)
        lbl_un.grid(row=2, column=3, sticky="w", padx=4)
        etq(3, 0, "Margen para volver atrás")
        tk.Entry(f, textvariable=v_hi, width=8).grid(row=3, column=1, sticky="w", padx=6)
        tk.Label(f, text="(evita que parpadee cuando el valor está justo en el límite)", bg="#f8f9fa", fg="#7f8c8d",
                 font=("Segoe UI", 8)).grid(row=3, column=2, columnspan=2, sticky="w")
        etq(4, 0, "Esperar antes de actuar")
        tk.Entry(f, textvariable=v_re, width=8).grid(row=4, column=1, sticky="w", padx=6)
        tk.Label(f, text="segundos", bg="#f8f9fa", fg="#7f8c8d", font=fuente).grid(row=4, column=2, sticky="w")
        etq(5, 0, "ENTONCES")
        ttk.Combobox(f, textvariable=v_acc, values=["Prender", "Apagar"], state="readonly", width=10).grid(row=5, column=1, sticky="w", padx=6)
        ttk.Combobox(f, textvariable=v_sal, values=nombres_salidas, state="readonly", width=12).grid(row=5, column=2, columnspan=2, sticky="w")
        etq(6, 0, "Volver sola a los")
        tk.Entry(f, textvariable=v_du, width=8).grid(row=6, column=1, sticky="w", padx=6)
        tk.Label(f, text="segundos (0 = hace lo contrario cuando deja de cumplirse)", bg="#f8f9fa", fg="#7f8c8d",
                 font=("Segoe UI", 8)).grid(row=6, column=2, columnspan=2, sticky="w")
        tk.Label(w, text=("Ejemplos:\n"
                          "• Luz exterior de noche: sensor Luz, menor que 20, margen 10, esperar 60 → Prender el relé.\n"
                          "• Alarma: sensor Movimiento, mayor que 0,5, esperar 0, volver sola a los 60 → Prender la sirena.\n"
                          "• Ventilador por calor: sensor Temperatura, mayor que 30, margen 2 → Prender el relé.\n"
                          "La regla actúa solo cuando el valor cruza el límite: si prendés o apagás a mano desde la página, se respeta.\n"
                          "En la página aparece un interruptor «Automático» para activarla o desactivarla desde el celular."),
                 bg="#eaf2f8", fg="#1b4f72", font=("Segoe UI", 8), justify="left", anchor="w", wraplength=440, padx=8, pady=6
                 ).pack(padx=14, pady=(4, 2), fill="x")
        lbl_err = tk.Label(w, text="", bg="#f8f9fa", fg="#c0392b", font=("Segoe UI", 9, "bold"), wraplength=440)
        lbl_err.pack()

        def unidad(*_):
            u = unidades.get(v_sen.get(), "")
            lbl_un.config(text=u if u else ("(1 = movimiento)" if "mov" in v_sen.get().lower() else ""))
        v_sen.trace_add("write", unidad)
        unidad()

        def aceptar():
            nuevo = {"nombre": v_nom.get().strip(), "sensor": v_sen.get(), "op": "<" if v_op.get() == "menor que" else ">",
                     "umbral": v_um.get().strip().replace(",", "."), "histeresis": v_hi.get().strip().replace(",", ".") or "0",
                     "salida": v_sal.get(), "prender": v_acc.get() == "Prender",
                     "retardo": v_re.get().strip() or "0", "duracion": v_du.get().strip() or "0"}
            if not re.fullmatch(r"[\w ]{1,16}", nuevo["nombre"]):
                lbl_err.config(text="El nombre solo puede tener letras, números, espacios y _ (máximo 16).")
                return
            if nuevo["nombre"].lower() in {(o.get("nombre") or "").lower() for o in otras}:
                lbl_err.config(text="Ya hay otra regla con ese nombre.")
                return
            for k, nom in (("umbral", "el valor límite"), ("histeresis", "el margen"), ("retardo", "la espera"), ("duracion", "la duración")):
                try:
                    if float(nuevo[k]) < 0 and k != "umbral":
                        raise ValueError
                    float(nuevo[k])
                except ValueError:
                    lbl_err.config(text=f"Revisá {nom}: tiene que ser un número" + (" (no negativo)." if k != "umbral" else "."))
                    return
            res["v"] = nuevo
            w.destroy()
        bf = tk.Frame(w, bg="#f8f9fa"); bf.pack(pady=(4, 12))
        tk.Button(bf, text="✅ Aceptar", command=aceptar, bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=12).pack(side="left", padx=4)
        tk.Button(bf, text="Cancelar", command=w.destroy, width=10).pack(side="left", padx=4)
        self._centrar_sobre(w, padre)
        w.grab_set()
        padre.wait_window(w)
        return res["v"]

    def abrir_sensores(self):
        """Ventana con los sensores y las reglas automáticas de la placa elegida."""
        try:
            salidas = armar_pines(self.cfg["pines"])[0]
        except ValueError as ex:
            messagebox.showerror("Sensores", f"Primero arreglá los pines: {ex}", parent=self.v)
            return
        nombres_salidas = [n for _p, n, _c in salidas]
        sens = json.loads(json.dumps(self.cfg.get("sensores") or []))
        regs = json.loads(json.dumps(self.cfg.get("reglas") or []))
        w = tk.Toplevel(self.v)
        w.withdraw()
        w.title(f"📡 Sensores y reglas de {self._nombre_ap()}")
        w.configure(bg="#f8f9fa")
        w.resizable(False, False)
        w.transient(self.v)
        tk.Label(w, text=f"Sensores y reglas automáticas de «{self._nombre_ap()}»", font=("Segoe UI", 12, "bold"),
                 bg="#f8f9fa", fg="#2c3e50").pack(pady=(10, 0))
        tk.Label(w, text="Los sensores muestran su valor en la solapa «Sensores» de la página. Las reglas actúan solas en el ESP32 (aunque se caiga internet).",
                 font=("Segoe UI", 8), bg="#f8f9fa", fg="#7f8c8d", wraplength=560).pack()
        nb = ttk.Notebook(w)
        nb.pack(padx=12, pady=8, fill="both")
        t1 = tk.Frame(nb, bg="#f8f9fa"); nb.add(t1, text="📡 Sensores")
        t2 = tk.Frame(nb, bg="#f8f9fa"); nb.add(t2, text="⚙️ Reglas automáticas")

        def hacer_lista(padre, columnas):
            fr = tk.Frame(padre, bg="#f8f9fa"); fr.pack(padx=8, pady=8, fill="x")
            tv = ttk.Treeview(fr, columns=[c[0] for c in columnas], show="headings", height=8, selectmode="browse")
            for c, ancho in columnas:
                tv.heading(c, text=c)
                tv.column(c, width=ancho, anchor="w")
            tv.pack(side="left", fill="x")
            return fr, tv
        fr1, tv1 = hacer_lista(t1, [("Nombre", 130), ("Tipo", 190), ("Pin", 50), ("Avisos", 150)])
        fr2, tv2 = hacer_lista(t2, [("Nombre", 110), ("Condición", 190), ("Acción", 160), ("Opciones", 130)])

        def lecturas_actuales():
            try:
                return armar_sensores({"pines": self.cfg["pines"], "sensores": sens})
            except ValueError:
                return []

        def refrescar():
            tv1.delete(*tv1.get_children())
            for i, x in enumerate(sens):
                av = []
                if str(x.get("amin", "")).strip():
                    av.append(f"< {x['amin']}")
                if str(x.get("amax", "")).strip():
                    av.append(f"> {x['amax']}")
                tv1.insert("", "end", iid=str(i), values=(x.get("nombre"), TIPOS_SENSOR.get(x.get("tipo"), "?"), f"GPIO {x.get('pin')}", "  ".join(av) or "—"))
            tv2.delete(*tv2.get_children())
            uni = {l["nombre"]: l["unidad"] for l in lecturas_actuales()}
            for i, g in enumerate(regs):
                cond = f"{g.get('sensor')} {'<' if g.get('op') == '<' else '>'} {g.get('umbral')} {uni.get(g.get('sensor'), '')}".strip()
                acc = f"{'Prender' if g.get('prender', True) else 'Apagar'} {g.get('salida')}"
                op = f"espera {g.get('retardo')} s" + (f" · dura {g.get('duracion')} s" if float(g.get('duracion') or 0) > 0 else "")
                tv2.insert("", "end", iid=str(i), values=(g.get("nombre"), cond, acc, op))

        def elegido(tv):
            s_ = tv.selection()
            return int(s_[0]) if s_ else None

        def sensor_agregar():
            n = self._dialogo_sensor(w, None, sens)
            if n:
                sens.append(n)
                refrescar()

        def sensor_editar():
            i = elegido(tv1)
            if i is None:
                return
            otros = [x for k, x in enumerate(sens) if k != i]
            n = self._dialogo_sensor(w, sens[i], otros)
            if n:
                viejo = sens[i]["nombre"]
                sens[i] = n
                if viejo != n["nombre"]:            # las reglas siguen al sensor aunque cambie de nombre
                    for g in regs:
                        if g.get("sensor") == viejo:
                            g["sensor"] = n["nombre"]
                        elif g.get("sensor", "").startswith(viejo + " ") and n["tipo"] in ("DHT22", "DHT11"):
                            g["sensor"] = n["nombre"] + g["sensor"][len(viejo):]
                refrescar()

        def sensor_quitar():
            i = elegido(tv1)
            if i is None:
                return
            nom = sens[i]["nombre"]
            usan = [g for g in regs if g.get("sensor", "") == nom or g.get("sensor", "").startswith(nom + " ")]
            if usan and not messagebox.askyesno("Quitar sensor", f"«{nom}» lo usan {len(usan)} regla(s). También se quitan esas reglas. ¿Seguir?", parent=w):
                return
            for g in usan:
                regs.remove(g)
            sens.pop(i)
            refrescar()

        def regla_agregar():
            nombres = [l["nombre"] for l in lecturas_actuales()]
            if not nombres:
                messagebox.showinfo("Reglas", "Primero agregá un sensor en la solapa «Sensores».", parent=w)
                return
            uni = {l["nombre"]: l["unidad"] for l in lecturas_actuales()}
            n = self._dialogo_regla(w, None, nombres, nombres_salidas, uni, regs)
            if n:
                regs.append(n)
                refrescar()

        def regla_editar():
            i = elegido(tv2)
            if i is None:
                return
            nombres = [l["nombre"] for l in lecturas_actuales()]
            uni = {l["nombre"]: l["unidad"] for l in lecturas_actuales()}
            otras = [g for k, g in enumerate(regs) if k != i]
            n = self._dialogo_regla(w, regs[i], nombres, nombres_salidas, uni, otras)
            if n:
                regs[i] = n
                refrescar()

        def regla_quitar():
            i = elegido(tv2)
            if i is not None:
                regs.pop(i)
                refrescar()

        for fr, a, e, q in ((fr1, sensor_agregar, sensor_editar, sensor_quitar), (fr2, regla_agregar, regla_editar, regla_quitar)):
            col = tk.Frame(fr, bg="#f8f9fa"); col.pack(side="left", padx=8, anchor="n")
            tk.Button(col, text="➕ Agregar", command=a, width=11).pack(pady=2)
            tk.Button(col, text="✏️ Editar", command=e, width=11).pack(pady=2)
            tk.Button(col, text="🗑 Quitar", command=q, width=11).pack(pady=2)
        tv1.bind("<Double-1>", lambda _e: sensor_editar())
        tv2.bind("<Double-1>", lambda _e: regla_editar())
        tk.Label(t1, text="Pines analógicos (luz, presión): 32, 33, 34, 35, 36, 39. Los pines que uses para sensores tienen que estar en — en la ventana de pines.",
                 font=("Segoe UI", 8), bg="#f8f9fa", fg="#7f8c8d", wraplength=560, justify="left").pack(padx=8, pady=(0, 6), anchor="w")
        tk.Label(t2, text="Cada regla agrega en la página un interruptor «Automático» para activarla o desactivarla.",
                 font=("Segoe UI", 8), bg="#f8f9fa", fg="#7f8c8d", wraplength=560, justify="left").pack(padx=8, pady=(0, 6), anchor="w")
        refrescar()

        def aceptar():
            cand = dict(self.cfg)
            cand["sensores"] = sens
            cand["reglas"] = regs
            try:
                lec = armar_sensores(cand)
                armar_reglas(cand, lec, salidas)
            except ValueError as ex:
                messagebox.showerror("Sensores y reglas", str(ex), parent=w)
                return
            self.cfg["sensores"] = sens
            self.cfg["reglas"] = regs
            nuevas = [l for l in libs_necesarias(self.cfg)]
            w.destroy()
            self._tras_cambio_config(f"📡 Sensores y reglas guardados ({resumen_sensores(self.cfg)}). "
                                     f"Para que la placa los use: ⚡ HACER TODO (o crear y grabar). Librerías necesarias: {', '.join(nuevas)}.")
        bf = tk.Frame(w, bg="#f8f9fa"); bf.pack(pady=(2, 12))
        tk.Button(bf, text="✅ Aceptar", command=aceptar, bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=14).pack(side="left", padx=4)
        tk.Button(bf, text="Cancelar", command=w.destroy, width=10).pack(side="left", padx=4)
        self._centrar_sobre(w, self.v)

    def abrir_codigo(self, padre=None):
        """Código propio: líneas que se agregan al sketch (para módulos que no están en el catálogo)."""
        padre = padre or self.v
        ex = dict(self.cfg.get("codigo_extra") or {})
        w = tk.Toplevel(padre)
        w.withdraw()
        w.title(f"🧩 Código propio de {self._nombre_ap()}")
        w.configure(bg="#f8f9fa")
        w.transient(padre)
        tk.Label(w, text="Código propio (para módulos que no están en el catálogo)", font=("Segoe UI", 12, "bold"),
                 bg="#f8f9fa", fg="#2c3e50").pack(pady=(10, 0))
        tk.Label(w, text=("Se agrega al sketch de «" + self._nombre_ap() + "». Pegá lo que trae el ejemplo del módulo. "
                          "Podés usar: ponerLuz(n, true/false) para las salidas, sensorVal[n] y sensorOk[n] para las lecturas, "
                          "Serial.println() para ver mensajes. La librería se instala en «📚 Librerías»."),
                 font=("Segoe UI", 8), bg="#f8f9fa", fg="#7f8c8d", wraplength=620, justify="left").pack(padx=12)
        cajas = {}
        for clave, titulo, alto in (("includes", "1) #include de la librería (una por línea, ej.: #include <Adafruit_BMP280.h>)", 3),
                                    ("globales", "2) Variables y funciones propias (opcional)", 5),
                                    ("setup", "3) Va dentro de setup() (se ejecuta una vez al encender)", 4),
                                    ("loop", "4) Va dentro de loop() (se repite todo el tiempo; no uses delay largos)", 5)):
            tk.Label(w, text=titulo, bg="#f8f9fa", font=("Segoe UI", 9, "bold"), anchor="w").pack(padx=12, pady=(6, 0), anchor="w")
            fr = tk.Frame(w, bg="#f8f9fa"); fr.pack(padx=12, fill="x")
            t = tk.Text(fr, height=alto, width=86, font=("Consolas", 9), wrap="none", undo=True)
            sb = ttk.Scrollbar(fr, orient="vertical", command=t.yview)
            t.config(yscrollcommand=sb.set)
            t.pack(side="left", fill="x")
            sb.pack(side="left", fill="y")
            t.insert("1.0", ex.get(clave, ""))
            cajas[clave] = t

        def aceptar():
            nuevo = {k: t.get("1.0", "end").rstrip() for k, t in cajas.items()}
            if nuevo["includes"] and any(l.strip() and not l.strip().startswith("#include") for l in nuevo["includes"].splitlines()):
                messagebox.showerror("Código propio", "En el cuadro 1 solo puede haber líneas #include.", parent=w)
                return
            self.cfg["codigo_extra"] = {k: v for k, v in nuevo.items() if v}
            w.destroy()
            self._tras_cambio_config("🧩 Código propio guardado. Se agrega al sketch la próxima vez que lo grabes.")
        bf = tk.Frame(w, bg="#f8f9fa"); bf.pack(pady=(8, 12))
        tk.Button(bf, text="✅ Aceptar", command=aceptar, bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=14).pack(side="left", padx=4)
        tk.Button(bf, text="Cancelar", command=w.destroy, width=10).pack(side="left", padx=4)
        self._centrar_sobre(w, padre)

    def abrir_librerias(self):
        """Buscar, instalar y quitar librerías de Arduino (se guardan en Dependencias_Ofline)."""
        w = tk.Toplevel(self.v)
        w.withdraw()
        w.title("📚 Librerías de Arduino")
        w.configure(bg="#f8f9fa")
        w.transient(self.v)
        tk.Label(w, text="Librerías de Arduino", font=("Segoe UI", 12, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(pady=(10, 0))
        tk.Label(w, text=("Si comprás un módulo nuevo, buscá acá su librería (el nombre figura en la hoja del módulo o en su ejemplo) e instalala. "
                          "Se guarda en Dependencias_Ofline. Para usarla en el sketch: «🧩 Código propio»."),
                 font=("Segoe UI", 8), bg="#f8f9fa", fg="#7f8c8d", wraplength=600, justify="left").pack(padx=12)
        tk.Label(w, text="📁 Se guardan en: " + os.path.dirname(carpeta_libs()), font=("Segoe UI", 8), bg="#f8f9fa", fg="#27ae60",
                 wraplength=600, justify="left").pack(padx=12, anchor="w")
        v_q = tk.StringVar()
        fb = tk.Frame(w, bg="#f8f9fa"); fb.pack(padx=12, pady=6, fill="x")
        e = tk.Entry(fb, textvariable=v_q, width=40)
        e.pack(side="left")
        lbl = tk.Label(w, text="", bg="#f8f9fa", fg="#2c3e50", font=("Segoe UI", 9), wraplength=600, justify="left")
        cuerpo = tk.Frame(w, bg="#f8f9fa"); cuerpo.pack(padx=12, pady=4, fill="x")
        izq = tk.Frame(cuerpo, bg="#f8f9fa"); izq.pack(side="left", padx=(0, 10))
        der = tk.Frame(cuerpo, bg="#f8f9fa"); der.pack(side="left")
        tk.Label(izq, text="Resultados de la búsqueda", bg="#f8f9fa", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        lb_res = tk.Listbox(izq, width=46, height=12, exportselection=False)
        lb_res.pack()
        tk.Label(der, text="Instaladas", bg="#f8f9fa", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        lb_ins = tk.Listbox(der, width=40, height=12, exportselection=False)
        lb_ins.pack()
        estado = {"res": [], "ins": []}

        def msg(t, color="#2c3e50"):
            self.ui(lambda: lbl.config(text=t, fg=color))

        def cli_o_aviso():
            c = buscar_cli()
            if not c:
                msg("⚠ Todavía no hay arduino-cli: cerrá y abrí el programa (se descarga solo) o usá «Preparar ESP32».", "#c0392b")
            return c

        def cargar_instaladas():
            def tarea():
                c = cli_o_aviso()
                if not c:
                    return
                _, txt = self.ejecutar(f'"{c}" lib list --format json', mostrar=False, timeout=90)
                lista = []
                try:
                    dd = json.loads(txt[txt.index("{"):] if "{" in txt else txt)
                    items = dd.get("installed_libraries", dd) if isinstance(dd, dict) else dd
                    for it in items or []:
                        lib = it.get("library", it) if isinstance(it, dict) else {}
                        if lib.get("name"):
                            lista.append((lib["name"], lib.get("version", "")))
                except Exception:
                    pass
                lista.sort(key=lambda x: x[0].lower())
                estado["ins"] = lista

                def f():
                    lb_ins.delete(0, "end")
                    for n, v in lista:
                        lb_ins.insert("end", f"{n}  {v}")
                self.ui(f)
            threading.Thread(target=tarea, daemon=True).start()

        def buscar():
            q = v_q.get().strip()
            if not q:
                return
            msg("🔎 Buscando...")

            def tarea():
                c = cli_o_aviso()
                if not c:
                    return
                cod, txt = self.ejecutar(f'"{c}" lib search "{q}" --format json', mostrar=False, timeout=120)
                lista = []
                try:
                    dd = json.loads(txt[txt.index("{"):])
                    for it in dd.get("libraries", []):
                        lat = it.get("latest") or {}
                        lista.append((it.get("name", ""), lat.get("sentence", "")))
                except Exception:
                    pass
                lista = [x for x in lista if x[0]][:60]
                estado["res"] = lista

                def f():
                    lb_res.delete(0, "end")
                    for n, s_ in lista:
                        lb_res.insert("end", n)
                    lbl.config(text=(f"{len(lista)} resultado(s). Elegí uno y tocá «Instalar»." if lista else
                                     "No encontré nada (¿hay internet? probá con otra palabra, en inglés suele funcionar mejor)."),
                               fg="#2c3e50" if lista else "#c0392b")
                self.ui(f)
            threading.Thread(target=tarea, daemon=True).start()

        def instalar(nombre=None):
            if nombre is None:
                sel = lb_res.curselection()
                nombre = estado["res"][sel[0]][0] if sel else v_q.get().strip()
            if not nombre:
                return
            msg(f"⬇ Instalando «{nombre}»...")

            def tarea():
                c = cli_o_aviso()
                if not c:
                    return
                cod, txt = self.ejecutar(f'"{c}" lib install "{nombre}"', mostrar=False, timeout=300)
                if cod == 0:
                    extra = self.cfg.setdefault("librerias_extra", [])
                    if nombre not in extra and nombre not in libs_necesarias({"sensores": self.cfg.get("sensores")}):
                        extra.append(nombre)
                    self.ui(lambda: guardar_config(self.cfg))
                    msg(f"✅ «{nombre}» instalada.", "#27ae60")
                    cargar_instaladas()
                else:
                    msg("❌ No se pudo instalar: " + (txt.strip().splitlines()[-1] if txt.strip() else "sin detalle"), "#c0392b")
            threading.Thread(target=tarea, daemon=True).start()

        def instalar_zip():
            ruta = filedialog.askopenfilename(parent=w, title="Librería en ZIP", filetypes=[("Librería ZIP", "*.zip")])
            if not ruta:
                return
            msg("⬇ Instalando desde el ZIP...")

            def tarea():
                c = cli_o_aviso()
                if not c:
                    return
                os.environ["ARDUINO_LIBRARY_ENABLE_UNSAFE_INSTALL"] = "true"
                try:
                    antes = set(os.listdir(carpeta_libs()))
                except OSError:
                    antes = set()
                cod, txt = self.ejecutar(f'"{c}" lib install --zip-path "{ruta}"', mostrar=False, timeout=300)
                if cod == 0:
                    try:
                        nuevas = sorted(set(os.listdir(carpeta_libs())) - antes)
                        os.makedirs(DEPS_ZIPS, exist_ok=True)
                        copia = os.path.basename(ruta)
                        shutil.copy2(ruta, os.path.join(DEPS_ZIPS, copia))      # queda guardado el ZIP en Dependencias_Ofline
                        reg = [z for z in (self.cfg.get("librerias_zip") or []) if z.get("zip") != copia]
                        reg.append({"zip": copia, "nombre": (nuevas[0] if nuevas else os.path.splitext(copia)[0]).replace("_", " ")})
                        self.cfg["librerias_zip"] = reg
                        self.ui(lambda: guardar_config(self.cfg))
                    except OSError:
                        pass
                    msg("✅ Librería instalada desde el ZIP y guardada en Dependencias_Ofline.", "#27ae60")
                    cargar_instaladas()
                else:
                    msg("❌ No se pudo instalar el ZIP: " + (txt.strip().splitlines()[-1] if txt.strip() else "sin detalle"), "#c0392b")
            threading.Thread(target=tarea, daemon=True).start()

        def quitar():
            sel = lb_ins.curselection()
            if not sel:
                return
            nombre = estado["ins"][sel[0]][0]
            if nombre in libs_necesarias({"sensores": self.cfg.get("sensores")}):
                messagebox.showinfo("Librerías", f"«{nombre}» la necesita el programa o uno de tus sensores: no se puede quitar.", parent=w)
                return
            if not messagebox.askyesno("Quitar librería", f"¿Quitar «{nombre}»?", parent=w):
                return
            msg(f"🗑 Quitando «{nombre}»...")

            def tarea():
                c = cli_o_aviso()
                if not c:
                    return
                cod, _ = self.ejecutar(f'"{c}" lib uninstall "{nombre}"', mostrar=False, timeout=120)
                if cod == 0:
                    ex = self.cfg.get("librerias_extra") or []
                    if nombre in ex:
                        ex.remove(nombre)
                        self.ui(lambda: guardar_config(self.cfg))
                    msg(f"✅ «{nombre}» quitada.", "#27ae60")
                    cargar_instaladas()
                else:
                    msg("❌ No se pudo quitar.", "#c0392b")
            threading.Thread(target=tarea, daemon=True).start()

        tk.Button(fb, text="🔎 Buscar", command=buscar, width=10).pack(side="left", padx=4)
        tk.Button(fb, text="⬇ Instalar", command=instalar, bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=11).pack(side="left", padx=2)
        e.bind("<Return>", lambda _e: buscar())
        lb_res.bind("<Double-1>", lambda _e: instalar())
        lbl.pack(padx=12, anchor="w")
        bf = tk.Frame(w, bg="#f8f9fa"); bf.pack(pady=(4, 12))
        def cargar_en_placa():
            sel = lb_ins.curselection()
            if not sel:
                msg("Elegí una librería de la lista «Instaladas».", "#c0392b")
                return
            nombre = estado["ins"][sel[0]][0]
            heads = cabeceras_libreria(nombre)
            if not heads:
                msg(f"No encontré el archivo .h de «{nombre}»: agregalo a mano en «Código propio».", "#c0392b")
                return
            ex = dict(self.cfg.get("codigo_extra") or {})
            lineas = [l for l in (ex.get("includes") or "").splitlines() if l.strip()]
            nuevas = [f"#include <{h}>" for h in heads if f"#include <{h}>" not in lineas]
            ex["includes"] = "\n".join(lineas + nuevas)
            self.cfg["codigo_extra"] = {k: v for k, v in ex.items() if v}
            self._tras_cambio_config(f"📥 Librería {nombre} cargada en {self._nombre_ap()}: " + (", ".join(nuevas) if nuevas else "ya estaba incluida")
                                     + ". Para usarla, escribí su código en «Código propio» y grabá la placa.")
            msg(f"✅ «{nombre}» cargada en {self._nombre_ap()} ({', '.join(heads)}). Se abre «Código propio» para que sigas.", "#27ae60")
            self.abrir_codigo(w)
        tk.Button(bf, text="📥 Cargar en esta placa", command=cargar_en_placa, bg="#2980b9", fg="white",
                  font=("Segoe UI", 9, "bold"), width=22).pack(side="left", padx=4)
        tk.Button(bf, text="🗑 Quitar la elegida", command=quitar, width=18).pack(side="left", padx=4)
        tk.Button(bf, text="📦 Instalar desde ZIP...", command=instalar_zip, width=20).pack(side="left", padx=4)
        tk.Button(bf, text="🧩 Código propio...", command=lambda: self.abrir_codigo(w), width=18).pack(side="left", padx=4)
        tk.Button(bf, text="Cerrar", command=w.destroy, width=10).pack(side="left", padx=4)
        self._centrar_sobre(w, self.v)
        cargar_instaladas()

    def crear_todo(self, directo=False):
        """Crea .ino + .gs + .html desde las plantillas y les aplica contraseña, WiFi, AP, pines y URL."""
        if self.ocupado:
            return False
        self.guardar()
        if not self.clave_valida():
            return False
        if not self.var_clave.get():
            messagebox.showerror("Contraseña", "Escribí la contraseña web.")
            return False
        if not self.var_ssid.get():
            messagebox.showerror("WiFi", "Escribí el nombre de tu WiFi.")
            return False
        try:
            armar_pines(self.cfg["pines"])
        except ValueError as ex:
            messagebox.showerror("Pines", str(ex))
            return False
        carpeta = self.cfg["carpeta"]
        existen = [n for n in ("Codigo.gs", "Pagina.html", ARCHIVO_INO) if os.path.isfile(os.path.join(carpeta, n))]
        forzar = False
        if existen and not directo:
            r = messagebox.askyesnocancel("Archivos existentes", "En la carpeta ya están:\n" + "\n".join(existen) +
                                          "\n\n¿Reemplazarlos por archivos nuevos desde cero?\nSí = reemplazar   No = solo completar los que faltan y actualizar los datos")
            if r is None:
                return False
            forzar = r
        try:
            creados = asegurar_archivos(carpeta, forzar)
            self.escribir("🆕 Creados: " + (", ".join(creados) if creados else "ninguno (ya existían)"))
            self.escribir_ino()
            self.aplicar_gs(carpeta)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False
        self.escribir(f"✅ Listo en {carpeta}: .ino, .gs y .html con tus datos ({resumen_pines(self.cfg['pines'])}).")
        self.marcar("archivos", self.firma("arch"))
        self.set_estado("✅ Archivos creados. Ahora ⬆️ cargá al ESP32 y 🚀 subí al script.")
        return True

    def aplicar_gs(self, carpeta):
        """Pone contraseña y nombres de salidas/entradas en Codigo.gs (y Codigo_gs.txt si existe)."""
        for nombre in ("Codigo.gs", "Codigo_gs.txt"):
            ruta = os.path.join(carpeta, nombre)
            if not os.path.isfile(ruta):
                continue
            with open(ruta, "r", encoding="utf-8") as f:
                t = f.read()
            t = generar_gs(t, self.cfg)
            with open(ruta, "w", encoding="utf-8", newline="") as f:
                f.write(t)

    def _plantillas(self, carpeta):
        """Crea los archivos que falten y pasa a la version nueva los que sean de una version vieja."""
        creados = asegurar_archivos(carpeta)
        if creados:
            self.escribir("🆕 Archivos creados o actualizados: " + ", ".join(creados))

    def escribir_ino(self):
        ruta = os.path.join(self.cfg["carpeta"], ARCHIVO_INO)
        with open(ruta, "r", encoding="utf-8") as f:
            t = f.read()
        url = f'https://script.google.com/macros/s/{self.cfg["deployment_id"]}/exec'
        t = generar_ino(t, self.cfg, url)
        with open(ruta, "w", encoding="utf-8", newline="") as f:
            f.write(t)

    # ---------- Arduino / ESP32 ----------
    def obtener_cli(self):
        """Devuelve la ruta de arduino-cli; si no existe, la descarga (copia propia junto al programa)."""
        cli = buscar_cli()
        if cli:
            return cli
        self.set_estado("⬇️ Descargando arduino-cli (herramienta oficial de Arduino)...")
        try:
            zpath = os.path.join(tempfile.gettempdir(), "arduino-cli.zip")
            self.escribir("Descargando " + URL_CLI)
            urllib.request.urlretrieve(URL_CLI, zpath)
            destino = DEPS_CLI
            os.makedirs(destino, exist_ok=True)
            with zipfile.ZipFile(zpath) as z:
                z.extract("arduino-cli.exe", destino)
            os.remove(zpath)
        except Exception as e:
            self.escribir(f"ERROR descargando arduino-cli: {e}")
            return None
        return buscar_cli()

    def vigilar_puertos(self):
        """Mira cada segundo los puertos COM: al conectar el ESP32 lo elige solo; al sacarlo avisa."""
        ahora = puertos_com()
        if ahora is not None:
            prev = self._pc_prev
            actual = self.var_puerto.get().strip()
            if prev is None:
                if actual not in ahora and ahora:
                    self.var_puerto.set(ahora[-1])
            elif set(ahora) != set(prev):
                nuevos = [c for c in ahora if c not in prev]
                if not self.ocupado:
                    if nuevos:
                        self.var_puerto.set(nuevos[-1])
                        self.estado.config(text=f"🔌 ESP32 detectado en {nuevos[-1]}")
                    elif actual and actual not in ahora:
                        self.var_puerto.set(ahora[-1] if ahora else "")
                        self.estado.config(text=f"🔌 Se desconectó {actual}")
            self._pc_prev = ahora
            self.cb_puerto.config(values=ahora)
            actual = self.var_puerto.get().strip()
            if actual and actual in ahora:
                self.lbl_puerto.config(text=f"🔌 ESP32 detectado en {actual}", fg="#27ae60")
            else:
                self.lbl_puerto.config(text="⚠️ No se ve ningún ESP32: conectalo por USB", fg="#c0392b")
        self.v.after(1000, self.vigilar_puertos)

    def buscar_puertos(self):
        ahora = puertos_com()
        if ahora is not None:
            self._pc_prev = ahora
            self.cb_puerto.config(values=ahora)
            if ahora and self.var_puerto.get().strip() not in ahora:
                self.var_puerto.set(ahora[-1])
            return

        def tarea():
            cli = buscar_cli()
            if not cli:
                return
            cod, txt = self.ejecutar(f'"{cli}" board list --format json', mostrar=False)
            puertos = parsear_puertos(txt) if cod == 0 else []
            def f():
                self.cb_puerto.config(values=puertos)
                if puertos and self.var_puerto.get() not in puertos:
                    self.var_puerto.set(puertos[0])
            self.ui(f)
        threading.Thread(target=tarea, daemon=True).start()

    def _preparar(self):
        """Instala arduino-cli, el soporte ESP32 y las librerias. Corre dentro del hilo de trabajo. True si quedo listo."""
        cli = self.obtener_cli()
        if not cli:
            self.set_estado("❌ No se pudo conseguir arduino-cli (ver registro)")
            return False
        R = self._rangos
        _, txt = self.ejecutar(f'"{cli}" core list --format json', mostrar=False, timeout=60)
        ver = version_nucleo(txt)
        if ver:
            # ya esta instalado: no hace falta bajar el indice (evita esperas si internet o el Arduino IDE lo traban)
            self.escribir(f"✅ El soporte ESP32 ya está instalado (versión {ver}); no se toca.")
            self.fase(*R["idx"], "fijo")
            self.fase_fin()
            self.fase(*R["core"], "fijo")
            self.fase_fin()
        else:
            self.set_estado("⚙️ Actualizando índice de placas (si se queda aquí, cerrá el Arduino IDE y reintentá)...")
            self.fase(*R["idx"], "tiempo", T=4)
            cod, _ = self.ejecutar(f'"{cli}" core update-index --additional-urls {URL_ESP32}', timeout=180)
            if cod != 0:
                self.set_estado("❌ Falló el índice de placas: revisá internet y cerrá el Arduino IDE si está abierto")
                return False
            self.fase_fin()
            self.set_estado(f"⚙️ Instalando soporte ESP32 {NUCLEO_PROBADO} (tarda varios minutos, es grande)...")
            self.fase(*R["core"], "paquetes", total=22)
            cod, _ = self.ejecutar(f'"{cli}" core install esp32:esp32@{NUCLEO_PROBADO} --additional-urls {URL_ESP32}')
            if cod != 0:
                self.set_estado("❌ Falló la instalación del soporte ESP32 (ver registro)")
                return False
            self.fase_fin()
        self.fase(*R["lib"], "tiempo", T=6)
        _, lista = self.ejecutar(f'"{cli}" lib list --format json', mostrar=False, timeout=60)
        restaurar_zips(self.cfg, cli, self.escribir)
        lista = (lista or "").lower()
        for lib in libs_necesarias(self.cfg):
            # primero se mira sin internet: carpeta de bibliotecas de Arduino o lista de arduino-cli
            carpeta_lib = os.path.join(os.environ.get("ARDUINO_DIRECTORIES_USER")
                                       or os.path.join(os.path.expanduser("~"), "Documents", "Arduino"),
                                       "libraries", lib.replace(" ", "_"))
            if os.path.isdir(carpeta_lib) or lib.lower() in lista:
                self.escribir(f"✅ La librería {lib} ya estaba instalada.")
                continue
            self.set_estado(f"⚙️ Instalando librería {lib} (si se queda aquí, cerrá el Arduino IDE y reintentá)...")
            cod, txt = self.ejecutar(f'"{cli}" lib install "{lib}"', timeout=180)
            ya = ("ya existe" in txt.lower()) or ("already exists" in txt.lower())
            if ya:
                self.escribir(f"✅ La librería {lib} ya estaba instalada.")
            elif cod != 0:
                self.set_estado(f"❌ Falló la librería {lib}: revisá internet y cerrá el Arduino IDE si está abierto")
                return False
        self.fase_fin()
        self.ui(lambda: self.marcar("arduino", True))
        return True

    def cargar_esp32(self, directo=False, sin_preguntas=False, al_fin=None):
        """directo=True: lo usa «Renombrar»; no hace preguntas intermedias. Devuelve True si arrancó la tarea."""
        if self.ocupado:
            return False
        if self.var_wifi.get() and not directo:
            # Grabar por WiFi: si el nombre de «Red AP» es distinto al del ESP32 elegido, se lo está RENOMBRANDO.
            # Antes se pisaba el nombre sin avisar y no se podía cambiar; ahora se pregunta.
            m = re.match(r"^(.*?)\s+\(\d{1,3}(?:\.\d{1,3}){3}\)\s*$", self.var_host.get().strip())
            actual_esp = m.group(1) if m else ""
            nuevo_nombre = self.var_apssid.get().strip()
            if actual_esp and nuevo_nombre and nuevo_nombre != actual_esp:
                if not messagebox.askyesno("Cambiar el nombre del ESP32",
                        f"Este ESP32 se llama «{actual_esp}» y en «Red AP (nombre)» pusiste «{nuevo_nombre}».\n\n"
                        f"Si seguís, al grabarlo pasará a llamarse «{nuevo_nombre}» (en la página aparecerá con ese nombre y quedará como una placa nueva; la vieja «{actual_esp}» se puede quitar desde la página).\n\n"
                        f"¿Grabar con el nombre nuevo?\n\n(Si fue un descuido, tocá «No» y elegí de nuevo el ESP32 en la lista.)"):
                    return False
        self.guardar()
        puerto = self.var_puerto.get().strip()
        por_wifi = bool(self.var_wifi.get())
        host = self._destino_wifi()
        if por_wifi:
            if len(self.cb_host.cget("values")) > 1 and not self.var_host.get().strip():
                messagebox.showerror("ESP32 destino", "Hay varios ESP32 en la red: elegí a cuál grabar en la lista «ESP32 destino».")
                return False
            puerto = host
            if not (directo or sin_preguntas):
                vpn = vpn_activa()
                if vpn and not messagebox.askyesno("VPN activa", "Hay una VPN activa:\n\n   " + "\n   ".join(vpn) +
                                                   "\n\nCon la VPN prendida suele fallar la grabación por WiFi (el tráfico no llega al ESP32).\n"
                                                   "Conviene apagarla.\n\n¿Querés intentar igual?"):
                    return False
            elif vpn_activa():
                self.escribir("🛡️ Ojo: hay una VPN activa; si falla la grabación por WiFi, apagala y reintentá.")
        elif not puerto:
            messagebox.showerror("Puerto", "Conectá el ESP32 por USB (se detecta solo) o tildá «Grabar por WiFi».")
            return False
        if not self.clave_valida():
            return False
        if not self.var_ssid.get():
            messagebox.showerror("WiFi", "Escribí el nombre de tu WiFi.")
            return False
        carpeta = self.cfg["carpeta"]
        self._plantillas(carpeta)
        try:
            armar_pines(self.cfg["pines"])
        except ValueError as ex:
            messagebox.showerror("Pines", str(ex))
            return False
        if not por_wifi and not directo:
            self._evitar_nombre_repetido()
            if self.cancelado_nombre:
                return False
        sig_ino = self.firma("ino")
        primera = not (self.cfg.get("hechos") or {}).get("arduino")
        aviso = "Primero se prepara Arduino (soporte ESP32 y librerías: la primera vez tarda varios minutos).\n" if primera else ""
        if not (directo or sin_preguntas) and not messagebox.askyesno("Preparar y cargar", f"{aviso}Se va a actualizar el .ino con tus datos ({resumen_pines(self.cfg['pines'])}), compilarlo y grabarlo en el ESP32 {'por WiFi (' + puerto + ')' if por_wifi else 'por ' + puerto}.\n¿Seguimos?"):
            return False

        def tarea():
            self.set_ocupado(True)
            self.modo_pct(True)
            exito = False
            self._rangos = ({"idx": (0, 3), "core": (3, 58), "lib": (58, 62), "comp": (62, 85), "up": (85, 100)} if primera
                            else {"comp": (0, 55), "up": (55, 100)})
            try:
                if primera and not self._preparar():
                    return
                cli = self.obtener_cli()
                if not cli:
                    self.set_estado("❌ No se pudo conseguir arduino-cli (ver registro)")
                    return
                try:
                    self.escribir_ino()
                    self.escribir(f"✅ {ARCHIVO_INO} actualizado")
                except Exception as e:
                    self.escribir(f"ERROR: {e}")
                    self.set_estado("❌ No se pudo preparar el .ino (ver registro)")
                    return
                # Arduino exige que la carpeta se llame igual que el .ino: se arma una temporal con ese nombre
                # La carpeta de compilacion es SIEMPRE la misma: asi Arduino reutiliza lo ya compilado y
                # las veces siguientes tarda segundos en vez de minutos.
                base = os.path.join(tempfile.gettempdir(), "luces_esp32_build")
                sk = os.path.join(base, "luces_esp32_google_lcd")
                obj = os.path.join(base, "obj")
                os.makedirs(sk, exist_ok=True)
                os.makedirs(obj, exist_ok=True)
                shutil.copy2(os.path.join(carpeta, ARCHIVO_INO), os.path.join(sk, ARCHIVO_INO))
                self.set_estado("🔨 Compilando (la primera vez tarda unos minutos)...")
                self.fase(*self._rangos["comp"], "tiempo", T=150)
                self.escribir("ℹ️ Compilar no muestra avance: la primera vez puede tardar de 3 a 10 minutos. Cada 20 segundos aparece un aviso de que sigue vivo.")
                cod, _ = self.ejecutar(f'"{cli}" compile --fqbn {FQBN} --build-path "{obj}" "{sk}"', latido="Compilando")
                if cod != 0:
                    _, txt = self.ejecutar(f'"{cli}" core list --format json', mostrar=False)
                    ver = version_nucleo(txt)
                    if ver and ver != NUCLEO_PROBADO:
                        self.escribir(f"El soporte ESP32 instalado es {ver}; el sketch se probó con {NUCLEO_PROBADO}. Pruebo con esa versión...")
                        self.set_estado(f"⚙️ Instalando soporte ESP32 {NUCLEO_PROBADO} y reintentando...")
                        c2, _ = self.ejecutar(f'"{cli}" core install esp32:esp32@{NUCLEO_PROBADO} --additional-urls {URL_ESP32}')
                        if c2 == 0:
                            self.set_estado("🔨 Compilando de nuevo...")
                            cod, _ = self.ejecutar(f'"{cli}" compile --fqbn {FQBN} --build-path "{obj}" "{sk}"', latido="Compilando")
                if cod != 0:
                    self.set_estado("❌ Falló la compilación (ver registro). Si falta una librería, tocá ↺ Reactivar pasos y repetí el ⑤.")
                    return
                self.fase_fin()
                self.escribir("✅ Compilación terminada.")
                self.fase(*self._rangos["up"], "subida")
                self.set_estado("⬆️ Grabando en el ESP32... si aparece 'Connecting......' apretá y mantené BOOT hasta que empiece a grabar")
                destino = puerto
                extra = ""
                if por_wifi:
                    import socket
                    try:
                        destino = socket.gethostbyname(puerto)
                        self.escribir(f"📶 {puerto} → {destino}")
                    except OSError:
                        self.escribir(f"❌ No encuentro «{puerto}» en la red. El ESP32 debe tener ya el programa v15 (grabado una vez por USB), estar encendido y en el mismo WiFi. Probá escribiendo su IP (se ve en la pantalla LCD).")
                        self.set_estado("❌ No se encontró el ESP32 en la red")
                        return
                    extra = f' --protocol network --upload-field password="{self.var_clave.get()}"'
                while True:
                    cod, txt = self.ejecutar(f'"{cli}" upload -p {destino}{extra} --fqbn {FQBN} --input-dir "{obj}" "{sk}"')
                    if cod == 0:
                        break
                    if por_wifi:
                        self.escribir("Falló la grabación por WiFi. Revisá que sea la misma red, que el ESP32 ya tenga el programa v15 y la contraseña web; si no, usá el cable USB.")
                        self.set_estado("❌ Falló la grabación por WiFi (ver registro)")
                        return
                    if (not self.cancelado) and ("boot mode" in txt.lower() or "failed to connect" in txt.lower()) and self.preguntar_reintento():
                        self.set_estado("⬆️ Reintentando la grabación (sin volver a compilar)...")
                        continue
                    self.escribir("Si dice 'Connecting......' y falla: mantené apretado el botón BOOT del ESP32 mientras graba, y revisá que el cable USB sea de datos.")
                    self.set_estado("❌ Falló la grabación (ver registro)")
                    return
                self.fase_fin()
                exito = True
                self.set_estado("✅ ESP32 grabado. Tocá 🚀 Subir y publicar si cambiaste pines o contraseña.")
                self.ui(lambda: self.marcar("cargado", sig_ino))
                self.escribir("✅ Listo: el ESP32 ya tiene el programa nuevo.")
                if getattr(self, "_renombrando_de", None):
                    self.ui(self._fin_renombrar)
            except Exception:
                self.escribir("❌ Error inesperado:\n" + traceback.format_exc())
                self.set_estado("❌ Error inesperado (ver registro)")
            finally:
                self.modo_pct(False, final=exito)
                if not exito and getattr(self, "_renombrando_de", None):
                    self.ui(self._deshacer_renombrar)
                self.set_ocupado(False)
                self.buscar_puertos()
                if al_fin:
                    self.ui(lambda: al_fin(exito))
        threading.Thread(target=tarea, daemon=True).start()
        return True

    # ---------- un solo boton: ③ archivos, ④ subir y publicar, ⑤ compilar y grabar ----------
    def hacer_todo(self):
        """Hace en orden los pasos 3, 4 y 5 que todavia falten; si algo falla, se detiene."""
        if self.ocupado:
            return
        if not (self.req_ok and self.login_ok):
            messagebox.showwarning("Hacer todo", "Primero hacé el paso ① (instalar lo que falta) y el ② (conectar con Google).")
            return
        self.guardar()
        carpeta = self.var_carpeta.get().strip()

        def hecho(n):
            h = self.cfg.get("hechos") or {}
            if n == 3:
                return (all(os.path.isfile(os.path.join(carpeta, x)) for x in ("Codigo.gs", "Pagina.html", ARCHIVO_INO))
                        and h.get("archivos") == self.firma("arch"))
            if n == 4:
                return h.get("subido") == self.firma("gs")
            return h.get("cargado") == self.firma("ino")
        nombres = {3: "③ crear/actualizar los archivos", 4: "④ subir y publicar el script en Google",
                   5: "⑤ compilar y grabar el ESP32 (" + ("por WiFi" if self.var_wifi.get() else "por cable USB") + ")"}
        forzar = all(hecho(n) for n in (3, 4, 5))
        if forzar:
            if not messagebox.askyesno("Hacer todo", "Todo está al día (no cambió nada desde la última vez).\n\n¿Repetir igual los 3 pasos?"):
                return
            lista = [3, 4, 5]
        else:
            lista = [n for n in (3, 4, 5) if not hecho(n)]
            if not messagebox.askyesno("Hacer todo", "Se van a hacer, en orden y sin más preguntas:\n\n" +
                                       "\n".join(nombres[n] for n in lista) + "\n\nSi un paso falla, se detiene.\n¿Empezamos?"):
                return

        def fin(ok):
            if ok:
                self.escribir("🎉 Listo: todo hecho.")
                self.set_estado("🎉 Todo listo")
            else:
                self.escribir("⛔ Se detuvo en el paso ⑤ (ver registro).")

        def paso5():
            if 5 in lista:
                self.escribir("▶ Paso ⑤: compilar y grabar el ESP32...")
                if not self.cargar_esp32(sin_preguntas=True, al_fin=fin):
                    self.escribir("⛔ Se detuvo en el paso ⑤.")
            else:
                fin(True)

        def tras4(ok):
            if ok:
                paso5()
            else:
                self.escribir("⛔ Se detuvo en el paso ④ (ver registro).")

        def paso4():
            if 4 in lista:
                self.escribir("▶ Paso ④: subir y publicar el script...")
                if not self.subir(directo=True, al_fin=tras4):
                    self.escribir("⛔ Se detuvo en el paso ④.")
            else:
                paso5()

        if 3 in lista:
            self.escribir("▶ Paso ③: archivos...")
            if not self.crear_todo(directo=True):
                self.escribir("⛔ Se detuvo en el paso ③.")
                return
        paso4()

    # ---------- renombrar un ESP32 (todo automatico) ----------
    def renombrar(self):
        """Pide el nombre nuevo y hace todo solo: cambia «Red AP», genera el .ino, compila y graba (WiFi o USB)."""
        if self.ocupado:
            return
        from tkinter import simpledialog
        por_wifi = bool(self.var_wifi.get())
        m = re.match(r"^(.*?)\s+\(\d{1,3}(?:\.\d{1,3}){3}\)\s*$", self.var_host.get().strip())
        if por_wifi:
            if m and m.group(1):
                actual = m.group(1)
            elif len(self.cb_host.cget("values")) > 1:
                messagebox.showerror("Renombrar", "Hay varios ESP32 en la red: primero elegí cuál en la lista «ESP32 destino».")
                return
            else:
                messagebox.showerror("Renombrar", "Primero tocá «🔎 Buscar» para encontrar el ESP32 en la red (o destildá «Grabar por WiFi» y usá el cable USB).")
                return
            donde = "por WiFi (sin cable)"
        else:
            if not self.var_puerto.get().strip():
                messagebox.showerror("Renombrar", "Conectá el ESP32 por USB (se detecta solo) o tildá «Grabar por WiFi» y elegí el ESP32.")
                return
            actual = self._nombre_ap()
            donde = f"por cable USB ({self.var_puerto.get().strip()})"
        nuevo = simpledialog.askstring(
            "✏️ Renombrar ESP32",
            f"ESP32 actual: «{actual}»  ·  se graba {donde}\n\n"
            f"Escribí el nombre NUEVO (letras, números, - o _; sin espacios; hasta 24).\n"
            f"Al aceptar se hace todo solo: cambia el nombre, compila y graba.",
            parent=self.v, initialvalue=actual)
        if nuevo is None:
            return
        nuevo = nuevo.strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,24}", nuevo):
            messagebox.showerror("Renombrar", "El nombre solo puede tener letras sin tilde, números, guion (-) o guion bajo (_), sin espacios, hasta 24 caracteres.")
            return
        if nuevo == actual:
            messagebox.showinfo("Renombrar", f"Ya se llama «{nuevo}». No hay nada que cambiar.")
            return
        self.set_estado("🔎 Comprobando que el nombre no esté usado en la red...")
        self.v.update_idletasks()
        try:
            usados = [n for n, _ in buscar_esp32_ota(2.5)]
        except Exception:
            usados = []
        self.set_estado("Listo.")
        if nuevo.lower() in {u.lower() for u in usados}:
            messagebox.showerror("Renombrar", f"Ya hay un ESP32 llamado «{nuevo}» en la red.\nElegí otro nombre.")
            return
        self._renombrando_de = actual
        self.escribir(f"✏️ Renombrando «{actual}» → «{nuevo}»...")
        self.var_apssid.set(nuevo)
        if not self.cargar_esp32(directo=True):
            self._deshacer_renombrar()

    def _fin_renombrar(self):
        viejo = getattr(self, "_renombrando_de", None)
        self._renombrando_de = None
        if not viejo:
            return
        nuevo = self._nombre_ap()
        if viejo != nuevo:
            (self.cfg.get("perfiles") or {}).pop(viejo, None)
            self.guardar()
        self.var_host.set("")
        self.escribir(f"✅ Listo: «{viejo}» ahora se llama «{nuevo}». En la página va a aparecer con el nombre nuevo; "
                      f"la vieja «{viejo}» queda hasta que la quites con «Quitar esta placa».")
        self.v.after(9000, lambda: self.comprobar_ota(silencioso=True))

    def _deshacer_renombrar(self):
        viejo = getattr(self, "_renombrando_de", None)
        self._renombrando_de = None
        if not viejo:
            return
        nuevo = self._nombre_ap()
        if nuevo != viejo:
            (self.cfg.get("perfiles") or {}).pop(nuevo, None)
            self.var_apssid.set(viejo)
            self.guardar()
        self.escribir(f"↩️ No se pudo renombrar: el ESP32 sigue llamándose «{viejo}».")

    def preguntar_reintento(self):
        """Pregunta (desde el hilo de trabajo) si reintenta la grabacion. True = reintentar."""
        listo = threading.Event()
        res = [False]

        def f():
            try:
                res[0] = messagebox.askretrycancel(
                    "La placa no entró en modo de grabación",
                    "El ESP32 no entró en modo de grabación.\n\n"
                    "1) Tocá Reintentar.\n"
                    "2) Cuando aparezcan los puntitos verdes en el registro, apretá y mantené el botón BOOT del ESP32.\n"
                    "3) Si hace falta, tocá una vez EN (reset) sin soltar BOOT.\n"
                    "4) Soltá BOOT cuando empiece a grabar.\n\n"
                    "No se vuelve a compilar: va directo a grabar.", parent=self.v)
            finally:
                listo.set()
        self.ui(f)
        listo.wait()
        return res[0]

    def crear_ino(self):
        if self.ocupado:
            return
        self.guardar()
        if not self.clave_valida():
            return
        if not self.var_ssid.get():
            messagebox.showerror("WiFi", "Escribí el nombre de tu WiFi.")
            return
        carpeta = self.cfg["carpeta"]
        ruta = os.path.join(carpeta, ARCHIVO_INO)
        self._plantillas(carpeta)
        if not messagebox.askyesno("Crear .ino", f"Se van a poner en {ARCHIVO_INO} la contraseña, el WiFi, el AP, el enlace del script y los pines elegidos.\n({resumen_pines(self.cfg['pines'])})\n¿Seguimos?"):
            return
        try:
            self.escribir_ino()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.escribir(f"✅ {ARCHIVO_INO} actualizado: contraseña, WiFi, AP y pines listos.")
        self.set_estado("✅ .ino creado. Ahora 🚀 Subir y publicar (para que el script tenga los mismos nombres) y cargá el .ino al ESP32.")
        if messagebox.askyesno("Listo", "El .ino quedó listo.\nRecordá tocar también 🚀 Subir y publicar para que la página tenga las mismas salidas y entradas.\n¿Abro la carpeta para abrir el .ino con el Arduino IDE?"):
            try:
                os.startfile(carpeta)
            except Exception:
                pass

    def crear_script_nuevo(self):
        """Crea un proyecto NUEVO en script.google.com con el nombre elegido (no toca los que ya tenés)."""
        if self.ocupado:
            return
        self.guardar()
        nombre = self.var_nombre.get().strip()
        if not nombre or not re.fullmatch(r"[\w .\-]{1,60}", nombre):
            messagebox.showerror("Nombre", "Escribí un nombre para el script nuevo (letras, números, espacios, guiones; máximo 60).")
            return
        if not shutil.which("clasp"):
            messagebox.showwarning("Falta clasp", "Primero tocá Instalar lo que falta.")
            return
        if self.var_clave.get() and not self.clave_valida():
            return
        try:
            armar_pines(self.cfg["pines"])
        except ValueError as ex:
            messagebox.showerror("Pines", str(ex))
            return
        carpeta = self.cfg["carpeta"]
        if not messagebox.askyesno("Crear script nuevo", f"Se va a crear un proyecto NUEVO en tu cuenta de Google llamado:\n\n   {nombre}\n\ny se le van a subir Codigo.gs y Pagina.html. Tus otros scripts (por ejemplo 'Mi Casa') no se tocan.\n\nDespués este programa pasa a usar el nuevo.\n¿Seguimos?"):
            return

        def tarea():
            self.set_ocupado(True)
            tmp = tempfile.mkdtemp(prefix="nuevo_apps_script_")
            try:
                self._plantillas(carpeta)
                self.aplicar_gs(carpeta)
                for a in ARCHIVOS:
                    shutil.copy2(os.path.join(carpeta, a), os.path.join(tmp, a))
                with open(os.path.join(tmp, "appsscript.json"), "w", encoding="utf-8") as f:
                    json.dump(MANIFIESTO, f, indent=2)
                self.set_estado("🆕 Creando el proyecto en Google...")
                ruta_clasp = os.path.join(tmp, ".clasp.json")
                cod, ultimo = 1, ""
                # Segun la version de clasp el comando se llama create o create-script, y el tipo puede variar
                for cmd in (f'clasp create --type webapp --title "{nombre}" --rootDir .',
                            f'clasp create-script --type standalone --title "{nombre}" --rootDir .',
                            f'clasp create --type standalone --title "{nombre}" --rootDir .'):
                    cod, ultimo = self.ejecutar(cmd, cwd=tmp)
                    if cod == 0 and os.path.isfile(ruta_clasp):
                        break
                    self.escribir("⚠️ Ese comando no funcionó, pruebo otra forma...")
                if cod != 0 or not os.path.isfile(ruta_clasp):
                    self.set_estado("❌ No se pudo crear el proyecto (ver registro). ¿Activaste la API de Apps Script?")
                    self.ofrecer_api(ultimo)
                    resumen = "\n".join((ultimo or "").strip().splitlines()[-6:])
                    if "Apps Script API" not in (ultimo or ""):
                      self.ui(lambda: messagebox.showerror("No se creó el script nuevo",
                            "Google no creó el proyecto, así que NO se tocó ningún script existente.\n\nÚltimo mensaje de clasp:\n" + resumen))
                    return
                with open(ruta_clasp, "r", encoding="utf-8") as f:
                    nuevo_id = json.load(f)["scriptId"]
                # clasp create puede traer su propio appsscript.json: se vuelve a poner el nuestro
                with open(os.path.join(tmp, "appsscript.json"), "w", encoding="utf-8") as f:
                    json.dump(MANIFIESTO, f, indent=2)
                self.set_estado("⬆️ Subiendo archivos al proyecto nuevo...")
                cod, _ = self.ejecutar("clasp push --force", cwd=tmp)
                if cod != 0:
                    self.set_estado("❌ El proyecto se creó pero falló la subida (ver registro)")
                    return
                # Se guarda ya el ID del script nuevo (y se borra el de la implementación vieja, que ya no sirve)
                def guardar_ids():
                    self.var_script.set(nuevo_id)
                    self.var_deploy.set("")
                    self.guardar()
                self.ui(guardar_ids)
                self.set_estado("📢 Publicando la aplicación web...")
                cod, txt = self.ejecutar(f'clasp deploy -d "{nombre}"', cwd=tmp)
                m = re.search(r"(AKfy[\w-]{20,})", txt or "")
                if not m:
                    # Algunas versiones de clasp no imprimen el ID al desplegar: se lo pide a la lista de implementaciones
                    _, lista = self.ejecutar("clasp deployments", cwd=tmp)
                    ids = re.findall(r"(AKfy[\w-]{20,})", lista or "")
                    m = re.search(r"(AKfy[\w-]{20,})", ids[-1]) if ids else None
                if not m:
                    self.set_estado("❌ El script se creó y se subió, pero falló la publicación (ver registro)")
                    resumen = "\n".join(((txt or "").strip().splitlines())[-6:])
                    self.ui(lambda: messagebox.showerror("Falló la publicación",
                            "El script nuevo se creó y tiene el código, pero Google no lo publicó como aplicación web.\n\nÚltimo mensaje de clasp:\n" + resumen))
                    return
                dep = m.group(1)
                def f():
                    self.var_deploy.set(dep)
                    self.guardar()
                    self.cfg.setdefault("hechos", {})["nombre_creado"] = nombre
                    self.marcar("subido", self.firma("gs"))
                self.ui(f)
                url = f"https://script.google.com/macros/s/{dep}/exec"
                self.escribir(f"✅ Script '{nombre}' creado y publicado.")
                self.escribir("URL: " + url)
                self.escribir("Abrí esa URL UNA vez en el navegador y aceptá los permisos de Google (primera vez del script nuevo).")
                self.escribir("Después tocá ⬆️ Crear .ino y cargar al ESP32 (el .ino usa el enlace nuevo).")
                self.set_estado("✅ Script nuevo listo. Abrí la URL una vez y aceptá permisos; luego cargá el ESP32.")
            except Exception as e:
                self.escribir(f"ERROR: {e}")
                self.set_estado("❌ Error inesperado (ver registro)")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
                self.set_ocupado(False)
        threading.Thread(target=tarea, daemon=True).start()

    def subir(self, directo=False, al_fin=None):
        if self.ocupado:
            return False
        self.guardar()
        carpeta = self.cfg["carpeta"]
        self._plantillas(carpeta)
        if not self.cfg["script_id"] or not self.cfg["deployment_id"]:
            messagebox.showerror("Faltan datos", "Completá el ID del script y el ID de la implementación.")
            return False
        if not shutil.which("clasp"):
            messagebox.showwarning("Falta clasp", "Primero tocá Instalar lo que falta.")
            return False
        if self.var_clave.get() and not self.clave_valida():
            return False
        try:
            armar_pines(self.cfg["pines"])
        except ValueError as ex:
            messagebox.showerror("Pines", str(ex))
            return False
        sig_gs = self.firma("gs")
        nom = self.var_nombre.get().strip()
        if nom and "nombre_creado" not in (self.cfg.get("hechos") or {}):
            # configuracion sin ese dato (por ejemplo copiada o de una version anterior): se toma el nombre actual
            # como el del script que ya existe, para no avisar de «pisar un script» sin motivo
            self.cfg.setdefault("hechos", {})["nombre_creado"] = nom
            guardar_config(self.cfg)
        if nom and nom != (self.cfg.get("hechos") or {}).get("nombre_creado"):
            if not messagebox.askyesno("⚠️ Vas a pisar un script existente",
                                       f"Todavía NO creaste en Google un script llamado '{nom}'.\n\n"
                                       f"Si seguís, se REEMPLAZA el código del script que ya existe (ID {self.var_script.get().strip()[:12]}...), "
                                       f"por ejemplo 'Mi Casa'.\n\nPara no pisarlo, cancelá y tocá '🆕 Crear script NUEVO con ese nombre'.\n\n¿Reemplazar igual?"):
                return False
        if not directo and not messagebox.askyesno("Confirmar", "Se va a reemplazar el código del script en Google por el de la carpeta y publicar una versión nueva.\n¿Seguimos?"):
            return False

        def tarea():
            self.set_ocupado(True)
            tmp = tempfile.mkdtemp(prefix="subir_apps_script_")
            ok = False
            try:
                self.aplicar_gs(carpeta)
                self.escribir("🔐 Contraseña y nombres de salidas/entradas puestos en Codigo.gs")
                # Se trabaja en una carpeta temporal: la tuya no se toca ni se llena de archivos.
                for a in ARCHIVOS:
                    shutil.copy2(os.path.join(carpeta, a), os.path.join(tmp, a))
                with open(os.path.join(tmp, "appsscript.json"), "w", encoding="utf-8") as f:
                    json.dump(MANIFIESTO, f, indent=2)
                with open(os.path.join(tmp, ".clasp.json"), "w", encoding="utf-8") as f:
                    json.dump({"scriptId": self.cfg["script_id"], "rootDir": "."}, f)

                self.set_estado("⬆️ Subiendo archivos...")
                cod, txt_push = self.ejecutar("clasp push --force", cwd=tmp)
                if cod != 0:
                    self.ofrecer_api(txt_push)
                    self.set_estado("❌ Falló la subida. ¿Activaste la API de Apps Script? (ver registro)")
                    self.escribir("Si dice 'User has not enabled the Apps Script API', activala en https://script.google.com/home/usersettings")
                    return

                self.set_estado("📢 Publicando versión nueva...")
                cod, _ = self.ejecutar(f'clasp deploy -i {self.cfg["deployment_id"]} -d "Subido desde el programa"', cwd=tmp)
                if cod != 0:
                    self.set_estado("❌ Subido, pero falló la publicación (ver registro)")
                    return
                url = f'https://script.google.com/macros/s/{self.cfg["deployment_id"]}/exec'
                self.escribir("✅ Listo. La URL no cambió: " + url)
                self.ui(lambda: self.marcar("subido", sig_gs))
                self.set_estado("✅ Subido y publicado en la misma URL")
                ok = True
            except Exception as e:
                self.escribir(f"ERROR: {e}")
                self.set_estado("❌ Error inesperado (ver registro)")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
                self.set_ocupado(False)
                if al_fin:
                    self.ui(lambda: al_fin(ok))
        threading.Thread(target=tarea, daemon=True).start()
        return True

    def cerrar(self):
        if self.ocupado:
            if not messagebox.askyesno("Hay una tarea en curso", "Se está compilando o grabando.\n¿Querés cancelarla y cerrar el programa?", parent=self.v):
                return
        matar_arbol(self.proc_actual)
        matar_huerfanos()
        self.guardar()
        self.v.destroy()

    def _centrar_ventana(self):
        """Pone la ventana centrada SIN fijarle un tamaño: crece sola con el contenido y nunca se corta."""
        self.v.update_idletasks()
        w, h = self.v.winfo_reqwidth(), self.v.winfo_reqheight()
        x = max(0, (self.v.winfo_screenwidth() - w) // 2)
        y = max(0, (self.v.winfo_screenheight() - h) // 2 - 20)
        self.v.geometry(f"+{x}+{y}")

    def _ajustar_ventana(self):
        """Si el contenido creció y la ventana quedó fuera de la pantalla, la corre para que se vea entera."""
        try:
            self.v.geometry("")                 # vuelve a tamaño automático (se ajusta al contenido)
            self.v.update_idletasks()
            w, h = self.v.winfo_reqwidth(), self.v.winfo_reqheight()
            x, y = self.v.winfo_x(), self.v.winfo_y()
            nx = max(0, min(x, self.v.winfo_screenwidth() - w - 10))
            ny = max(0, min(y, self.v.winfo_screenheight() - h - 60))
            if (nx, ny) != (x, y):
                self.v.geometry(f"+{nx}+{ny}")
        except tk.TclError:
            pass

    def correr(self):
        for a in AVISOS_DEPS:
            self.v.after(300, lambda t=a: self.escribir(t))
        self.v.mainloop()


# ---------- Plantillas de los 3 archivos (guardadas dentro del programa) ----------
_PLANTILLAS = {
    "Codigo.gs": """
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
""",
    "Pagina.html": """
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
""",
    "luces_esp32_google_lcd.ino": """
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
""",
}


def plantilla(nombre):
    import base64, zlib
    return zlib.decompress(base64.b64decode("".join(_PLANTILLAS[nombre].split()))).decode("utf-8")


MARCAS_PLANTILLA = {"Codigo.gs": "PLANTILLA_MULTI v18", "Pagina.html": "PLANTILLA_MULTI v19",
                    ARCHIVO_INO: "PLANTILLA_MULTI v19"}
MARCA_PLANTILLA = "PLANTILLA_MULTI v19"


def asegurar_archivos(carpeta, forzar=False):
    """Crea los archivos que falten (o todos si forzar=True). Devuelve la lista de los creados."""
    os.makedirs(carpeta, exist_ok=True)
    creados = []
    for nombre in ("Codigo.gs", "Pagina.html", ARCHIVO_INO):
        ruta = os.path.join(carpeta, nombre)
        viejo = False
        if os.path.isfile(ruta) and not forzar:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    viejo = MARCAS_PLANTILLA[nombre] not in f.read(400)
            except OSError:
                viejo = False
            if viejo:
                # archivo de una version anterior (una sola placa): se guarda copia y se pasa a la nueva
                try:
                    shutil.copy2(ruta, ruta + ".version_vieja")
                except OSError:
                    pass
        if forzar or viejo or not os.path.isfile(ruta):
            with open(ruta, "w", encoding="utf-8", newline="") as f:
                f.write(plantilla(nombre))
            creados.append(nombre + (" (actualizado a la versión nueva, copia en .version_vieja)" if viejo else ""))
    return creados


# ---------- Ventana de verificación de dependencias (se muestra al iniciar) ----------
# Lista de (nombre, módulo) que ESTE programa necesita de Python. Solo usa la biblioteca estándar;
# tkinter es lo único que puede faltar según cómo se instaló Python. Node.js y clasp no son
# librerías pip: van como filas extra con su propio botón de instalación automática.
DEPENDENCIAS = [("tkinter", "tkinter")]

def instalar_node_simple():
    """Node.js: primero la versión portátil en Dependencias_Ofline; si falla, winget o el instalador oficial."""
    if descargar_node_portatil():
        return True
    if shutil.which("winget"):
        subprocess.run("winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements",
                       shell=True, creationflags=CREAR_SIN_VENTANA)
        asegurar_path()
        if shutil.which("node"):
            return True
    try:
        with urllib.request.urlopen("https://nodejs.org/dist/index.json", timeout=30) as r:
            lista = json.loads(r.read().decode("utf-8"))
        ver = next(x["version"] for x in lista if x.get("lts"))
        destino = os.path.join(tempfile.gettempdir(), f"node-{ver}-x64.msi")
        urllib.request.urlretrieve(f"https://nodejs.org/dist/{ver}/node-{ver}-x64.msi", destino)
        subprocess.run(f'msiexec /i "{destino}" /passive /norestart', shell=True, creationflags=CREAR_SIN_VENTANA)
        try:
            os.remove(destino)
        except Exception:
            pass
    except Exception:
        pass
    asegurar_path()
    return bool(shutil.which("node"))


def descargar_cli_simple():
    """Baja solo arduino-cli (sin el Arduino IDE completo) a una carpeta junto al programa."""
    try:
        zpath = os.path.join(tempfile.gettempdir(), "arduino-cli.zip")
        urllib.request.urlretrieve(URL_CLI, zpath)
        destino = DEPS_CLI
        os.makedirs(destino, exist_ok=True)
        with zipfile.ZipFile(zpath) as z:
            z.extract("arduino-cli.exe", destino)
        os.remove(zpath)
    except Exception:
        pass
    return cli_en_deps() or bool(buscar_cli())


def _soporte_esp32_en_carpeta():
    """True si el soporte ESP32 ya está en Dependencias_Ofline\\arduino\\data (se mira la carpeta, es instantáneo)."""
    base = os.path.join(DEPS_ARDUINO, "data", "packages", "esp32", "hardware", "esp32")
    try:
        for v in os.listdir(base):
            d = os.path.join(base, v)
            if os.path.isfile(os.path.join(d, "boards.txt")) and os.path.isfile(os.path.join(d, "platform.txt")):
                herr = os.path.join(DEPS_ARDUINO, "data", "packages", "esp32", "tools")
                return os.path.isdir(herr)
    except OSError:
        pass
    return False


def _libs_en_carpeta():
    base = os.path.join(DEPS_ARDUINO, "user", "libraries")
    try:
        hay = {n.lower().replace("_", " ").replace("-", " ") for n in os.listdir(base)}
    except OSError:
        return False
    return all(l.lower().replace("_", " ").replace("-", " ") in hay for l in LIBRERIAS)


def estado_arduino(cli):
    """(soporte ESP32 instalado, librerías instaladas) mirando las carpetas de Dependencias_Ofline (rápido, sin
    internet). Solo si no se ve nada se consulta al arduino-cli como respaldo (leyendo únicamente su salida normal)."""
    core = _soporte_esp32_en_carpeta()
    libs = _libs_en_carpeta()
    if cli and not (core and libs):
        try:
            if not core:
                r = subprocess.run([cli, "core", "list", "--format", "json"], capture_output=True, text=True, timeout=30,
                                   creationflags=CREAR_SIN_VENTANA)
                core = bool(version_nucleo(r.stdout or ""))
            if not libs:
                r = subprocess.run([cli, "lib", "list", "--format", "json"], capture_output=True, text=True, timeout=30,
                                   creationflags=CREAR_SIN_VENTANA)
                txt = (r.stdout or "").lower()
                libs = all(lib.lower() in txt for lib in LIBRERIAS)
        except Exception:
            pass
    return core, libs


def descargar_arduino_simple(cli, core_ok, libs_ok, estado=None):
    """Baja el soporte ESP32 y las librerías de Arduino a Dependencias_Ofline (lo que falte)."""
    def decir(t):
        if estado:
            estado(t)
    try:
        if not core_ok:
            decir("core")
            subprocess.run([cli, "core", "update-index", "--additional-urls", URL_ESP32], capture_output=True, timeout=300,
                           creationflags=CREAR_SIN_VENTANA)
            subprocess.run([cli, "core", "install", f"esp32:esp32@{NUCLEO_PROBADO}", "--additional-urls", URL_ESP32],
                           capture_output=True, creationflags=CREAR_SIN_VENTANA)
        if not libs_ok:
            decir("libs")
            for lib in LIBRERIAS:
                subprocess.run([cli, "lib", "install", lib], capture_output=True, timeout=300, creationflags=CREAR_SIN_VENTANA)
    except Exception:
        pass


class VentanaVerificacion:
    def __init__(self):
        self._pending_after_ids = []
        self.iniciar = False
        self.deps_ok = True

        self.ventana = tk.Tk()
        poner_icono(self.ventana)
        self.ventana.title("🔍 Verificación de dependencias")
        self.ventana.resizable(False, False)
        self.ventana.configure(bg="#f8f9fa")
        # aparece adelante para que se vea, pero a los 0,8 s deja de ser "siempre encima" (no tapa las demás ventanas)
        self.ventana.attributes("-topmost", True)
        self.ventana.after(800, lambda: self._soltar_topmost())
        self.ventana.protocol("WM_DELETE_WINDOW", self._cerrar)
        BG = "#f8f9fa"

        tk.Label(self.ventana, text="📦 Verificando dependencias", font=("Segoe UI", 14, "bold"),
                 bg=BG, fg="#2c3e50").pack(pady=(12, 0))
        tk.Label(self.ventana, text="Asegurando que todo esté listo para comenzar", font=("Segoe UI", 9),
                 bg=BG, fg="#7f8c8d").pack(pady=(0, 8))

        self.labels_estado = {}
        for nombre, _modulo in DEPENDENCIAS:
            self.labels_estado[nombre] = self._fila(nombre)
        # Requisitos extra que no son librerías pip
        self.lbl_node = self._fila("Node.js")
        self.lbl_clasp = self._fila("clasp")
        self.lbl_cli = self._fila("arduino-cli")
        self.lbl_core = self._fila("Soporte ESP32")
        self.lbl_libs = self._fila("Librerías")
        self._auto_hecho = False

        self.barra = ttk.Progressbar(self.ventana, mode="determinate", length=380)
        self.barra.pack(pady=(10, 4))
        self.lbl_general = tk.Label(self.ventana, text="🔍 Preparando...", bg=BG, fg="#2c3e50", font=("Segoe UI", 9))
        self.lbl_general.pack()

        self.frame_botones = tk.Frame(self.ventana, bg=BG)
        self.frame_botones.pack(pady=8)
        self.Iniciar_app = tk.Button(self.frame_botones, text="🚀 Iniciar aplicación", state="disabled", bg="#95a5a6",
                                     fg="white", font=("Segoe UI", 9, "bold"), command=self._iniciar)
        self.Iniciar_app.pack(side="left", padx=4)
        self.btn_instalar = tk.Button(self.frame_botones, text="📦 Instalar lo que falta", state="disabled",
                                      command=self._instalar_extras, bg="#3498db", fg="white", font=("Segoe UI", 9, "bold"))
        self.btn_instalar.pack(side="left", padx=4)

        self.ventana.update_idletasks()
        w = 400
        h = self.ventana.winfo_reqheight() + 16
        x = (self.ventana.winfo_screenwidth() - w) // 2
        y = (self.ventana.winfo_screenheight() - h) // 2
        self.ventana.geometry(f"{w}x{h}+{x}+{y}")
        threading.Thread(target=self._verificar, daemon=True).start()

    # ---------- utilidades ----------
    def _fila(self, nombre):
        f = tk.Frame(self.ventana, bg="#f8f9fa"); f.pack(fill="x", padx=20, pady=1)
        tk.Label(f, text=nombre, width=14, anchor="w", font=("Segoe UI", 9, "bold"), bg="#f8f9fa").pack(side="left")
        lbl = tk.Label(f, text="⏳ Pendiente", anchor="w", bg="#f8f9fa")
        lbl.pack(side="left")
        return lbl

    def _programar(self, ms, fn):
        id_ = self.ventana.after(ms, fn)
        self._pending_after_ids.append(id_)
        return id_

    def _cancelar_pendientes(self):
        for id_ in self._pending_after_ids:
            try:
                self.ventana.after_cancel(id_)
            except Exception:
                pass
        self._pending_after_ids = []

    def _soltar_topmost(self):
        try:
            if self.ventana.winfo_exists():
                self.ventana.attributes("-topmost", False)
        except Exception:
            pass

    def _config_seguro(self, widget, **kwargs):
        try:
            if widget.winfo_exists():
                widget.config(**kwargs)
        except tk.TclError:
            pass

    def _ui(self, widget, **kwargs):
        self._programar(0, lambda: self._config_seguro(widget, **kwargs))

    # ---------- verificación ----------
    def _verificar(self):
        total = len(DEPENDENCIAS) + 5
        idx = 0
        for nombre, modulo in DEPENDENCIAS:
            lbl = self.labels_estado[nombre]
            self._ui(self.lbl_general, text=f"🔍 Verificando {nombre}...")
            try:
                __import__(modulo)
                self._ui(lbl, text="✅ Instalado")
            except Exception:
                # Si alguna vez se suma una librería pip, aquí se instala con pip install <nombre> --quiet
                self._ui(lbl, text="⏳ Instalando...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", nombre, "--quiet"],
                                          creationflags=CREAR_SIN_VENTANA)
                    __import__(modulo)
                    self._ui(lbl, text="✅ Instalado")
                except Exception:
                    self._ui(lbl, text="❌ Error")
                    self.deps_ok = False
            idx += 1
            self._ui(self.barra, value=(idx / total) * 100)
        self._verificar_extras(idx, total)

    def _verificar_extras(self, idx, total):
        preparar_entorno_deps()
        asegurar_path()
        self._ui(self.lbl_general, text="🔍 Buscando en Dependencias_Ofline...")
        node = shutil.which("node")
        self._ui(self.lbl_node, text=("✅ En Dependencias_Ofline" if node_en_deps() else "✅ Instalado en la PC") if node else "❌ Falta")
        idx += 1
        self._ui(self.barra, value=(idx / total) * 100)
        clasp = shutil.which("clasp")
        self._ui(self.lbl_clasp, text=("✅ En Dependencias_Ofline" if clasp_en_deps() else "✅ Instalado en la PC") if clasp else "❌ Falta")
        idx += 1
        self._ui(self.barra, value=(idx / total) * 100)
        cli = buscar_cli()
        self._ui(self.lbl_cli, text=("✅ En Dependencias_Ofline" if cli_en_deps() else "✅ Instalado en la PC") if cli else "❌ Falta")
        idx += 1
        self._ui(self.barra, value=(idx / total) * 100)
        core_ok, libs_ok = estado_arduino(cli)
        self._core_ok, self._libs_ok = core_ok, libs_ok
        self._ui(self.lbl_core, text="✅ Instalado" if core_ok else ("❌ Falta (se baja una vez)" if cli else "⏳ Pendiente"))
        idx += 1
        self._ui(self.barra, value=(idx / total) * 100)
        self._ui(self.lbl_libs, text="✅ Instaladas" if libs_ok else ("❌ Faltan (se bajan una vez)" if cli else "⏳ Pendiente"))
        idx += 1
        self._ui(self.barra, value=(idx / total) * 100)
        todo = bool(node and clasp and cli)
        completo = node_en_deps() and clasp_en_deps() and cli_en_deps() and core_ok and libs_ok
        if not completo and not self._auto_hecho:
            # primera vez (o falta algo en Dependencias_Ofline): se baja todo solo; si no hay internet y la PC ya
            # tiene Node, clasp y arduino-cli, el programa sigue igual con esos
            self._auto_hecho = True
            self._programar(0, self._instalar_extras)
            return
        self._ui(self.btn_instalar, state="disabled" if completo else "normal")
        if todo and self.deps_ok:
            self._ui(self.lbl_general, text="✅ Todo listo: iniciando..." if completo else "⚠️ Iniciando (algo no se pudo bajar: se reintenta al grabar)")
            self._programar(1200 if completo else 2500, self._iniciar)
        elif todo:
            self._ui(self.lbl_general, text="⚠️ Falta tkinter u otra librería de Python (ver arriba)")
        else:
            self._ui(self.lbl_general, text="⚠️ Falta Node.js, clasp o arduino-cli (¿hay internet?): reintentá con el botón")
        self._ui(self.Iniciar_app, state="normal", bg="#27ae60")

    def _instalar_extras(self):
        self.btn_instalar.config(state="disabled")
        self.Iniciar_app.config(state="disabled", bg="#95a5a6")
        self._ui(self.lbl_general, text="📦 Descargando a Dependencias_Ofline (la primera vez tarda unos minutos)...")

        def tarea():
            try:
                if not node_en_deps():
                    self._ui(self.lbl_node, text="⏳ Descargando...")
                    instalar_node_simple()
                preparar_entorno_deps()
                asegurar_path()
                if shutil.which("node") and not clasp_en_deps():
                    self._ui(self.lbl_clasp, text="⏳ Instalando...")
                    subprocess.run(comando_instalar_clasp(), shell=True, creationflags=CREAR_SIN_VENTANA)
                    preparar_entorno_deps()
                    asegurar_path()
                if not cli_en_deps():
                    self._ui(self.lbl_cli, text="⏳ Descargando...")
                    descargar_cli_simple()
                cli = buscar_cli()
                if cli:
                    core_ok, libs_ok = estado_arduino(cli)
                    if not (core_ok and libs_ok):
                        if not core_ok:
                            self._ui(self.lbl_core, text="⏳ Descargando (varios minutos, es grande)...")
                        if not libs_ok:
                            self._ui(self.lbl_libs, text="⏳ Esperando...")
                        self._ui(self.lbl_general, text="📦 Bajando el soporte ESP32: puede tardar varios minutos, no cierres...")
                        descargar_arduino_simple(cli, core_ok, libs_ok)
            finally:
                self._verificar_extras(0, 5)
        threading.Thread(target=tarea, daemon=True).start()

    # ---------- cierre ----------
    def _iniciar(self):
        if self.iniciar:
            return
        self.iniciar = True
        self._cancelar_pendientes()
        self.ventana.quit()
        self.ventana.destroy()

    def _cerrar(self):
        self._cancelar_pendientes()
        sys.exit(0)

    def correr(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    VentanaVerificacion().correr()
    App().correr()
