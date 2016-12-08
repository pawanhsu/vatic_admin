function change_links (target_links){
    $('#target-links').empty();

  var num = target_links.length;

  for(var i = 0; i < num; i++) {

      var link = $('<a/>').attr('href', target_links[i][1]).html(target_links[i][0]+"'s link<br>");

        $('#target-links').append(link);
  }
  //$('#target-links').html(container);



}


$(function() {
    $('#next-button').click(function() {
      var frame = parseInt($('#alert-img').attr("frame-num"));
      var video = $("#video-selection").val().slice(13)

        $.ajax({
            url: '/next',
            data:  {"frame":frame, "video":video},
            type: 'GET',
            success: function(response) {
              console.log(response);
                var img = new Image();
                img.src = response["img_url"];
                img.onload = function(){
     $("#alert-img").attr("src", img.src);
     $("#alert-img").attr("frame-num", response["frame_num"]);
     console.log(response);
 }
     $("#frame-num").html(response["frame_num"]);
     $("#alert-info").html(JSON.stringify(response["alert"]));
     change_links(response["target_links"]);








              //$("#alert-img").replaceWith(response);

            },
            error: function(error) {
                console.log(error);

            }
        });
    });





    $('#previous-button').click(function() {
      var frame = parseInt($('#alert-img').attr("frame-num"));
      var video_name = $("#video-selection").val().slice(13)

        $.ajax({
            url: '/previous',
            data:  {"frame":frame, "video":video_name},
            type: 'GET',
            success: function(response) {
              console.log(response);
                var img = new Image();
                img.src = response["img_url"];
                img.onload = function(){
     $("#alert-img").attr("src", img.src);
     $("#alert-img").attr("frame-num", response["frame_num"]);
     console.log(response);
 }
     $("#frame-num").html(response["frame_num"]);
     $("#alert-info").html(JSON.stringify(response["alert"]));
     change_links(response["target_links"]);





              //$("#alert-img").replaceWith(response);

            },
            error: function(error) {
                console.log(error);

            }
        });
    });






});
