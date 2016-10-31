def parse_txt(file="sample_output.txt"):

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
        outside = bool(outside)
        occu = bool(occu)
        auto = bool(occu)
        label = label.replace('"', '')

        bbox_elements = ["xmin", "ymin", "xmax", "ymax", "outside", "occu", "auto", "label"]
        bbox = {}
        for key in bbox_elements:
            bbox[key] = locals()[key]

        if frame not in annotations:
            annotations[frame] = {}
        annotations[frame][objID] = bbox

    return annotations


def compare(annotations_dict):
    min_frame = min([min(annotations.keys()) for annotations in annotations_dict.values()])
    max_frame = max([max(annotations.keys()) for annotations in annotations_dict.values()])
    alert_frames = {}
    for frame in range(min_frame, max_frame+1):
        num_objs = {}
        for worker in annotations_dict:
            num_objs[worker] = len(annotations_dict[worker].get(frame, []))
        num_objs_list = num_objs.values()
        if not num_objs_list.count(num_objs_list[0]) == len(num_objs_list):
            alert_frames[frame] = num_objs
    return alert_frames






if __name__ == "__main__":
        annotations_a = parse_txt()
        annotations_b = parse_txt()
        annotations_dict = {"A": annotations_a, "B": annotations_b}
        alert_frames = compare(annotations_dict)
