from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    email = db.Column(db.String(150), unique=True, nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class AirportManagement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    AirportName = db.Column(db.String(100))
    CityName = db.Column(db.String(100))
    Area = db.Column(db.String(100))

class TicketCounter(db.Model):
    TicketId = db.Column(db.Integer, primary_key=True)
    PassengerId = db.Column(db.Integer, db.ForeignKey('passengers.PassengerId'))
    Source = db.Column(db.String(100))
    Destination = db.Column(db.String(100))
    Price = db.Column(db.Float)
    FlightId = db.Column(db.Integer, db.ForeignKey('flight.FlightId'))
    SeatNumber = db.Column(db.String(10))

    passenger = db.relationship('Passengers', back_populates='ticket')

    def to_dict(self):
        return {
            'TicketId': self.TicketId,
            'Source': self.Source,
            'Destination': self.Destination,
            'Price': self.Price,
            'FlightId': self.FlightId,
            'SeatNumber': self.SeatNumber
        }

class Flight(db.Model):
    FlightId = db.Column(db.Integer, primary_key=True)
    FlightName = db.Column(db.String(100))
    Capacity = db.Column(db.Integer)
    StartingTime = db.Column(db.String(100))
    ReachingTime = db.Column(db.String(100))
    Source = db.Column(db.String(100))
    Destination = db.Column(db.String(100))
    Price = db.Column(db.Float)

    def to_dict(self):
        return {
            'FlightId': self.FlightId,
            'FlightName': self.FlightName,
            'Capacity': self.Capacity,
            'StartingTime': self.StartingTime,
            'ReachingTime': self.ReachingTime,
            'Source': self.Source,
            'Destination': self.Destination,
            'Price': self.Price
        }

class Employees(db.Model):
    __tablename__ = 'employees'
    EmployeeId = db.Column(db.Integer, primary_key=True)
    EmployeeName = db.Column(db.String(100))
    EmployeeSalary = db.Column(db.Float)
    Designation = db.Column(db.String(100))

    def to_dict(self):
        return {
            'EmployeeId': self.EmployeeId,
            'EmployeeName': self.EmployeeName,
            'EmployeeSalary': self.EmployeeSalary,
            'Designation': self.Designation
        }

class AirportEmployees(Employees):
    __tablename__ = 'airport_employees'
    EmployeeId = db.Column(db.Integer, db.ForeignKey('employees.EmployeeId'), primary_key=True)
    Department = db.Column(db.String(100))

    def to_dict(self):
        data = super().to_dict()
        data['Department'] = self.Department
        return data

class AirplaneEmployees(Employees):
    __tablename__ = 'airplane_employees'
    EmployeeId = db.Column(db.Integer, db.ForeignKey('employees.EmployeeId'), primary_key=True)

    def to_dict(self):
        return super().to_dict()

class Runway(db.Model):
    RunwayNumber = db.Column(db.Integer, primary_key=True)
    FlightName = db.Column(db.String(100))
    OccupiedStatus = db.Column(db.Boolean)

class Passengers(db.Model):
    PassengerId = db.Column(db.Integer, primary_key=True)
    PassengerName = db.Column(db.String(100))
    PassengerAge = db.Column(db.Integer)
    
    ticket = db.relationship('TicketCounter', back_populates='passenger', uselist=False)
    luggage = db.relationship('Luggage', back_populates='passenger', uselist=False)

    def to_dict(self):
        return {
            'PassengerId': self.PassengerId,
            'PassengerName': self.PassengerName,
            'PassengerAge': self.PassengerAge,
            'TicketId': self.ticket.TicketId if self.ticket else None,
            'LuggageId': self.luggage.LuggageId if self.luggage else None,
            'TicketDetails': self.ticket.to_dict() if self.ticket else None,
            'LuggageDetails': self.luggage.to_dict() if self.luggage else None
        }

class NoticeBoard(db.Model):
    FlightId = db.Column(db.Integer, db.ForeignKey('flight.FlightId'), primary_key=True)
    FlightName = db.Column(db.String(100))
    ArrivalTime = db.Column(db.String(100))
    DepartureTime = db.Column(db.String(100))
    Source = db.Column(db.String(100))
    Destination = db.Column(db.String(100))
    Status = db.Column(db.String(50))

class Luggage(db.Model):
    LuggageId = db.Column(db.Integer, primary_key=True)
    PassengerId = db.Column(db.Integer, db.ForeignKey('passengers.PassengerId'))
    FlightId = db.Column(db.Integer, db.ForeignKey('flight.FlightId'))
    NoOfLuggages = db.Column(db.Integer)

    passenger = db.relationship('Passengers', back_populates='luggage')

    def to_dict(self):
        return {
            'LuggageId': self.LuggageId,
            'FlightId': self.FlightId,
            'NoOfLuggages': self.NoOfLuggages
        }


class NewsletterSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'subscribed_at': self.subscribed_at.isoformat()
        }

