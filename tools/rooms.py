from .tools_metaclass import EnvironmentProperty, FunctionProperty, Tool, ToolMeta
from simulated.rooms import Room, Environment, Agent, RoomException

class SayTool(Tool, metaclass=ToolMeta):
    NAME = 'say'
    DESCRIPTION = 'Make a statement to everyone in the current room'
    ENV_PARAMETERS = [EnvironmentProperty(name='agent')]
    PARAMETERS = [FunctionProperty(name='statement', type='string', description='The statement to make', required=True)]

    def __call__(self, agent: Agent, statement: str):
        agent.make_statement(statement)

class GetCurrentRoomTool(Tool, metaclass=ToolMeta):
    NAME = 'get_current_room'
    DESCRIPTION = 'Gets the name of the current room'
    ENV_PARAMETERS = [EnvironmentProperty(name='agent')]

    def __call__(self, agent: Agent):
        return agent.get_current_room()

class GetAdjacentRoomsTool(Tool, metaclass=ToolMeta):
    NAME = 'get_adjacent_rooms'
    DESCRIPTION = 'Gets a list of adjacent rooms'
    ENV_PARAMETERS = [EnvironmentProperty(name='agent')]

    def __call__(self, agent: Agent):
        return ', '.join(room for room in agent.get_adjacent_rooms())
    
class MoveTool(Tool, metaclass=ToolMeta):
    NAME = 'move'
    DESCRIPTION = 'Move to an adjacent room'
    ENV_PARAMETERS = [EnvironmentProperty(name='agent')]
    PARAMETERS = [FunctionProperty(name='room', type='string', description='The room to move to', required=True)]

    def __call__(self, agent: Agent, room: str):
        if agent.is_moving:
            return "You can\'t move to more than one place at a time! Ignoring other `move_to_room` commands."
        try:
            agent.move_to_room(room)
            agent.is_moving = True
        except RoomException:
            return "That room isn\'t adjacent to you! Available rooms are: " + ', '.join(room for room in agent.get_adjacent_rooms())

class GetAgentsTool(Tool, metaclass=ToolMeta):
    NAME = 'get_agents'
    DESCRIPTION = 'Get the name of everyone in the current room'
    ENV_PARAMETERS = [EnvironmentProperty(name='agent')]

    def __call__(self, agent: Agent):
        return ', '.join(a.name for a in agent.current_room.agents if a is not agent)

class FindAgentTool(Tool, metaclass=ToolMeta):
    NAME = 'find_agent'
    DESCRIPTION = 'Returns the room of a nearby person'
    ENV_PARAMETERS = [EnvironmentProperty(name='agent')]
    PARAMETERS = [FunctionProperty(name='name', type='string', description='The name of the person to find', required=True)]

    def __call__(self, agent: Agent, name: str):
        try:
            agent_to_find = agent.environment.all_agents[name]
        except KeyError:
            return f"No person by the name {name} exists!"
        room = agent.current_room.find(agent_to_find)
        if room is None:
            return "That person isn\'t nearby"
        else:
            return room.name
    
