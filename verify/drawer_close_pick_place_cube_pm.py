import argparse

import cv2
import numpy as np
import torch
from isaaclab.app import AppLauncher


# Create argparser
parser = argparse.ArgumentParser()
parser.add_argument("--size", type=float, default=1.0, help="Side-length of cuboid")
parser.add_argument(
    "--num_envs", type=int, default=1, help="Number of environments to spawn."
)
parser.add_argument(
    "--width",
    type=int,
    default=1280,
    help="Width of the viewport and generated images. Defaults to 1280",
)
parser.add_argument(
    "--height",
    type=int,
    default=720,
    help="Height of the viewport and generated images. Defaults to 720",
)

AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
args_cli.enable_cameras = True
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

from teleillusion.actor.puppeteer import Puppeteer
from teleillusion.scheduler.orchester import Orchester
from teleillusion.scheduler.task import BaseTask
from teleillusion.tools.recorder import DummyRecorder, Recorder
from teleillusion.utils.logging_setup import set_global_log_level
from teleillusion_tests.skill_oriented_tasks.drawer_close_pick_place_cube_pm.drawer_close_pick_place_cube_pm_env import (
    DrawerClosePickPlaceCubeEnv,
)
from teleillusion_tests.skill_oriented_tasks.drawer_close_pick_place_cube_pm.drawer_close_pick_place_cube_pm_env_cfg import (
    DrawerClosePickPlaceCubeEnvCfg,
)


set_global_log_level("DEBUG")


def main():
    # Initialize the environment

    env_cfg = DrawerClosePickPlaceCubeEnvCfg()
    env = DrawerClosePickPlaceCubeEnv(cfg=env_cfg)

    # here to warmup the env first so that the motion planner is initialized
    env.warmup()

    env.create_puppeteers(puppeteer_type=Puppeteer)

    orchester = Orchester(env=env)
    orchester.setup_recorder(recorder_cls=Recorder, save_dir="./recordings2")
    orchester.load_all_tasks(task_cls=BaseTask)

    orchester.sync_spin_all_for_n_epochs(epoch_number=1)

    # Close the environment
    env.close()


if __name__ == "__main__":
    main()
