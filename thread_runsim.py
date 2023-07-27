import quadcopter,gui,controller

# Constants
QUAD_DYNAMICS_UPDATE = 0.002 # seconds
CONTROLLER_DYNAMICS_UPDATE = 0.005 # seconds
run = True

def Point2Point():
    # Set goals to go to
    GOALS = [(1,1,1),(1,2,4),(-1,-1,2),(-1,1,4)]
    YAWS = [0,3.14,-1.54,1.54]
    # Define the quadcopters
    QUADCOPTER={'position':[1,0,0],'orientation':[0,0,0],'L':0.3,'r':0.1,'prop_size':[10,4.5],'weight':1.2}
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


if __name__ == "__main__":
    Point2Point()
