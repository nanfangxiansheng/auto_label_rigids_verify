

import os
import time
from pathlib import Path
import numpy as np
import cv2
import argparse
#from pxr import Usd, Sdf

# Isaac Lab imports
from isaaclab.app import AppLauncher
launcher = AppLauncher(headless=True, enable_cameras=True)
app = launcher.app
from isaaclab.sim.simulation_context import SimulationContext
import isaaclab.sim as sim_utils
from isaaclab.sensors.camera import Camera, CameraCfg
import isaacsim.core.utils.stage as stage_utils
import isaacsim.core.utils.prims as prim_utils
from isaaclab.sim import SimulationCfg
import json
import time
import base64
import requests
import requests
from pxr import Usd, UsdGeom
from usdtoolbox.core.xform.reader import TransformReader
import re
import trimesh
from isaaclab.utils.warp import convert_to_warp_mesh
from isaaclab.utils.warp import raycast_mesh
import torch
from isaacsim.core.prims import XFormPrim
from pxr import Gf

from  usdtoolbox.core.xform.writer import TransformWriter
from usdtoolbox.core.types import Transform,Translation,Rotation,Scale
from usdtoolbox.physics.rigidbody.writer import RigidBodyWriter
from pxr import Usd, UsdGeom, Gf, Sdf, UsdShade
import math
from usdtoolbox.physics.collision.builder import CollisionShapeBuilder
def get_or_set_scale(prim, new_scale=None, mul=None):
    xformable = UsdGeom.Xformable(prim)

    scale_op = None
    for op in xformable.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeScale:
            scale_op = op
            break

    if scale_op is None:
        scale_op = xformable.AddScaleOp()

    current_scale = scale_op.Get()

    if new_scale is not None:
        scale_op.Set(Gf.Vec3f(*new_scale))
    elif mul is not None:
        scale_op.Set(Gf.Vec3f(
            current_scale[0] * mul,
            current_scale[1] * mul,
            current_scale[2] * mul
        ))

    return scale_op.Get()
