from __future__ import division
from itertools import groupby
from operator import itemgetter
from collections import OrderedDict
from branch_dependent_utils import DUMP_TXT_DATA



class Annotation():
    #Max would change this and connects to SQLALCHEMY
    def _load_workers(self):
        return [worker for worker, box_file in self.assignments.items()]

    #Max would change this and connects to SQLALCHEMY
    def _load_boxes(self):
        return {worker: parse_txt(box_file) for worker, box_file in self.assignments.items()}


    #Max would change this and connects to SQLALCHEMY
    def update(self):
        DUMP_TXT_DATA(self.video)
        self._boxes = self._load_boxes()
        self.boxes = self._boxes.copy()
        self.paths = get_paths(self.boxes)
        self.alerts = get_alerts(self.boxes, self.paths)
        self.errors = get_errors(self.workers, self.alerts, self.paths)


    def __init__(self, assignments, video):
        self.assignments = assignments
        self.video = video
        self.workers = self._load_workers()
        self._boxes = self._load_boxes()
        #Filtered boxes
        self.boxes = self._boxes.copy()
        self.paths = get_paths(self.boxes)
        self.alerts = get_alerts(self.boxes, self.paths)
        self.errors = get_errors(self.workers, self.alerts, self.paths)

    def filter(self, selected_labels):
        print("Start to Filter")
        if "all" in selected_labels :
            self.boxes = self._boxes.copy()
        else:
            self.boxes = self._filter_label(selected_labels)

        self.paths = get_paths(self.boxes)
        self.alerts = get_alerts(self.boxes, self.paths)
        self.errors = get_errors(self.workers, self.alerts, self.paths)


    def _filter_label(self, selected_labels):
        filtered_boxes = {worker: {} for worker in self.workers}
        for worker in self._boxes:
            for frame, boxes in self._boxes[worker].items():
                for box_id, box in boxes.items():
                    label = box['label']
                    if label in selected_labels:
                        if frame not in filtered_boxes[worker]:
                            filtered_boxes[worker][frame] = {}
                        filtered_boxes[worker][frame][box_id] = box
        print(filtered_boxes)
        return filtered_boxes



def get_errors(workers, alerts, paths):

    class PopHash():
        def __init__(self,):
            self._hash = {}

        def _add(self, i, inputs):

            for key in inputs:
                if key not in self._hash:
                    self._hash[key] = []
                self._hash[key].append(i)

        def _pop(self, i):
            outputs = []
            for key in self._hash.keys():
                if self._hash[key][-1] != i:
                    start = self._hash[key][0]
                    end = self._hash[key][-1]
                    outputs.append((key, start, end))
                    del self._hash[key]
            return outputs


        def add_and_pop(self, i, inputs):
            self._add(i, inputs)
            return self._pop(i)


    def update_error(error_IDs):
        for error_ID, start, end in error_IDs:
            if type(error_ID) is tuple:

                path_ID_A,  path_ID_B = error_ID
                worker_A, box_ID_A = parse_ID(path_ID_A)
                worker_B, box_ID_B = parse_ID(path_ID_B)
                label_A = paths[path_ID_A][start]['label']
                label_B = paths[path_ID_B][start]['label']

                error_A = {"type":"label-distinct", "start": start, "end": end, "owner": path_ID_A, "reference": path_ID_B, "label":(label_A, label_B)}
                errors[worker_A].append(error_A)
                error_B = {"type":"label-distinct", "start": start, "end": end, "owner": path_ID_B, "reference": path_ID_A, "label":(label_B, label_A)}
                errors[worker_B].append(error_B)

            else:
                path_ID_A, worker_B = error_ID.split("\t")
                worker_A, box_ID_A = parse_ID(path_ID_A)
                label_A = paths[path_ID_A][start]['label']
                error_A = {"type":"surplus", "start": start, "end": end, "owner": path_ID_A, "reference": worker_B, "label":label_A}
                errors[worker_A].append(error_A)
                error_B = {"type":"missing", "start": start, "end": end, "owner": path_ID_A, "reference": worker_A, "label":label_A}
                errors[worker_B].append(error_B)






    parse_ID = lambda new_ID: new_ID.split("_")
    compose_ID = lambda worker, box_ID: "{}_{}".format(worker, box_ID)
    flatten = lambda l: [item for sublist in l for item in sublist]
    pop_hash = PopHash()


    errors = {worker: [] for worker in workers}
    if len(alerts) == 0:
        return errors

    max_frame = max(alerts.keys())

    for frame in range(max_frame+1):
        alert = alerts.get(frame, {})
        isolations = []

        for path_ID,  worker_B_list in alert.get("isolated", {}).items():
            isolations += ["{}\t{}".format(path_ID, worker_B) for worker_B in worker_B_list]

        unmatches = alert.get("label-distinct",[])
        error_IDs = pop_hash.add_and_pop(frame, isolations + unmatches)
        update_error(error_IDs)

    error_IDs = pop_hash.add_and_pop(frame + 1, [])
    update_error(error_IDs)
    print("Errors Loaded")
    return {worker: sorted(errors[worker], key=lambda x: x["start"]) for worker in workers}






def get_paths(boxes):
    paths = {}
    frames = boxes.values()[0].keys()
    for frame in frames:
        IOU_map = get_IOU_map(boxes, frame)
        #print(IOU_map)
        for worker_A in IOU_map:
            for box_id_A in IOU_map[worker_A]:
                box_A = boxes[worker_A][frame][box_id_A].copy()
                box_A["match"] = IOU_map[worker_A][box_id_A]
                new_box_id_A = "{}_{}".format(worker_A, box_id_A)
                if new_box_id_A not in paths:
                    paths[new_box_id_A] = {}
                paths[new_box_id_A][frame] = box_A
    print("Paths Loaded")
    return paths




