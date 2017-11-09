
// goto alert box frame
function mark_alert_box(object) {
    var frame = parseInt(object.getAttribute("data-frame"));
    var alert = object.getAttribute("data-alert");
    var alert_owner = alert.split("_")[0];
    var alert_boxno = alert.split("_")[1];

    page_update_seek(frame);
}


// go to frames
function page_update_seek(frame) {

    var video = $("#video-selection").val().slice(13);
    var new_frame_data = video_frames[frame];
    var preload_range = {
        start: frame_num_offset_frames(frame, -300),
        end: frame_num_offset_frames(frame, 300)
    };
    var preload_cleanup = "ALL";
    preload_images(video, preload_range, preload_cleanup)
    render_image(frame, video);

    update_alert(new_frame_data["alert"]);
}


function page_update(url) {
    var frame = parseInt($("#frame-num").html());
    var video = $("#video-selection").val().slice(13);

    if (url === "/next") {
        frame = frame_num_offset_frames(frame, 1);
        // frame = frame + 1;
    } else if (url == "/previous") {
        frame = frame_num_offset_frames(frame, -1);
        // frame = frame - 1;
    } else {
        console.err("page update method not implemented");
        return;
    }

    if (!video_frames.hasOwnProperty(frame)) {
        console.log("end or out of range");
        stop();
        return;
    }
    var new_frame_data = video_frames[frame]

    render_image(frame, video);
    $("#frame-num").html(frame);

    update_alert(new_frame_data["alert"]);
}


function next_update() {
    page_update("/next");
}

function previous_update() {
    page_update("/previous");
}

function play() {
    clearInterval(rewind_ID);
    if (play_ID == 0) {
        play_ID = setInterval(function() {
            page_update("/next");
        }, refresh_interval);
    }
}

function rewind() {
    clearInterval(play_ID);
    if (rewind_ID == 0) {
        rewind_ID = setInterval(function() {
            page_update("/previous");
        }, refresh_interval);
    }
}

function stop() {
    clearInterval(play_ID);
    clearInterval(rewind_ID);
    play_ID = 0;
    rewind_ID = 0;
}


var play_ID = 0;
var rewind_ID = 0;

function dump_segment(video) {
    $.ajax({
        url: "/dump_segment",
        type: 'GET',
        data: {
            'video_name': video,
        },
        success: function(html) {

            $("#processing").css({
                "height": "225px",
                "width": "300px",
                "left": "42%",
                "top": "33%"
            })
            $("#processing").attr("src", "static/success.gif");
            setTimeout(function() {
                window.location.reload(1);
            }, 1700);
        }
    });
}


function check_fire(data) {
    console.log(data);
    $.ajax({
        url: "/box_check",
        type: 'GET',
        data: data
    });
}


function box_events() {

    if ($(this).hasClass("error_checkbox")) {
        error_id = $(this).data("error");
        data = {
            "type": "error",
            "id": error_id
        };

        if ($(this).is(":checked")) {
            data["action"] = "insert"
            check_fire(data);

        } else {
            data["action"] = "remove"
            check_fire(data);

        }
    } else if ($(this).hasClass("segment_checkbox")) {
        segment_id = $(this).data("segmentid");
        video_name = $(this).data("videoname");
        name_segment = $(this).attr('name');
        data = {
            "type": "segment",
            "segmentid": segment_id,
            "videoname": video_name
        };
        segment_autocancel_id = $(".segment_checkbox[name=" + name_segment + "]").not(this).data("segmentid");
        data_autocancel = {
            "type": "segment",
            "segmentid": segment_autocancel_id,
            "videoname": video_name
        };
        if ($(this).is(":checked")) {
            data["action"] = "insert";
            check_fire(data);
            data_autocancel["action"] = "remove";
            check_fire(data_autocancel);
        } else {
            data["action"] = "remove";
            check_fire(data);
        }
    }
}


function render_boxes(boxes, svg) {

    d3.selectAll("g.box").remove();
    var num = boxes.length;
    for (var i = 0; i < num; i++) {
        var box = boxes[i];
        var box_group = svg.append("g").attr("class", "box").attr("id", box["source"] + "-" + box["id"]);

        box_group.append("rect")
            .attr("x", box['xmin'])
            .attr("y", box['ymin'])
            .attr("width", box['xmax'] - box['xmin'])
            .attr("height", box['ymax'] - box['ymin'])
            .style("stroke", color_map[box["source"]])
            .style("stroke-width", 3)
            .style("fill", "none");

        box_group.append("rect")
            .attr("x", box['xmin'] - 2)
            .attr("y", box['ymin'] - 17)
            .attr("width", 7.5 * (box["source"] + "-" + box["id"]).length + 0.5)
            .attr("height", 15)
            .attr("fill", color_map[box["source"]])
            .style("opacity", 0.6);

        box_group.append("text")
            .attr("x", box['xmin'])
            .attr("y", box['ymin'] - 5)
            .text(box["source"] + "-" + box["id"])
            .attr("font-size", "14px")
            .attr("fill", "white");
    }
}


