# 🌐 AI-Enabled Cloudless Home Ecosystem (AIECHE)

**AIECHE** is a privacy-first smart home automation system that operates entirely without cloud dependency. It features a modular architecture with a local home server, AI-powered voice assistant (LLaMA 3.1), smart scheduling, and secure peer-to-peer remote access via Tailscale — all running on affordable, local hardware like Raspberry Pi and ESP32.

---

## 🔧 Project Goal

To design a decentralized smart home ecosystem that prioritizes:
- **User privacy**
- **Offline operation**
- **AI-driven automation**
- **Energy efficiency**
- **Secure remote access without cloud exposure**

---

## ✨ Core Features

- ⚙️ **Automation Server**  
  Flask-based local backend for controlling devices and managing schedules.

- 🔐 **Tailscale VPN Integration**  
  Enables peer-to-peer remote control without exposing ports or using cloud relays.

- 🧠 **AI Voice Assistant (LLaMA 3.1)**  
  Processes voice or text commands locally via structured JSON.

- 🕒 **AI Pattern Recognition**  
  Learns user behavior and proposes energy-saving schedules.

- 🗂️ **Private NAS Server**  
  Secure, local file storage accessible via app.

- 📺 **RTSP Camera Stream Integration**  
  Streams and records IP camera feeds using MediaMTX.

- 📶 **ESP32-Based Smart Switchboxes**  
  Custom firmware enables fan/light control with real-time sync.

- 📱 **Flutter Mobile App (AIECHE App)**  
  Unified control panel for devices, schedules, NAS, and camera feeds.

---

## 🧩 System Architecture

```plaintext
User App ↔ Tailscale VPN ↔ Local Home Server
        ├── Automation Server
        ├── AI Server (Ollama + LLaMA 3.1)
        ├── NAS Server
        └── Stream Server (MediaMTX)
                    ↓
              ESP32 Switchboxes
