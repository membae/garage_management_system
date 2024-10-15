from flask import Flask, request, jsonify,make_response
from models import db, User, Vehicle, Service, Appointment, ServiceVehicle
from models import db, User, Vehicle, Service, Appointment, ServiceVehicle
from datetime import datetime
from flask_migrate import Migrate
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Garage routes</h1>'

# Register User and Manage Vehicle Information
@app.route('/users', methods=['POST'])
def register_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'], phone_number=data['phone_number'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'}), 201


@app.route('/users/<int:user_id>/vehicles', methods=['POST'])
def add_vehicle(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    new_vehicle = Vehicle(
        make=data['make'], 
        model=data['model'], 
        year=data['year'], 
        license_plate=data['license_plate'],
        owner=user
    )
    db.session.add(new_vehicle)
    db.session.commit()
    return jsonify({'message': 'Vehicle added successfully!'}), 201


@app.route('/users/<int:user_id>/vehicles', methods=['GET'])
def get_user_vehicles(user_id):
    user = User.query.get_or_404(user_id)
    vehicles = Vehicle.query.filter_by(user_id=user.id).all()
    return jsonify([{'id': v.id, 'make': v.make, 'model': v.model, 'year': v.year} for v in vehicles]), 200

# Schedule Service Appointment
@app.route('/appointments', methods=['POST'])
def schedule_appointment():
    data = request.get_json()
    user_id = data['user_id']
    vehicle_id = data['vehicle_id']
    service_date = datetime.strptime(data['service_date'], "%Y-%m-%d %H:%M:%S")
    status = 'scheduled'

    # Check user and vehicle exist
    user = User.query.get(user_id)
    if user is None:
         return jsonify({"error": f"User with ID {user_id} does not exist."}), 404
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle is None:
        return jsonify({"error": f"Vehicle with ID {vehicle_id} does not exist."}), 404

    new_appointment = Appointment(user=user, vehicle=vehicle, service_date=service_date, status=status)
    try:
        db.session.add(new_appointment)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({"error": "Could not schedule appointment. Please check the details."}), 500

    return jsonify({'message': 'Appointment scheduled successfully!'}), 201

# View List of Services Offered by the Garage
@app.route('/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    return jsonify([{'id': s.id, 'service_name': s.service_name, 'description': s.description, 'price': str(s.price)} for s in services]), 200

# Garage Owner: Manage Services
@app.route('/services', methods=['POST'])
def add_service():
    data = request.get_json()
    new_service = Service(
        service_name=data['service_name'], 
        description=data['description'], 
        price=data['price']
    )
    db.session.add(new_service)
    db.session.commit()
    return jsonify({'message': 'Service added successfully!'}), 201


@app.route('/services/<int:service_id>', methods=['PATCH'])
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    data = request.get_json()

    service.service_name = data.get('service_name', service.service_name)
    service.description = data.get('description', service.description)
    service.price = data.get('price', service.price)

    db.session.commit()
    return jsonify({'message': 'Service updated successfully!'}), 200


@app.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Service deleted successfully!'}), 200

# Garage Owner: View Customer Requests
@app.route('/appointments', methods=['GET'])
def view_appointments():
    appointments = Appointment.query.all()
    return jsonify([
        {
            'id': a.id, 
            'user': a.user.name, 
            'vehicle': f"{a.vehicle.make} {a.vehicle.model}", 
            'service_date': a.service_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': a.status
        } for a in appointments
    ]), 200

@app.route('/appointments/<int:appointment_id>', methods=['PATCH'])
def mark_appointment_complete(appointment_id):
    # Fetch the appointment by ID
    appointment = Appointment.query.get_or_404(appointment_id)

    # Update the status
    appointment.status = 'complete'

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': f'Appointment {appointment_id} marked as complete!'}), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)