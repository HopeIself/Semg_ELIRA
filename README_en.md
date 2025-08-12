<p align="right">
  <a href="./README.md">中文</a> | <a href="./README_en.md">English</a>
</p>

# Semg\_ELIRA

**ELIRA** (Electromyography-based Life Rehabilitation Assistant) — An intelligent rehabilitation assistance system based on EMG signals.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Demo Illustrations](#demo-illustrations)
3. [User Guide (Links + Images)](#user-guide)
4. [Requirements (Environment)](#requirements)
5. [Demo Examples](#demo-examples)
6. [Documentation](#documentation)
7. [Features](#features)
8. [Releases & Supported Platforms](#releases--supported-platforms)
9. [Installation & Deployment](#installation--deployment)
10. [License](#license)
11. [Module Overview](#module-overview)

---

## System Overview

This project aims to build an **intelligent, multi-platform collaborative rehabilitation assistance system** designed for the general public, especially for students, office workers, post-surgery light rehabilitation users, and people with sub-health conditions.

The system integrates **EMG signal acquisition, IoT communication, AI-driven analysis, cloud-based processing, and multi-modal interactive guidance**, using AI Agents to achieve end-to-end intelligent management.

Users wear an EMG acquisition device, and the system checks the wearing status (signal strength) to ensure safety and effectiveness. Through the frontend (Vue-based web or mobile app), users can select an AI assistant (DeepSeek, Tongyi Qianwen, Doubao) and start training. The frontend plays training videos with voice prompts.

The EMG signals are amplified by the device, sampled by an Arduino ADC, transmitted to an STM32, and uploaded to the cloud. The Python core module is deployed in the cloud, calling large language models to generate training plans, recognize EMG motion states, and create personalized rehabilitation schemes based on seven standard medical actions.

During training, the system evaluates motion quality in real time, provides feedback on EMG feature changes, and generates illustrated evaluation reports after each session. The AI Agent acts as a rehabilitation assistant, analyzing reports and answering user questions. All data is stored in the cloud, and the mobile app can retrieve it in real time.

---

## Demo Illustrations

### System Architecture

<div align="center">
  <img src="./images/architecture.png" alt="System Architecture" style="max-width:100%;height:auto;" />
</div>

### Hardware & Data Acquisition Flow

<div align="center">
  <img src="./images/device_flow.png" alt="Acquisition Flow" style="max-width:100%;height:auto;" />
</div>

---

## User Guide

Quick links to common usage scenarios:

* **Web Frontend**: See `docs/web/README.md` or visit `http://<your-host>/`. <br/> <img src="./images/web_ui.png" alt="Web UI Screenshot" style="max-width:60%;height:auto;" />

* **Mobile App (Android / iOS)**: See `docs/mobile/README.md` and install the corresponding APK / TestFlight build. <br/> <img src="./images/app_screenshot.png" alt="App Screenshot" style="max-width:60%;height:auto;" />

* **Cloud Analysis Console**: See `docs/cloud/console.md`. <br/> <img src="./images/cloud_console.png" alt="Cloud Console" style="max-width:60%;height:auto;" />

> Tip: The `docs/` directory contains detailed usage manuals and navigation guides (search for “Quick Start” for direct jumps).

---

## Requirements

**Hardware**

* EMG acquisition device (ADC output capable)
* Arduino or compatible acquisition module
* STM32 or similar MCU for data packaging and upload
* Gateway or terminal with Wi-Fi / NB-IoT (depending on deployment)

**Software (Cloud / Local)**

* Python 3.8+ (3.10 recommended)
* Common dependencies: `numpy`, `scipy`, `pandas`, `matplotlib`, `torch` (for model inference), `fastapi`, `uvicorn`
* Database (choose one): PostgreSQL / MySQL / SQLite (for small-scale testing)
* Message queue (optional): Redis / RabbitMQ
* Frontend: Node.js 16+, Vue 3

---

## Demo Examples

Provided examples:

* `examples/simulated_acquisition.py` — Simulate EMG data acquisition and upload.
* `examples/run_analysis.py` — Run the cloud analysis module locally and generate a report.
* `examples/demo_frontend/` — Frontend demo source code (run with `npm run dev`).

Quick demo run:

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run simulated acquisition
python examples/simulated_acquisition.py

# Run analysis service in another terminal
python examples/run_analysis.py
```

---

## Documentation

* The `docs/` directory contains: system design, API documentation, frontend guide, hardware wiring diagrams, and data format specifications.
* Recommended reading (local or cloud-stored PDFs): medical action classification, EMG signal processing basics, relevant research papers.

---

## Features

* Real-time EMG data acquisition and upload
* Wear detection (signal strength and electrode contact quality)
* AI-driven personalized training plan generation (supports DeepSeek, Tongyi Qianwen, Doubao, etc.)
* Training video playback with voice prompts
* Real-time motion quality evaluation and feedback
* Illustrated evaluation report generation after each session
* Multi-platform sync (Web / App / Cloud) and data storage
* Remote doctor access and report sharing

---

## Releases & Supported Platforms

* Frontend: Web (modern browsers), Android (APK), iOS (IPA/TestFlight)
* Backend/Cloud: Linux x86\_64 (Ubuntu 20.04+ recommended), deployable to public cloud (Alibaba Cloud, AWS, Azure, Volcano Cloud, etc.) or private servers
* Embedded: Supports common MCUs (STM32 series, Arduino) and sensing modules

---

## Installation & Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/Semg_ELIRA.git
cd Semg_ELIRA
```

### 2. Configure Cloud Environment

* Create a Python virtual environment: `pip install -r requirements.txt`
* Configure `.env` (see `.env.example`): database URL, model path, cloud storage credentials, third-party API keys

### 3. Deploy Backend Service (Example)

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 4. Start Frontend (Web)

```bash
cd frontend
npm install
npm run build    # or npm run dev for development
```

### 5. Embedded Firmware

* Compile and flash STM32 firmware, configure networking and acquisition channels
* Upload Arduino acquisition scripts and test ADC output

### 6. Verification

* Use simulation scripts or hardware acquisition to upload data
* Access the frontend or call APIs to view analysis results and reports

---

## License

The project uses the **MIT License** by default (you may replace the `LICENSE` file with Apache-2.0 or GPL-3.0 if needed).

---

## Module Overview

1. **Device Wearing & Signal Check** — Detects electrode placement, signal strength, and noise filtering.
2. **Training Preparation & Guidance (TBD)** — Plays training videos, voice prompts, and controls timing.
3. **EMG Acquisition & Data Upload** — Sampling, packaging, and transmitting data from MCU/acquisition device.
4. **Cloud Analysis & Personalized Plan Generation** — Core AI logic using large models for plan creation and real-time evaluation.
5. **Real-time Monitoring & Feedback** — Visualization, anomaly alerts, and improvement suggestions.
6. **Result Summary & Report Output** — Illustrated/PDF report generation and history tracking.
7. **Remote Doctor Analysis & Feedback** — Allows doctors to review history, conduct tele-consultations, and publish suggestions.

---

## Acknowledgements

Thanks to the project team and all contributors. To participate in development or testing, see `CONTRIBUTING.md`.
