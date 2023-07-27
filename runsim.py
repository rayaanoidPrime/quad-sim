import time
import quadcopter,gui,controller


QUAD_DYNAMICS_UPDATE = 0.002 # seconds
CONTROLLER_DYNAMICS_UPDATE = 0.005 # seconds
run = True

def quad_sim(t, Ts , quad , ctrl , gui_object , goal , y):
    ctrl.update_target(goal)
    ctrl.update_yaw_target(y)
    ctrl.update()
    quad.update(QUAD_DYNAMICS_UPDATE)
    t+=Ts
    gui_object.position = quad.get_position()
    gui_object.orientation = quad.get_orientation()
    gui_object.update()

    return t
    


def Point2Point():
    start_time = time.time()
    # Simulation Setup
    # --------------------------- 
    Ti = 0
    Ts = 0.005
    Tf = 20
    numTimeStep = int(Tf/Ts+1)

    # Set goals to go to
    GOALS = [(1,1,2),(1,-1,4),(-1,-1,2),(-1,1,4)]
    YAWS = [0,3.14,-1.54,1.54]

    # Define the quadcopters
    QUADCOPTER={'position':[1,1,2],'orientation':[0,0,0],'L':0.3,'r':0.1,'prop_size':[10,4.5],'weight':1.2}
    # Controller parameters
    CONTROLLER_PARAMETERS = {'Motor_limits':[4000,10000],
                    'Tilt_limits':[-10,10],
                    'Yaw_Control_Limits':[-900,900],
                    'Z_XY_offset':500,
                    'Linear_PID':{'P':[300,300,7000],'I':[0.04,0.04,4.5],'D':[450,450,5000]},
                    'Linear_To_Angular_Scaler':[1,1,0],
                    'Yaw_Rate_Scaler':0.18,
                    'Angular_PID':{'P':[22000,22000,1500],'I':[0,0,4.5],'D':[12000,12000,0]},
                    }
    quad = quadcopter.Quadcopter(QUADCOPTER)
    gui_object = gui.GUI(quad=QUADCOPTER , get_position=quad.get_position,get_orientation=quad.get_orientation)
    ctrl = controller.Controller_PID_Point2Point(quad.get_state,quad.get_time,quad.set_motor_speeds,params=CONTROLLER_PARAMETERS)

    # Run Simulation
    # ---------------------------
    t = Ti
    global run
    while run==True:
        for goal,y in zip(GOALS,YAWS):
            t = quad_sim(t , QUAD_DYNAMICS_UPDATE , quad , ctrl , gui_object, goal , y)
            if(t >= Tf):
                run = False
                break
    end_time = time.time()
    print( "Simulated {:.2f}s in {:.6f}s.".format(t,end_time-start_time) )

if __name__ == "__main__":
    Point2Point()
   
