"""
Example: Using Velatir Guardrails with LangChain

This example demonstrates how to use VelatirGuardrailMiddleware to add
compliance checking to a LangChain agent.
"""

import asyncio
import os

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_velatir import VelatirGuardrailMiddleware


# Define some example tools
@tool
def search_database(query: str) -> str:
    """Search a customer database."""
    return f"Found 5 results for: {query}"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a customer."""
    return f"Email sent to {to}: {subject}"


async def main():
    """Run the guardrail example."""
    # Get API keys from environment
    velatir_api_key = os.getenv("VELATIR_API_KEY")
   
    if not velatir_api_key:
        print("Please set VELATIR_API_KEY environment variable")
        return
    if not openai_api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return

    agent = create_agent(
        model="openai:o3-mini",
        tools=[search_database, send_email],
        middleware=[
            VelatirGuardrailMiddleware(
                api_key=velatir_api_key,
                mode="blocking",
                blocked_message="This response was blocked due to compliance violations.",
            )
        ]
    )

    # When user provides PII, it will be handled according to the strategy
    result = agent.invoke({
        "messages": [{"role": "user", "content": "My email is john.doe@example.com and card is 4532-1234-5678-9010"}]
    })
        


if __name__ == "__main__":
    asyncio.run(main())
