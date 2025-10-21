import pathlib

from dotenv import load_dotenv
from freeplay_python_langgraph import FreeplayLangGraph
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

current_dir = pathlib.Path(__file__).parent
env_path = current_dir.parent.parent.parent / ".env"
load_dotenv(str(env_path))

# Ensure API keys are set in your environment
# OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY

freeplay = FreeplayLangGraph()


@tool
def weather_of_location(location: str):
    """Get the weather of a location."""
    return f"It's 60 degrees and foggy in {location}."


def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


def create_call_model(prompt_name: str):
    """Factory function to create call_model function for a specific prompt."""

    def call_model(state: MessagesState):
        response = freeplay.invoke(
            prompt_name=prompt_name,
            variables={"location": "San Francisco"},
            history=state["messages"],
            tools=tools,
        )
        return {"messages": [response]}

    return call_model


tools = [weather_of_location]
tool_node = ToolNode(tools)


def create_workflow(prompt_name: str):
    """Create a LangGraph workflow for a specific prompt."""
    # Define a new graph
    workflow = StateGraph(MessagesState)

    # Create call_model function for this prompt
    call_model = create_call_model(prompt_name)

    # Define the two nodes we will cycle between
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # Set the entrypoint as `agent`
    workflow.set_entry_point("agent")

    # Add conditional edge
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )

    # Add normal edge from `tools` to `agent`
    workflow.add_edge("tools", "agent")

    # Initialize memory to persist state between graph runs
    checkpointer = MemorySaver()

    # Compile the workflow
    return workflow.compile(checkpointer=checkpointer)


def test_prompt(prompt_name: str, model_provider: str):
    """Test a specific prompt with the LangGraph workflow."""
    print(f"\n{'='*60}")
    print(f"Testing {model_provider} with prompt: {prompt_name}")
    print(f"{'='*60}")

    app = create_workflow(prompt_name)

    try:
        final_state = app.invoke(
            {
                "messages": [
                    HumanMessage(
                        content="what is the weather in sf? And what about LA?"
                    )
                ]
            },
            config={"configurable": {"thread_id": f"{prompt_name}_conversation"}},
        )
        if final_state and "messages" in final_state and final_state["messages"]:
            print(f"✓ Success! Final response: {final_state['messages'][-1].content}")
        else:
            print("✗ No final message content found or final_state is not as expected.")
            print(f"Final state: {final_state}")
    except Exception as e:
        print(f"✗ Error invoking LangGraph app: {e}")


# Test all three prompts
if __name__ == "__main__":
    print("Testing multiple Freeplay prompts with different model providers")

    # Test OpenAI prompt
    test_prompt("my-openai-prompt", "OpenAI")

    # Test Anthropic prompt
    test_prompt("my-anthropic-prompt", "Anthropic")

    # Test Google prompt
    test_prompt("my-google-prompt", "Google")

    print(f"\n{'='*60}")
    print("All tests completed!")
    print(f"{'='*60}")
