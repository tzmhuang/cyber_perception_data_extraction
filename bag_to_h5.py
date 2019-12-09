import sys, os
import re
import reader.bag_reader as bag_reader

DIR = os.path.dirname(os.path.abspath(__file__))+'/'

if __name__ == "__main__":
    data_dir = os.path.abspath(sys.argv[1])
    assert os.path.isdir(data_dir), "Input must be a directory."
    reader = bag_reader.BagReader(["apollo.perception.PerceptionObstacles", "apollo.localization.LocalizationEstimate"])
    files = os.listdir(data_dir)
    files.sort()
    filtered_files = [f for f in files if re.match('[0-9]*.record.[0-9]*', f)]
    assert len(filtered_files) > 0, "Empty directory, No bag found."
    for f in filtered_files:
        print "Processing: " + f + "......"
        file_path = os.path.abspath(data_dir+'/'+f)
        assert os.path.exists(file_path), "File does not exist: %s" % file_path
        reader.load(file_path)
    reader.save_h5(os.path.basename(data_dir))
