let mymap;
let stationData;
let sensorType;
$(document).ready(() => {
    mymap = L.map('mapid').setView([19.1334, 72.9133], 14);

	L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
			'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		id: 'mapbox/streets-v11',
		tileSize: 512,
		zoomOffset: -1
	}).addTo(mymap);
    addHomeMarker();
	//L.marker([19.1334, 72.9133]).addTo(mymap);
})
const addHomeMarker = () => {
    var greenIcon = L.icon({
    iconUrl: '../static/home.png',

    iconSize:     [50, 50], // size of the icon
    shadowSize:   [50, 64], // size of the shadow
    iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
    shadowAnchor: [4, 62],  // the same for the shadow
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
        });
    L.marker([19.1334, 72.9133], {icon: greenIcon}).addTo(mymap).bindPopup("IIT Bombay.");
};
function loadData (dataType){
    $('#overlay').css('display', 'block')
    if(dataType === 'getC'){
        ajaxGet('/getC', {}, getCapabilityCallBack);
    }else if(dataType === 'descSensor'){
        ajaxGet('/getDescSensor', {}, getDescSensor);
    }else if(dataType === 'AirT'){
        ajaxGet('/getAirTemp', {}, getAirTemp);
    }else if(dataType === 'WaterLevel'){
        ajaxGet('/getWaaterLevel', {}, getWaterLevel);
    }
}
const getCapabilityCallBack = (data) => {
    $('#WCS').css('display', 'block');
    $('.getCapDetails').css('display', 'block');
    $('.indi_sensor_lst').css('display', 'none');
    stationData = data.station;
    $('#getC').val(data.xml);
    let station_list_wrapper = $('.stationList');
    station_list_wrapper.html('');
    let station_html = '';
    station_list_wrapper.append(`<option value="0">-- Please Select Station --</option>`)
    addMarkerGetCapability(data);
    $.each(data.station, (index, val) => {
        station_html = `<option value="${val['name']}">${index} - ${val['name']}</option>`;
        station_list_wrapper.append(station_html);
    });

    let server_wrapper = $('.server_details');
    server_wrapper.html('');
    let serverHtml = `<h3>Server Details</h3>
                       <div class="row">
                            <div class="col-md-6">Provide Name - ${data.providerName}</div>
                            <div class="col-md-6">Provider Site - ${data.providerSite}</div>
                       </div>
                        <div class="row">
                            <p>Provider Address - ${data.address}</p>
                        </div>`;
    server_wrapper.html(serverHtml);
    $('#overlay').css('display', 'none');
}

const getDescSensor = (data) => {
     $('#WCS').css('display', 'block');
     $('.indi_sensor_lst').css('display', 'none');
     $('#getC').val(data.responseText);
     removeAttributes();
     addHomeMarker();
     mymap.flyTo([19.1334, 72.9133],13);
     $('#overlay').css('display', 'none');
}

const getAirTemp = (data) => {
    $('#WCS').css('display', 'block');
    sensorType = 'air_temperature';
     populate_sensor_list(data);
}

const getWaterLevel = (data) => {
    $('#WCS').css('display', 'block');
    sensorType = 'waves';
     populate_sensor_list(data);

}
const graphMap = (data) => {
    $('#getC').val(data.xml);
    let lat = +data.location.split(' ')[0];
     let long = +data.location.split(' ')[1];
     var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: data.data.map(x => x.date),
        datasets: [{
            label: 'Water Level',
            data: data.data.map(x => +x.val),
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
removeAttributes();
L.marker([lat, long]).addTo(mymap);
mymap.flyTo([lat, long],5);
// var marker = L.marker([51.5, -0.09]).addTo(mymap);
$('#overlay').css('display', 'none');
}

const removeAttributes = () => {
    let all_markers = mymap._layers;
	let all_keys = Object.keys(all_markers);
	$.each(all_keys, (index, value) => {
		if (index != 0){
			mymap._layers[value].remove();
		};
	})
}

const addMarkerGetCapability = (data) => {
    removeAttributes();
    addHomeMarker();
    $.each(data.station, (index, value) => {
        let lat = value['cords'].split(' ')[0];
        let long = value['cords'].split(' ')[1];
		L.marker([lat, long]).addTo(mymap)
			.bindPopup(`<p><b>Name- ${value['name']}</b> <br>
				Address - ${value['description']} <br></p>`)
			.on('popupopen', function (popup) {

			});
	});
}

$('.stationList').on('change', function(){
    let single_station = stationData.filter(x => x.name === this.value)[0];
    let wrapper = $('.stationDetails');
    wrapper.html('');
    let params = single_station.params.join(', ');
    let html = `<div class="row">Station Name - ${single_station['name']}</div>
                <div class="row">Station Description - ${single_station['description']}</div>
                <div class="row">Station Supported Parameters - ${params}</div>`;
    wrapper.append(html);
    let lat = single_station['cords'].split(' ')[0];
    let long = single_station['cords'].split(' ')[1];
    mymap.flyTo([lat, long],13);
})


const populate_sensor_list = (data) => {
     $('#overlay').css('display', 'block');
    $('.getCapDetails').css('display', 'none');
    $('.indi_sensor_lst').css('display', 'block');
    stationData = data
    $('#getC').val('Please Select any sensor to view its xml and data');
    $('#getC').attr('disabled', true);
    let station_list_wrapper = $('.indi_stationList');
    station_list_wrapper.html('');
    let station_html = '';
    station_list_wrapper.append(`<option value="0">-- Please Select Station --</option>`)
    $.each(data, (index, val) => {
        station_html = `<option value="${val['name']}">${index + 1}. ${val['name']}</option>`;
        station_list_wrapper.append(station_html);
    });
    $('#overlay').css('display', 'none');
}

const single_sensor_Callback = (data) => {
    if(data.data.length === 0){
        $('#getC').val(data.text);
        //$('#map').css('display', 'none');
    }else{
        graphMap(data);
        //$('#map').css('display', 'block');
    }
    $('#overlay').css('display', 'none');
}

$('#sensor_submit').click(() => {
    $('#overlay').css('display', 'block');
   let sensorId = $('.indi_stationList').val();
   let start_date = $('#start_date').val();
   let end_date = $('#end_date').val();
   let diff = (new Date(start_date) - new Date(end_date))/(1000*3600*24);
   if (sensorId === "0" || start_date === "" || end_date === "" || diff > 31){
       toastr.error('Please select appropriate station or start/end date and the ' +
           'date interval should be less than 31 days ');
   }else{
       start_date = start_date + 'T00:00:00Z';
       end_date = end_date + 'T00:00:00Z';
       sensorId = sensorId.split('-')[1];
       ajaxPost('/getSensorData', {'sensorId': sensorId,
           'sensorType': sensorType, 'startDate': start_date, 'endDate': end_date}, single_sensor_Callback);
   }
});