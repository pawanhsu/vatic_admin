from config import *
import json
from subprocess import call

#Dump the annotaton from the given video
def DUMP_TXT_DATA(video_name='all', output_dir="data/query"):

    default_user_map = user_map["default"]


    videos = []
    for user in default_user_map:

        videos += ["{}_{}".format(user, video)  for video in default_user_map[user] if video == video_name or video_name=='all']
    print("Default: {}".format(videos))
    for video in videos:
        vatic_path = "/root/vatic"
        output_path = "{}/{}.txt".format(output_dir, video)
        merge_cmd = "--merge --merge-threshold 0.5"
        inside_cmd = "cd {}; turkic dump {} -o {} {}".format(vatic_path, video, output_path, merge_cmd)
        cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', inside_cmd]
        print(" ".join(cmd))
        call(cmd)


#Need Modification
def get_target_links(video_name, frame_num):
    links = []


    N_segment = frame_num / K_FRAME
    OFFSET_segment = frame_num

    default_user_map = user_map["default"]

    #Links for default map
    for user in sorted(default_user_map):
        if video_name not in default_user_map[user]:
        	continue
        pivot = default_user_map[user][video_name][N_segment].find("?")

        if N_segment > 1 and frame_num % K_FRAME < OFFSET:
            base_link = "{}/{}".format(VATIC_ADDRESS, default_user_map[user][video_name][N_segment-1][pivot:])
            final_link = "{}&frame={}".format(base_link, OFFSET_segment)
            links.append((user+'(A)', final_link))
            base_link = "{}/{}".format(VATIC_ADDRESS, default_user_map[user][video_name][N_segment][pivot:])
            final_link = "{}&frame={}".format(base_link, OFFSET_segment)
            links.append((user+'(B)', final_link))

        else:
            base_link = "{}/{}".format(VATIC_ADDRESS, default_user_map[user][video_name][N_segment][pivot:])
            final_link = "{}&frame={}".format(base_link, OFFSET_segment)
            links.append((user, final_link))


    return sorted(links)

def get_workers(user_map):
    default_user_map = user_map["default"]
    workers = default_user_map.keys()
    return sorted(workers)



def get_user_map(MAP_PATH="vatic-docker/data/user_map.json"):

    user_map = json.load(open(MAP_PATH))

    target_video_names = set()
    for user in user_map:
        for video_name in user_map[user]:
            target_video_names.add(video_name)



    return {"default": user_map}





def get_assignments(user_map):
    default_user_map = user_map["default"]

    assignments = {}


    for user in default_user_map:
        for video in default_user_map[user]:
            TXT_path = "./vatic-docker/data/query/{}_{}.txt".format(user, video)
            if video not in assignments:
                assignments[video] = {}
            assignments[video][user] = TXT_path



    return assignments


def get_videos(user_map):
    #Filter out only the video has unique follower
    default_user_map = user_map["default"]

    videos = []
    for user in default_user_map:
     	videos += [video for video in default_user_map[user] if video not in videos]
    return videos


def dump_user_map():
    INSIDE_CMD = 'cd {}; turkic list --detail'.format(VATIC_PATH)
    CMD = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', INSIDE_CMD]
    print(" ".join(CMD))
    call(CMD)


user_map = get_user_map()
