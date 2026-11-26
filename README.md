# Luces ESP32 Web

Control de luces/relés, entradas y sensores con **ESP32** desde el celular, mediante una página web hecha con **Google Apps Script** (varias placas en una sola página).

## Qué incluye
- `Subir_a_Apps_Script.pyw`: programa de escritorio (Python 3 + Tkinter, Windows) que hace todo:
  - instala Node.js, clasp y arduino-cli de forma portátil en `Dependencias_Ofline` (se descargan una sola vez);
  - crea el `.ino`, el `Codigo.gs` y la `Pagina.html` con tus datos (pines, WiFi, clave);
  - sube y publica el script en Google con clasp;
  - compila y graba el ESP32 por USB o por WiFi (OTA).
- Sensores (LDR, presión, PIR, DS18B20, DHT22/11, analógico genérico) y reglas automáticas.
- Librerías extra y código propio para módulos nuevos.
- `Tutorial_Luces_ESP32.docx`: tutorial paso a paso.
- `Construir_exe.bat`: arma el `.exe` con PyInstaller.

## Cómo usarlo
1. Instalá Python 3 con Tkinter (Windows).
2. Ejecutá `Subir_a_Apps_Script.pyw`.
3. Seguí los pasos ① a ⑤ de la ventana (o **⚡ HACER TODO**).

## Instalador (.exe)
El `.exe` no está en el código: se publica en [Releases](../../releases).

## Privacidad
No subas `config_subir_script.json` ni la carpeta `Control_Reles`: tienen tu clave de la página y la contraseña del WiFi. El `.gitignore` ya los excluye.
