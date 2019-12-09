#   Input: hdf5['obstacles']
#   Output: hdf5['Obstacles']
#   Attempt to fuse obstacles that are wrongly detected two due to lost track

import os, sys
sys.path.append('/apollo/data_extraction/tools')
import h5py
import numpy as np
import matplotlib.pyplot as plt

import merge_sort



def fuse(f,new_f_name, look_range, t_thresh, d_thresh):
    with new_f
    sorted_obs_list = sort_by_timestamp(f['obstacles'])
    last_i = 0
    last_obs = sorted_obs_list[0]
    fused_obstacles_list = []
    for i in range(1,len(sorted_obs_list)):
        k = 0
        while k <= look_range:
            curr_obs = sorted_obs_list[i+k]
            k += 1
            if curr_obs['data'][0,0] <= last_obs['data'][-1,0]:
                pass
            if is_same_obs(last_obs, curr_obs, t_thresh, d_thresh):
                fused_obs_data = np.concatenate((last_obs['data'][:],curr_obs['data']), 0)
            else:
                # do sth else
        last_obs = sorted_obs_list[i]
   return


def is_same_obs(before_obs, after_obs, t_thresh, d_thresh):
    disappear_time = before_obs['data'][-1,0]
    disappear_pos = (before_obs['data'][-1,1],before_obs['data'][-1,2])
    appear_time = after_obs['data'][0,0]
    appear_pos = (after_obs['data'][0,1],after_obs['data'][0,2])
    td = appear_time - disappear_time
    d = l2_dist(appear_pos, disappear_pos)
    if td < t_thresh and d < d_thresh:
        return True
    return False


def sort_by_timestamp(f_obstacles):
    obs_list = list(f_obstacles.values())
    obs_appear_time = [f_obstacles[k]['data'].value[0,0] for k in f_obstacles.keys()]
    obs_dict = dict(zip(obs_appear_time,obs_list))
    ms = merge_sort.MergeSort(obs_appear_time)
    ms.sort()
    sorted_obs = [obs_dict[t] for t in obs_appear_time]
    return sorted_obs


def l2_dist(pt1, pt2):
    return ((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)**0.5 


if __name__ == "__main__":
    f_path = sys.argv[1]
    assert os.path.exists(f_path), 'File does not exist'
    with h5py.File(f_path,'r') as f:
        obs = f['obstacles']
        sorted_obs = sort_by_timestamp(obs)
        times = [obs[i]['data'][0,0] for i in obs.keys()]
        sorted_times = [sorted_obs[i]['data'][0,0] for i in range(len(sorted_obs))]
        fig, ax = plt.subplots(1,1)
        # ax.plot(range(len(sorted_obs)), times, 'b.')
        ax.plot(range(len(sorted_obs)), sorted_times, 'r.')
        plt.show()
