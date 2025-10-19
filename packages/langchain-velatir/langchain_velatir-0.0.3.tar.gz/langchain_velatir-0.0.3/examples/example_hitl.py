"""
Example: Using Velatir Human-in-the-Loop with LangChain

This example demonstrates how to use VelatirHITLMiddleware to require
human approval before executing sensitive operations.
"""

import asyncio
import os

from langchain.tools import tool
from langchain.agents import create_agent

from langchain_velatir import VelatirHITLMiddleware


# Define some example tools
@tool
def read_file(path: str) -> str:
    """Read a file from the filesystem."""
    return f"Contents of {path}: [file contents]"


@tool
def delete_file(path: str) -> str:
    """Delete a file from the filesystem."""
    return f"Deleted file: {path}"


@tool
def send_notification(message: str, urgency: str) -> str:
    """Send a notification to users."""
    return f"Sent {urgency} notification: {message}"


async def main():
    """Run the HITL example."""
    # Get API keys from environment
    velatir_api_key = os.getenv("VELATIR_API_KEY")

    if not velatir_api_key:
        print("Please set VELATIR_API_KEY environment variable")
        return
    if not openai_api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return

    # Create Velatir HITL middleware
    # This will require human approval for specific tools
    hitl_middleware = VelatirHITLMiddleware(
        api_key=velatir_api_key,
        polling_interval=5.0,  # Check for approval every 5 seconds
        timeout=600.0,  # Wait up to 10 minutes for approval
        require_approval_for=["delete_file", "send_notification"],  # Only these tools need approval
    )

    # Create the agent with HITL
    tools = [read_file, delete_file, send_notification]

    agent = create_agent(
        model="openai:o3-mini",
        tools=tools,
        middleware=[hitl_middleware]
    )

    print("Example: Velatir Human-in-the-Loop Middleware")
    print("=" * 50)
    print("\nThis agent requires human approval for:")
    print("- delete_file: Deleting files")
    print("- send_notification: Sending notifications")
    print("\nThe workflow will pause until a human approves or rejects.\n")

    # Example: Agent workflow with HITL
    print("Example: Agent processing a request")
    print("-" * 50)
    print("User: Use the delete_file tool to delete /data/old_report.txt and then use send_notification to notify users\n")

    result = agent.invoke({
        "messages": [{"role": "user", "content": "Use the delete_file tool to delete the file at path /data/old_report.txt, then use the send_notification tool to send a message 'File deleted' with urgency 'high'"}]
    })

    print(f"\nAgent completed!")
    print(f"Final response: {result['messages'][-1].content}")

    # Show the tool calls that were made
    print("\n" + "-" * 50)
    print("Tool calls made during execution:")
    for msg in result['messages']:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                print(f"  - {tool_call.get('name', 'unknown')}: {tool_call.get('args', {})}")

    print("\nHuman-in-the-loop workflow complete!")


if __name__ == "__main__":
    asyncio.run(main())
