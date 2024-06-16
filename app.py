from flask import Flask, request, jsonify, render_template
import geopandas as gpd
from shapely.geometry import Polygon, Point
import pandas as pd
import numpy as np

app = Flask(__name__)

def generate_rectilinear_path(polygon, spacing=10):
    minx, miny, maxx, maxy = polygon.bounds
    x_coords = np.arange(minx, maxx, spacing)
    y_coords = np.arange(miny, maxy, spacing)
    
    waypoints = []
    for y in y_coords:
        line = [Point(x, y) for x in x_coords]
        for point in line:
            if polygon.contains(point):
                waypoints.append((point.x, point.y, 50))  # Assuming 50m altitude

    return waypoints

def generate_kml(waypoints):
    kml_template = """
    <?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:wpml="http://www.dji.com/wpmz/1.0.2">
      <Document>
        <wpml:missionConfig>
          <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
          <wpml:finishAction>goHome</wpml:finishAction>
          <wpml:exitOnRCLost>executeLostAction</wpml:exitOnRCLost>
          <wpml:executeRCLostAction>goBack</wpml:executeRCLostAction>
          <wpml:globalTransitionalSpeed>2.5</wpml:globalTransitionalSpeed>
          <wpml:droneInfo>
            <wpml:droneEnumValue>68</wpml:droneEnumValue>
            <wpml:droneSubEnumValue>0</wpml:droneSubEnumValue>
          </wpml:droneInfo>
        </wpml:missionConfig>
        <Folder>
          <wpml:templateId>0</wpml:templateId>
          <wpml:executeHeightMode>relativeToStartPoint</wpml:executeHeightMode>
          <wpml:waylineId>0</wpml:waylineId>
          <wpml:distance>0</wpml:distance>
          <wpml:duration>0</wpml:duration>
          <wpml:autoFlightSpeed>2.5</wpml:autoFlightSpeed>
          {}
        </Folder>
      </Document>
    </kml>
    """
    placemarks = ""
    for i, waypoint in enumerate(waypoints):
        placemarks += f"""
        <Placemark>
          <Point>
            <coordinates>{waypoint[0]},{waypoint[1]}</coordinates>
          </Point>
          <wpml:index>{i}</wpml:index>
          <wpml:executeHeight>{waypoint[2]}</wpml:executeHeight>
          <wpml:waypointSpeed>2.5</wpml:waypointSpeed>
        </Placemark>
        """
    return kml_template.format(placemarks)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    gdf = gpd.GeoDataFrame.from_features(data['features'])
    polygon = gdf.iloc[0].geometry
    waypoints = generate_rectilinear_path(polygon, spacing=0.0001)  # Adjust spacing as needed
    kml_content = generate_kml(waypoints)
    return jsonify({'kml': kml_content})

if __name__ == '__main__':
    app.run(debug=True)
