$( document ).ready(function(){

	$(".read-notification-switch").change(function () {
		let dataString =JSON.stringify({notification: $(this).attr("name"),read: !$(this).prop('checked')})
		console.log(dataString);
		$.ajax({
		   url: "/readnotification/",
		   type: "post",
		   timeout: 1000,
		   datatype: "json",
		   data: dataString
		});
    });

	var csrftoken = $.cookie('csrftoken');

	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
    });
	$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
    });
});

function csrfSafeMethod(method) {
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}