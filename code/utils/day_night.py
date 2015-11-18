import nibabel as nib
import csv
import json
# import pprint as pp


''' Returns a tuple of four arrays: day_slices, night_slices, int_slices, and
ext_slices, each of which contain the indices that correspond to the scene
description.
'''

class SceneSlicer:
    def __init__(self, sub_num):
        with open('../../data/data_path.json', 'r') as fh:
            self.data_paths = json.load(fh)
        self.images = [0] * 8
        self.scene_slices = [0] * 8
        self.sub_num = sub_num
        self.segment_duration = [902, 882, 876, 976, 924, 878, 1086, 673.4]
        self.scene_desc = {}
        self.scene_keys = []

    def generate_scene_desc_dict(self):
        # scene_desc is a dictionary mapping a time to a tuple
        # where the first value corresponds to if scene happened in the day time
        # and the second corresponds to if the scene was internal
        IS_DAY = 0
        IS_INT = 1

        with open('../../ds113_study_description/stimulus/task001/annotations/scenes.csv', 'rb') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=['seconds', 'scene', 'day-night', 'int-ext'])
            for row in reader:
                scene_time = int(float(row['seconds']))
                self.scene_desc[scene_time] = (row['day-night'] == "DAY", row['int-ext'] == "INT")
        self.scene_keys = self.scene_desc.keys()
        self.scene_keys.sort()

    def get_image(self, run_num):
        if self.images[run_num] == 0:
            sub_str = 'sub' + str(self.sub_num)
            img_path = "../../" + self.data_paths['bold_dico_7Tad2grpbold7Tad'][sub_str]['runs'][run_num]["path"]
            img = nib.load(img_path)
            self.images[run_num] = img
        return self.images[run_num]

    def get_scene_slices(self, run_num):
        if not self.images[run_num]:
            self.get_image(run_num)
        if not self.scene_keys:
            self.generate_scene_desc_dict()
        if self.scene_slices[run_num] == 0:
            IS_DAY = 0
            IS_INT = 1

            day_slices = []
            night_slices = []
            int_slices = []
            ext_slices = []
            img = self.images[run_num]

            # Keeping track of where we are in the scene list
            key_index = 0
            scene_start = 0
            for i in range(run_num):
                scene_start += self.segment_duration[i]
            for i in range(len(self.scene_keys)):
                if self.scene_keys[i] > scene_start:
                    key_index = i
                    break
            print self.scene_keys
            for i in range(img.shape[3]):
                print img.shape[3]
                # print i
                if key_index + 1 < len(self.scene_keys) and (i * 2) + scene_start >= self.scene_keys[key_index + 1]:
                    # print key_index
                    key_index += 1
                # print (i * 2) + scene_start
                curr_time = self.scene_keys[key_index]
                # print curr_time
                day_slices.append(i) if self.scene_desc[curr_time][IS_DAY] else night_slices.append(i)
                int_slices.append(i) if self.scene_desc[curr_time][IS_INT] else ext_slices.append(i)
            self.scene_slices[run_num] = (day_slices, night_slices, int_slices, ext_slices)
        print self.scene_slices
        return self.scene_slices[run_num]

ss = SceneSlicer(1)
ss.get_scene_slices(6)
ss.get_scene_slices(7)
