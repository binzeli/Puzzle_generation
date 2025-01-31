## A Multi-Agent Collaborative Reasoning Framework for Generating Physics Puzzles

We utilized the CREATE 2D physics puzzle environment as a testbed for LLM-driven 2D physics puzzle generation. We devised a multi-agent ReAct framework that integrates reasoning with action feedback loops. This framework enables LLMs to interact dynamically with their environment, adapting actions based on real-time feedback. By leveraging the distinct expertise of individual agents, our framework preserves the complex reasoning pathways required for solving and generating puzzles, which was impossible with basic prompting or single-agent approaches.

## Example output from LLM
An example of the response from LLM is provided in [example_output](./example_output).

## Prompts
The context and step-by-step guidance provided to the ReAct agent can be found in the [utils](./utils) folder.
Specifically, the following four files contain the context for the ReAct approaches:
- `system_header_prompt_puzzle_generate_multiple_agents.py`
- `system_header_prompt_puzzle_generate_one_agent.py`
- `system_header_prompt_puzzle_solve_multiple_agents.py`
- `system_header_prompt_puzzle_solve_one_agent.py`

The prompt for the Designer and Solver agent are in the [LLM_agents](./LLM_agents) folder.

## Actions that ReAct agent have access to
The functions for all actions that an ReAct agent have access to are in the [LLM_tools](./LLM_tools) folder.
- `puzzle_generate_multi_agents.py`
- `puzzle_generate_one_agent.py`
- `puzzle_sol_multi_agents.py`
- `puzzle_sol_one_agent.py`

## Run Experiments
The files for running the three LLM approaches are in the [LLM_agents](./LLM_agents) folder. Each of the three approaches has two files corresponding to the puzzle solution task and puzzle generation task.

## Experiment Results
The simulation images for each of the five attempts for all three approaches can be found in the [Experiment Results](./Experiment%20Results) folder.
