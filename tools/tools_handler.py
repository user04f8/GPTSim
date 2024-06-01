import json
from dataclasses import dataclass
from typing import List

from .tools_metaclass import Tool, ToolMeta, EnvironmentProperty, FunctionProperty

TOOL_COMPLETED_DEFAULT = 'Completed'

@dataclass
class ToolCallFunction:
    name: str
    arguments: str  # str-ified json

@dataclass
class ToolCall:
    function: ToolCallFunction

def handle_tool_call(tool_call: ToolCall, env: dict) -> dict:
    tool_name = tool_call.function.name
    
    try:
        funct = ToolMeta.functions[tool_name]
        
        tool_args = json.loads(tool_call.function.arguments)
        env_args = []
        for property in ToolMeta.function_properties[tool_name]:
            env_args.append(
                env.get(property.name, property.default)
            )
            
        funct_out = funct(*env_args, **tool_args)
        if funct_out is not None:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool", 
                "name": tool_name,
                "content": funct_out
            }
        return {
                "tool_call_id": tool_call.id,
                "role": "tool", 
                "name": tool_name,
                "content": TOOL_COMPLETED_DEFAULT
            }
    except Exception as e:
        print(f'WARNING: encountered exception {e} while running tool {tool_name}')
        return {
            "tool_call_id": tool_call.id,
            "role": "tool", 
            "name": tool_name,
            "content": f"Error: {e}"
        }

def handle_tool_calls(tool_calls, env: dict) -> List[dict]:
    funct_resps = []

    if tool_calls:
        for tool_call in tool_calls:
            funct_resp = handle_tool_call(tool_call, env)
            funct_resps.append(funct_resp)
    
    return funct_resps
    