from __future__ import annotations

from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass

from teleillusion.environment.base_env_cfg import BaseEnvCfg
from teleillusion.motion.motion_interface import PoseInterface
from teleillusion.tools.setup_helper import SetupHelper

@configclass
class DrawerClosePickPlaceCubeEnvCfg(BaseEnvCfg):
    """
    Configuration for drawer closing, pick and place task with RM75 dual-arm robot.

    Task: Close drawer, pick up a cube, and place it on a platform.
    """

    # scene cfg, is placed here since different tasks may have different number of environments to clone
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=1, env_spacing=20.0, replicate_physics=True
    )
    rigid_usd_path:str=""

    def __post_init__(self,):
        ######### DO NOT EDIT REGION START #########
        super().__post_init__()

        # Add global dome light for illumination
        self.add_global_dome_light(
            texture_file=f"teleillusion/submodules/SimAssets/HDR/test_bg.jpg",
        )

        # Add background scene elements from collection
        self.add_scene_cfg(
            name="background_living_room",
            usd_path=f"teleillusion/submodules/SimAssets/usd/bg_assets/background_img_only/instance.usda",
        )
        self.add_scene_cfg(
            name="background_living_room_left",
            usd_path=f"teleillusion/submodules/SimAssets/usd/bg_assets/background_img_only/instance.usda",
            pos=[1, -0.78, 0],
            rot=[0.7071, 0, 0, 0.7071],
        )
        self.add_scene_cfg(
            name="background_living_room_right",
            usd_path=f"teleillusion/submodules/SimAssets/usd/bg_assets/background_img_only/instance.usda",
            pos=[0.78, 1, 0],
            rot=[0.7071, 0, 0, -0.7071],
        )
        self.add_scene_cfg(
            name="terrain",
            usd_path=f"teleillusion/submodules/SimAssets/usd/bg_assets/textured_ground_no_collision/instance.usda",
            pos=[0, 0, -2],
        )

        # Set time sync mode for recording
        self.set_time_sync_mode("A_mode", record_freq=60)

        # Configure RM75 dual-arm robot
        robot_setup = SetupHelper()
        robot_setup.load_robot_setup_cfg("dual_rm75_robotiq_cfg_nov05")
        origin_pose = PoseInterface.from_translation_and_eulerzyx(
            translation=[0.0, 0, 1.38], eulerzyx=[0.0, 0.0, 0.0]
        )
        robot_setup.set_setup_origin_pose(origin_pose=origin_pose)
        self.add_robot_setup(robot_setup=robot_setup)

        # Add table from collection
        self.add_rigid_object_cfg_from_collection(
            name="textureless_table_for_teleop_90cm",
            chosed_articulated_object_collection="pm_articulated_objects.yaml",
            used_articulated_object_collection=True,
        )

        ######### DO NOT EDIT REGION END #########

        # Add wooden cabinet with drawer (top drawer is opened)
        # self.add_articulated_object_cfg_from_collection(
        #     name="pm_drawer_44817",
        #     chosed_articulated_object_collection="pm_articulated_objects.yaml",
        #     used_articulated_object_collection=True,

        # )

        # Add distractor objects from collection
        #self.add_rigid_object_cfg_from_collection(name="marker_pen01_distractor",chosed_articulated_object_collection="pm_articulated_objects.yaml",used_articulated_object_collection=True)
        #self.add_rigid_object_cfg_from_collection(name="pen_holder01_distractor",chosed_articulated_object_collection="pm_articulated_objects.yaml",used_articulated_object_collection=True)
        #self.add_rigid_object_cfg_from_collection(name="cube2_distractor",chosed_articulated_object_collection="pm_articulated_objects.yaml",used_articulated_object_collection=True)
        # Add target platform for placing the cube
        # Note: Keeping pos and scale parameters as they are task-specific

        self.add_rigid_object_cfg_from_collection(
            name="platform", pos=[0.55, 0.45, 0.905], scale=[0.4, 0.2, 1.0]
            ,chosed_articulated_object_collection="pm_articulated_objects.yaml",used_articulated_object_collection=True
        )

        #Add cube1 - the main object to be picked and placed
        # self.add_rigid_object_cfg_from_collection(
        #     name="cube1",
        #     chosed_articulated_object_collection="pm_articulated_objects.yaml",
        #     used_articulated_object_collection=True,
        # )
        self.add_rigid_object_cfg(name="sauce1",usd_path=str(self.rigid_usd_path),
                                  pos=[0.43,0.2,0.91],
                                  rot=[1,0,0,0],
                                  scale=[1,1,1],
                                  )


