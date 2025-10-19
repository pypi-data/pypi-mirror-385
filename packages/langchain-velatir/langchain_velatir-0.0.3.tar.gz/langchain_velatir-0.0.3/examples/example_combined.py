"""
Example: Combining Guardrails and Human-in-the-Loop

This example demonstrates how to use both VelatirGuardrailMiddleware and
VelatirHITLMiddleware together for comprehensive governance.
"""

import asyncio
import os

from langchain.tools import tool
from langchain.agents import create_agent

from langchain_velatir import VelatirGuardrailMiddleware, VelatirHITLMiddleware


# Define example tools
@tool
def process_customer_data(customer_id: str, operation: str) -> str:
    """Process customer data with specified operation."""
    return f"Processed data for customer {customer_id}: {operation}"


@tool
def generate_report(report_type: str, filters: dict) -> str:
    """Generate a business report."""
    return f"Generated {report_type} report with filters: {filters}"


@tool
def execute_transaction(amount: float, account: str) -> str:
    """Execute a financial transaction."""
    return f"Executed transaction: ${amount} to {account}"


async def main():
    """Run the combined example."""
    # Get API keys from environment
    velatir_api_key = os.getenv("VELATIR_API_KEY")

    if not velatir_api_key:
        print("Please set VELATIR_API_KEY environment variable")
        return
    if not openai_api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return

    # Create both middleware components
    guardrail_middleware = VelatirGuardrailMiddleware(
        api_key=velatir_api_key,
        mode="blocking",
        blocked_message="This response was blocked due to compliance violations.",
    )

    hitl_middleware = VelatirHITLMiddleware(
        api_key=velatir_api_key,
        polling_interval=5.0,
        timeout=600.0,
        require_approval_for=["process_customer_data", "execute_transaction"],
    )

    # Create the agent with both middleware components
    tools = [process_customer_data, generate_report, execute_transaction]

    agent = create_agent(
        model="openai:o3-mini",
        tools=tools,
        middleware=[guardrail_middleware, hitl_middleware]
    )

    print("Example: Combined Guardrails + Human-in-the-Loop")
    print("=" * 50)
    print("\nThis agent has:")
    print("\n1. GUARDRAILS (after_agent)")
    print("\n2. HUMAN-IN-THE-LOOP (before_tool)")
    print("\n3. LAYERED PROTECTION:")
    print("   - HITL checks BEFORE tool execution")
    print("   - Guardrails check AFTER agent response")
    print("   - Complete governance coverage\n")

    # Example workflow
    print("Example Workflow:")
    print("-" * 50)
    print("\nRunning agent with combined guardrails and HITL middleware...\n")

    # Run a comprehensive example that exercises both middleware
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Please process customer data for customer CUST-001 to update their email address to john.doe@example.com"}]
    })

    print("\n" + "=" * 50)
    print("Agent completed!")
    print(f"Final response: {result['messages'][-1].content}")
    print("\n" + "=" * 50)
    print("Complete governance achieved!")
    print("- Human oversight for sensitive operations (HITL)")
    print("- Automated compliance checking for all responses (Guardrails)")
    print("- Audit trail in Velatir dashboard")


if __name__ == "__main__":
    asyncio.run(main())
