import asyncio
from typing import Set, List, Dict, Tuple, Optional, Literal
from dataclasses import dataclass


from simulated.rooms import Agent, Environment
from tools import handle_tool_calls, ToolMeta, ToolCall
from utils import debug_log, warn_log

@dataclass
class AgentMessage:
    content: str
    role: Literal["assistant"]
    tool_calls: List[ToolCall]

Message = Dict[str, str] | AgentMessage

class AgentWrapper:
    TYPE = ''

    def __init__(self, name: str, flavor_title: str, goal: str, env: Environment, roles: Set[str] = set()):
        self.name = name
        self.simulation_agent = Agent(name, env)
        self.goal = goal
        self.roles = roles
        
        self.message_history: List[Message] = [
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

    def get_response(self) -> AgentMessage:
        return AgentMessage(content="",
                            tool_calls=[])
    
    def update_pre(self):
        self.add_message('\n'.join(self.simulation_agent.read_heard_statements()))

    def update_with_response(self, message: AgentMessage):
        self.message_history.append(message)
        if message.content is not None:
            warn_log(f'{self.name}[{self.TYPE}] generated nonempty content "{message.content}"')
        debug_log(f'{self.name}[{self.TYPE}] generated response: ')
        debug_log(message)
        tool_resps = handle_tool_calls(message.tool_calls, {'agent': self.simulation_agent})
        for resp in tool_resps:
            self.message_history.append(resp)
        
        self.simulation_agent.tick_status()
    
    def update(self):
        self.update_with_response(self.get_response())

class AsyncAgentWrapper(AgentWrapper):
    async def update_pre(self):
        self.add_message('\n'.join(self.simulation_agent.read_heard_statements()))

    async def update(self):
        # to guaruntee concurrency run update_pre() separately
        self.update_with_response(await self.get_response())