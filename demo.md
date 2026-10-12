# VulnBank MCP: Demo

This demo shows an AI agent connected to **VulnBank** through an **MCP (Model Context Protocol) server**. The agent can check the app's status, list its vulnerabilities, and run live tool calls against it, all from plain-English prompts.

> **Warning:** VulnBank is a deliberately vulnerable application built for learning. Run it only on your own machine (`127.0.0.1`). Never deploy it or expose it to a network.

---

## Architecture

```
┌──────────────┐   MCP    ┌─────────────────────┐   HTTP    ┌──────────────────┐
│  AI Agent    │ ───────► │  vulnbank-mcp       │ ────────► │  VulnBank        │
│ (Antigravity)│ ◄─────── │  (NitroStack server)│ ◄──────── │  Flask app :5000 │
└──────────────┘          └─────────────────────┘           └──────────────────┘
```

- **VulnBank**: the vulnerable Flask banking app (`github.com/Prateep07/vulnbank`)
- **vulnbank-mcp**: the MCP server that exposes VulnBank's functionality as tools (Python, NitroStack-based)
- **Agent**: any MCP-capable client. The demo uses Antigravity.

---

## Prerequisites

- Python 3.x
- Git
- An MCP-capable agent or IDE (the demo uses Antigravity)
- VulnBank cloned and runnable locally

---

## How to run

### 1. Start VulnBank

```bash
git clone https://github.com/Prateep07/vulnbank.git
cd vulnbank
pip install -r requirements.txt
python app.py
```

VulnBank should now be reachable at `http://127.0.0.1:5000`.

### 2. Set up the MCP server

In a second terminal:

```bash
git clone https://github.com/Prateep07/vulnbank-mcp.git
cd vulnbank-mcp

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

### 3. Run the MCP server

```bash
.venv\Scripts\python.exe main.py      # Windows
# python main.py                      # macOS / Linux
```

Leave this terminal running. The server talks to VulnBank at `http://127.0.0.1:5000`.

### 4. Connect your agent

Register the server in your agent's MCP configuration so it launches the command above.

```json
{
  "mcpServers": {
    "vulnbank": {
      "command": "<path-to>/vulnbank-mcp/.venv/Scripts/python.exe",
      "args": ["<path-to>/vulnbank-mcp/main.py"]
    }
  }
}
```

Restart or refresh the agent. The VulnBank tools should now be listed as available.

---

## What it can do

Once connected, you can drive VulnBank with natural-language prompts.

| Capability                        | Example prompt                                     | What the agent does                                                                                                                              |
| --------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Health / status check**         | `show vulnbank status`                             | Calls the server and reports connection state, backend reachability, base URL, HTTP status, number of active labs, and available endpoints       |
| **Vulnerability inventory**       | `list all the vulnerabilities with their severity` | Returns a table of every lab with its OWASP category, endpoint, severity, and description                                                        |
| **Live tool use for explanation** | `using tools explain sql injection`                | Runs real requests against the login endpoint (a normal attempt, then an injection payload) and explains the result using the actual tool output |

### Example 1: Status check

**Prompt:** `show vulnbank status`

| Property            | Value                                                                                                    |
| ------------------- | -------------------------------------------------------------------------------------------------------- |
| Status              | connected                                                                                                |
| Backend Reachable   | true                                                                                                     |
| Base URL            | `http://127.0.0.1:5000`                                                                                  |
| HTTP Status         | 200 OK                                                                                                   |
| Active Labs         | 7 (2 Critical, 5 High)                                                                                   |
| Available Endpoints | `/login`, `/logout`, `/dashboard`, `/account/<account_id>`, `/transfer`, `/admin`, `/restore`, `/import` |

### Example 2: Vulnerability list

**Prompt:** `list all the vulnerabilities with their severity`

| ID  | Vulnerability Lab                  | Endpoint                | Severity     | Description                                                               |
| --- | ---------------------------------- | ----------------------- | ------------ | ------------------------------------------------------------------------- |
| A01 | Broken Access Control (IDOR)       | `/account/<account_id>` | High         | Account ownership is not properly enforced                                |
| A02 | Cryptographic Failures             | `/login`                | High         | Training app uses weak password hashing                                   |
| A03 | Injection (SQL Injection)          | `/login`                | **Critical** | Login endpoint is vulnerable to SQL injection bypasses                    |
| A04 | Insecure Design                    | `/transfer`             | High         | Fund transfer workflow lacks critical validation and transaction controls |
| A05 | Security Misconfiguration          | `/admin`                | High         | Admin dashboard is exposed without proper authorization barriers          |
| A08 | Software & Data Integrity Failures | `/restore`              | **Critical** | Restore endpoint demonstrates unsafe Python object deserialization        |
| A10 | Server-Side Request Forgery (SSRF) | `/import`               | High         | Import endpoint accepts unvalidated, user-controlled remote URLs          |

**Summary:** 7 labs total, 2 Critical and 5 High.

### Example 3: Live SQL injection walkthrough

**Prompt:** `using tools explain sql injection`

The agent runs two tool calls against `/login`:

1. **Standard login attempt**: `alice` with a wrong password. Authentication fails as expected (`logged_in: false`).
2. **SQL injection payload**: `' OR '1'='1' --` as the username. The payload closes the string, adds an always-true condition, and comments out the password check, so the query matches a user row without a valid password.

It then explains the vulnerable query pattern:

```sql
-- Intended query
SELECT * FROM users WHERE username = '<USER_INPUT>' AND password = '<PASSWORD_INPUT>'

-- Query after injection
SELECT * FROM users WHERE username = '' OR '1'='1' --' AND password = 'ignored_password'
```

---

## Troubleshooting

| Problem                            | Fix                                                                                     |
| ---------------------------------- | --------------------------------------------------------------------------------------- |
| Agent says VulnBank is unreachable | Make sure VulnBank is running on port 5000 before starting the MCP server               |
| Tools don't appear in the agent    | Check the MCP config path, then restart the agent and confirm `main.py` is running      |
| `ModuleNotFoundError`              | Activate the virtual environment and re-run the dependency install                      |
| Port 5000 already in use           | Stop the other process, or change the port in VulnBank and in the MCP server's base URL |

---

## Related

- [VulnBank](https://github.com/Prateep07/vulnbank): the vulnerable Flask app (OWASP Top 10 labs, exploit scripts, writeups)
- [Model Context Protocol](https://modelcontextprotocol.io): the protocol used to expose tools to agents

## Disclaimer

This project is for **education and authorized security testing only**. Do not use these techniques against systems you do not own or have explicit permission to test.
