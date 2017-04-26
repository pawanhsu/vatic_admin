function change_links (target_links){
  var links_list = $('#target-links')
  links_list.empty();

  var num = target_links.length;
  for(var i = 0; i < num; i++) {
      var span = $('<span/>').attr("class", "glyphicon glyphicon-hand-right");
      var text = $('<h4/>').html(target_links[i][0] + "'s Segment  " ).append(span);
      var link = $('<a/>').attr('href', target_links[i][1]).append(text);
      var item = $('<li/>').attr('class', "list-group-item").append(link);
      links_list.append(item);
}



}

function update_wrong_number(alert){
  var w_list = $("#w-list");
  w_list.empty();
  if("wrong_number" in alert){

    for(var user in alert["wrong_number"]) {
        var span = $('<span/>').attr("class", "badge").html(alert["wrong_number"][user]);
        var item = $('<li/>').attr('class', "list-group-item").append(span).append(user);
        w_list.append(item);
        }
  }

}









function update_isolation(alert){

  var i_list = $("#i-list");
  i_list.empty();
  if("isolation" in alert){

    for(var user in alert["isolation"]) {
        var span = $('<span/>').attr("class", "badge").html(Object.keys(alert["isolation"][user]).length);
        var item = $('<li/>').attr('class', "list-group-item").append(span).append(user);
        i_list.append(item);
        }
  }

  }











function update_alert(alert){
  update_wrong_number(alert);
  update_isolation(alert);
}





function page_update_seek(frame){

  var video = $("#video-selection").val().slice(13);


  var new_frame_data = video_frames[frame];


  var preload_range = {
    start: frame_num_offset_frames(frame,-300), 
    end: frame_num_offset_frames(frame,300)
  };
  var preload_cleanup = "ALL";
  preload_images(video, preload_range, preload_cleanup)
  render_image(frame, video);
  $("#frame-num").html(frame);

  update_alert(new_frame_data["alert"]);
  change_links(new_frame_data["target_links"]);

  /*
    $.ajax({
        url: "/seek",
        data:  {"frame":frame, "video":video},
        type: 'GET',
        success: function(response) {


          //console.log(response);
          render_image(frame, video);

 $("#frame-num").html(response["frame_num"]);

 update_alert(response["alert"]);
 change_links(response["target_links"]);

        },
        error: function(error) {
            console.log(error);

        }
    });
  */
}




