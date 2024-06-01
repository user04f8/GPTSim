

import asyncio
from async_gpt import AsyncGPTAgent
from render import PygameView
from simulated.rooms import Room, TownEnvironment

from utils import debug_log, await_text_input

def build_env():

    town_env = TownEnvironment('Townton', ['Inn', 'Market'])

    Room('Winery', town_env, connect_to={town_env.default_room, Room('Cellar', town_env)})
    Room('Palace', town_env, connect_to={town_env.default_room, Room('Throne Room', town_env), Room('Dungeon', town_env)})

    return town_env

def build_agents(env):

    agents = [
        AsyncGPTAgent('Alice', 'villager', 'have a 1-on-1 conversation with each resident of Townton', env, {'villager'}),
        AsyncGPTAgent('Bob', 'villager', 'direct everyone in Townton to go to the throne room within the palace', env, {'villager'}),
        AsyncGPTAgent('Eve', 'merchant', 'recruit someone in Townton to stay at the market', env, {'villager'}),
        ]

    for agent in agents:
        agent.add_message("Messages other people send you look like this: \n" +
            "Person: This is a message!" +
            " (Use the `say` tool to respond to these messages.)")
        agent.add_message(f"You're currently in the {agent.simulation_agent.current_room.name}, but you can move to these: {', '.join(room.name for room in agent.simulation_agent.current_room.adjacent_rooms)}" +
            " (Use the `move` tool to move around.)")

    return agents

async def main():
    env = build_env()
    agents = build_agents(env)
    render_event = asyncio.Event()
    PygameView(env).start_loop(render_event)
    
    input_ = None
    while input_ != 'q':
        # pre_updates = [agent.update_pre() for agent in agents]
        # _ = await asyncio.gather(*pre_updates)
        # updates = [agent.update() for agent in agents]
        # _ = await asyncio.gather(*updates)

        render_event.set()

        # print("Press Enter to continue...")
        # input_ = await await_text_input()



if __name__ == '__main__':
    asyncio.run(main())
