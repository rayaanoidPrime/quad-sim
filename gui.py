import numpy as np
import math
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as Axes3D
import sys

class GUI():
    # 'quad' is a dictionary of format: quad = {'position':quad_position,'orientation':quad_orientation,'arm_span':quad_arm_span}
    def __init__(self, quad , get_position=None, get_orientation=None):
        if get_position is not None:
            self.get_position = get_position
        if get_orientation is not None:
            self.get_orientation = get_orientation
        self.L = quad['L']
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot( projection='3d')
        self.ax.set_xlim3d([-2.0, 2.0])
        self.ax.set_xlabel('X')
        self.ax.set_ylim3d([-2.0, 2.0])
        self.ax.set_ylabel('Y')
        self.ax.set_zlim3d([0, 5.0])
        self.ax.set_zlabel('Z')
        self.ax.set_title('Quadcopter Simulation')
        self.init_plot()


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

    def init_plot(self):
        self.l1, = self.ax.plot([],[],[],color='blue',linewidth=3,antialiased=False)
        self.l2, = self.ax.plot([],[],[],color='red',linewidth=3,antialiased=False)
        self.hub, = self.ax.plot([],[],[],marker='o',color='green', markersize=6,antialiased=False)

    def update(self ,  position=None, orientation=None):
        if position is None:
            position = self.get_position()
        if orientation is None:
            orientation = self.get_orientation()
            
        R = self.rotation_matrix(orientation)
        L = self.L
        points = np.array([ [-L,0,0], [L,0,0], [0,-L,0], [0,L,0], [0,0,0], [0,0,0] ]).T

          # Rotate only the arm points by 45 degrees about the z-axis
        arm_rotation_matrix = self.rotation_matrix([0, 0, np.radians(45)])
        arm_points = points[:, :4]  # Select arm points
        rotated_arm_points = np.dot(arm_rotation_matrix, arm_points)
        points[:, :4] = rotated_arm_points

        points = np.dot(R,points)
        points[0,:] += position[0]
        points[1,:] += position[1]
        points[2,:] += position[2]
        self.l1.set_data(points[0,0:2],points[1,0:2])
        self.l1.set_3d_properties(points[2,0:2])
        self.l2.set_data(points[0,2:4],points[1,2:4])
        self.l2.set_3d_properties(points[2,2:4])
        self.hub.set_data(points[0,5],points[1,5])
        self.hub.set_3d_properties(points[2,5])
        plt.pause(0.000000000000001)

    