function page_update(url){
  var frame = parseInt($("#frame-num").html());
  var video = $("#video-selection").val().slice(13);

  if (url === "/next") {
    frame = frame_num_offset_frames(frame,1);
    // frame = frame + 1;
  } else if (url == "/previous") {
    frame = frame_num_offset_frames(frame,-1);
    // frame = frame - 1;
  } else {
    console.err("not imp");
    return ;
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
  change_links(new_frame_data["target_links"]);


  /*
    $.ajax({
        url: url,

        data:  {"frame":frame, "video":video},
        type: 'GET',
        success: function(response) {
          console.log(response);

          render_image(response["frame_num"], video);

 $("#frame-num").html(response["frame_num"]);
 update_alert(response["alert"]);
 change_links(response["target_links"]);

        },
        error: function(error) {
            console.log(error);

        }
    });
  */
}

function next_update(){

  page_update("/next");
}




function previous_update(){
  page_update("/previous");


}

function play(){
  clearInterval(rewind_ID);
  if (play_ID == 0){
    play_ID  = setInterval(function(){
      page_update("/next");
    }, refresh_interval);
  }
}

function rewind(){
  clearInterval(play_ID);
  if (rewind_ID == 0){
    rewind_ID = setInterval(function(){
      page_update("/previous");
    }, refresh_interval);
  }
}

function stop(){
    clearInterval(play_ID);
    clearInterval(rewind_ID);
    play_ID = 0;
    rewind_ID = 0;


}



play_ID = 0;
rewind_ID = 0;


function check_fire(error_data){

  console.log(error_data);
  $.ajax({
     url: "/box_check",
     type: 'GET',
     data: error_data
           });

}



function box_events(){
  /*
  video = $(this).data("video");
  master = $(this).data("master");
  reference = $(this).data("reference");
  type = $(this).data("type");
  begin = $(this).data("begin");
  end = $(this).data("end");
  box_id = $(this).data("id");


  error_data = {"video":video, "master":master, "reference": reference,"box_id":box_id, "type":type, "begin":begin,"end":end}
  */
  error_id = $(this).data("error");
  error_data = {"id": error_id};



  if($(this).is(":checked")){
    error_data["action"] = "insert"
    check_fire(error_data);
  }
  else {
    error_data["action"] = "remove"
    check_fire(error_data);

  }
}






function render_boxes(boxes, svg){







           d3.selectAll("g.box").remove();
           var num = boxes.length;
           for(var i = 0; i < num; i++) {
             var box = boxes[i];

             var box_group = svg.append("g").attr("class", "box").attr("id", box["source"] + "-" + box["id"]);



             box_group.append("rect")
             .attr("x", box['xmin'])
             .attr("y", box['ymin'])
             .attr("width", box['xmax'] - box['xmin'])
             .attr("height", box['ymax'] - box['ymin'])
             .style("stroke",color_map[box["source"]])
             .style("stroke-width",3)
             .style("fill", "none");



             box_group.append("rect")
                .attr("x", box['xmin']-2)
                .attr("y", box['ymin'] - 17)
                .attr("width", 7.5*(box["source"] + "-" + box["id"]).length + 0.5)
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




function highlight_box(box_id){
  d3.selectAll(".box").style("opacity", 0);
  d3.select("#"+box_id).style("opacity",1);
  console.log(box_id);

}


function show_all_box(box_id){
  d3.selectAll(".box").style("opacity", 1);


}




function get_color_map(){
  var color_map = {};
  var meta_tags = $("meta");
  var num = meta_tags.length;
  for (i=0; i<num; i++){
    color_map[meta_tags[i].name] = meta_tags[i].content;

  }
  return color_map





}


function check_buffer(video_name,frame) {
  // console.log(frame, preload_status.start, preload_status.end);
  // default load 20 second at init
  // and check backward 5 second and forword 5 second 
  // if not enough, load 10 seconds
  if (preload_status.loading === true) {
    return;
  }
  var should_buffer_back = frame_num_offset_frames(frame, -150);
  should_buffer_back = parseInt(should_buffer_back);
  var should_buffer_foword = frame_num_offset_frames(frame, 150);
  should_buffer_foword = parseInt(should_buffer_foword);
  // console.log(preload_status.start, should_buffer_back);
  if (preload_status.start > should_buffer_back) {
    console.log("back buffer not enough");
    var load_range = {
      start: frame_num_offset_frames(preload_status.start,-300),
      end: frame_num_offset_frames(preload_status.start,-1)
    }
    var cleanup_range = {
      start: frame_num_offset_frames(preload_status.end,-300),
      end: preload_status.end.toString()
    }
    console.log(load_range);
    console.log(cleanup_range);
    preload_images(video_name,load_range, cleanup_range);
  }
  // console.log(preload_status.end, should_buffer_foword);
  if (preload_status.end < should_buffer_foword) {
    console.log("foword buffer not enough");
    var load_range = {
      start: frame_num_offset_frames(preload_status.end,1),
      end: frame_num_offset_frames(preload_status.end,300)
    }
    var cleanup_range = {
      start: preload_status.start.toString(),
      end: frame_num_offset_frames(preload_status.start,300)
    }
    console.log(load_range);
    console.log(cleanup_range);
    preload_images(video_name,load_range, cleanup_range);
  }

}


function render_image(frame, video){
    check_buffer(video,frame);



    // var params = { frame:frame, video:video };
    // var img_url = "/image?" + jQuery.param(params);
    var img_url = frame_to_path(video, frame)
    // console.log(img_url)
      var svg = d3.select("#alert-svg");
      var jq_svg = $("#alert-svg");
      if (lastShowImage !== undefined) {
        jq_svg.find(lastShowImage).attr("display", "none");
      }
      var image_selector = "#img-" + frame.toString();
      
      var target_image = jq_svg.find(image_selector)
      lastShowImage = image_selector;
      // console.log(target_image)
      target_image.attr("display","");


       $.ajax({
           url:"/alert_boxes" ,
           data:  {"frame":frame, "video":video},
           type: 'GET',
           success: function(response) {
             //console.log(response);

             render_boxes(response, svg)

           },
           error: function(error) {
               console.log(error);

           }
       });
     }

function preload_images_cleanup(cleanup) {
  var jq_svg = $("#alert-svg");
  if (typeof(cleanup)==="object") {
    var frame_start_value = cleanup.start;
    var frame_end_value = cleanup.end;
  }
  for (var frame in video_frames) {
    var frame_value = parseInt(frame);
    if (cleanup === "ALL") {
      //console.log("remove all cache");
    } else if (frame_value < frame_start_value) {
      continue;
    } else if (frame_value >  frame_end_value) {
      break;
    }
    var image_selector = "#img-" + frame.toString();
    var target_image = jq_svg.find(image_selector)
    target_image.remove();
  }
}
function preload_images(video_name, preload, cleanup) {
  if (cleanup!=null) {
    preload_images_cleanup(cleanup)
  }
  console.log("preload image:", preload)
  var svg = d3.select("#alert-svg");
  var frame_start_value = parseInt(preload.start);
  var frame_end_value = parseInt(preload.end);
  preload_status.loading = true;
  if (cleanup==null || cleanup === "ALL") {
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
    if (frame_value >  frame_end_value) {
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
    if (frame_value >  frame_end_value) {
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
      .attr("id", "img-"+frame)
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

    var frame = parseInt($('#alert-svg').attr("frame-num"));
    var video = $("#video-selection").val().slice(13);


    console.log("preloading all images");
    $.ajax({
      url: '/frames?' + $.param({video: video}) ,
      type: 'GET', 
      success: function(response) {
        video_frames = response.data;
        frame_indexs = Object.keys(video_frames);
        console.log(response);
        // alert("start load images");
        // 30fps * 20 second = 600
        var preload_end = frame_num_offset_frames(frame, 600);
        var preload_range = {
          start: frame,
          end: preload_end
        }
        var cleanup_range = null;
        preload_images(video,preload_range,cleanup_range);

        render_image(frame, video);
      },
      error: function(error) {
      
      }
    })



    $("tr").not(':first').hover(
  function () {
  console.log(this.getAttribute("box-id"));
  highlight_box(this.getAttribute("box-id"));
  },
  function () {
    show_all_box();
  }
);










})


// some low level function for genernator very basic values
function frame_to_path(video_name, frame_num) {
  dir_A = Math.floor(frame_num / 10000).toString();
  dir_B = Math.floor(frame_num / 100).toString();
  path = [img_base_path + video_name, dir_A, dir_B, frame_num + ".jpg" ]

  return path.join("/");
}

function frame_num_to_index(frame_num) {
  return frame_indexs.indexOf(frame_num.toString());
}
function frame_num_offset_frames(frame_num, offset) {
  var current_index = parseInt(frame_num_to_index(frame_num));
  var new_index = current_index + parseInt(offset);
  var new_num = frame_indexs[new_index.toString()];
  if (new_num===undefined) {
    if (offset>0) {
      new_num = frame_indexs[frame_indexs.length - 1];
    } else if (offset < 0) {
      new_num = frame_indexs[0];
    }
  }
  return new_num;
}
