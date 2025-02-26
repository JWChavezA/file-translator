# file-translator
File translator by quantities using the source folder address, using Python.
# File Translator

Este proyecto es una aplicación de escritorio en Python que traduce archivos de texto,
PDF y Word (`.txt`, `.pdf`, `.docx`) de un idioma a otro. Se basa en la librería
[googletrans](https://pypi.org/project/googletrans/) (versión no oficial de Google Translate)
y en otras herramientas de Python para manejar los archivos.

> **Aviso**: `googletrans` es una librería no oficial. Puede romperse o fallar por cambios
en la API de Google. Si necesitas una alternativa más estable, considera usar la
[API oficial de DeepL](https://www.deepl.com/pro-api) o un modelo de traducción offline
(Marian, M2M100, etc.).

## Características

- **Interfaz gráfica** con [Tkinter](https://docs.python.org/3/library/tkinter.html).
- **Traducción automática** usando `googletrans`.
- **Detección automática** del idioma de origen (opcional).
- **Soporta** `.txt`, `.pdf`, `.docx`.
- **Mantiene imágenes** y formato básico en archivos `.docx`.
- **Barra de progreso** y opción de **cancelar** el proceso de traducción.
- **Reintentos automáticos** hasta 3 veces en caso de fallos.
- **Listado final** de archivos que no se pudieron traducir.

## Requisitos

- **Python 3.8+**  
- Librerías:
  - `googletrans==4.0.0-rc1`
  - `langdetect`
  - `pdfminer.six`
  - `python-docx`
  - `plyer`
  - `tkinter` (viene incluido con Python en la mayoría de instalaciones estándar)
  - (Opcional) `requests`, `sentencepiece`, `transformers` si pruebas modelos offline

Instálalas con:
```bash
pip install googletrans==4.0.0-rc1 langdetect pdfminer.six python-docx plyer
