from __future__ import division
from itertools import groupby
from operator import itemgetter
from collections import OrderedDict


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
            max_IOUs[worker_b] = {}
            if worker_a == worker_b:
                max_IOUs[worker_b]["value"] = 1
                max_IOUs[worker_b]["id"] = "self"
            else:
                max_IOUs[worker_b]["value"] = 0
                max_IOUs[worker_b]["id"] = "?"
                for b_id, bbox_b in bboxes_b.items():
                    IOU = get_IOU(bbox_a, bbox_b)
                    if IOU > max_IOUs[worker_b]["value"]:
                         max_IOUs[worker_b]["value"] = IOU
                         max_IOUs[worker_b]["id"] = b_id

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
            for worker_b, info in max_IOUs.items():
                max_IOU = info["value"]

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


    def compare_matching(threshold=0.5, ignore_occu=True):


        def get_unmatching(max_IOU_map, threshold):
            infos = {}
            for worker_A in max_IOU_map:
                for box_A in max_IOU_map[worker_A]:
                    for worker_B in max_IOU_map[worker_A][box_A]:
                        if worker_A != worker_B:

                            IOU = max_IOU_map[worker_A][box_A][worker_B]["value"]
                            if IOU > threshold:
                                box_B = max_IOU_map[worker_A][box_A][worker_B]["id"]
                                label_A = annotations_dict[worker_A][frame][box_A]["label"]

                                label_B = annotations_dict[worker_B][frame][box_B]["label"]
                                if label_A != label_B:
                                    info = {worker_A}

                                if worker_A not in infos:
                                    infos[worker_A] = {}
                                if box_A not in infos[worker_A]:
                                    infos[worker_A][box_A] = {"label":label_A, "unmatched":{}}
                                infos[worker_A][box_A]["unmatched"][worker_B] = {"label": label_B, "id":box_B}
            return infos

        max_IOU_map = build_max_IOU_map(annotations_dict, frame)
        unmatched_info = get_unmatching(max_IOU_map, threshold)


        if len(unmatched_info) > 0 :
            if frame not in alert_frames:
                alert_frames[frame] = {}
            alert_frames[frame]["wrong-class"] = unmatched_info




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
            compare_matching()

    return alert_frames


def get_boxID_map(alerts,annotation_map, workers):
    box_ID_map = {}
    for video_name in alerts:
        box_ID_map[video_name] = {}
        for frame in alerts[video_name]:
            isolations = alerts[video_name][frame].get("isolation" ,{})


            for worker_A, isolation in isolations.items():
                #print(unmatchings)
                #print(worker_A)

                for box_id_A, IOU_list in isolation.items():
                    box_A = annotation_map[video_name][worker_A][frame][box_id_A].copy()
                    box_A["matching"] = {}
                    for worker in workers:
                        if worker == worker_A:

                            box_A["matching"][worker] = "owner"
                        elif worker in IOU_list:
                            box_A["matching"][worker] = "missing"

                        else:
                            box_A["matching"][worker] = "matched"

                        new_box_id_A = "{}_{}".format(worker_A, box_id_A)
                        if new_box_id_A not in box_ID_map[video_name]:
                            box_ID_map[video_name][new_box_id_A] = {}
                        box_ID_map[video_name][new_box_id_A][frame] = box_A


            unmatchings = alerts[video_name][frame].get("wrong-class" ,{})
            #print(unmatchings)
            for worker_A, unmatching in unmatchings.items():
                for box_id_A, info in unmatching.items():
                    label_A = info["label"]
                    for worker_B, B_info in info["unmatched"].items():
                        label_B = B_info["label"]
                        box_id_B = B_info["id"]
                        new_box_id_A = "{}_{}".format(worker_A, box_id_A)
                        if new_box_id_A not in box_ID_map[video_name]:
                            box_ID_map[video_name][new_box_id_A] = {}

                        if frame not in box_ID_map[video_name][new_box_id_A]:
                            box_ID_map[video_name][new_box_id_A][frame] = {}

                        box_A = annotation_map[video_name][worker_A][frame][box_id_A].copy()
                        box_A["unmatching"] = {}
                        box_ID_map[video_name][new_box_id_A][frame] = box_A

                        #print(frame, worker_B)
                        box_B = annotation_map[video_name][worker_B][frame][box_id_B]
                        new_box_id_B = "{}_{}".format(worker_B, box_id_B)
                        info = [new_box_id_A, new_box_id_B, label_A, label_B]
                        box_ID_map[video_name][new_box_id_A][frame]["unmatching"][worker_B] = info





    return box_ID_map




