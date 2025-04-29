<div align="center">
    <img src="https://raw.githubusercontent.com/Benzo-Fury/ProxE/refs/heads/master/public/images/banner-rounded.png" width="900px">
    <h1>Control Every Byte</h1>
    <h4>
        Lightweight, Python-based proxy server designed for speed, simplicity, and control.
    </h4>
</div>

<div align="center" styles="margin-top: 10px">
    <img src="https://img.shields.io/badge/open-source-brightgreen" />
    <a href="https://wakatime.com/badge/user/562ef0a6-af5f-4e3d-b92f-23fc331558ea/project/77366a07-9ee3-414d-90a2-78da4e6fbfa1">
    <img src="https://wakatime.com/badge/user/562ef0a6-af5f-4e3d-b92f-23fc331558ea/project/77366a07-9ee3-414d-90a2-78da4e6fbfa1.svg" alt="wakatime"></a>
    
</div>


## Features 📦

- 🔄 Supports HTTP and HTTPS tunneling 
- ⚙️ Fully configurable
- 📊 Built-in TinyDB logging system for real-time traffic tracking and authentication
- 🧱 Clean event-based structure for easy extensibility
- 🐍 Lightweight Python implementation with minimal dependencies
- 🧪 Easily testable with raw sockets or browser proxy settings

## Getting Started 🚀

```bash
git clone https://github.com/Benzo-Fury/ProxE
cd ProxE
pip install -r requirements.txt
python src/main.py
```

## Database 🗂️
ProxE uses a built-in **TinyDB** instance to handle usage logging and user authentication — no server setup required. All data is stored in a local `database.json` file located at the root of the project.

This file is managed entirely by ProxE: it is automatically created if missing and updated internally. You do not need to manually modify or maintain it.

> ⚠️ The database system can be disabled via the `disable-database` option in your config file, or using the `--disable-database` flag when running in executable mode.

### Visualizing the Database 📄
ProxE does not ship with a built-in GUI for viewing or editing data, as it is designed for small-scale, local use. If you'd like to inspect the data, especially for larger or more complex entries, consider using an external JSON visualization tool such as [JSON Crack](https://jsoncrack.com/) or [JSON Editor Online](https://jsoneditoronline.org/).

## Usage Logging 📊
Each request received by the proxy is logged with the following information:

| Field                  | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `client_ip`            | The IP address of the device that made the request                          |
| `destination_ip`          | The target domain or IP address of the request                              |
| `method`               | The HTTP method used (`GET`, `POST`, `CONNECT`, etc.)                       |
| `received_at`          | Timestamp when the request was first received by the proxy                  |
| `resolved_at`          | Timestamp when the request or tunnel was closed or completed                |
| `protocol`             | Indicates whether the request was handled via standard HTTP or CONNECT (HTTPS) |

> ⏱ **Note:** CONNECT requests (used for HTTPS) may remain open longer than standard HTTP requests. This is expected behavior due to the nature of tunneling.

> ⚠️ Usage logging can be disabled via the `usage_logging` setting in your config file, or using the `--disable-usage-logging` flag in executable mode.


## Authentication🔐

ProxE supports a built-in authentication system that restricts access to the proxy using **username and password credentials**. This is especially useful in shared environments or when running the proxy on public-facing networks.

All user credentials are stored in the internal TinyDB database in the following format:

```json
{
    "username": "Benzo-Fury",
    "password": "hashed-or-plain-password"
}
```

### 🔒 Secure Passwords with Bcrypt

By default, **all passwords should be hashed using [bcrypt](https://en.wikipedia.org/wiki/Bcrypt)** before being stored. Bcrypt is a modern, secure hashing algorithm that:

- Automatically adds a unique salt
- Makes brute-force attacks extremely difficult
- Ensures stored passwords cannot be reversed

This is the **recommended approach for all production environments**.

### 🔑 How to Generate Bcrypt Passwords

To create a bcrypt-hashed password for use in your database, use the [bcrypt-generator.com](https://bcrypt-generator.com) website or generate one using Python:

```py
import bcrypt

password = "your-secret-password"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed.decode())
```

Then place the resulting hashed value in your user record:

```json
{
    "username": "Benzo-Fury",
    "password": "$2b$12$e0xq8C..."
}
```

### 🧪 Plaintext Mode (For Testing Only)

If you're working in a development environment or need faster testing, you can **disable bcrypt hashing** and store passwords as plaintext instead.

> ⚠️ This is **not secure** and should never be used in public or shared deployments.

To enable plaintext mode, you can enable `plain-text-passwords` in the config file, or use the `--disable-bcrypt-password` executable flag.

In this mode, passwords will be compared as raw strings without hashing.

## Unencrypted Proxy Credentials 🔐

ProxE is designed to be accessible to all clients without requiring custom setup or tooling. This includes compatibility with browsers, operating systems, and other clients that support standard HTTP proxies.

However, due to limitations in the **HTTP proxy protocol itself**, there is a important security implication to be aware of:

When a client (such as a browser) initiates a request to an HTTPS destination through a proxy, it sends a `CONNECT` request that looks like this:

```http
CONNECT example.com:443 HTTP/1.1
Proxy-Authorization: Basic dXNlcjpwYXNz
```

This `CONNECT` request — including the authentication headers — is sent **in plaintext over HTTP**, even if the final destination is HTTPS. This behavior is **standard across all browsers and operating systems**.

This means that if a man-in-the-middle (MITM) has access to the network (e.g., public Wi-Fi), **they can read the proxy credentials and reuse them** unless additional safeguards are in place.


### ✅ How to Protect Your Proxy

To reduce the risk of proxy credential leaks:

- Only run ProxE on **trusted networks** (LAN, VPN, or SSH tunnels)
- Avoid using the proxy on public or unsecured Wi-Fi
- Only allow trusted IP's connecting to your proxy

In future versions, ProxE may offer built-in support for TLS termination or encrypted control channels to address this limitation more directly.

>**Note:** This is not a vulnerability in ProxE — it is a limitation of the HTTP proxy protocol and client behavior. For full end-to-end encryption of all proxy traffic, use a SOCKS5 proxy or a VPN-based solution.

## Planned Features 🛠️

- [x] Event-based socket piping system
- [x] HTTP and HTTPS (via CONNECT) support
- [x] Config-based customization (config.py)
- [x] Tunnel and request logging
- [x] User logging and authentication
- [ ] Improved console logging via the logger class
- [ ] Standalone mode - Compiled executable that executes ProxE in a console and allows configuration through flags..
- [ ] TLS interception / MITM (optional toggle) (maybe)
- [ ] Potentially support Stunnel on a secondary port for encrypted CONNECT requests.