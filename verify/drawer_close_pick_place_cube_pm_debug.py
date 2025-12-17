import argparse

from isaaclab.app import AppLauncher

import argparse

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
parser.add_argument("--usd_path", help="Path to the USD file (default: origin_path/model_fixed1.usda)")

AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
args_cli.enable_cameras = True
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

from teleillusion.actor.puppeteer import Puppeteer
from teleillusion.skill.drawer import singleton_push_drawer
from teleillusion.skill.pick_place_object import (
    singleton_pick_object,
    singleton_place_object,
)
from teleillusion.tools.recorder import Recorder
from teleillusion.utils.logging_setup import set_global_log_level
from teleillusion_tests.skill_oriented_tasks.drawer_close_pick_place_cube_pm.drawer_close_pick_place_cube_pm_env import (
    DrawerClosePickPlaceCubeEnv,
)
from teleillusion_tests.skill_oriented_tasks.drawer_close_pick_place_cube_pm.drawer_close_pick_place_cube_pm_env_cfg import (
    DrawerClosePickPlaceCubeEnvCfg,
)

import omni
import omni.kit.app

set_global_log_level("DEBUG")


def main():
    # Initialize the environment

    #parser = argparse.ArgumentParser(description="Process USD files for grasp and place tasks")
    #parser.add_argument("--usd_path", help="Path to the USD file (default: origin_path/model_fixed1.usda)")
    args = parser.parse_args()
    rigid_usd_path=args.usd_path
    env_cfg = DrawerClosePickPlaceCubeEnvCfg(rigid_usd_path=rigid_usd_path)
    env = DrawerClosePickPlaceCubeEnv(cfg=env_cfg)

    # here to warmup the env first so that the motion planner is initialized
    env.warmup()

    # we find our actor here

    actor = env.compound_actor

    # we construct a puppeteer here
    puppeteer = Puppeteer(actor=actor, env=env, env_id=0)

    puppeteer.setup_recorder(recorder_cls=Recorder, save_dir="./recordings2")
    loop_count=0

        # needed for singleton env
    puppeteer.reset(reset_env=True)
    # the puppeteer can make the robot plan and do something until finished (currently 'all the trajectory has been consumed')

    puppeteer.spin(step_number=25)

    # Close the drawer
    # singleton_push_drawer(
    #     puppeteer,
    #     target_object="pm_drawer_44817",
    #     side="left",
    #     layer="handle0",
    #     move_away_distance=0.08,
    #     push_distance=0.12,
    # )

    # Pick up the rubiks cube
    singleton_pick_object(
        puppeteer,
        target_object="sauce1",
        side="left",
        command="grasp",
        grasp_percentage=0.75,
    )

    # Place the cube on the target platform
    singleton_place_object(
        puppeteer,
        target_object="platform",
        side="left",
    )

    puppeteer.spin(step_number=25)

    # Check if task succeeded
    if env.condition_manager.is_ending_success(env_id=0):
        print("✅ Task succeeded: drawer opened and cube placed on target!")
        usd_path_split=rigid_usd_path.split("/")
        store_text_path=rigid_usd_path[:-len(usd_path_split[-1])]
        print("store_text_path:",store_text_path)
        usd_specific_name=usd_path_split[-1].split(".")[0]
        usd_count_name=usd_specific_name[-1]#获得usd对应的count比如base0.usd,base1.usd
        with open(f"{store_text_path}base{usd_count_name}.txt","w") as f:
            f.write("success")
            f.close()
        
        puppeteer.save_recording()
    else:
        print("❌ Task failed!")
    loop_count+=1
    env.close()

    simulation_app.close()
    omni.kit.app.get_app().quit()



if __name__ == "__main__":
    main()
