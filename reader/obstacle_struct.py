from collections import namedtuple


class Obstacle(object):
    def __init__(self, obs_id, obs_type):
        self.id = obs_id
        self.type = obs_type
        self.data_pt = namedtuple(
            'data_pt', 'timestamp, x, y, global_x, global_y, vx, vy, length, width, height')
        self.column_names = list(self.data_pt._fields)
        self.data = []
        return

    def append(self, timestamp, x, y, global_x, global_y, vx, vy, length, width, height):
        d = self.data_pt(timestamp, x, y, global_x, global_y,
                         vx, vy, length, width, height)
        self.data.append(d)
        return

    def get(self):
        return self.data

    def concatenate(self, new_obs):
        assert self.__class__ == new_obs.__class__, "Different class cannot concatenate"
        assert self.data.shape[1] == new_obs.get(
        ).shape[1], "Different shape cannot concatenate"
        return self.data.append(new_obs.get())

    def __str__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.id, self.type)


class LaneMarker(object):
    def __init__(self, lane_pos):
        assert lane_pos in ['left', 'right', 'leftleft',
                            'rightright'], "Unrecognized LaneType."
        self.lane_pos = lane_pos
        self.data_pt = namedtuple(
            'data_pt', 'timestamp, c0, c1, c2, c3, longitude_start, longitude_end')
        self.column_names = list(self.data_pt._fields)
        self.data = []
        return

    def append(self, timestamp, c0, c1, c2, c3, longitude_start, longitude_end):
        d = self.data_pt(timestamp, c0, c1, c2, c3,
                         longitude_start, longitude_end)
        self.data.append(d)
        return

    def get(self):
        return self.data

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.lane_pos)


# Testing
if __name__ == "__main__":
    test_obs = Obstacle(1, 'VEHICLE')
    test_obs.append(timestamp=123, x=1, y=2, vx=0.1, vy=0.0)
    print(test_obs)
    print(test_obs.get())

    test_lane = LaneMarker('left')
    test_lane.append(timestamp=123, c0=1, c1=1, c2=1, c3=1,
                     longitudinal_start=0, longitudinal_end=0)
    print(test_lane)
    print(test_lane.get())
