<div align="center">
    <img src="https://raw.githubusercontent.com/Benzo-Fury/ProxE/refs/heads/master/public/images/banner-rounded.png" width="900px">
    <h1>Control Every Byte</h1>
    <h4>
        Lightweight, Python-based proxy server designed for speed, simplicity, and control.
    </h4>
</div>

<div align="center" styles="margin-top: 10px">
    <img src="https://img.shields.io/badge/open-source-brightgreen" />
    <a href="https://wakatime.com/badge/user/562ef0a6-af5f-4e3d-b92f-23fc331558ea/project/77366a07-9ee3-414d-90a2-78da4e6fbfa1"><img src="https://wakatime.com/badge/user/562ef0a6-af5f-4e3d-b92f-23fc331558ea/project/77366a07-9ee3-414d-90a2-78da4e6fbfa1.svg" alt="wakatime"></a>
</div>


## Features

- 🔄 Supports HTTP and HTTPS tunneling 
- ⚙️ Fully configurable
- 📊 Built-in SQLite logging system for real-time traffic tracking
- 🧱 Clean event-based structure for easy extensibility
- 🐍 Lightweight Python implementation with minimal dependencies
- 🧪 Easily testable with raw sockets or browser proxy settings

## How It Works

ProxE uses custom `Socket` and `Tunnel` classes to handle raw TCP connections. When an HTTP `CONNECT` request is received, a tunnel is formed and traffic is piped in both directions.

Sockets use event driven architecture to handle their lifecycle and data transfer. Events like `bytes_received` and `close-request`, make it easy to hook into any part of the proxy process.


## Getting Started

```bash
git clone https://github.com/Benzo-Fury/ProxE
cd ProxE
pip install -r requirements.txt
python main.py
```