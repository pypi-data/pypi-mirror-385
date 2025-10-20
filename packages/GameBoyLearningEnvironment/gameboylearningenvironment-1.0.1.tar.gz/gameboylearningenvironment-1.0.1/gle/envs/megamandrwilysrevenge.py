from typing import Any, SupportsFloat

import numpy as np
from gymnasium.core import ObsType, ActType, RenderFrame
from pyboy import PyBoy
from pyboy.utils import WindowEvent
from gymnasium import Env, spaces
import importlib.resources

from gle.envs.general import ALL_ACTIONS, ALL_RELEASE_ACTIONS


class MegaManDrWilysRevenge(Env):
    # 0xC000 - 0xC09F Y-loc X-loc, tile, attribute
    CHARACTER_X_POS_ADDR = 0xC000   # ?
    CHARACTER_Y_POS_ADDR = 0xC001   # ?
    LIVES_ADDR = 0xC108
    UNLOCKED_WEAPONS1_ADDR = 0xDFA1
    WEAPONS1_NAMES = ['Mega Buster', 'Rolling Cutter', 'Thunder Beam', 'Ice Slasher',
                      'Fire Storm', 'Carry', 'Atomic Fire', 'Time Stopper']
    #   $01: Mega Buster
    #   $02: Rolling Cutter
    #   $04: Thunder Beam
    #   $08: Ice Slasher
    #   $10: Fire Storm
    #   $20: Carry
    #   $40: Atomic Fire
    #   $80: Time Stopper
    UNLOCKED_WEAPONS2_ADDR = 0xDFA2
    WEAPONS2_NAMES = ['Quick Boomerang', 'Bubble Lead', 'Mirror Buster', '', '', '', '', '']
    #   $01: Quick Boomerang
    #   $02: Bubble Lead
    #   $04: Mirror Buster
    HP_ADDR = 0xDFA3
    MIRROR_BUSTER_ADDR = 0xDFAD

    def __init__(self, level: str, window_type: str = 'null', save_path: str | None = None,
                 load_path: str | None = None, max_actions: int | None = None, all_actions: bool = False,
                 return_sound: bool = False, rgba: bool = False,):
        assert level in ['cutman', 'iceman', 'elecman', 'fireman', 'wily'], 'Please choose a valid level between cutman, iceman, fireman, wily'
        super().__init__()
        self.prev_action_idx = None
        self.max_actions = max_actions
        self.actions_taken = 0
        self.window_type = window_type
        self.rgba = rgba
        # Sound
        self.return_sound = return_sound

        with importlib.resources.path('gle.roms', "Mega Man - Dr. Wily's Revenge (E) [!].gb") as rom_path:
            self.pyboy = PyBoy(
                str(rom_path),
                window_type=self.window_type
            )

        self.save_path = save_path
        self.load_path = load_path
        if load_path is not None:
            self.load()
        else:
            self.load_path = f'states/megaman_drwily/{level}.state'
            self.load()

        print(f'CARTRIDGE: {self.pyboy.cartridge_title}')

        if all_actions:
            self.actions = ALL_ACTIONS
            self.release_actions = ALL_RELEASE_ACTIONS
        else:
            self.actions = [
                WindowEvent.PRESS_BUTTON_A,
                WindowEvent.PRESS_BUTTON_B,
                WindowEvent.PRESS_ARROW_UP,
                WindowEvent.PRESS_ARROW_DOWN,
                WindowEvent.PRESS_ARROW_RIGHT,
                WindowEvent.PRESS_ARROW_LEFT,
                WindowEvent.PASS,
                [WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.PRESS_BUTTON_A],
                [WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.PRESS_BUTTON_B],
                [WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.PRESS_BUTTON_A, WindowEvent.PRESS_BUTTON_B],
                [WindowEvent.PRESS_ARROW_LEFT, WindowEvent.PRESS_BUTTON_A],
                [WindowEvent.PRESS_ARROW_LEFT, WindowEvent.PRESS_BUTTON_B],
                [WindowEvent.PRESS_ARROW_LEFT, WindowEvent.PRESS_BUTTON_A, WindowEvent.PRESS_BUTTON_B]
            ]

            self.release_actions = [
                WindowEvent.RELEASE_BUTTON_A,
                WindowEvent.RELEASE_BUTTON_B,
                WindowEvent.RELEASE_ARROW_UP,
                WindowEvent.RELEASE_ARROW_DOWN,
                WindowEvent.RELEASE_ARROW_RIGHT,
                WindowEvent.RELEASE_ARROW_LEFT,
                WindowEvent.PASS,
                [WindowEvent.RELEASE_ARROW_RIGHT, WindowEvent.RELEASE_BUTTON_A],
                [WindowEvent.RELEASE_ARROW_RIGHT, WindowEvent.RELEASE_BUTTON_B],
                [WindowEvent.RELEASE_ARROW_RIGHT, WindowEvent.RELEASE_BUTTON_A, WindowEvent.RELEASE_BUTTON_B],
                [WindowEvent.RELEASE_ARROW_LEFT, WindowEvent.RELEASE_BUTTON_A],
                [WindowEvent.RELEASE_ARROW_LEFT, WindowEvent.RELEASE_BUTTON_B],
                [WindowEvent.RELEASE_ARROW_LEFT, WindowEvent.RELEASE_BUTTON_A, WindowEvent.RELEASE_BUTTON_B]
            ]

        if self.rgba:
            self.observation_space = spaces.Box(low=0, high=255, shape=(4, 144, 160), dtype=np.uint8)
        else:
            self.observation_space = spaces.Box(low=0, high=255, shape=(3, 144, 160), dtype=np.uint8)
        self.action_space = spaces.Discrete(len(self.actions))

        self.screen = self.pyboy.screen

        self.reset()

    #   ******************************************************
    #               GYMNASIUM OVERRIDING FUNCTION
    #   ******************************************************
    def step(
            self, action: ActType
    ) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]] | tuple[ObsType, np.ndarray, SupportsFloat, bool, bool, dict[str, Any]]:
        self.take_action(action)
        obs = self.render()
        info = self.get_info()

        self.actions_taken += 1
        done = False
        if self.max_actions == self.actions_taken:
            done = True
        if info['lives'] == 0:
            done = True

        if self.return_sound:
            return obs, self.screen.sound.ndarray, 1.0, done, False, info
        else:
            return obs, 1.0, done, False, info

    def reset(
            self,
            *,
            seed: int | None = None,
            options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:
        self.close()
        self.prev_action_idx = None
        self.actions_taken = 0

        if self.load_path is None:
            self.skip_game_initial_video()

        return self.render(), self.get_info()

    def render(self) -> RenderFrame | list[RenderFrame] | None:
        if self.rgba:
            screen_obs = self.screen.ndarray  # (144, 160, 4) RGBA
        else:
            screen_obs = self.screen.ndarray[:, :, :-1]  # (144, 160, 3) RGB
        return screen_obs.reshape((screen_obs.shape[2], screen_obs.shape[0], screen_obs.shape[1]))  # (3, 144, 160)

    def close(self):
        self.pyboy.stop(save=False)
        with importlib.resources.path('gle.roms', "Mega Man - Dr. Wily's Revenge (E) [!].gb") as rom_path:
            self.pyboy = PyBoy(
                str(rom_path),
                window_type=self.window_type
            )
        if self.load_path is not None:
            self.load()
        self.screen = self.pyboy.screen

    #   ******************************************************
    #                FUNCTION FOR MOVING IN THE GAME
    #   ******************************************************
    def skip_game_initial_video(self):
        while not self.pyboy.tick():
            if self.pyboy.frame_count == 300 and self.pyboy.frame_count == 800:
                self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
            if self.pyboy.frame_count == 305 and self.pyboy.frame_count == 805:
                self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
            if self.pyboy.frame_count == 850:
                break

    #   ******************************************************
    #                  SAVE AND LOAD FUNCTIONS
    #   ******************************************************
    def save(self) -> None:
        with open(self.save_path, "wb") as f:
            self.pyboy.save_state(f)

    def load(self) -> None:
        with open(self.load_path, "rb") as f:
            self.pyboy.load_state(f)

    #   ******************************************************
    #              UTILITY FUNCTIONS USED IN OVERRIDING
    #   ******************************************************
    def take_action(self, action_idx: int):
        if self.prev_action_idx is None or self.prev_action_idx == action_idx:
            self.prev_action_idx = action_idx
            selected_action = self.actions[self.prev_action_idx]
            if isinstance(selected_action, list):
                for action in selected_action:
                    self.pyboy.send_input(action)
                    self.pyboy.tick(5)
            else:
                self.pyboy.send_input(selected_action)
                self.pyboy.tick(10)
        else:  # different action
            # release previous actions
            old_actions_to_be_released = self.release_actions[self.prev_action_idx]
            if isinstance(old_actions_to_be_released, list):
                for action in old_actions_to_be_released[::-1]:
                    self.pyboy.send_input(action)
                    self.pyboy.tick()
            else:
                self.pyboy.send_input(old_actions_to_be_released)
                self.pyboy.tick()
            # Take new action
            self.prev_action_idx = action_idx
            selected_action = self.actions[self.prev_action_idx]
            if isinstance(selected_action, list):
                for action in selected_action:
                    self.pyboy.send_input(action)
                    self.pyboy.tick(5)
            else:
                self.pyboy.send_input(selected_action)
                self.pyboy.tick(10)

    def take_action2(self, action_idx: int):
        self.pyboy.send_input(self.actions[action_idx])
        self.pyboy.tick(7)
        self.pyboy.send_input(self.release_actions[action_idx])
        self.pyboy.tick(8)

    def get_info(self) -> dict:
        info = dict()
        info['x_pos'] = self.pyboy.memory[self.CHARACTER_X_POS_ADDR]
        info['y_pos'] = self.pyboy.memory[self.CHARACTER_Y_POS_ADDR]
        info['lives'] = self.pyboy.memory[self.LIVES_ADDR]
        info['hp'] = self.pyboy.memory[self.HP_ADDR]
        info['weapons1'] = self.decode_weapons(self.UNLOCKED_WEAPONS1_ADDR, self.WEAPONS1_NAMES)
        info['weapons2'] = self.decode_weapons(self.UNLOCKED_WEAPONS2_ADDR, self.WEAPONS2_NAMES)
        info['mirror_buster_addr'] = self.pyboy.memory[self.MIRROR_BUSTER_ADDR]
        return info

    #   ******************************************************
    #                        UTILITIES
    #   ******************************************************
    def decode_weapons(self, addr, names):
        return [names[i] for i in self.list_one_bits_locations(addr)]

    def list_one_bits_locations(self, addr: int) -> list:
        value = self.pyboy.memory[addr]
        ones = list()
        for i in range(8):
            if value & (1 << i):
                ones.append(i)
        return ones
