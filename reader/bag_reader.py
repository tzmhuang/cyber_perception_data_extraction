from conf.config import ConfigParser
from proto_parser import load_all_parser
from google.protobuf.descriptor_pb2 import FileDescriptorProto
from cyber_py import record
from cyber_py import cyber
import h5py
import datetime
import time
import sys
import os
sys.path.append('/apollo/data_extraction/')


DIR = os.path.dirname(os.path.abspath(__file__)) + \
    '/../'  # '/apollo/data_extraction/'
CONF_DIR = '/apollo/data_extraction/conf/'
CONF = ConfigParser().load(CONF_DIR + './config.yaml')['BAG_READER']
DTYPE_LIST = CONF['DTYPE_LIST']
SAVE_DIR = DIR + CONF['SAVE_DIR']  # TODO: Need to fix to accomodate abs_path


class BagReader(object):
    def __init__(self, datatype):
        self.datatype = list(datatype)
        assert self.datatype.__class__ == list, 'datatype should be a list.'

        self.msg_parsers = load_all_parser()
        assert len(self.msg_parsers.keys()
                   ) > 0, "msg_parser empty, %s" % self.msg_parsers
        for d in self.datatype:
            self.dtype_check(d)
        return

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.datatype)

    def load(self, file):
        timenow = time.time()  # Timer
        f = record.RecordReader(file)
        # TODO: Improve efficiency
        for channel, msg, datatype, timestamp in f.read_messages():
            # Parse localization before perception due to dependency
            if datatype == "apollo.localization.LocalizationEstimate":
                if "apollo.localization.LocalizationEstimate" in self.datatype:
                    self.msg_parsers[datatype].parse(msg)
        f = record.RecordReader(file)
        for channel, msg, datatype, timestamp in f.read_messages():
            # TODO: Deal with all cases, e.g. only perception no localization etc...
            if datatype == "apollo.perception.PerceptionObstacles":
                if "apollo.perception.PerceptionObstacles" in self.datatype:
                    self.msg_parsers[datatype].parse(
                        msg, self.msg_parsers["apollo.localization.LocalizationEstimate"])
        print("Load Time: %f" % (time.time() - timenow))  # Timer
        return

    def get(self, datatype):
        # takes one datatype as input
        self.dtype_check(datatype)
        return self.msg_parsers[datatype]

    def save_h5(self, name='data'):
        timenow = time.time()  # Timer
        # save data to h5py file format
        now = datetime.datetime.now()
        time_str = "%s-%s-%s_%s:%s:%s" % (now.year, now.month,
                                          now.day, now.hour, now.minute, now.second)
        file_name = "%s_%s" % (name, time_str) + '.hdf5'
        file_dir = SAVE_DIR + '/' + file_name
        with h5py.File(file_dir, 'w-') as f:
            for datatype in self.datatype:
                if datatype == 'apollo.perception.PerceptionObstacles':
                    """ 
                    A dict {'obs_id' : Obstacle, ...}
                    Data is stored in u'/obj_<id>/data'
                    """
                    data = self.get(datatype).get()
                    obs_grp = f.create_group('obstacles')
                    lane_grp = f.create_group('lanemarkers')
                    for k in data['obstacles'].keys():
                        dname = "obj_%s" % k
                        grp = obs_grp.create_group(dname)
                        obs_data = data['obstacles'][k]
                        dset = grp.create_dataset(
                            'data', data=obs_data.get(), dtype='float64')
                        dset.attrs['ID'] = obs_data.id
                        dset.attrs['Type'] = obs_data.type
                        dset.attrs['Columns'] = obs_data.column_names
                    for k in data['lanemarkers'].keys():
                        dname = k + '_lane'
                        grp = lane_grp.create_group(dname)
                        lm_data = data['lanemarkers'][k]
                        dset = grp.create_dataset(
                            'data', data=lm_data.get(), dtype='float64')
                        dset.attrs['LanePos'] = lm_data.lane_pos
                        dset.attrs['Columns'] = lm_data.column_names

                elif datatype == 'apollo.localization.LocalizationEstimate':
                    data = self.get(datatype).get()
                    grp = f.create_group('localization')
                    pose_data = data['localization']['pose']
                    dset = grp.create_dataset(
                        'pose', data=pose_data.get(), dtype='float64')
                    dset.attrs['Columns'] = pose_data.column_names

                else:
                    raise TypeError('Do not support type: %s' % datatype)
        print("Save Time: ", time.time() - timenow)  # Timer
        return

    def dtype_check(self, dtype):
        assert dtype in DTYPE_LIST, 'Only support the following datatype: %s' % (
            DTYPE_LIST)
        return


if __name__ == "__main__":
    # Testing
    reader = BagReader(["apollo.perception.PerceptionObstacles"])
    reader.load(sys.argv[1])
    reader.save_h5('test_data')
