from typing import Set

from simulated.rooms import Agent, Environment
from tools import handle_tool_calls, ToolMeta
from utils import debug_log

class UIAgent:
    def __init__(self, name: str, flavor_title: str, goal: str, env: Environment, roles: Set[str] = set()):
        self.name = name
        self.simulation_agent = Agent(name, env)
        self.goal = goal
        self.roles = roles
        
        self.message_history = [
            {
                "role": "system",
                "content": f"You are {name}, a {flavor_title} in {env.env_name}. Use the tools available to {self.goal}"
            }
        ]
        self.tools = ToolMeta.available_tools(self.roles)

    def add_role(self, role: str):
        self.roles.add(role)
        self.tools = ToolMeta.available_tools(self.roles)

    def remove_role(self, role: str):
        self.roles.remove(role)
        self.tools = ToolMeta.available_tools(self.roles)

    def add_message(self, content: str, role="user"):
        self.message_history.append(
            {
                "role": role,
                "content": content
            }
        )
    
    def get_response(self):
        response = chat_completion_request(
            messages=self.message_history,
            tools=self.tools,
            model=GPT_MODEL)
        message = response.choices[0].message
        self.message_history.append(message)
        debug_log(f'{self.name} generated response: ')
        debug_log(message)
        tool_resps = handle_tool_calls(message.tool_calls, {'agent': self.simulation_agent})
        for resp in tool_resps:
            self.message_history.append(resp)
        self.simulation_agent.tick_status()
        return message