function highlight_box(box_id) {
    d3.selectAll(".box").style("opacity", 0);
    d3.select("#" + box_id).style("opacity", 1);
    console.log(box_id);
}


function show_all_box(box_id) {
    d3.selectAll(".box").style("opacity", 1);
}

function get_color_map() {
    var color_map = {};
    var meta_tags = $("meta");
    var num = meta_tags.length;
    for (i = 0; i < num; i++) {
        color_map[meta_tags[i].name] = meta_tags[i].content;

    }
    return color_map
}

// ensure image cache buffer always has 10 second(10*30fps) forward and backward.
function check_buffer(video_name, frame) {

    if (preload_status.loading === true) {
        return;
    }
    var should_buffer_back = frame_num_offset_frames(frame, -150);
    should_buffer_back = parseInt(should_buffer_back);
    var should_buffer_foword = frame_num_offset_frames(frame, 150);
    should_buffer_foword = parseInt(should_buffer_foword);

    if (preload_status.start > should_buffer_back) {
        console.log("back buffer not enough");
        var load_range = {
            start: frame_num_offset_frames(preload_status.start, -300),
            end: frame_num_offset_frames(preload_status.start, -1)
        }
        var cleanup_range = {
            start: frame_num_offset_frames(preload_status.end, -300),
            end: preload_status.end.toString()
        }
        console.log(load_range);
        console.log(cleanup_range);
        preload_images(video_name, load_range, cleanup_range);
    }
    if (preload_status.end < should_buffer_foword) {
        console.log("foword buffer not enough");
        var load_range = {
            start: frame_num_offset_frames(preload_status.end, 1),
            end: frame_num_offset_frames(preload_status.end, 300)
        }
        var cleanup_range = {
            start: preload_status.start.toString(),
            end: frame_num_offset_frames(preload_status.start, 300)
        }
        console.log(load_range);
        console.log(cleanup_range);
        preload_images(video_name, load_range, cleanup_range);
    }
}


function oninput_seekbar(seekbar) {
    console.log("seekbar on input");
}

function onchange_seekbar(seekbar) {
    // console.log("seekbar on change");
    var total_frame_index = (frame_indexs.length - 1);
    var target_progress = parseFloat(seekbar.value);
    var target_frame_index = Math.floor(total_frame_index * target_progress);
    var target_frame_num = frame_indexs[target_frame_index];

    var preload_range = {
        start: frame_num_offset_frames(target_frame_num, -600),
        end: frame_num_offset_frames(target_frame_num, 600)
    }
    preload_images(preload_status.video_name, preload_range, "ALL");
    render_image(target_frame_num, preload_status.video_name);

    console.log(target_progress, target_frame_index);
}

function update_seekbar(frame) {
    var seekbar = document.getElementById("seekbar");
    var current_frame_index = parseInt(frame_num_to_index(frame));
    var total_frame_index = (frame_indexs.length - 1)

    var progress = current_frame_index / total_frame_index;

    seekbar.value = progress;
}


var boxes; //global variable: preload boxes cache
function render_image(frame, video) {

    check_buffer(video, frame);
    update_seekbar(frame);

    $("#frame-num").html(frame);

    // var params = { frame:frame, video:video };
    // var img_url = "/image?" + jQuery.param(params);
    var img_url = frame_to_path(video, frame)
    var svg = d3.select("#alert-svg");
    var jq_svg = $("#alert-svg");
    if (lastShowImage !== undefined) {
        jq_svg.find(lastShowImage).attr("display", "none");
    }
    var image_selector = "#img-" + frame.toString();

    var target_image = jq_svg.find(image_selector)
    lastShowImage = image_selector;

    target_image.attr("display", "");
    /*
    $.ajax({
        url: "/alert_boxes",
        data: {
            "frame": frame,
            "video": video
        },
        type: 'GET',
        success: function(response) {
            //console.log(response);
            render_boxes(response, svg)
        },
        error: function(error) {
            console.log(error);
        }
    });
    */
    //need to cache box information just like image
    frame_boxes = boxes[frame];
    render_boxes(frame_boxes,svg);
}

