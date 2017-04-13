from __future__ import division
#Read the bboxes txt file and return a dictionary
def parse_txt(file="sample_output.txt", selected_class="all"):

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
        #label = label.replace('"', '')

        #Ignoring occulusion or outside of the frame
        if occu or outside:
            continue
        if(selected_class != 'all'):
            if label != selected_class:
                continue
        bbox_elements = ["xmin", "ymin", "xmax", "ymax", "outside", "occu", "auto", "label"]
        bbox = {}
        for key in bbox_elements:
            bbox[key] = locals()[key]

        if frame not in annotations:
            annotations[frame] = {}
        annotations[frame][objID] = bbox

    return annotations

def report_annotation(annotation, filter = {}):

    report = {"N_boxes":0, "N_frames": 0}
    if filter:
        report["N_frames"] = 0
        offset = filter["offset"]
        duration = filter["duration"]
        period = filter["period"]
        is_target = lambda frame: 0 <= (frame % period - offset) <= duration


        for frame in annotation:
            if not is_target(frame):
                print(frame)
                report["N_frames"] += 1
                report["N_boxes"] += len(annotation[frame])

    else:

        for frame in annotation:
            if not is_target(frame):
                print(frame)
                report["N_frames"] += 1
                report["N_boxes"] += len(annotation[frame])
    return report




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





def build_max_IOU_map(annotations_dict, frame):

    def get_max_IOUs(worker_a, bbox_a):
        max_IOUs = {}
        for worker_b in annotations_dict:
            bboxes_b = annotations_dict[worker_b].get(frame, {})
            if worker_a == worker_b:
                max_IOUs[worker_b] = 1
            else:
                max_IOUs[worker_b] = 0
                for bbox_b in bboxes_b.values():
                    IOU = get_IOU(bbox_a, bbox_b)
                    max_IOUs[worker_b] = max(IOU, max_IOUs[worker_b])
        return max_IOUs


    max_IOUs_map = {}
    for worker in annotations_dict:
        max_IOUs_map[worker] = {}
        for objID, bbox in annotations_dict[worker].get(frame,{}).items():

            max_IOUs_map[worker][objID] = get_max_IOUs(worker, bbox)
    return max_IOUs_map

def get_isolations(annotations_dict, frame, threshold):
    max_IOU_map = build_max_IOU_map(annotations_dict, frame)
    isolated_bboxes = {}
    for worker, IOU_table in max_IOU_map.items():
        for objID, max_IOUs in IOU_table.items():
            for worker_b, max_IOU in max_IOUs.items():
                if max_IOU < threshold:
                    if worker not in isolated_bboxes:
                        isolated_bboxes[worker] = {}
                    if objID not in isolated_bboxes[worker]:
                        isolated_bboxes[worker][objID] = {}
                    isolated_bboxes[worker][objID][worker_b] = max_IOU
    return isolated_bboxes






#Take the dictionary from different annotators and return the alert frames
def get_alert(annotations_dict):


    def compare_num_objs():
        #A map storing num_objs from each worker
        num_objs_map = {}
        for worker in annotations_dict:
            num_objs = len(annotations_dict[worker].get(frame, []))
            num_objs_map[worker] = num_objs
        #List the num_objs of each worker
        num_objs_list = num_objs_map.values()
        #Markt the frame when the num_objs of each worker are not consistent
        if not num_objs_list.count(num_objs_list[0]) == len(num_objs_list):
            if frame not in alert_frames:
                alert_frames[frame] = {}
            alert_frames[frame]["wrong_number"] = num_objs_map


    #Sub-function for comparing number of IOUs
    def compare_IOUs(threshold=0.5, ignore_occu=True):



        isolated_bboxes = get_isolations(annotations_dict, frame, threshold)


        if len(isolated_bboxes) > 0 :
            if frame not in alert_frames:
                alert_frames[frame] = {}
            alert_frames[frame]["isolation"] = isolated_bboxes





    #print(annotations_dict.values())
    min_frame = float("inf")
    max_frame = 0
    for annotations in annotations_dict.values():
        frames = annotations.keys()
        if frames:
            min_frame = min(min_frame, min(frames))
            max_frame = max(max_frame, max(frames))


    alert_frames = {}
    if min_frame < max_frame:

        for frame in range(min_frame, max_frame+1):

            compare_num_objs()
            compare_IOUs()

    return alert_frames


if __name__ == "__main__":
        annotations_a = parse_txt("FOO.txt")
        annotations_b = parse_txt("BAR.txt")
        annotations_dict = {"A": annotations_a, "B": annotations_b}
        alert_frames = compare(annotations_dict)
        #annotations_b[0][0]["xmax"] +=50
        #annotations_b[0][0]["xmin"] +=50

        #alert_frames = compare(annotations_dict)