def get_alerts(boxes, paths, IOU_min=0.5):

    parse_ID = lambda new_ID: new_ID.split("_")
    compose_ID = lambda worker, box_ID: "{}_{}".format(worker, box_ID)
    def get_frames(boxes):
        min_frame = 0
        max_frame = boxes.values()[0].keys()[0]
        for worker in boxes:
            max_frame = max(max_frame, max(boxes[worker].keys()))
            min_frame = min(min_frame, min(boxes[worker].keys()))
        return range(min_frame, max_frame+1)

    def label_equal(box_ID_A, box_ID_B):
        label_A = paths[box_ID_A][frame]["label"]
        label_B = paths[box_ID_B][frame]["label"]
        #print(box_ID_A,label_A, box_ID_B,label_B)
        return label_A == label_B



    alerts = {}
    workers = boxes.keys()
    frames = boxes.values()[0].keys()
    for frame in frames:
        target_IDs = []
        alert = {"box-amount":{}, "label-distinct": set(), "isolated": {}}
        for worker in boxes:
            #print(worker, frame)
            target_frame =  boxes[worker].get(frame, [])
            target_IDs += [ "{}_{}".format(worker, box_id) for box_id in target_frame]
            alert["box-amount"][worker] = len(target_frame)
        for target_ID in target_IDs:
            match = paths[target_ID][frame]["match"]
            for worker_B in match:
                box_ID_B = compose_ID(worker_B, match[worker_B]['id'])
                IOU = match[worker_B]['value']
                worker_A, _ = parse_ID(target_ID)
                if match[worker_B]['id'] == "lost" or IOU < IOU_min:
                    if target_ID not in alert["isolated"]:
                        alert["isolated"][target_ID] = []
                    alert["isolated"][target_ID].append(worker_B)
                elif not label_equal(target_ID ,box_ID_B):
                    unmatch_pair = sorted([target_ID, box_ID_B])
                    unmatch_pair = tuple(unmatch_pair)
                    alert["label-distinct"].add(unmatch_pair)
        alert["label-distinct"] = list(alert["label-distinct"])
        alerts[frame] = alert
    print("Alerts Loaded")
    return alerts



#Read the bboxes txt file and return a dictionary
def parse_txt(file="sample_output.txt", selected_class=["all"]):

    annotations = {}

    f = open(file)
    for line in f:
        #print(line.strip().split(" "))
        objID,xmin, ymin, xmax, ymax, frame, outside, occu, auto, label = line.strip().split(" ")

        objID = int(objID)
        xmin = int(xmin)
        ymin = int(ymin)
        xmax = int(xmax)
        ymax = int(ymax)
        frame = int(frame)
        outside = bool(int(outside))
        occu = bool(int(occu))
        auto = bool(int(auto))
        label = label.replace('"', '')

        #Ignoring occulusion or outside of the frame
        if occu or outside:
            continue
        if('all' not in selected_class):
            if label not in selected_class:
                continue
        bbox_elements = ["xmin", "ymin", "xmax", "ymax", "outside", "occu", "auto", "label"]
        bbox = {}
        for key in bbox_elements:
            bbox[key] = locals()[key]

        if frame not in annotations:
            annotations[frame] = {}
        annotations[frame][objID] = bbox
    print("Bboxes Loaded")
    return annotations





def get_intersection(box_a, box_b):
    x1_a, y1_a, x2_a, y2_a = box_a["xmin"], box_a["ymin"], box_a["xmax"], box_a["ymax"]
    x1_b, y1_b, x2_b, y2_b = box_b["xmin"], box_b["ymin"], box_b["xmax"], box_b["ymax"]

    #get the width and height of overlap rectangle
    overlap_width =  min(x2_a, x2_b) - max(x1_a, x1_b)
    overlap_height = min(y2_a, y2_b) - max(y1_a, y1_b)

    #If the width or height of overlap rectangle is negative, it implies that two rectangles does not overlap.
    if overlap_width > 0 and overlap_height > 0:
        return overlap_width * overlap_height
    else:
        return 0


def get_IOU(box_a, box_b):

    intersection = get_intersection(box_a, box_b)
    if intersection == 0 :
        return 0

    #Union = A + B - I(A&B)
    area_a = (box_a["xmax"] - box_a["xmin"]) * (box_a["ymax"] - box_a["ymin"])
    area_b = (box_b["xmax"] - box_b["xmin"]) * (box_b["ymax"] - box_b["ymin"])
    union_area = area_a + area_b - intersection

    return intersection / union_area



def get_IOU_map(boxes, frame):

    def get_IOUs(worker_a, bbox_a):
        IOUs = {}
        for worker_b in boxes:
            bboxes_b = boxes[worker_b].get(frame, {})
            if worker_a != worker_b:
                IOUs[worker_b] = {}
                IOUs[worker_b]["value"] = 0
                IOUs[worker_b]["id"] = "lost"
                for b_id, bbox_b in bboxes_b.items():
                    IOU = get_IOU(bbox_a, bbox_b)
                    if IOU > IOUs[worker_b]["value"]:
                         IOUs[worker_b]["value"] = IOU
                         IOUs[worker_b]["id"] = b_id
        return IOUs


    IOU_map = {}
    for worker in boxes:
        IOU_map[worker] = {}
        for objID, bbox in boxes[worker].get(frame,{}).items():

            IOU_map[worker][objID] = get_IOUs(worker, bbox)
    return IOU_map




if __name__ == "__main__":
        assignments = {"FOO": "FOO.txt", "BAR": "BAR.txt"}
        video = "Highway-Day"
        annotation = Annotation(assignments, video)
        annotation.filter(["van", "truck"])
