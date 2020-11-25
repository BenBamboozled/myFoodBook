$(document).ready(function () {
  $("button[job='edit-post']").click(function (event) {

    event.preventDefault();
    window.location.href='/post/' + $(this).children("#pen").attr("value")+'/update';
  });

  
  $("button[job='delete-post']").click(function (event) {

    event.preventDefault();
    window.location.href='/post/' + $(this).children("#trash").attr("value") +'/delete';
  });

  $("button[job='like-post']").click(function (event) {
    event.preventDefault();
    console.log("ello");
    var btn = $(this);
    var likes = $(this).children('i');
    var label = $(this).children('p');
    
    $.ajax({
      type: 'GET',
      url: '/like/'+ $(this).children('#thumbs-up').attr("value"),
      contentType: "application/json",
      dataType: 'json',
      success: function(json){
        likes.html( json.likes );
        likes.toggleClass("fa-thumbs-down");
        likes.toggleClass("fa-thumbs-up");
        label.html( json.label );
        btn.toggleClass("btn-success");
        btn.toggleClass("btn-secondary");
        console.log(json.error)
      },
      error:function (xhr, ajaxOptions, thrownError){
        if(xhr.status==500) {
            alert('Must be logged in to like a post');
        }
    }
    });

  });
    
   $( ".share" ).click( function(event) {		
    event.preventDefault();
    var id =  $(this).children('i').attr("value");
    console.log(id);

    var url = "https://facebook.com/sharer/sharer.php?u=myfoodbook.me%2Fpost%2F" + id;
    console.log( url);

    $('#facebook-share').attr("href", url );

    url = "https://twitter.com/intent/tweet/?text=Check%20out%20this%20post%20I%20found%20on%20My%20Food%20Book!&url=myfoodbook.me%2Fpost%2F" + id;
    $('#twitter-share').attr("href", url );

    url = "mailto:?subject=Check%20out%20this%20post%20I%20found%20on%20My%20Food%20Book&body=myfoodbook.me%2Fpost%2F" + id;
    $('#mail-share').attr("href", url );

  });

  $("button[job='disable-account']").click(function (event) {
    event.preventDefault();

    var txt;
    var r = confirm("Are you sure you want to disable your profile? You will not be able to log in to your account but your post and pictures will stay on the site.");
    if (r == true) {
      window.location.replace('/disable-profile')
    } 

  });

  $("button[job='delete-account']").click(function (event) {
    event.preventDefault();

    var txt;
    var r = confirm("Are you sure you want to delete your profile? Your full account will be deleted along with any posts or pictures. ");
    if (r == true) {
      window.location.replace('/delete-profile')
    } 
  });


});
