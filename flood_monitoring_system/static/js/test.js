$( function(){
	$( "#device-date-1" ).datetimepicker({dateFormat:'dd/mm/yy'});
	$( "#station-date-1" ).datetimepicker({dateFormat:'dd/mm/yy'});
	$( "#notification-date-1" ).datetimepicker({dateFormat:'dd/mm/yy'});

	$( "#stats" ).hide();
});
let tables = [];
$( document ).ready(function(){
//DEFINE TABLES
 tables = ["#station-table", "#sensor-table", "#alert-table"];

//POPULATE STATIONS SELECT===========================================================
	$.ajax({
	   url: "http://127.0.0.1:8000/get-stations/",
	   async:false,
	   success: function (d) {
		  data = d;
	   }
	});

	station_select = $("#station-select-1");

	for(let i = 0; i< data.length; i++){
        station_select.append(new Option(data[i]['fields'].label, data[i]['fields'].label));
    }

	//SORT-----------------------------------------------
	var options = $('#station-select-1 option');
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

//TABLE JS===========================================================================
	//ADD BUTTON
    $( ".add-btn" ).on( "click", function() {
		//gets the tbody of the table related to the button
		var tbody = $(this).closest('table').children('tbody');

		//get the last row
		var lastRow = tbody.find("tr:last-child");
		//gets the last rows input
		var input = lastRow.find("input:first-child, select:first-child, textarea:first-child");
		//gets the id of that input
		var lastId = input.attr("id");
		//if its null go to the next collumn
		while(lastId == null){
			lastId = input.next('td').find('input, select, textarea');
		}
		//get its html and increment id
		var oldNum =  lastId.match(/\d+/)[0];
		var newNum = parseInt(oldNum) +1;

		var tempRow = lastRow.clone();
		//clear values
		tempRow.find('td').each (function() {
			var input = $(this).find("input, select, textarea");
			if ( !input.is("select") ){
		  		input.attr("value","");
			}else{
				input.find('option:selected').removeAttr("selected");
				input.find('option:first-child').attr("selected", "true");
			}
		});

		tempRow = "<tr>"+tempRow.html()+"</tr>";
		var newRow = tempRow.replace(new RegExp("-"+oldNum, 'g') , "-"+newNum);

		//add new row
		tbody.append(newRow);

		//CHECK FOR DATE LISTNERS=========================================================
		var dateInputs = [];

		var row = tbody.find("tr:last-child");
		var col = row.find("td:first-child");
		input = col.find("input, select, textarea");
		var id = input.attr("id");
		while(typeof id !== "undefined"){
			if (input.hasClass("hasDatepicker")){
				dateInputs.push(input);
			}

			//next col in row
			col = col.next("td");
			input = col.find("input, select, textarea");
			id = input.attr("id");
		}
		//FOR EVERY NEW DATEPICKER
		for(var i=0; i<dateInputs.length; i++) {
			dateInputs[i].on('focus', function(){
			  if(!$(this).data('datepickerclass')) {
			   $(this).removeClass("hasDatepicker");
			   $(this).datetimepicker({dateFormat:'dd/mm/yy'});
			   $(this).datetimepicker("show");
			  }
			});
		}

		//================================================================================

    });
	//DELETE BUTTON
  	$( document).on( "click", ".del-btn" ,function() {
		//if accepted
		if (confirm('Are you sure you want to delete this item?')) {
			//get the tbody related to the button
			var tbody = $(this).closest("tbody");
			//get number of rows
			var numOfRows = tbody.prop('rows').length;
			if(numOfRows > 1){//only if there's more than one
				//remove row
				$(this).closest("tr").remove();
				//upadte Id's  so they're in accending order
				var row =  tbody.find("tr:first-child");
				for(var i = 1; i < numOfRows; i++){
					//get first col of row
					var col = row.find("td:first-child");				//col
					var input = col.find("input, select, textarea");	//col's input
					var id = input.attr("id");							//col's input id
					while(typeof id !== "undefined"){									//while input id exists
						//update id with i
						var oldNum =  id.match(/\d+/)[0];
						input.attr("id", id.replace(new RegExp("-"+oldNum, 'g') , "-"+i));
						//next col in row
						col = col.next("td");
						input = col.find("input, select, textarea");
						id = input.attr("id");
					}
					var rowHtml = row.html();
					row.html();
					//go to next row
					row = row.next('tr');
				}

			}else{//can't do because you nee more than one
				alert("Cannot Delete. You must have at least one row.")
			}
		}
	});

  	//GENERATE RESULTS
	$("#gen").click(function() {
		if(form_is_valid()){
			console.log("FORM IS VALID");
            $("#test-form").submit();
        }
	});


    //GLOBAL LISTNER====================================================================
	var timeoutId;
	$(document).on('keyup change', 'input, select, textarea',function(e) {
			clearTimeout(timeoutId);
			timeoutId = setTimeout(function() {
			validate($(this));
		}, 100);
	});

});





//VALIDATORS===================================================================
function form_is_valid(){
	let valid = true;
	for(var x = 0; x < tables.length; x++) {
        let table = getTableContents(tables[x]);
        console.log(table);
        for (let i = 0; i < table.length; i++) {
            for (let j = 0; j < table[i].length; j++) {
                let item = table[i][j];
                if(!validate(item)){
                	valid = false;
				}
            }
        }
    }
	return valid;
}
function validate(item){
	let valid = true;
	let type = item.attr('vtype');
	if(type == "select"){
		if(!isSelected(item)){
			valid = false;
			item.addClass("input-error");
		}else{
			item.removeClass("input-error");
		}
	}else if(type == "text"){
		if(!validateText(item)){
			valid = false;
			item.addClass("input-error");
		}else{
			item.removeClass("input-error");
		}
	}else if(type == "number"){
		if(!validateNum(item)){
			valid = false;
			item.addClass("input-error");
		}else{
			item.removeClass("input-error");
		}
	}else if(type == "date"){
		if(!validateDate(item)){
			valid = false;
			item.addClass("input-error");
		}else{
			item.removeClass("input-error");
		}
	}
	return valid;
}

function validateDate(item){
	let date = item.val();
	let re = /^([1-9]|([012][0-9])|(3[01]))\/([0]{0,1}[1-9]|1[012])\/\d\d\d\d\s([0-1]?[0-9]|2?[0-3]):([0-5]\d)$/;
	return re.test(date);
}

function validateNum(item){
	let num = item.val();
	return (num.length >0) && !isNaN(num)
}

function validateText(item){
	let txt = item.val();
	return txt.length > 0
}
function isSelected(item){
	return item.val() !== "" && item.val() !== null ;
}

//MISC=========================================================================
function getTableContents(tableId){
	var table = $(tableId).children('tbody');
	var tableRow = table.find("tr:first-child");
	var numOfRows = table.prop('rows').length;
	var arr = [];

	//remember it's impossible to be less than 1
	for(var i = 0; i < numOfRows; i++){
		var tableRowInputs = []																		//for 2d array
		var numOfInputs = tableRow.children('td').length;											//num of inputs
		var tableCol= tableRow.children("td:first-child");												//get first col
			for(var j = 0; j < numOfInputs; j++){													//for each col
				var item = tableCol.find("input:first-child, select:first-child, textarea:first-child");
				if(item.length){																	//if item is an input
					tableRowInputs.push(item);														//add to array of inputs
				}
				tableCol = tableCol.next("td");														//go to next col
			}
		arr.push(tableRowInputs);
		tableRow = tableRow.next("tr");
	}
	return arr;
}