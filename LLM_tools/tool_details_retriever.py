from llama_index.llms.openai import OpenAI
from llama_index.core.indices.struct_store import JSONQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
import json

class ToolDetailsRetriever:
    json_path = "/home/bili/Desktop/gen_env_llm/create/tool_documentation.json"
    with open(json_path, 'r') as file:
        json_value = json.load(file)
    
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "description": "Schema for describing different tools",
        "type": "object",
        "properties": {
            "tools": {
                "description": "List of different tools",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "tool_id": {
                            "description": "Unique identifier for the tool",
                            "type": "integer",
                        },
                        "angle": {
                            "description": "Angle of the tool object with the negative x-axis. Value is in radians",
                            "type": "float",
                        },
                        "elasticity": {
                            "description": "Elasticity of the tool object, describing how bouncy it is",
                            "type": "float",
                        },
                        "tool_type": {
                            "description": "The type of physical object that the tool defines could be a Ramp, Trampoline, Fan, Cannon, etc. The names start with capitalized first letter",
                            "type": "string",
                        },
                        "extra_info": {
                            "description": "Gives more information about the tool, properties vary depending on tool type",
                            "type": "object",
                            "properties": {
                                "friction": {
                                    "description": "Defines friction coefficient of the tool object",
                                    "type" : "float",
                                },
                                "max_angle": {
                                    "description": "Defines maximum angle a hinge like object such as a see saw can turn in radians",
                                    "type" : "float",
                                },
                                "on_left": {
                                    "description": "Defines whether or not the ball in a see saw like object is placed on the left",
                                    "type" : "boolean",
                                },
                                "ball_mass": {
                                    "description": "Defines the mass of the ball placed on a see saw like object",
                                    "type" : "float",
                                },
                                "force": {
                                    "description": "Defines the force of a propellant type object such as a fan or a cannon",
                                    "type" : "float",
                                },
                            }
                        }
                    },
                    "required": ["tool_id", "tool_type"],
                },
            },
        },
        "required": ["tools"]
    }

    @classmethod
    def get_tool(cls):
        # llm = OpenAI(model="gpt-3.5-turbo-0613")
        llm = OpenAI(model="gpt-4")
        raw_json_query_engine = JSONQueryEngine(
            json_value=cls.json_value,
            json_schema=cls.json_schema,
            llm=llm,
            synthesize_response=False,
        )
        tool = QueryEngineTool(
            query_engine=raw_json_query_engine,
            metadata=ToolMetadata(
                name="tool_details_retriever_raw",
                description=(
                    "Provides information in raw json format about the different create game tool objects that are available for use."
                    "Use plain text to describe some properties of tools you are interested in to get a JSON response detailing the properties of all matching tools."
                ),
            ),
        )
        return tool

