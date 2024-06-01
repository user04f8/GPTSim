import asyncio
import threading
import pygame
from pygame import gfxdraw  # need explicit import for gfxdraw
import sys
from math import hypot, sin, cos, atan2
import colorsys
from typing import Dict, Tuple
import hashlib

# from termcolor import cprint



from simulated.rooms import Environment, Room
from render_utils import optimize_room_positions

COLORS = {
    'bg': (220, 220, 220),
    'edges': (20, 20, 20),
    'text': (20, 20, 20)
}

def rgb_float_to_int(cs):
    return tuple(int(255 * c) for c in cs)

def gen_color(r: Room):
    # hash_object = hashlib.sha256(s.encode())
    # hex_dig = hash_object.hexdigest()
    
    # # Convert the hexadecimal hash to an integer
    # int_value = int(hex_dig, 16)
    
    # # Normalize the integer value to a float between 0 and 1
    # max_value = 2**256 - 1  # Maximum value for a SHA-256 hash
    int_value = sum(ord(room.name[0]) - ord('A') for room in r.adjacent_rooms) + ord(r.name[0]) - ord('A')
    max_value = (len(r.adjacent_rooms) + 1) * (ord('Z') - ord('A'))
    hue = int_value / max_value
    return rgb_float_to_int(colorsys.hls_to_rgb(hue, 0.8, 0.8))

class Colorify(dict):
    def get(self, key):
        if key not in self:
            self[key] = gen_color(key)
        return self[key]
    
node_colors = Colorify()

class RenderData:
    room_positions: Dict[str, Tuple[int, int]] = {}
    agent_colors: Dict[str, Tuple[int, int, int]] = {}

class PygameView:
    def __init__(self, environment: Environment):
        pygame.init()
        self.screen_width, self.screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen_width //= 2
        self.screen_height //= 2
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), flags=pygame.RESIZABLE)
        pygame.display.set_caption('Environment Visualization')

        self.environment = environment

        self.margin = 50
        self.scale = 1.0

        self.render_data = RenderData()
        self.update_agent_colors()
        self.update_room_pos()

    def update_room_pos(self):
        x_min = y_min = self.margin
        x_max = self.screen_width - self.margin
        y_max = self.screen_height - self.margin
        self.render_data.room_positions = optimize_room_positions(self.environment, (x_min, x_max), (y_min, y_max)) # set positions

    def update_agent_colors(self):
        for i, agent in enumerate(self.environment.all_agents_by_name.values()):
            self.render_data.agent_colors[agent] = rgb_float_to_int(colorsys.hsv_to_rgb(i / len(self.environment.all_agents_by_name), 0.9, 0.9))

    def int_rescale(self, x):
        return int(self.scale * x)

    def draw_circle(self, x, y, r, color):
        gfxdraw.filled_circle(self.screen, x, y, self.int_rescale(r), color)
        gfxdraw.aacircle(self.screen, x, y, self.int_rescale(r), color)

    def draw_line(self, color, start_pos, end_pos, width=1):
        x0, y0 = start_pos
        x1, y1 = end_pos
        midpnt_x, midpnt_y = (x0+x1)/2, (y0+y1)/2  # Center of line segment.
        length = hypot(x1-x0, y1-y0)
        angle = atan2(y0-y1, x0-x1)  # Slope of line.
        width2, length2 = width/2 * self.scale, length/2
        sin_ang, cos_ang = sin(angle), cos(angle)

        width2_sin_ang  = width2*sin_ang
        width2_cos_ang  = width2*cos_ang
        length2_sin_ang = length2*sin_ang
        length2_cos_ang = length2*cos_ang

        # Calculate box ends.
        ul = (midpnt_x + length2_cos_ang - width2_sin_ang,
            midpnt_y + width2_cos_ang  + length2_sin_ang)
        ur = (midpnt_x - length2_cos_ang - width2_sin_ang,
            midpnt_y + width2_cos_ang  - length2_sin_ang)
        bl = (midpnt_x + length2_cos_ang + width2_sin_ang,
            midpnt_y - width2_cos_ang  + length2_sin_ang)
        br = (midpnt_x - length2_cos_ang + width2_sin_ang,
            midpnt_y - width2_cos_ang  - length2_sin_ang)

        gfxdraw.aapolygon(self.screen, (ul, ur, br, bl), color)
        gfxdraw.filled_polygon(self.screen, (ul, ur, br, bl), color)


    def render(self):
        self.screen.fill(COLORS['bg'])

        room_positions = self.render_data.room_positions

        # Draw connections under circles
        for room in self.environment.all_rooms_by_name.values():
            for adj_room in room.adjacent_rooms:
                self.draw_line(COLORS['edges'], room_positions[room.name], room_positions[adj_room.name], 2)

        for room in self.environment.all_rooms_by_name.values():
            x, y = room_positions[room.name]
            circ_size = 28 + 6*len(room.adjacent_rooms)
            self.draw_circle(x, y, circ_size + 2, COLORS['edges'])
            self.draw_circle(x, y, circ_size, node_colors.get(room))
            
            font = pygame.font.Font(None, self.int_rescale(22))
            text = font.render(room.name, True, COLORS['text'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
            for i, agent in enumerate(room.agents):
                self.draw_circle(x + 12*i - 6*len(room.agents) - 18, y + 36, 11, self.render_data.agent_colors[agent])
        
        pygame.display.flip()

    def loop(self, render_event: asyncio.Event):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.render()

            if render_event.is_set():
                print('HERE')
                render_event.clear()
            pygame.time.wait(100)

    def start_loop(self, render_event: asyncio.Event):
        threading.Thread(target=self.loop, args=(render_event,), daemon=True).start()

if __name__ == '__main__':
    from simulated.rooms import TownEnvironment, Agent

    env = TownEnvironment('MyTown', rooms=['Village', 'Market', 'Inn'])
    agent1 = Agent('Alice', env)
    agent2 = Agent('Bob', env)
    agent3 = Agent('Charlie', env)
    Agent('1', env), Agent('2', env), Agent('3', env), Agent('4', env)
    
    # Move agents to different rooms for demonstration
    agent1.move_to_room('Village')
    agent2.move_to_room('Market')
    agent3.move_to_room('Inn')

    view = PygameView(env)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        view.render()
        pygame.time.wait(100)

    pygame.quit()
    sys.exit()
