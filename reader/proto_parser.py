import sys
import os
import inspect

from cyber_py import cyber
from cyber_py import record
import numpy as np

from modules.planning.proto import planning_pb2
from modules.canbus.proto import chassis_pb2
from modules.control.proto import control_cmd_pb2
from modules.perception.proto import perception_obstacle_pb2
from modules.localization.proto import localization_pb2

from obstacle_struct import Obstacle
from obstacle_struct import LaneMarker
from localization_struct import Pose
from conf.config import ConfigParser

CONF_DIR = '/apollo/data_extraction/conf/'
CONF = ConfigParser().load(CONF_DIR + './config.yaml')['PROTO_PARSER']
DEBUG_MODE = CONF['DEBUG_MODE']


class PerceptionObstacleParser(object):
    def __init__(self):
        self.obstacles = {}
        self.lanemarkers = {}
        self.msg = perception_obstacle_pb2.PerceptionObstacles()
        self.dtype = "apollo.perception.PerceptionObstacles"
        return

    def parse_obstacle(self, ego_pose):
        timestamp = self.msg.header.timestamp_sec
        for obs in self.msg.perception_obstacle:
            # TODO: calculate global x, global y coordinate
            # rel_x = obs.position.x
            # rel_y = obs.position.y - ((obs.position.y > 0).astype(int)*2-1)*obs.width/2
            # glb_x = np.cos(ego_pose.heading)*rel_x - \
            #     np.sin(ego_pose.heading)*rel_y + ego_pose.position_x
            # glb_y = np.sin(ego_pose.heading)*rel_x + \
            #     np.cos(ego_pose.heading)*rel_y + ego_pose.position_y
            glb_x = np.cos(ego_pose.heading)*obs.position.x - \
                np.sin(ego_pose.heading)*obs.position.y + ego_pose.position_x
            glb_y = np.sin(ego_pose.heading)*obs.position.x + \
                np.cos(ego_pose.heading)*obs.position.y + ego_pose.position_y
            if obs.id in self.obstacles.keys():
                self.obstacles[obs.id].append(
                    timestamp=timestamp, x=obs.position.x, y=obs.position.y,
                    global_x=glb_x, global_y=glb_y, vx=obs.velocity.x,
                    vy=obs.velocity.y, length=obs.length,
                    width=obs.width, height=obs.height)
            else:
                new_obstacle = Obstacle(obs_id=obs.id, obs_type=obs.type)
                new_obstacle.append(
                    timestamp=timestamp, x=obs.position.x, y=obs.position.y,
                    global_x=glb_x, global_y=glb_y, vx=obs.velocity.x,
                    vy=obs.velocity.y, length=obs.length,
                    width=obs.width, height=obs.height)
                self.obstacles[obs.id] = new_obstacle
        return

    def parse_lanemarker(self, ego_pose):
        timestamp = self.msg.header.timestamp_sec
        left_lm = self.msg.lane_marker.left_lane_marker
        right_lm = self.msg.lane_marker.right_lane_marker

        if 'left' not in self.lanemarkers.keys():
            new_lanemarker = LaneMarker('left')
            new_lanemarker.append(timestamp=timestamp, c0=left_lm.c0_position,
                                  c1=left_lm.c1_heading_angle, c2=left_lm.c2_curvature,
                                  c3=left_lm.c3_curvature_derivative, longitude_start=left_lm.longitude_start,
                                  longitude_end=left_lm.longitude_end)
            self.lanemarkers['left'] = new_lanemarker
        else:
            self.lanemarkers['left'].append(timestamp=timestamp, c0=left_lm.c0_position,
                                            c1=left_lm.c1_heading_angle, c2=left_lm.c2_curvature,
                                            c3=left_lm.c3_curvature_derivative, longitude_start=left_lm.longitude_start,
                                            longitude_end=left_lm.longitude_end)

        if 'right' not in self.lanemarkers.keys():
            new_lanemarker = LaneMarker('right')
            new_lanemarker.append(timestamp=timestamp, c0=right_lm.c0_position,
                                  c1=right_lm.c1_heading_angle, c2=right_lm.c2_curvature,
                                  c3=right_lm.c3_curvature_derivative, longitude_start=right_lm.longitude_start,
                                  longitude_end=right_lm.longitude_end)
            self.lanemarkers['right'] = new_lanemarker
        else:
            self.lanemarkers['right'].append(timestamp=timestamp, c0=right_lm.c0_position,
                                             c1=right_lm.c1_heading_angle, c2=right_lm.c2_curvature,
                                             c3=right_lm.c3_curvature_derivative, longitude_start=right_lm.longitude_start,
                                             longitude_end=right_lm.longitude_end)
        return

    def parse(self, perception_msg, localization_parser):
        # TODO: retreive localization info by timestamp search
        self.msg.ParseFromString(perception_msg)
        ego_pose = localization_parser.get_pose_by_timestamp(
            self.msg.header.timestamp_sec)
        self.parse_obstacle(ego_pose)
        self.parse_lanemarker(ego_pose)
        return

    def get(self):
        return {'obstacles': self.obstacles, 'lanemarkers': self.lanemarkers}


