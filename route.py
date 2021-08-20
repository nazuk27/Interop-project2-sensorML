from flask import Flask,request,redirect,jsonify,session
from flask.templating import render_template
from classes.functions import Call
import json
import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

@app.route('/')
def home_return():
    return render_template("index.html")

@app.route('/getC', methods=['GET'])
def getCapabilities():
    call = Call()
    resp = call.get_Capabilities(APP_ROOT)
    return jsonify(resp)

@app.route('/getDescSensor', methods=['GET'])
def getDescSensor():
    call = Call()
    resp = call.descSensor(APP_ROOT)
    return resp

@app.route('/getAirTemp', methods=['GET'])
def getAirTemp():
    call = Call()
    resp = call.airTemp(APP_ROOT)
    return jsonify(resp)

@app.route('/getWaaterLevel', methods=['GET'])
def getWaterLevel():
    call = Call()
    resp = call.wavesLevel(APP_ROOT)
    return jsonify(resp)

@app.route('/getSensorData', methods=['POST'])
def getSensorData():
    data = request.get_json(force=True)
    call = Call()
    sensorId = data['sensorId']
    sensorType = data['sensorType']
    start_date = data['startDate']
    end_date = data['endDate']
    resp = call.specific_sensor_data(sensorId, sensorType, start_date, end_date)
    return jsonify(resp)

if __name__ == '__main__':
    app.secret_key = os.urandom(32)
    app.run(debug=True)
