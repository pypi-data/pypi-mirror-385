# 🏷️ etikettierer – Label & QR Code Generator with Printer Support

## ⚠️ Disclaimer

This software is an independent product and is **not developed, maintained, or endorsed** by Zebra, Brother, or any other printer manufacturer.  
All trademarks, brand names, and product names referenced in this software are the property of their respective owners.

The software is designed to interface with **Zebra** and **Brother QL** printers, but it is **not affiliated with or supported by them**.  
Use of this software is at the user's own risk. The developers assume **no liability** for damages, malfunctions, or losses arising from its use.

By using this software, you acknowledge that the developers are **not responsible for any damage, malfunction, or loss** resulting from its use.

---

## 🧩 Introduction

**etikettierer** is a Python package for generating **print-ready labels** containing QR codes and human-readable sample names.

Each label consists of:
- Sample name (text)
- Two QR codes:
  - One encoding the **Electronic Lab Notebook (ELN)** link
  - One encoding the **sample name**

### Features

- Generate QR labels programmatically  
- Export labels as **PNG images**  
- Print directly to:
  - 🖨️ **Zebra ZD421 (ZPL protocol)**
  - 🖨️ **Brother QL-800 (USB)**
  - 🖨️ **Windows system printers**

---

## 📦 Installation

Install from PyPI (all printer dependencies included):

```bash
pip install etikettierer
```

# ⚙️ Printer Setup

All required libraries — including **Brother QL** and **Windows printing support** — are automatically installed.

💡 On non-Windows systems, `pywin32` (Windows-only dependency) is skipped automatically.

---

## 🧾 Zebra ZD421 (ZPL-compatible)

1. Install the official Zebra driver:  
   👉 [Zebra Setup Utilities](https://www.zebra.com/us/en/support-downloads.html)
2. Verify the printer name in your system (e.g., `ZDesigner ZD421-203dpi ZPL`).
3. Printing is handled via the **ZPL protocol** using the built-in `zpl` Python library.

---

## 🧾 Brother QL-800

- Uses the Python **brother_ql** library (included automatically).  
- Recommended connection: **USB**

### Setup Steps

1. On Windows, install the **libusb-win32** filter driver (required for USB communication).  
   You can install the Python interface with:
   ```bash
   pip install pyusb
2. Brother devices are typically identified by hardware IDs such as `vid:04F9:XXXX`.
3. After installing the USB filter, restart your computer.

> 📝 No official Brother drivers are required when using this package.

---

## 🧠 QR Code Error Correction Levels

The QR code’s error correction level controls its redundancy and damage tolerance.

| Level | Correction | Description |
|:------|:------------|:-------------|
| **L (7%) - High Capacity** | 7% of codewords can be restored | Highest capacity, lowest redundancy |
| **M (15%) - Standard** | 15% of codewords can be restored | Standard level (**default**) |
| **Q (25%) - Higher Security** | 25% of codewords can be restored | Increased reliability |
| **H (30%) - Very Robust** | 30% of codewords can be restored | Most robust against damage |

---

## 🔍 Troubleshooting

| Issue | Cause | Solution |
|:------|:------|:----------|
| **Font not found (arial.ttf)** | Missing on Linux/macOS | Install Arial or modify to another font |
| **Brother printer not detected** | USB filter missing | Install libusb-win32 and restart |
| **Zebra printer not responding** | Incorrect printer name | Check printer name in system settings |
| **pywin32 fails on macOS/Linux** | Platform-specific dependency | Automatically skipped outside Windows |

---

## 📜 License

This package is distributed under the **GNU General Public License (GPL) v3**.  
See the `LICENSE` file for full details.

---

## 🧠 About

Developed at the  
**Leibniz Institute of Polymer Research Dresden e.V. (IPF)**

Originally created for internal use to streamline **laboratory labeling and sample tracking workflows**.

---

## 📧 Contact

- **sambale@ipfdd.de**  
- **henn@ipfdd.de**
