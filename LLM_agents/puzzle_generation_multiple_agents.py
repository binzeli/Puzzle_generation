import os
import replicate
os.environ["REPLICATE_API_TOKEN"] = "r8_LMZoyy9Hh5CebwLEVDl3Sg8KWj5rxvB3xv6YQ"
os.environ['OPENAI_API_KEY'] = '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'
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
 )
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from LLM_tools.tool_details_retriever import ToolDetailsRetriever
from LLM_tools.puzzle_generate_multi_agents import CreateEnv

from llama_index.llms.openai import OpenAI
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.settings import Settings

from llama_index.core.agent.react_multimodal.step import (
    MultimodalReActAgentWorker,
)
from llama_index.core.agent import AgentRunner
from llama_index.core.multi_modal_llms import MultiModalLLM
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.agent.react.formatter import ReActChatFormatter
from utils.system_header_prompt_puzzle_generate_multiple_agents import REACT_MM_CREATE_SYSTEM_HEADER
from llama_index.core.agent import Task
from llama_index.core.schema import ImageDocument

Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")

tool_details_retriever = ToolDetailsRetriever.get_tool()
create_env = CreateEnv()
create_env_tools = create_env.to_tool_list()




mm_llm = OpenAIMultiModal(model="gpt-4o-2024-05-13", max_new_tokens=1000)

# Option 2: Initialize AgentRunner with OpenAIAgentWorker
react_step_engine = MultimodalReActAgentWorker.from_tools(
    create_env_tools,

    multi_modal_llm=mm_llm,
    react_chat_formatter=ReActChatFormatter(system_header=REACT_MM_CREATE_SYSTEM_HEADER),
    verbose=True,
    max_iterations=100
)
agent = AgentRunner(react_step_engine)

query_str = ("Design a puzzle where the blue ball on the right needs to push the red ball down to the goal on the left.")



image_document = ImageDocument(image_path="/home/bili/Desktop/scenario_generation_llm/puzzle_solution_scenarios/example_puzzle.jpg")

task = agent.create_task(
    query_str,
    extra_state={"image_docs": [image_document]},
)


def execute_step(agent: AgentRunner, task: Task):
    step_output = agent.run_step(task.task_id)
    if step_output.is_last:
        response = agent.finalize_response(task.task_id)
        print(f"> Agent finished: {str(response)}")
        return response
    else:
        return None


def execute_steps(agent: AgentRunner, task: Task):
    response = execute_step(agent, task)
    while response is None:
        response = execute_step(agent, task)
    return response

response = execute_steps(agent, task)
print(response)
print(create_env.env_json)
print("\n")

