// NAVIGATION: OFF CANVAS

$(".nav-trigger").on("click", function(e){
	e.preventDefault();
	e.stopPropagation();
	$(".nav-block").toggleClass("nav-block-open");
});

$(".nav-block").on("click", function(e){
 	e.stopPropagation();
});

$(window).on("click", function(){
	$(".nav-block").removeClass("nav-block-open");
});


// ACTIVE NAV STYLING

$(".nav li a").each(function(){
	if(this.href == window.location.href) {
		$(this).addClass("active");
	}
});

function disableButton(){
	$('.disable-btn').prop('disabled',true);
    setTimeout(function(){
       // enable click after 1 second
       $('.disable-btn').prop('disabled',false);
    },1000);
}

function play() {
	var text = document.getElementById("text");
	var voice = document.getElementById("voice");
	var random = document.getElementById("random");
	var speak = document.getElementById("speak");
	if ( random.checked ) {
		var url = "http://192.168.1.160:5080/chatbot_audio/randomtms/" + new Date().getTime() + "/" + voice.value + "/000000/it/";
		if ( text.value !== undefined && text.value !== '') {
			url = url + text.value
		}
		var audio = document.getElementById("audio");
		audio.src = url;
		audio.load();
		audio.play();  
		disableButton();
	} else if ( speak.checked ) {
		if ( text.value === undefined || text.value === '') {
			alert("To use Speak button, Text is mandatory.")
		} else {
			var voice = document.getElementById("voice");		
			var url = "http://192.168.1.160:5080/chatbot_audio/repeat/learn/" + text.value + "/" + voice.value + "/000000/it/audio.mp3";
			var audio = document.getElementById("audio");
			audio.src = url;
			audio.load();
			audio.play(); 
			disableButton();
		}

	}
}

function changeVoiceValue()
{
	var random = document.getElementById("random");
	var speak = document.getElementById("speak");
	if ( random.checked ) {
		document.getElementById("voice").value = 'random';
	} else if ( speak.checked ) {
		document.getElementById("voice").value = 'google';
	}
}