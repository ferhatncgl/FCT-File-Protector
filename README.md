# 🛡️ FCT File Protector


HOW TO USE GUIDE: https://youtu.be/4GsUzqp1UDc

A high-security, professional-grade directory encryption tool built with Python. It utilizes industry-standard **AES-256-GCM** for encryption and **Argon2id** for key derivation, ensuring your data remains inaccessible even under reverse engineering or brute-force attempts.

<img width="541" height="572" alt="resim" src="https://github.com/user-attachments/assets/14bd33e8-87c1-41d1-a191-f53994373bd2" />

## ✨ Features
- **Modern UI:** Sleek dark-themed interface powered by CustomTkinter.
- **Drag & Drop:** Easily encrypt/decrypt folders and files by dropping them into the app.
- **Argon2id KDF:** State-of-the-art key derivation resistant to GPU/ASIC brute-forcing.
- **AES-256-GCM:** Authenticated encryption that ensures data integrity and confidentiality.
- **Keyfile Support (Optional):** Add an extra layer of security by requiring a specific file alongside your password.
- **Secure Shredding (Optional):** Physically destroys original files after encryption using a 3-pass random data overwrite (Irreversible).

## 🔒 Security Specifications
- **Encryption:** AES-256-GCM (Galois/Counter Mode)
- **Key Derivation:** Argon2id (Iterations: 3, Memory: 64MB, Parallelism: 4)
- **File Integrity:** Automatically verified via GCM Authentication Tags.

## 🚀 Installation (For Developers)

How to install andd run FCT File Protector in Terminal: https://www.youtube.com/watch?v=LuDDeCtuyYY

1. Clone the repository:

```bash
   git clone [https://github.com/ferhatncgl/FCT-File-Protector.git](https://github.com/ferhatncgl/FCT-File-Protector.git)

```


2. Install dependencies:
 ```bash
   pip install cryptography customtkinter tkinterdnd2

```


3. Run the app:
```bash
python main.py

```



## 📦 How to Download (.exe)

If you just want to use the program, go to the [Releases](https://github.com/ferhatncgl/FCT-File-Protector/releases) section and download the latest `.zip` file. Extract it and run `FCT File Protector.exe`.

## ⚠️ Disclaimer

**Secure Shredding** is a permanent action. Files deleted using this feature **cannot** be recovered even with forensic data recovery software. Use at your own risk.

---

Developed with ❤️ by [@ferhatncgl](https://www.google.com/search?q=https://github.com/ferhatncgl)
