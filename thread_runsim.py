import argparse
import os
import quadcopter,gui,controller
import pandas as pd
from LOD_parser import lod_parser,get_coeffs
from Mass_props_parser import mass_props_parser
from Vspaero_parser import vsp_parser
from Polar_parser import polar_parser

# Constants
QUAD_DYNAMICS_UPDATE = 0.002 # seconds
CONTROLLER_DYNAMICS_UPDATE = 0.005 # seconds
run = True


def Point2Point():
    LOD_df = lod_parser(LOD_filepath)
    wing_mass_props_df,tot_mass_props_df = mass_props_parser(mass_props_filepath)
    input_df = vsp_parser(vspaero_filepath)
    polar_df = polar_parser(polar_filepath)

    Sref = input_df['Sref'][0]
    Cref = input_df['Cref'][0]
    rho = input_df['Rho'][0]
    Vinf = input_df['Vinf'][0]
    m = tot_mass_props_df["Mass"]
    x_cg = tot_mass_props_df["cgX"]
    y_cg = tot_mass_props_df["cgY"]
    z_cg = tot_mass_props_df["cgZ"]
    Ixx = tot_mass_props_df["Ixx"]
    Iyy = tot_mass_props_df["Iyy"]
    Izz = tot_mass_props_df["Izz"]
    Ixy = tot_mass_props_df["Ixy"]
    Ixz = tot_mass_props_df["Ixz"]
    Iyz = tot_mass_props_df["Iyz"]

    aero_df = get_coeffs(x_cg , LOD_df)

    # Set goals to go to
    GOALS = [(1,1,1),(1,2,4),(-1,-1,2),(-1,1,4)]
    YAWS = [0,3.14,-1.54,1.54]
    # Define the quadcopters
    QUADCOPTER={'position':[1,0,0],'orientation':[0,0,0],'L':0.3,'r':0.1,'prop_size':[10,4.5],'weight':1.2 , 
                'aero_df':aero_df , 'polar_df': polar_df,  'cg':[x_cg,y_cg,z_cg] , 'rho' : rho , 'Vinf' : Vinf , 'Sref' : Sref , 'Cref' : Cref}
    # Controller parameters
    CONTROLLER_PARAMETERS = {'Motor_limits':[4000,10000],
                        'Tilt_limits':[-10,10],
                        'Yaw_Control_Limits':[-900,900],
                        'Z_XY_offset':500,
                        'Linear_PID':{'P':[300,300,5000],'I':[0.0,0.0,4.5],'D':[450,450,5000]},
                        'Linear_To_Angular_Scaler':[1,1,0],
                        'Yaw_Rate_Scaler':0.18,
                        'Angular_PID':{'P':[22000,22000,1500],'I':[0,0,1.2],'D':[12000,12000,0]},
                        }

    # Make objects for quadcopter, gui and controller
    quad = quadcopter.Quadcopter(QUADCOPTER)
    gui_object = gui.GUI(quad=QUADCOPTER , get_position=quad.get_position,get_orientation=quad.get_orientation)
    ctrl = controller.Controller_PID_Point2Point(quad.get_state,quad.get_time,quad.set_motor_speeds,params=CONTROLLER_PARAMETERS)
    # Start the threads
    quad.start_thread(dt=QUAD_DYNAMICS_UPDATE)
    ctrl.start_thread(update_rate=CONTROLLER_DYNAMICS_UPDATE)
    # Update the GUI while switching between destination poitions
    while(run==True):
        for goal,y in zip(GOALS,YAWS):
            ctrl.update_target(goal)
            ctrl.update_yaw_target(y)
            for i in range(300):
                # gui_object.position = quad.get_position()
                # gui_object.orientation = quad.get_orientation()
                gui_object.update()
    quad.stop_thread()
    ctrl.stop_thread()

def parse_args():
    parser = argparse.ArgumentParser(description="Quadcopter Simulator")
    parser.add_argument("--OpenVSP-folder", type=str, default=-1.0, help='Folder path where .LOD , MassProps.txt and .vspaero files are located ')
    return parser.parse_args()

if __name__ == "__main__":

    args = parse_args()
    # Extract file paths based on the provided folder path
    base_folder = args.OpenVSP_folder.strip()
 
    LOD_filename = [file for file in os.listdir(base_folder) if file.endswith(".lod")]
    mass_props_filename = [file for file in os.listdir(base_folder) if file.endswith("_MassProps.txt")]
    vspaero_filename = [file for file in os.listdir(base_folder) if file.endswith(".vspaero")]
    polar_filename = [file for file in os.listdir(base_folder) if file.endswith(".polar")]

    # Check if exactly one file is found for each extension
    if len(LOD_filename) > 1 or len(mass_props_filename) > 1 or len(vspaero_filename) > 1 or len(polar_filename) > 1:
        raise ValueError("Expected exactly one file with .lod, _MassProps.txt, .polar and .vspaero extension in the folder.")
    if len(LOD_filename) == 0 or len(mass_props_filename) == 0 or len(vspaero_filename) == 0 or len(polar_filename) == 0:
        raise ValueError("Expected file with .lod, _MassProps.txt, .polar  and .vspaero extension in the folder.")

    # Build the complete file paths
    LOD_filepath = os.path.join(base_folder, LOD_filename[0])
    mass_props_filepath = os.path.join(base_folder, mass_props_filename[0])
    vspaero_filepath = os.path.join(base_folder, vspaero_filename[0])
    polar_filepath = os.path.join(base_folder, polar_filename[0])

    Point2Point()
