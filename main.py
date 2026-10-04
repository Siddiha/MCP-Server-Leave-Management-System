from mcp.server.fastmcp import FastMCP
from datetime import date
from typing import List

# In-memory mock database with 20 leave days to start
employee_leaves = {
    "E001": {"balance": 18, "history": ["2024-12-25", "2025-01-01"]},
    "E002": {"balance": 20, "history": []}
}

# Create MCP server
mcp = FastMCP("LeaveManager")

# Tool: Check Leave Balance
@mcp.tool()
def get_leave_balance(employee_id: str) -> str:
    """Check how many leave days are left for the employee"""
    data = employee_leaves.get(employee_id)
    if data:
        return f"{employee_id} has {data['balance']} leave days remaining."
    return "Employee ID not found."

# Tool: Apply for Leave with specific dates
@mcp.tool()
def apply_leave(employee_id: str, leave_dates: List[str]) -> str:
    """
    Apply leave for specific dates (e.g., ["2025-04-17", "2025-05-01"])
    """
    if employee_id not in employee_leaves:
        return "Employee ID not found."

    if not leave_dates:
        return "Please give at least one date."

    # Each date must be a real date in YYYY-MM-DD format and not in the past
    for leave_date in leave_dates:
        try:
            parsed = date.fromisoformat(leave_date)
        except ValueError:
            return f"Invalid date '{leave_date}'. Use the format YYYY-MM-DD."
        if parsed < date.today():
            return f"Cannot apply leave for a past date: {leave_date}."

    # The same date can't be listed twice in one request
    if len(set(leave_dates)) != len(leave_dates):
        return "Duplicate dates in your request. Each date can only be listed once."

    # The same date can't be booked twice across requests
    history = employee_leaves[employee_id]["history"]
    already_taken = [d for d in leave_dates if d in history]
    if already_taken:
        return f"Leave already applied for: {', '.join(already_taken)}."

    requested_days = len(leave_dates)
    available_balance = employee_leaves[employee_id]["balance"]

    if available_balance < requested_days:
        return f"Insufficient leave balance. You requested {requested_days} day(s) but have only {available_balance}."

    # Deduct balance and add to history
    employee_leaves[employee_id]["balance"] -= requested_days
    history.extend(leave_dates)

    return f"Leave applied for {requested_days} day(s). Remaining balance: {employee_leaves[employee_id]['balance']}."


# Tool: Leave history
@mcp.tool()
def get_leave_history(employee_id: str) -> str:
    """Get leave history for the employee"""
    data = employee_leaves.get(employee_id)
    if data:
        history = ', '.join(data['history']) if data['history'] else "No leaves taken."
        return f"Leave history for {employee_id}: {history}"
    return "Employee ID not found."

# Resource: Greeting
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! How can I assist you with leave management today?"

if __name__ == "__main__":
    mcp.run()