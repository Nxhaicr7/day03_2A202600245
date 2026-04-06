import sys
sys.path.insert(0, ".")

from src.agent.agent import ReActAgent
from src.core.openai_provider import OpenAIProvider
from src.tools.tool_registry import TOOLS


def main():
    llm = OpenAIProvider()
    agent = ReActAgent(llm=llm, tools=TOOLS)

    print("=" * 60)
    print("  ReAct Research Agent")
    print("  Type your question and press Enter.")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    while True:
        try:
            prompt = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not prompt:
            continue
        if prompt.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        print("\n" + "-" * 60)
        result = agent.run(prompt)
        print("-" * 60)
        print(f"\nAgent:\n{result}")


if __name__ == "__main__":
    main()