def main():
    parser = argparse.ArgumentParser(description="Process USD files for semantic segmentation and grasp point detection")

    parser.add_argument("--usd_path", help="Path to the USD file (default: origin_path/model_fixed1.usda)")
    args = parser.parse_args()
    usd_path=args.usd_path
    stage1=Usd.Stage.Open(usd_path)
    usd_path_split=usd_path.split("/")
    print("usd_path_split:",usd_path_split)
    usd_specific_name=usd_path_split[-1].split(".")[0]
    usd_count_name=usd_specific_name[-1]#获得usd对应的count比如base0.usd,base1.usd
    sub_folder_name=usd_path_split[-4]

    print("sub_folder_name:",sub_folder_name)
    print("usd_count_name:",usd_count_name)
    json_path=f"/home/hcy/work/robotwin_json/{sub_folder_name}/model_data{usd_count_name}.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            json_data = json.load(f)
            if json_data.get("scale") is not None:
                scale_data=json_data["scale"]#scale_data是浮点数列表，必须要获得原来的scale_data
                if json_data.get("center") is not None:
                    center=json_data["center"]
                    object_center_height=scale_data[1]*center[1]#获得物体的中心高度，以标定合适的抓握位置
                else:
                    object_center_height=0.03#默认的中心高度
            else:

                scale_data=[1,1,1]
                if json_data.get("center") is not None:
                    center=json_data["center"]
                    object_center_height=scale_data[1]*center[1]#获得物体的中心高度，以标定合适的抓握位置
                else:
                    object_center_height=0.03#默认的中心高度
    else:
        print("json_path not exist")
        scale_data=[1,1,1]
        object_center_height=0.03#默认的中心高度
    object_center_height=round(0.6*object_center_height,3)#保留三位小数即可
    if object_center_height<0.03:
        object_center_height=0.03#设置一个最低的抓握高度
    prim_path="/root/model"
    origin_path="/root"
    reader=TransformReader()#读入transform的类
    path1=stage1.GetPrimAtPath(prim_path)
    origin_path1=stage1.GetPrimAtPath(origin_path)
    first_out=reader.read_trs_components(path1)
    print(first_out)
    tran=None
    rot=None
    scale=None
    rigidbodywriter=RigidBodyWriter(stage1)
    collsionbuilder=    CollisionShapeBuilder(stage1,origin_path1) #添加碰撞体  
    rigidbodywriter.apply_rigid_body_api(origin_path1)#添加刚体
    collision=collsionbuilder.add_mesh_collider(simplify=True)
    print("applied rigid body api")
    if first_out is not None:
        tran,rot,scale=first_out
    pattern = r'x=([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?),\s*y=([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?),\s*z=([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)'
    if tran is not None:#说明此时已经有了trs
        #writer.write_local(path1,xform_specific)#首先需要对模型文件进行scale尺度的缩放以使得其成为正常大小，最终发现这种写法是不对的
        k=get_or_set_scale(path1,new_scale=(scale_data[0],scale_data[1],scale_data[2]))#应当调用gpt写的这个更改函数
        prim_path="/root"
        #随后需要标注默认的frame
        left_grasp_path=prim_path+"/left_grasp"#一共需要设计六个frame,分别对应grasp,open,place和left和right
        right_grasp_path=prim_path+"/right_grasp"
        left_open_path=prim_path+"/left_open"
        right_open_path=prim_path+"/right_open"
        left_place_path=prim_path+"/left_place"
        right_place_path=prim_path+"/right_place"
        left_grasp_xform=UsdGeom.Xform.Define(stage1,left_grasp_path)
        right_grasp_xform=UsdGeom.Xform.Define(stage1,right_grasp_path)
        left_open_xform=UsdGeom.Xform.Define(stage1,left_open_path)
        right_open_xform=UsdGeom.Xform.Define(stage1,right_open_path)
        left_place_xform=UsdGeom.Xform.Define(stage1,left_place_path)
        right_place_xform=UsdGeom.Xform.Define(stage1,right_place_path)
        #设置默认的抓握的translate
        left_grasp_xform.AddTranslateOp().Set((0,0,object_center_height))#默认抓握点在(0,0,0)
        right_grasp_xform.AddTranslateOp().Set((0,0,object_center_height))
        left_open_xform.AddTranslateOp().Set((0,0,object_center_height))
        right_open_xform.AddTranslateOp().Set((0,0,object_center_height))
        left_place_xform.AddTranslateOp().Set((0,0,object_center_height))
        right_place_xform.AddTranslateOp().Set((0,0,object_center_height))
        #这里是添加默认的旋转位姿
        left_grasp_op=left_grasp_xform.AddOrientOp()
        left_quat = Gf.Quatf(0.5, Gf.Vec3f(0.5, 0.5, 0.5))#矫正后的
        left_grasp_op.Set(left_quat)
        right_grasp_op=right_grasp_xform.AddOrientOp()
        right_quat=left_quat
        right_grasp_op.Set(right_quat)
        #对open添加旋转位姿
        left_open_op=left_open_xform.AddOrientOp()
        left_open_op.Set(left_quat)
        right_open_op=right_open_xform.AddOrientOp()
        right_open_op.Set(right_quat)
        #对place添加旋转位姿
        left_place_op=left_place_xform.AddOrientOp()
        left_place_quat=Gf.Quatf(-0.5, Gf.Vec3f(0.5, -0.5, 0.5))#矫正后的真实值
        left_place_op.Set(left_place_quat)
        right_place_op=right_place_xform.AddOrientOp()
        right_place_op.Set(left_place_quat)
        #还需要设置默认的scale值
        left_grasp_xform.AddScaleOp().Set((1,1,1))
        right_grasp_xform.AddScaleOp().Set((1,1,1))
        left_open_xform.AddScaleOp().Set((1,1,1))
        right_open_xform.AddScaleOp().Set((1,1,1))
        left_place_xform.AddScaleOp().Set((1,1,1))
        right_place_xform.AddScaleOp().Set((1,1,1))
    else:#此时也就是说明model xform就不存在TRS
        print("prim has no TRS components")
        prim_path_xform=UsdGeom.Xform.Define(stage1,prim_path)
        prim_path_xform.AddTranslateOp().Set((0,0,0))
        prim_path_xform.AddOrientOp().Set(Gf.Quatf(1,(0,0,0)))
        prim_path_xform.AddScaleOp().Set((scale_data[0],scale_data[1],scale_data[2]))
        #随后需要标注默认的frame
        prim_path="/root"
        left_grasp_path=prim_path+"/left_grasp"#一共需要设计六个frame,分别对应grasp,open,place和left和right
        right_grasp_path=prim_path+"/right_grasp"
        left_open_path=prim_path+"/left_open"
        right_open_path=prim_path+"/right_open"
        left_place_path=prim_path+"/left_place"
        right_place_path=prim_path+"/right_place"
        left_grasp_xform=UsdGeom.Xform.Define(stage1,left_grasp_path)
        right_grasp_xform=UsdGeom.Xform.Define(stage1,right_grasp_path)
        left_open_xform=UsdGeom.Xform.Define(stage1,left_open_path)
        right_open_xform=UsdGeom.Xform.Define(stage1,right_open_path)
        left_place_xform=UsdGeom.Xform.Define(stage1,left_place_path)
        right_place_xform=UsdGeom.Xform.Define(stage1,right_place_path)
        #设置默认的抓握的translate
        left_grasp_xform.AddTranslateOp().Set((0,0,object_center_height))#默认抓握点在(0,0,0)
        right_grasp_xform.AddTranslateOp().Set((0,0,object_center_height))
        left_open_xform.AddTranslateOp().Set((0,0,object_center_height))
        right_open_xform.AddTranslateOp().Set((0,0,object_center_height))
        left_place_xform.AddTranslateOp().Set((0,0,object_center_height))
        right_place_xform.AddTranslateOp().Set((0,0,object_center_height))
        #这里是添加默认的旋转位姿
        left_grasp_op=left_grasp_xform.AddOrientOp()
        left_quat = Gf.Quatf(0.5, Gf.Vec3f(0.5, 0.5, 0.5))
        left_grasp_op.Set(left_quat)
        right_grasp_op=right_grasp_xform.AddOrientOp()
        right_quat=left_quat
        right_grasp_op.Set(right_quat)
        #对open添加旋转位姿
        left_open_op=left_open_xform.AddOrientOp()
        left_open_op.Set(left_quat)
        right_open_op=right_open_xform.AddOrientOp()
        right_open_op.Set(right_quat)
        #对place添加旋转位姿
        left_place_op=left_place_xform.AddOrientOp()
        left_place_quat=Gf.Quatf(-0.5, Gf.Vec3f(0.5, -0.5, 0.5))
        left_place_op.Set(left_place_quat)
        right_place_op=right_place_xform.AddOrientOp()
        right_place_op.Set(left_place_quat)
        #还需要设置默认的scale值
        left_grasp_xform.AddScaleOp().Set((1,1,1))
        right_grasp_xform.AddScaleOp().Set((1,1,1))
        left_open_xform.AddScaleOp().Set((1,1,1))
        right_open_xform.AddScaleOp().Set((1,1,1))
        left_place_xform.AddScaleOp().Set((1,1,1))
        right_place_xform.AddScaleOp().Set((1,1,1))
    stage1.GetRootLayer().Save()


if __name__=="__main__":
    main()











