$(function() {
    $('#next-button').click(function() {
      var frame = parseInt($('#alert-img').attr("frame-num"));

        $.ajax({
            url: '/next',
            data:  {"frame":frame},
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


              //$("#alert-img").replaceWith(response);

            },
            error: function(error) {
                console.log(error);

            }
        });
    });





    $('#previous-button').click(function() {
      var frame = parseInt($('#alert-img').attr("frame-num"));

        $.ajax({
            url: '/previous',
            data:  {"frame":frame},
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


              //$("#alert-img").replaceWith(response);

            },
            error: function(error) {
                console.log(error);

            }
        });
    });






});
