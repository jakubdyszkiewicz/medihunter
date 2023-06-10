from flask import Flask, request, jsonify
from medicover_session import Appointment, MedicoverSession
from datetime import datetime
import base64
import appdirs
import json

app = Flask(__name__)

def parse_basic_auth_header(auth_header):
    auth_type, encoded_credentials = auth_header.split(' ', 1)
    if auth_type != 'Basic':
        raise ValueError('Invalid authentication type')
    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8').replace('\n', '')
    username, password = decoded_credentials.split(':')
    return username, password

def logged_in_med_session():
    username, password = parse_basic_auth_header(request.headers.get('Authorization'))
    med_session = MedicoverSession(username, password)
    med_session.log_in()
    return med_session

@app.route('/params/regions', methods=['GET'])
def get_regions():
    med_session = logged_in_med_session()
    med_regions = med_session.load_available_regions()
    return med_regions

@app.route('/params/specializations', methods=['GET'])
def get_specializations():
    region = request.args.get('region')
    if not region:
        return jsonify({'error': 'region is required'}), 400

    med_session = logged_in_med_session()
    med_specializations = med_session.load_available_specializations(region=region, bookingtype=2)
    return med_specializations

@app.route('/params/clinics', methods=['GET'])
def get_clinics():
    region = request.args.get('region')
    if not region:
        return jsonify({'error': 'region is required'}), 400
    specialization = request.args.get('specialization')
    if not specialization:
        return jsonify({'error': 'specialization is required'}), 400

    med_session = logged_in_med_session()
    med_specializations = med_session.load_available_clinics(region=region, bookingtype=2, specialization=specialization)
    return med_specializations

@app.route('/params/doctors', methods=['GET'])
def get_doctors():
    region = request.args.get('region')
    if not region:
        return jsonify({'error': 'region is required'}), 400
    specialization = request.args.get('specialization')
    if not specialization:
        return jsonify({'error': 'specialization is required'}), 400
    clinic = request.args.get('clinic')
    if not clinic:
        return jsonify({'error': 'clinic is required'}), 400

    med_session = logged_in_med_session()
    med_doctors = med_session.load_available_doctors(region=region, bookingtype=2, specialization=specialization, clinic=clinic)
    return med_doctors

def toDate(dateString): 
    return datetime.datetime.strptime(dateString, "%Y-%m-%d").date()

@app.route('/find', methods=['GET'])
def find_appointments():
    region = request.args.get('region')
    if not region:
        return jsonify({'error': 'region is required'}), 400
    specialization = request.args.get('specialization', default=-1, type=int)
    clinic = request.args.get('clinic', default=-1, type=int)
    doctor = request.args.get('doctor', default=-1, type=int)
    start_date = request.args.get('start_date', default = datetime.today(), type = toDate)
    # end_date = request.args.get('end_date')

    med_session = logged_in_med_session()

    found_appointments = med_session.search_appointments(
        region=region,
        bookingtype=2,
        specialization=specialization,
        clinic=clinic,
        doctor=doctor,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=None,
        start_time="0:00",
        end_time="23:59",
        service=-1,
        disable_phone_search=False
    )

    if not found_appointments:
        return jsonify([])

    return jsonify([appointment._asdict() for appointment in found_appointments])

if __name__ == '__main__':
    app.run(host='0.0.0.0')
