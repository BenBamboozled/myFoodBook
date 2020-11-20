const tagContainer = $(".tag-container")
const input = $(".tag-container input")


let tags = [];


function createTag(label){
  const div = document.createElement('div');
  div.setAttribute('class', 'tag');
  const span = document.createElement('span');
  span.innerHTML= label;
  const closeBtn = document.createElement('i');
  closeBtn.setAttribute('class','fas fa-times');
  closeBtn.setAttribute('job','remove-tag');
  closeBtn.setAttribute('data-id',label);

  div.appendChild(span);
  div.appendChild(closeBtn);
  return div;
  
}

function clearTags() {
  document.querySelectorAll('.tag').forEach(tag => {
    tag.parentElement.removeChild(tag);
  });
}

function addTags() {
  clearTags();
  tags.slice().reverse().forEach(tag => {
    tagContainer.prepend(createTag(tag));
  });
}



$(document).on('keypress',function(e) {
  if(e.which == 13) {
      e.target.value.split(',').forEach(tag => {
      tags.push(tag); 
    });
      
    addTags();
    input.val("");
  }
});


document.addEventListener('click', function(e){
  
  const job = e.target.getAttribute('job');
  if(job=="remove-tag"){
    const value = e.target.getAttribute('data-id');
    const index = tags.indexOf(value);

    tags = [...tags.slice(0,index),...tags.slice(index + 1)];
    console.log(tags);

    addTags();
  
  }
})


$(document).ready(function () {

  $("i[job='menu']").click(function (event) {
    event.preventDefault();
    $(".desktopMenu").toggleClass("open");

  });


  $("i[job='make-search']").click(function (event) {
    event.preventDefault();

    newSearch = $("#search-bar-input").val();

    if (newSearch) {
      console.log(newSearch);
      $(".mobileSearch").toggleClass("open");
      $("#search-bar-input").blur();
      $("#search-bar-input").val(undefined);
    } else {
      $(".mobileSearch").toggleClass("open");
      $("#search-bar-input").focus();
    }
  });

  $("i[job='desktop-search']").click(function (event) {
    event.preventDefault();

    newSearch = $("#search-query").val();

    if (newSearch) {
      console.log(newSearch);
      $("#search-query").blur();
      $("#search-query").val(undefined);
    } else {
    }
  });

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
    console.log('/like/' + $(this).children('#thumbs-up').attr("value"));
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
      }



    });

  });
  



  $(".tag").click(function (event) {
    event.preventDefault();    

    const value = event.getAttribute('data-id');
    const index = tags.indexOf(value);

    tags = [...tags.slice(0,index),...tags.slice(index + 1)];
  });


  $( "i[job='add-friend']" ).click( function(event) {		
		event.preventDefault();
    console.log('/send-invite/' + $(this).parent().children("#add-button").attr("sender") + '/' + $(this).parent().children("#add-button").attr("value"));
    
    $.ajax({
      type: 'POST',
      url: '/send-invite/',
      data: {
        sender:$(this).parent().children("#add-button").attr("sender"), 
        receiver:$(this).parent().children("#add-button").attr("value"),
        csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
      },
      success: function(){
        window.location.assign('/');
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

});
