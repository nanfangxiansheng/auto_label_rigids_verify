from __future__ import annotations

from typing import Generator

from teleillusion.actor.puppeteer import Puppeteer
from teleillusion.actor.strategy import BaseStrategy
from teleillusion.environment.base_env import BaseEnv
from teleillusion.environment.condition_manager import ConditionManager
from teleillusion.skill.drawer import parallel_push_drawer
from teleillusion.skill.pick_place_object import (
    parallel_pick_object,
    parallel_place_object,
)


def example_strategy_builder(puppeteer: Puppeteer) -> Generator:
    """
    Strategy for closing drawer, picking up a cube, and placing it on a platform.

    Steps:
    1. Stabilize the robot
    2. Close the top drawer
    3. Pick up the cube
    4. Place the cube on the target platform
    """

    # Before any movement, stabilize the robot
    yield from puppeteer.yield_final_action(steps=50)

    # Step 1: Close the top drawer of the wooden cabinet
    yield from parallel_push_drawer(
        puppeteer,
        target_object="wooden_cabinet_top_opened",
        side="left",
        layer="top",
        move_away_distance=0.08,
        push_distance=0.12,
    )
    yield from puppeteer.yield_action()
    yield from puppeteer.yield_final_action(steps=25)

    # Step 2: Pick up the cube
    yield from parallel_pick_object(
        puppeteer,
        target_object="cube1",
        side="left",
        command="grasp",
        grasp_percentage=0.5,
    )
    yield from puppeteer.yield_action()
    yield from puppeteer.yield_final_action(steps=25)

    # Step 3: Place the cube on the target platform
    yield from parallel_place_object(
        puppeteer,
        target_object="platform",
        side="left",
        approach_offset=0.05,
        place_offset=0.0,
    )
    yield from puppeteer.yield_action()
    yield from puppeteer.yield_final_action(steps=25)


class DrawerClosePickPlaceCubeEnv(BaseEnv):
    """
    Environment for drawer closing, pick and place task.

    Task:
    1. Close the top drawer of a wooden cabinet
    2. Pick up a cube
    3. Place the cube on a platform

    Success Conditions:
    - The drawer must be fully closed
    - The cube must be on top of the platform
    """

    def __init__(self, cfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        # Load parallel strategy for multi-environment execution
        self.strategy_type = BaseStrategy
        self.strategy_builder = example_strategy_builder

        # Configure success conditions
        self.condition_manager = ConditionManager(self)
        # Condition 1: Check if the top drawer is fully closed

        # Condition 2: Check if cube1 is on top of the platform
        self.condition_manager.add_object_on_the_top_of_reference_condition(
            object_name="sauce1",
            reference_object_name="platform",
        )

    def check_success(self):
        pass
