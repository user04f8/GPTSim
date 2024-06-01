from typing import Dict, Set, Optional, Iterable

from uuid import UUID, uuid4

class RoomException(Exception):
    pass

class Room:
    def __init__(self, name: str, environment: 'Optional[Environment]' = None, connect_to = set()):
        self.name = name
        self.adjacent_rooms: Set[Room] = set()
        self.agents: Set[Agent] = set()
        for room in connect_to:
            self.connect(room)
        if environment is not None:
            environment.all_rooms_by_name[name] = self

    def __str__(self):
        return self.name

    def add_agent(self, agent):
        self.agents.add(agent)

    def remove_agent(self, agent):
        self.agents.remove(agent)

    def make_statement(self, source, statement):
        for agent in self.agents:
            if agent is not source:
                agent.hear_statement(statement)

    def find(self, agent: 'Agent') -> Optional['Room']:
        if agent in self.agents:
            return self
        for room in self.adjacent_rooms:
            if agent in room.agents:
                return room
        return None

    def connect(self, room: 'Room'):
        self.adjacent_rooms.add(room)
        room.adjacent_rooms.add(self)

    def get_adjacent_room_names(self):
        return {room.name for room in self.adjacent_rooms}
    
    def get_room_if_adjacent(self, room_name):
        room = {room for room in self.adjacent_rooms if room.name == room_name}
        if len(room) == 0:
            raise RoomException(f'Room not found: {room_name}')
            # self.rooms[room_name] = Room(room_name)
        elif len(room) >= 2:
            print(f'WARN: Duplicate rooms with same name: {room_name} (choosing arbitrary)')

        return room.pop()

class Environment:
    def __init__(self, default='DEFAULT'):
        self.default_room = Room(default)
        self.all_rooms_by_name: Dict[str, Room] = {default: self.default_room}
        self.all_agents_by_name: Dict[str, Agent] = {}

        self.env_name: str = ''

    # def get_agent(self, agent_name: str) -> "Agent":
    #     return self.all_agents[agent_name]

class TownEnvironment(Environment):
    def __init__(self, town_name: str = 'Townton', rooms: Iterable[str] = ['Village']):
        super().__init__(default='Town Square')
        self.env_name = town_name
        for room in rooms:
            Room(name=room, environment=self, connect_to={self.default_room})

class Agent:

    def __init__(self, name: str, environment: Environment):
        self.name = name
        self.current_room: Room = environment.default_room
        self.current_room.add_agent(self)
        self.heard_statements = []
        self.environment = environment
        self.environment.all_agents_by_name[self.name] = self

        self.is_moving = False

    def tick_status(self):
        self.is_moving = False

    def get_current_room(self):
        return self.current_room.name

    def get_adjacent_rooms(self):
        return self.current_room.get_adjacent_room_names()

    def move_to_room(self, room_name: str):
        new_room = self.current_room.get_room_if_adjacent(room_name)

        self.current_room.make_statement(self, f"{self.name} exited to the {room_name}")
        self.current_room.remove_agent(self)
        self.current_room = new_room
        new_room.add_agent(self)
        new_room.make_statement(self, f"{self.name} joined the {room_name}")

    def make_statement(self, statement):
        self.current_room.make_statement(self, f'{self.name}: {statement}')

    def hear_statement(self, statement):
        self.heard_statements.append(statement)

    def read_heard_statements(self):
        statements = self.heard_statements
        self.heard_statements = []
        return statements
