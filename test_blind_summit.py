#!/usr/bin/env python3

from client import SynchronousClient, HUD, PraseArgs, Frame, Agent
from mapping import MapViewer
from planning import HybridGame
import time
import numpy as np
from datetime import datetime



import os


if __name__ == "__main__":
   
    args = PraseArgs()
    args.map = "Town03"
    ego_path = [(42, 0, -1, False), (1806, 0, -1, False), (43, 0, -1, False), (489, 0, -1, False), (8, 0, -2, False)]
    #truck_path = [(8, 0, 1), (14, 0, -1), (7, 0, 1)]
    #ego_path = [(8, 0, 1, False)]
    v_max = 20
    a_max = 6
    dt_sim = 0.1
    dt_plan = 5*dt_sim

    save_folder  = os.getcwd()+ "/data/map/"
    filename = save_folder+"Town03"+'.ot'

    client = None
    try:
        # set up carla client
        client = SynchronousClient(args, dt = dt_sim)
           
        client.setup_ego_vehicle(autopilot = False)
        client.add_lidar(visualize=False, h_fov=360)  # when lidar is visualized, the map viewer is dead
        client.add_depth_camera(yaw = 0, name = "0", visualize=False, fov = 110)
        client.add_depth_camera(yaw = 90, name = "90", visualize=False, fov = 110)
        client.add_depth_camera(yaw = 180, name = "180", visualize=False, fov = 110)
        client.add_depth_camera(yaw = -90, name = "-90", visualize=False, fov = 110)
        client.ego.set_simulate_physics(False)

        # have a truck moving constant speed
        #truck = Agent(client, truck_path, 295, 10)

        # set up planner
        game = HybridGame(client, filename, ego_path, v_max =v_max, a_max=a_max,  dp = 0.5, dl = 0.5, dt_sim = dt_sim, dt_plan = dt_plan, dv = 0.5)
        game.initialize_game(1, 0, v_max)

        # set up map viewer
        frame = Frame(args.width, args.height)
        hud = HUD(args.width, args.height)
        map_view = MapViewer(args)
        map_view.start(client, follow_ego=False)

        for i in range(40):
          
            #truck.tick()
            client.tick()
            hud.tick(client, game)
            map_view.tick(client)
            client.render()
            map_view.render(frame, shadow_list=None)
            hud.render(frame)
            frame.update_frame()
        input("Press Enter to continue...")


        for _ in range(85):
            # tick all modules
            #truck.tick()
            client.tick()
            hud.tick(client, game)
            map_view.tick(client)
            # get all sensor data                        
            semantic_point_cloud = client.lidar_list[0].semantic_raw_data
            sensor_data = [camera.image for camera in client.depth_camera_list]
            sensor_pose = [camera.get_pose() for camera in client.depth_camera_list]

            sensor_data.append(semantic_point_cloud)
            
            game.tick(sensor_data, sensor_pose, False)
            shadow_list = game.info_space.get_shadow_for_plot()
                            
            client.render()
            map_view.render(frame, shadow_list=shadow_list)
            hud.render(frame)
            frame.update_frame()
        game.plot_hist()
            
            
    finally:
        if client:
            client.destroy()