class LocalizationParser():
    def __init__(self):
        self.localization = {}
        self.msg = localization_pb2.LocalizationEstimate()
        self.dtype = "apollo.localization.LocalizationEstimate"
        self.last_matched_ind = 0
        return

    def parse_pose(self, localization_msg):
        self.msg.ParseFromString(localization_msg)
        timestamp = self.msg.header.timestamp_sec
        pose = self.msg.pose
        if 'pose' not in self.localization.keys():
            pose_data = Pose()
            pose_data.append(timestamp=timestamp, position_x=pose.position.x, position_y=pose.position.y,
                             heading=pose.heading, linear_velocity_x=pose.linear_velocity.x, linear_velocity_y=pose.linear_velocity.y)
            self.localization['pose'] = pose_data
        else:
            self.localization['pose'].append(timestamp=timestamp, position_x=pose.position.x, position_y=pose.position.y,
                                             heading=pose.heading, linear_velocity_x=pose.linear_velocity.x, linear_velocity_y=pose.linear_velocity.y)
        return

    def parse(self, localization_msg):
        self.parse_pose(localization_msg)
        return

    def get_pose_by_timestamp(self, timestamp):
        i = self.last_matched_ind
        while i < len(self.localization['pose'].get())-1:
            if self.localization['pose'].get()[i].timestamp > timestamp:
                break
            i += 1
            if DEBUG_MODE:
                print('IN LOOP: ', i, len(self.localization['pose'].get()))
        curr_ind = i
        prev_ind = i-1
        if DEBUG_MODE:
            print(curr_ind, len(self.localization['pose'].get()))
        matched_ind = curr_ind if abs(self.localization['pose'].get()[curr_ind].timestamp - timestamp) < abs(
            self.localization['pose'].get()[prev_ind].timestamp - timestamp) else prev_ind
        self.last_matched_ind = matched_ind
        if DEBUG_MODE:
            print("TIMESTAMP: ", timestamp)
            print("MATCHED: ", matched_ind,
                  self.localization['pose'].get()[matched_ind])
            print("PREV: ", prev_ind,
                  self.localization['pose'].get()[prev_ind])
            print("CURR: ", curr_ind,
                  self.localization['pose'].get()[curr_ind])
        return self.localization['pose'].get()[matched_ind]

    def get(self):
        return {'localization': self.localization}


def load_all_parser():
    parsers = {}
    class_list = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            if obj.__module__ == "__main__" or obj.__module__ == "reader.proto_parser":
                class_list.append(obj)
    for c in class_list:
        parser_class = c()
        parsers[parser_class.dtype] = parser_class
    return parsers


if __name__ == "__main__":
    p = load_all_parser()
    print(p)
    print(p["apollo.perception.PerceptionObstacles"])
    print(p["apollo.perception.PerceptionObstacles"].dtype)
    print(p["apollo.perception.PerceptionObstacles"].get())
    print(p["apollo.perception.LocalizationEstimate"])
    print(p["apollo.perception.LocalizationEstimate"].dtype)
    print(p["apollo.perception.LocalizationEstimate"].get())
