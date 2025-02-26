# File Translator

This project is a Python desktop application that translates text, PDF, and Word (`.txt`, `.pdf`, `.docx`) files from one language to another. It uses the [googletrans](https://pypi.org/project/googletrans/) library (an unofficial version of Google Translate) and other Python tools to handle files.

> **Note**: `googletrans` is not an official library. It might break due to changes in the Google API. If you need a more stable alternative, consider using the [official DeepL API](https://www.deepl.com/pro-api) or an offline translation model (Marian, M2M100, etc.).

## Features

- **Graphical interface** built with [Tkinter](https://docs.python.org/3/library/tkinter.html).
- **Automatic translation** powered by `googletrans`.
- **Optional auto-detection** of the source language.
- **Supports** `.txt`, `.pdf`, and `.docx`.
- **Preserves images** and basic formatting in `.docx` files.
- **Progress bar** and a **cancel** button to stop the translation process.
- **Automatic retries** up to 3 times in case of errors.
- **Final list** of files that could not be translated.

## Requirements

- **Python 3.8+**
- Libraries:
  - `googletrans==4.0.0-rc1`
  - `langdetect`
  - `pdfminer.six`
  - `python-docx`
  - `plyer`
  - `tkinter` (usually included with standard Python installations)
  - (Optional) `requests`, `sentencepiece`, `transformers` if you test offline models

Install them with:
```bash
pip install googletrans==4.0.0-rc1 langdetect pdfminer.six python-docx plyer
