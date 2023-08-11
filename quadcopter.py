import numpy as np
import math
import scipy.integrate
import time
import datetime
import threading

class Propeller():
    def __init__(self, prop_dia, prop_pitch):
        self.dia = prop_dia
        self.pitch = prop_pitch
        self.speed = 0 #RPM
        self.thrust = 0

    def set_speed(self,speed):
        self.speed = speed
        # From http://www.electricrcaircraftguy.com/2013/09/propeller-static-dynamic-thrust-equation.html
        # self.thrust = 4.392e-8 * self.speed * math.pow(self.dia,3.5)/(math.sqrt(self.pitch))
        # self.thrust = self.thrust*(4.23e-4 * self.speed * self.pitch)
        self.thrust = 9.81

class Quadcopter():
    # State space representation: [x y z x_dot y_dot z_dot theta phi gamma theta_dot phi_dot gamma_dot]
    # From Quadcopter Dynamics, Simulation, and Control by Andrew Gibiansky
    def __init__(self,quad,gravity=9.81,b=0.847):
        #b = Torque/Thrust 
        self.AoI = quad['AoI']
        self.cm_df = quad['cm_df']
        self.aero_df = quad['aero_df']
        self.polar_df = quad['polar_df']
        self.no_of_aero_surfaces = self.aero_df.shape[0]
        self.cg = quad['cg']
        self.rho = quad['rho']
        self.Sref = quad['Sref']
        self.Cref = quad['Cref']
        self.L = quad['L']
        self.g = gravity
        self.b = b
        self.m = quad['weight']
        self.thread_object = None
        self.ode =  scipy.integrate.ode(self.state_dot).set_integrator('vode',nsteps=500,method='bdf')
        self.time = datetime.datetime.now()
        self.state = np.zeros(12)
        self.state[0:3] = quad['position']
        self.state[3] = -2 # Initial speed of quad in x dir 
        self.state[6:9] = quad['orientation']
        #wind model
        self.Vinf = self.state[3]
        self.qinf = 0.5*self.rho*self.Vinf*self.Vinf
        self.m1 = Propeller(quad['prop_size'][0],quad['prop_size'][1])
        self.m2 = Propeller(quad['prop_size'][0],quad['prop_size'][1])
        self.m3 = Propeller(quad['prop_size'][0],quad['prop_size'][1])
        self.m4 = Propeller(quad['prop_size'][0],quad['prop_size'][1])
        # From Quadrotor Dynamics and Control by Randal Beard
        # ixx=((2*quad['weight']*quad['r']**2)/5)+(2*quad['weight']*quad['L']**2)
        ixx = quad['I'][0]
        iyy=ixx
        # izz=((2*quad['weight']*quad['r']**2)/5)+(4*quad['weight']*quad['L']**2)
        izz = quad['I'][2]
        self.I = np.array([[ixx,0,0],[0,iyy,0],[0,0,izz]])
        self.invI = np.linalg.inv(self.I)
        self.run = True

    def rotation_matrix(self,angles):
        ct = math.cos(angles[0])
        cp = math.cos(angles[1])
        cg = math.cos(angles[2])
        st = math.sin(angles[0])
        sp = math.sin(angles[1])
        sg = math.sin(angles[2])
        R_x = np.array([[1,0,0],[0,ct,-st],[0,st,ct]])
        R_y = np.array([[cp,0,sp],[0,1,0],[-sp,0,cp]])
        R_z = np.array([[cg,-sg,0],[sg,cg,0],[0,0,1]])
        R = np.dot(R_z, np.dot( R_y, R_x ))
        return R

    def wrap_angle(self,val):
        return( ( val + np.pi) % (2 * np.pi ) - np.pi )
    
    
    def get_lift(self , aero_df):
        L = 0.0 
        for i in range(len(aero_df)):
            AoA = self.get_orientation()[1] + self.AoI
            dCl_dalpha = aero_df.iloc[i]["dCl_dalpha"]
            CL_0 = aero_df.iloc[i]["CL_0"]
            L += (dCl_dalpha*AoA + CL_0)*self.qinf*self.Sref
        return L
    
    def get_drag(self , polar_df):
        D = 0.0
        if len(polar_df) > 1:
            m = (polar_df.iloc[0]["CDtot"] - polar_df.iloc[1]["CDtot"])/(polar_df.iloc[0]["AoA"] - polar_df.iloc[1]["AoA"])
            if 0.0 in polar_df['AoA'].values:
                c = polar_df.loc[polar_df["AoA"] == 0.0 , 'CDtot'].iloc[0]
            else:
                c = polar_df.iloc[0]["CDtot"] - m*polar_df.iloc[0]["AoA"]
            AoA = self.get_orientation()[0]
            D+= (m*AoA + c)*self.qinf*self.Sref
        else:
            D = polar_df.iloc[0]["CDtot"]*self.qinf*self.Sref
        return D

  
    def get_moment(self,cm_df):
        M = 0.0
        for i in range(len(cm_df)):
            AoA = self.get_orientation()[1] + self.AoI
            M += (cm_df.iloc[i]['Slope']*AoA + cm_df.iloc[i]['Y-Intercept'])*self.qinf*self.Sref*self.Cref 
        return M
        

    def state_dot(self, time, state):
        state_dot = np.zeros(12)
        # The velocities(t+1 x_dots equal the t x_dots)
        state_dot[0] = self.state[3]
        state_dot[1] = self.state[4]
        state_dot[2] = self.state[5]
        # The acceleration
        
        tot_lift = self.get_lift(self.aero_df)
        tot_drag = self.get_drag(self.polar_df)
        x_dotdot = np.array([0,0,-self.g]) + np.dot(self.rotation_matrix(self.state[6:9]),np.array([0,0,(self.m1.thrust + self.m2.thrust + self.m3.thrust + self.m4.thrust)]))/self.m  + np.array([tot_drag,0,tot_lift])/self.m  #+ np.dot(self.rotation_matrix(self.state[6:9]),np.array([-tot_drag,0,0]))/self.m    
        state_dot[3] = x_dotdot[0]
        state_dot[4] = x_dotdot[1]
        state_dot[5] = x_dotdot[2]
        # The angular rates(t+1 theta_dots equal the t theta_dots)
        state_dot[6] = self.state[9]
        state_dot[7] = self.state[10]
        state_dot[8] = self.state[11]
        # The angular accelerations
        omega = self.state[9:12]
        tot_My = self.get_moment(self.cm_df)
        print(tot_My)
        tau = np.array([self.L*(self.m1.thrust-self.m3.thrust), self.L*(self.m2.thrust-self.m4.thrust)+tot_My , self.b*(self.m1.thrust-self.m2.thrust+self.m3.thrust-self.m4.thrust)])
        omega_dot = np.dot(self.invI, (tau - np.cross(omega, np.dot(self.I,omega))))
        state_dot[9] = omega_dot[0]
        state_dot[10] = omega_dot[1]
        state_dot[11] = omega_dot[2]
        return state_dot

    def update(self, dt):
        self.ode.set_initial_value(self.state,0)
        self.state = self.ode.integrate(self.ode.t + dt)
        self.state[6:9] = self.wrap_angle(self.state[6:9])
        self.state[2] = max(0,self.state[2])
        self.Vinf = self.state[3]
        self.qinf = 0.5*self.rho*self.Vinf*self.Vinf
        

    def set_motor_speeds(self,speeds):
        self.m1.set_speed(speeds[0])
        self.m2.set_speed(speeds[1])
        self.m3.set_speed(speeds[2])
        self.m4.set_speed(speeds[3])

    def get_position(self):
        return self.state[0:3]

    def get_linear_rate(self):
        return self.state[3:6]

    def get_orientation(self):
        return self.state[6:9]

    def get_angular_rate(self):
        return self.state[9:12]

    def get_state(self):
        return self.state

    def set_position(self,position):
        self.state[0:3] = position

    def set_orientation(self,orientation):
        self.state[6:9] = orientation

    def get_time(self):
        return self.time

    def thread_run(self,dt):
        rate = dt
        last_update = self.time
        while(self.run==True):
            time.sleep(0)
            self.time = datetime.datetime.now()
            if (self.time-last_update).total_seconds() > rate:
                self.update(dt)
                last_update = self.time

    def start_thread(self,dt=0.002):
        self.thread_object = threading.Thread(target=self.thread_run,args=(dt,))
        self.thread_object.start()

    def stop_thread(self):
        self.run = False
