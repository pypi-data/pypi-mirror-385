from fastmcp import FastMCP, Context
from fastmcp.prompts.prompt import PromptMessage, TextContent
from mcts_gen.services.ai_gp_simulator import AiGpSimulator

# 1. Create the core FastMCP server instance
mcp = FastMCP(
    name="mcts_gen_simulator_server"
)

# 2. Create an instance of our stateful simulator class.
#    The simulator's __init__ method will register its own methods as tools.
simulator = AiGpSimulator(mcp)

# 3. Define the built-in agent prompt using a decorator
@mcp.prompt(
    name="mcts_autonomous_search",
    description="Autonomous MCTS strategist workflow that emulates AGENTS.md content",
)
def mcts_autonomous_search(goal: str, ctx: Context) -> list[PromptMessage]:
    """
    Provides the AI with the standard workflow for running an MCTS search.
    This is the code-based version of the old AGENTS.md file.
    """
    intro = f"You are an autonomous MCTS strategist. Your goal is to find the optimal move. Task: {goal}"
    workflow = [
        "1. Call `reinitialize_mcts` with the game details.",
        "2. Implement a loop in your reasoning process for a fixed number of iterations.",
        "3. In each iteration, call `get_possible_actions` and then `run_mcts_round`.",
        "4. Analyze the `simulation_stats` from the output to refine your strategy for the next iteration.",
        "5. After your loop terminates, call `get_best_move` to get the final result."
    ]
    detail = "\n".join(workflow)
    return [
        PromptMessage(role="user", content=TextContent(type="text", text=intro)),
        PromptMessage(role="user", content=TextContent(type="text", text=detail)),
    ]

# 4. Run the server
if __name__ == "__main__":
    mcp.run()