from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Users Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    vehicles = db.relationship('Vehicle', back_populates='owner', lazy=True)
    appointments = db.relationship('Appointment', back_populates='user', lazy=True)


# Vehicles Table (One-to-Many with Users)
class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    owner = db.relationship('User', back_populates='vehicles')
    services = db.relationship('ServiceVehicle', back_populates='vehicle', lazy=True)
    appointments = db.relationship('Appointment', back_populates='vehicle', lazy=True)


# Services Table
class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    vehicles = db.relationship('ServiceVehicle', back_populates='service', lazy=True)


# Service_Vehicles Table (Many-to-Many between Services and Vehicles)
class ServiceVehicle(db.Model):
    __tablename__ = 'service_vehicles'
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)

    # Additional Columns
    service_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', back_populates='vehicles')
    vehicle = db.relationship('Vehicle', back_populates='services')


# Appointments Table (One-to-Many with Users and Vehicles)
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    service_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='appointments')
    vehicle = db.relationship('Vehicle', back_populates='appointments')
