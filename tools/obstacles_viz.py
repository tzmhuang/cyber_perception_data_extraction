import sys, os
import time
import h5py
import numpy as np
import matplotlib.pyplot as plt

# Plotting all obstacle Trajectories in a given hdf5 file

def obstacle_trajectory_plot(f_obstacles):
    np.random.seed(5) # set seed for plot comparison
    t_now = time.time()
    fig = plt.figure(1)
    ax = plt.subplot2grid((1,1), (0,0))
    ax.plot(0,0, 'r>', linewidth = 5.0)
    print("Plotting......")
    for i,k in enumerate(f_obstacles.keys()):
        data = f_obstacles[k]['data']
        x = data[:,1]
        y = data[:,2]- ((data[:,2] > 0).astype(int)*2-1)*data[:,8]/2
        
        color = np.random.rand(3)
        ax.plot(x,y, marker = 'x', color = color, linewidth = 0.5)
        ax.plot(x,y, color = color,linewidth = 0.7)
        if i%100==0:
            print "Progress: %2.2f /100......"% (float(i)/len(f_obstacles.keys())*100)
    print "Time Used: ", (time.time() - t_now)
    plt.show()
    return

def obstacle_global_trajectory_plot(f_obstacles, f_localization):
    np.random.seed(5) # set seed for plot comparison
    t_now = time.time()
    fig = plt.figure(1)
    ax = plt.subplot2grid((1,1), (0,0))
    ax.plot(0,0, 'r>', linewidth = 5.0)
    print("Plotting......")
    for i,k in enumerate(f_obstacles.keys()):
        data = f_obstacles[k]['data']
        x = data[:,3]
        y = data[:,4]      
        color = np.random.rand(5)
        ax.plot(x,y, marker = 'x', color = color, linewidth = 0.5)
        ax.plot(x,y, color = color,linewidth = 0.7)
        if i%100==0:
            print "Progress: %2.2f /100......"% (float(i)/len(f_obstacles.keys())*100)
    ego_x = f_localization['pose'][:,1]
    ego_y = f_localization['pose'][:,2]
    ax.plot(ego_x,ego_y, 'ro-', linewidth = 1)
    print "Time Used: ", (time.time() - t_now)
    plt.show()
    return

if __name__ == "__main__":
    f_path = sys.argv[1]
    assert os.path.exists(f_path), 'File does not exist'
    with h5py.File(f_path,'r') as f:
        obs = f['obstacles']
        localization = f['localization']
        obstacle_trajectory_plot(obs)
        obstacle_global_trajectory_plot(obs, localization)






