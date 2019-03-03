let data= {};
let data_preview;
let station_select;
let label_input;
$( document ).ready(function(){
	$.ajax({
	   url: "http://127.0.0.1:8000/get-stations/",
	   async:false,
	   success: function (d) {
	   	  console.log(d);
		  data = d;
	   }
	});

	station_select = $("#station-select");
	data_preview = $("#data-preview");
	label_input = $("#label");

	for(let i = 0; i< data.length; i++){
        station_select.append(new Option(data[i]['fields'].label, data[i]['fields'].RLOIid));
    }

	//SORT-----------------------------------------------
	var options = $('#station-select option');
	let arr = options.map(function(_, o) {
        return {
            t: $(o).text(),
            v: o.value
        };
    }).get();
	arr.sort(function(o1, o2) {
        return o1.t > o2.t ? 1 : o1.t < o2.t ? -1 : 0;
    });
    options.each(function(i, o) {
        o.value = arr[i].v;
        $(o).text(arr[i].t);
    });
    //--------------------------------------------------

	//BUTTON LISTENERS
    station_select.change(function() {
    	data_preview.empty();
	  id = station_select.val();
	  item = {};
	  for(let i = 0; i< data.length; i++){
         if(data[i]['fields'].RLOIid == id){
         	item = data[i];
		 }
	  }
	  label_input.val(item['fields'].label);
       for (var k in item['fields']) {
       	data_preview.append("<li class='list-group-item'><b>"+k+":</b> "+item['fields'][k]+"</li>");
       }
	});

    $( document).on( "click", ".del-btn" ,function() {
		//if accepted
		var btn = $(this);
		if (confirm('Are you sure you want unsubscribe from this station?')) {
			let dataString =JSON.stringify({station: $(this).attr("station")})
			$.ajax({
			   url: "/unsub/",
			   type: "post",
			   timeout: 1000,
			   datatype: "json",
			   data: dataString,
				success: function(d){
			   		d = $.parseJSON(d);
					console.log(d.status);
					if(d.status){
						let wanted = btn.parent().parent();
    					if (wanted.hasClass('row')) wanted.remove();
					}
				}
			});
		}
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