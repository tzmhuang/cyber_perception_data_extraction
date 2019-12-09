from collections import namedtuple


class Pose(object):
    def __init__(self):
        self.data_pt = namedtuple(
            'data_pt', 'timestamp, position_x, position_y, heading, \
                linear_velocity_x, linear_velocity_y')
        self.column_names = list(self.data_pt._fields)
        self.data = []
        return

    def append(self, timestamp, position_x, position_y, heading, linear_velocity_x, linear_velocity_y):
        d = self.data_pt(timestamp, position_x, position_y,
                         heading, linear_velocity_x, linear_velocity_y)
        self.data.append(d)
        return

    def get(self):
        return self.data

    def __str__(self):
        return '%s' % (self.__class__.__name__)
