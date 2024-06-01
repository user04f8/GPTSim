import threading

from tools import ToolMeta
from gpt import GPTAgent
from render import PygameView
from simulated.rooms import Agent, Environment, Room, TownEnvironment

from utils import debug_log

town_env = TownEnvironment('Townton', ['Inn', 'Market'])

Room('Winery', town_env, connect_to={town_env.default_room, Room('Cellar', town_env)})
Room('Palace', town_env, connect_to={town_env.default_room, Room('Throne Room', town_env), Room('Dungeon', town_env)})

agents = [
    GPTAgent('Alice', 'villager', 'have a 1-on-1 conversation with each resident of Townton', town_env, {'villager'}),
    GPTAgent('Bob', 'villager', 'direct everyone in Townton to go to the throne room within the palace', town_env, {'villager'}),
    GPTAgent('Eve', 'merchant', 'recruit someone in Townton to stay at the market', town_env, {'villager'}),
    # GPTAgent('Charlie', 'student', 'find a job in Townton', town_env, {'villager'}),
    # GPTAgent('Winston', 'noble', 'buy something extravagant', town_env, {'villager'})
    ]

# agents[0].simulation_agent.current_room = town_env.all_rooms['Market']
# agents[2].simulation_agent.current_room = town_env.all_rooms['Market']


for agent in agents:
    agent.add_message("Messages other people send you look like this: \n" +
        "Person: This is a message!" +
        " (Use the `say` tool to respond to these messages.)")
    agent.add_message(f"You're currently in the {agent.simulation_agent.current_room.name}, but you can move to these: {', '.join(room.name for room in agent.simulation_agent.current_room.adjacent_rooms)}" +
        " (Use the `move` tool to move around.)")


# VIEW INIT

view = PygameView(town_env)
render_thread = threading.Thread(name='render_thread', target=view.loop)
render_thread.start()

input_ = input("Press Enter if this render is OK...")

# MAIN LOOP

input_ = None
while input_ != 'q':
    for agent in agents:
        agent.update()
        
    debug_log('---')
    input_ = input("Press Enter to continue...")






for agent in agents:
    print(agent.message_history)
