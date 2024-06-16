var map = L.map('map').setView([39.8283, -98.5795], 4);  // Centered on USA

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems
    },
    draw: {
        polygon: true,
        polyline: false,
        circle: false,
        rectangle: true,
        marker: false,
        circlemarker: false
    }
});
map.addControl(drawControl);

map.on(L.Draw.Event.CREATED, function (event) {
    var layer = event.layer;
    drawnItems.addLayer(layer);
});

document.getElementById('generate').onclick = function() {
    var data = drawnItems.toGeoJSON();
    var altitude = document.getElementById('altitude').value;
    var speed = document.getElementById('speed').value;
    var cameraAction = document.getElementById('cameraAction').value;

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            geojson: data,
            altitude: altitude,
            speed: speed,
            cameraAction: cameraAction
        })
    })
    .then(response => response.json())
    .then(data => {
        var link = document.createElement('a');
        link.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(data.kml);
        link.download = 'waypoints.kml';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
};