function preload_images_cleanup(cleanup) {
    var jq_svg = $("#alert-svg");
    if (typeof(cleanup) === "object") {
        var frame_start_value = cleanup.start;
        var frame_end_value = cleanup.end;
    }
    for (var frame in video_frames) {
        var frame_value = parseInt(frame);
        if (cleanup === "ALL") {
            //console.log("remove all cache");
        } else if (frame_value < frame_start_value) {
            continue;
        } else if (frame_value > frame_end_value) {
            break;
        }
        var image_selector = "#img-" + frame.toString();
        var target_image = jq_svg.find(image_selector)
        target_image.remove();
    }
}
// preload image between "preload scope"
function preload_images(video_name, preload, cleanup) {
    preload_status.video_name = video_name;
    if (cleanup != null) {
        preload_images_cleanup(cleanup)
    }
    console.log("preload image:", preload)
    var svg = d3.select("#alert-svg");
    var frame_start_value = parseInt(preload.start);
    var frame_end_value = parseInt(preload.end);
    preload_status.loading = true;

    if (cleanup == null || cleanup === "ALL") {
        preload_status.start = parseInt(frame_start_value);
        preload_status.end = parseInt(frame_end_value);
    } else {
        console.log(cleanup.start, cleanup.end);
        console.log(preload_status.start, preload_status.end)
        if (parseInt(cleanup.start) === preload_status.start) {
            preload_status.start = parseInt(cleanup.end);
            preload_status.end = parseInt(frame_end_value);
        } else if (parseInt(cleanup.end) === preload_status.end) {
            preload_status.start = parseInt(frame_start_value);
            preload_status.end = parseInt(cleanup.start);
        } else {
            console.error("unknown");
        }
    }
    preload_status.loading_array = [];

    for (var frame in video_frames) {
        var frame_value = parseInt(frame);
        if (frame_value < frame_start_value) {
            continue;
        }
        if (frame_value > frame_end_value) {
            break;
        }
        preload_status.loading_array[frame_value] = false;
    }

    for (var frame in video_frames) {
        var frame_value = parseInt(frame);
        if (frame_value < frame_start_value) {
            // console.log("skip this frame", frame);
            continue;
        }
        if (frame_value > frame_end_value) {
            // console.log("break on this frame", frame);
            break;
        }
        //console.log(frame)
        var img_url = frame_to_path(video_name, frame)

        // console.log(img_url)
        svg.append("image")
            .attr("xlink:href", img_url)
            .attr("x", "0")
            .attr("y", "0")
            .attr("display", "none")
            .attr("id", "img-" + frame)
            .attr("onload", function() {
                preload_status.loading_array[frame_value] = true;
                for (var load_index in preload_status.loading_array) {
                    if (preload_status.loading_array[load_index] === false) {
                        return;
                    }
                }
                preload_status.loading = false;
                console.log("all done");
            });
    }
}

$(function() {
    // init function here
    color_map = get_color_map();

    $('#next-button').click(next_update);
    $('#previous-button').click(previous_update);
    $('#play-button').click(play);
    $('#rewind-button').click(rewind);
    $('#stop-button').click(stop)

    $("input:checkbox").change(box_events);
    $("input:radio").change(box_events);

    var frame = parseInt($('#alert-svg').attr("frame-num"));
    var video = $("#video-selection").val().slice(13);


    console.log("preloading all images");
    //console.log("preloading ")
    $.ajax({
        url: "/alert_boxes",
        data: {
            "video": video
        },
        type: 'GET',
        success: function(response) {
          boxes = response;
        },
        error: function(error) {
            console.log(error);
        }
    });
    $.ajax({
        url: '/frames?' + $.param({
            video: video
        }),
        type: 'GET',
        success: function(response) {
            // cache all frames information
            video_frames = response.data;
            frame_indexs = Object.keys(video_frames);
            console.log(response);

            // 30fps * 20 second = 600
            var preload_end = frame_num_offset_frames(frame, 600);
            var preload_range = {
                start: frame,
                end: preload_end
            }
            var cleanup_range = null;
            preload_images(video, preload_range, cleanup_range);
            render_image(frame, video);
        },
        error: function(error) {
            //error handling if not able to preload image
        }
    })
    $(".error_entry").hover(function() {
            var worker = this.getAttribute("data-worker");
            var box_id = this.getAttribute("data-box");
            var alert_box_id = worker + "-" + box_id;
            console.log("hover ===>", box_id, worker, alert_box_id);
            highlight_box(alert_box_id);
        },
        function() {
            show_all_box();
        }
    );
})

// some low level function for genernator very basic values
function frame_to_path(video_name, frame_num) {
    dir_A = Math.floor(frame_num / 10000).toString();
    dir_B = Math.floor(frame_num / 100).toString();
    path = [img_base_path + video_name, dir_A, dir_B, frame_num + ".jpg"]

    return path.join("/");
}

function frame_num_to_index(frame_num) {
    return frame_indexs.indexOf(frame_num.toString());
}

function frame_num_offset_frames(frame_num, offset) {
    var current_index = parseInt(frame_num_to_index(frame_num));
    var new_index = current_index + parseInt(offset);
    var new_num = frame_indexs[new_index.toString()];
    if (new_num === undefined) {
        if (offset > 0) {
            new_num = frame_indexs[frame_indexs.length - 1];
        } else if (offset < 0) {
            new_num = frame_indexs[0];
        }
    }
    return new_num;
}
