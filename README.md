# LeaveManager MCP Server

A small [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that lets an AI assistant (like Claude) check employee leave balances, apply for leave, and view leave history.

It is built with the official MCP Python SDK (`FastMCP`) and keeps all its data **in memory**, so it's a demo or learning project, not a production HR system.

---

## Features

| Type     | Name                | What it does                                                        |
| -------- | ------------------- | ------------------------------------------------------------------- |
| Tool     | `get_leave_balance` | Returns how many leave days an employee has left.                   |
| Tool     | `apply_leave`       | Applies leave for a list of dates and deducts them from the balance. |
| Tool     | `get_leave_history` | Lists every date the employee has taken leave.                      |
| Resource | `greeting://{name}` | Returns a personalized greeting message.                            |

### Sample data

The server starts with two employees:

| Employee ID | Balance | History                    |
| ----------- | ------- | -------------------------- |
| `E001`      | 18      | `2024-12-25`, `2025-01-01` |
| `E002`      | 20      | *(none)*                   |

---

## Requirements

- Python **3.10+**
- The MCP Python SDK **v1.x**: `mcp[cli]<2`

> [!IMPORTANT]
> Pin `mcp` below version 2. In `mcp` 2.x, `FastMCP` was renamed to `MCPServer`, so `from mcp.server.fastmcp import FastMCP` fails with `ModuleNotFoundError`. This server was tested with `mcp` **1.30.0**.

---

## Installation

```bash
cd MCP-Server

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install the MCP SDK (v1.x)
pip install "mcp[cli]<2"
```

---

## Running the server

```bash
python main.py
```

The server uses the **stdio** transport (the default for `mcp.run()`). When it starts, it waits quietly for an MCP client on stdin/stdout and prints nothing. That's normal. You usually don't run it by hand; an MCP client like Claude Desktop starts it for you.

### Testing with MCP Inspector

To test the tools in a browser UI:

```bash
mcp dev main.py
```

> `mcp dev` requires [`uv`](https://docs.astral.sh/uv/) and Node.js (`npx`) to be installed.

---

## Connecting to Claude Desktop

Open your Claude Desktop config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this, using the **absolute paths** on your machine:

```json
{
  "mcpServers": {
    "LeaveManager": {
      "command": "/ABSOLUTE/PATH/TO/MCP-Server/venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/MCP-Server/main.py"]
    }
  }
}
```

Restart Claude Desktop. The LeaveManager tools should then show up in the tools menu.

> If you have `uv` installed, you can instead run `mcp install main.py`, which writes this config for you.

---

## Tool reference

### `get_leave_balance`

Check how many leave days are left for the employee.

| Parameter     | Type     | Required |
| ------------- | -------- | -------- |
| `employee_id` | `string` | Yes      |

**Example:**

```json
{ "employee_id": "E001" }
```

```text
E001 has 18 leave days remaining.
```

---

### `apply_leave`

Apply leave for specific dates. Each date in the list counts as **one day**.

| Parameter     | Type              | Required |
| ------------- | ----------------- | -------- |
| `employee_id` | `string`          | Yes      |
| `leave_dates` | `array of string` | Yes      |

**Example:**

```json
{ "employee_id": "E002", "leave_dates": ["2025-04-17", "2025-05-01"] }
```

```text
Leave applied for 2 day(s). Remaining balance: 18.
```

If the balance is too low:

```text
Insufficient leave balance. You requested 19 day(s) but have only 18.
```

---

### `get_leave_history`

Get the leave history for the employee.

| Parameter     | Type     | Required |
| ------------- | -------- | -------- |
| `employee_id` | `string` | Yes      |

**Example:**

```json
{ "employee_id": "E001" }
```

```text
Leave history for E001: 2024-12-25, 2025-01-01
```

For an employee with no leave taken:

```text
Leave history for E002: No leaves taken.
```

---

### Resource: `greeting://{name}`

Returns a personalized greeting.

**Example:** reading `greeting://Sam` returns:

```text
Hello, Sam! How can I assist you with leave management today?
```

---

### Errors

If the `employee_id` doesn't exist, all three tools return:

```text
Employee ID not found.
```

---

## Example prompts

Once the server is connected, try asking Claude:

- "How many leave days does E001 have left?"
- "Apply leave for E002 on 2025-04-17 and 2025-05-01."
- "Show me the leave history for E001."

---

## Limitations

These are known limitations of the current code:

- **Data is not saved.** All changes are lost when the server restarts. Balances and history reset to the sample data.
- **No date validation.** `apply_leave` accepts any strings, including invalid dates like `"hello"` or dates in the past.
- **No duplicate check.** Applying for the same date twice (even in one request) counts as two days.
- **Fixed employees.** Only `E001` and `E002` exist. There is no tool to add employees.
- **No authentication.** Any connected client can view or change any employee's leave.

---

## Project structure

```text
MCP-Server/
├── main.py      # MCP server: tools, resource, and in-memory data
└── README.md
```