def group_continuous_int(data, mark):
    ranges = []
    for k, g in groupby(enumerate(data), lambda (i,x):i-x):
        group = map(itemgetter(1), g)
        ranges.append((group[0], group[-1]))
    return [(start, end, mark) for start, end in ranges if start != end]




def group_errors(box_ID_map, workers):
    errors = {}
    get_user = lambda box_id: box_id[:box_id.find("_")]
    #initalization
    for video_name in box_ID_map:
        errors[video_name] = {}
        for worker in workers:
            errors[video_name][worker] = {}
            errors[video_name][worker]["missing"] = []
            errors[video_name][worker]["surplus"] = []
            errors[video_name][worker]["unmatched"] = []




    for video_name in box_ID_map:

        for worker in workers:

            #Filling the "MISSING" field of the dictionary
            for box_ID in box_ID_map[video_name]:

                missings = []
                unmatchings = []
                info = []
                for frame in  sorted(box_ID_map[video_name][box_ID].keys()):
                    box = box_ID_map[video_name][box_ID][frame]
                    user_name = get_user(box_ID)
                    if user_name == worker:
                        continue

                    if "matching" in box:
                        status = box["matching"][worker]

                        if status == "owner":
                            break
                        elif status == "missing":
                            missings.append(frame)
                    elif "unmatching" in box:
                        if worker in box["unmatching"]:
                            info = box["unmatching"][worker]

                            unmatchings.append(frame)


                error_missing = group_continuous_int(missings, box_ID)

                error_unmatching = group_continuous_int(unmatchings, info)
                errors[video_name][worker]["missing"] += error_missing
                errors[video_name][worker]["unmatched"] += error_unmatching
                user_name = get_user(box_ID)
                #Fillinh the surplus field of the dictionary by reversing the *MISSING'
                for error in error_missing:

                    error_surplus = list(error)
                    error_surplus.append(worker)
                    error_surplus = tuple(error_surplus)
                    errors[video_name][user_name]["surplus"] += [error_surplus]





    #print(errors[video_name][worker]["unmatched"])
    normalized_errors = {}
    for video_name in box_ID_map:
        normalized_errors[video_name] = {}
        for worker in workers:
            errors[video_name][worker]["mixed"] = errors[video_name][worker]["missing"] + errors[video_name][worker]["surplus"] + errors[video_name][worker]["unmatched"]
            normalized_errors[video_name][worker] = []
            for i, error in  enumerate(errors[video_name][worker]["mixed"]):
                #print(error)
                if type(error[2]) == type([]):
                    error_type = "unmatched"

                    start = error[0]
                    end = error[1]
                    reference, reference_box_id = error[2][0].split("_")
                    reference_label = error[2][2]
                    self_worker ,box_id = error[2][1].split("_")
                    unmatched_info = {"reference_label":reference_label, "reference_id":reference_box_id}
                    normalized_error = {"type":error_type, "reference":reference, "start":start, "end":end, "box_id":box_id, "unmatched_info":unmatched_info}


                else:
                    if len(error) == 3:
                        error_type = "missing"
                        reference, box_id = error[2].split("_")
                        start = error[0]
                        end = error[1]

                    elif len(error) == 4:
                        error_type = "surplus"
                        reference = error[3]
                        box_id = error[2].split("_")[1]
                        start = error[0]
                        end = error[1]

                    normalized_error = {"type":error_type, "reference":reference, "start":start, "end":end, "box_id":box_id}
                #print(worker, normalized_error)
                normalized_errors[video_name][worker].append(normalized_error)





    return OrderedDict(sorted(normalized_errors.items(), key= lambda x: x[0]))






if __name__ == "__main__":


        annotations_a = parse_txt("FOO.txt")
        annotations_b = parse_txt("BAR.txt")
        annotations_dict = {"A": annotations_a, "B": annotations_b}
        workers = annotations_dict.keys()
        alert_frames = get_alert(annotations_dict)
        box_ID_map = get_boxID_map({"dummy": alert_frames},{"dummy":annotations_dict},  workers)
        errors = group_errors(box_ID_map, workers)
        #annotations_b[0][0]["xmax"] +=50
        #annotations_b[0][0]["xmin"] +=50

        #alert_frames = compare(annotations_dict)
