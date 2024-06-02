import asyncio
import threading
from typing import List

from async_gpt import AsyncGPTAgent, AsyncAgentWrapper
from simulated.rooms import Room, Environment, TownEnvironment
from utils import debug_log, await_text_input, threadsafe_start_pygame_loop

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
    data_queue = asyncio.Queue()
    render_event = asyncio.Event()
    update_agents_event = asyncio.Event()
    update_rooms_event = asyncio.Event()
    stop_event = asyncio.Event()
    env = build_env()
    agents = build_agents(env)

    pygame_thread = threading.Thread(target=threadsafe_start_pygame_loop, args=(env, data_queue, render_event, update_agents_event, update_rooms_event, stop_event), daemon=True)
    pygame_thread.start()

    try:

        # agents[0].simulation_agent.move_to_room('Inn')
        # new = AsyncGPTAgent('New', '', '', env)
        # update_agents_event.set()
        render_event.set()
        
        await asyncio.sleep(0.5)



        input_ = None
        while input_ != 'q':
            pre_updates = [agent.update_pre() for agent in agents]
            _ = await asyncio.gather(*pre_updates)
            updates = [agent.update() for agent in agents]
            _ = await asyncio.gather(*updates)

            render_event.set()

            await asyncio.sleep(0.5)

            # print("Press Enter to continue...")
            # input_ = await await_text_input()
    finally:
        stop_event.set()
        pygame_thread.join(5.0)

if __name__ == '__main__':
    asyncio.run(main())
