from flask import render_template, request, redirect, url_for, flash, session,jsonify, abort, Response, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from functools import wraps
from . import db
from .models import User, AirportManagement, TicketCounter, Flight, Employees, AirportEmployees, AirplaneEmployees, Runway, Passengers, NoticeBoard, Luggage, NewsletterSubscriber
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta, time
import json

class AirportForm(FlaskForm):
    AirportName = StringField('Airport Name', validators=[DataRequired()])
    CityName = StringField('City Name', validators=[DataRequired()])
    Area = StringField('Area', validators=[DataRequired()])
    submit = SubmitField('Add Airport')

# Define the admin-required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'admin':
            return render_template('dashboard.html', role='admin')
        else:
            return render_template('dashboard.html', role='user')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']  
            password = request.form['password']
            role = request.form['role']  

            # Check if the username or email already exists
            user = User.query.filter((User.username == username) | (User.email == email)).first()
            if user:
                flash('Username or email already exists')
                return redirect(url_for('register'))

            # Create new user with email
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful, please login.')
            return redirect(url_for('login'))
        return render_template('register.html')


    @app.route('/airport_management', methods=['GET', 'POST'])
    @login_required
    @admin_required 
    def airport_management():
        form = AirportForm()
        if form.validate_on_submit():
            new_airport = AirportManagement(
                AirportName=form.AirportName.data,
                CityName=form.CityName.data,
                Area=form.Area.data
            )
            db.session.add(new_airport)
            db.session.commit()
            flash('Airport added successfully.', 'success')
            return redirect(url_for('airport_management'))
        
        airports = AirportManagement.query.all()
        return render_template('airport_management.html', form=form, airports=airports)

    @app.route('/ticket_counter')
    @login_required
    def ticket_counter():
        return render_template('ticket_counter.html')

    @app.route('/flight_details')
    @login_required
    def flight_details():
        flights = Flight.query.all()
        return render_template('flight_details.html')

    @app.route('/employee_management')
    @login_required
    @admin_required
    def employee_management():
        return render_template('employee_management.html')

    @app.route('/runway_details')
    @login_required
    @admin_required  
    def runway_details():
        return render_template('runway_details.html')

    @app.route('/passenger_details')
    @login_required
    def passenger_details():
        return render_template('passenger_details.html')

    @app.route('/notice_board')
    @login_required
    @admin_required  
    def notice_board():
        return render_template('notice_board.html')

    @app.route('/luggage_details')
    @login_required
    def luggage_details():
        return render_template('luggage_details.html')

    @app.route('/add_airport', methods=['POST'])
    @login_required
    @admin_required  
    def add_airport():
        airport_name = request.form['AirportName']
        city_name = request.form['CityName']
        area = request.form['Area']
        new_airport = AirportManagement(AirportName=airport_name, CityName=city_name, Area=area)
        db.session.add(new_airport)
        db.session.commit()
        return redirect(url_for('airport_management'))
    
    @app.route('/delete_airport/<int:airport_id>', methods=['POST'])
    @login_required
    @admin_required  
    def delete_airport(airport_id):
        airport = AirportManagement.query.get_or_404(airport_id)
        db.session.delete(airport)
        db.session.commit()
        flash('Airport deleted successfully.', 'success')
        return redirect(url_for('airport_management'))
    

    @app.route('/get_flights', methods=['GET'])
    @login_required
    def get_flights():
        flights = Flight.query.all()
        return jsonify([flight.to_dict() for flight in flights])

    @app.route('/add_flight', methods=['POST'])
    @login_required
    @admin_required
    def add_flight():
        data = request.json
        new_flight = Flight(
            FlightName=data['FlightName'],
            Capacity=int(data['Capacity']),
            StartingTime=data['StartingTime'],
            ReachingTime=data['ReachingTime'],
            Source=data['Source'],
            Destination=data['Destination'],
            Price=float(data['Price'])
        )
        db.session.add(new_flight)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Flight added successfully'})

    @app.route('/update_flight/<int:flight_id>', methods=['PUT'])
    @login_required
    @admin_required
    def update_flight(flight_id):
        flight = Flight.query.get_or_404(flight_id)
        data = request.json
        flight.FlightName = data['FlightName']
        flight.Capacity = int(data['Capacity'])
        flight.StartingTime = data['StartingTime']
        flight.ReachingTime = data['ReachingTime']
        flight.Source = data['Source']
        flight.Destination = data['Destination']
        flight.Price = float(data['Price'])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Flight updated successfully'})

    @app.route('/delete_flight/<int:flight_id>', methods=['DELETE'])
    @login_required
    @admin_required
    def delete_flight(flight_id):
        flight = Flight.query.get_or_404(flight_id)
        db.session.delete(flight)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Flight deleted successfully'})



    @app.route('/get_employees', methods=['GET'])
    @login_required
    @admin_required
    def get_employees():
        all_employees = Employees.query.all()
        airport_employees = AirportEmployees.query.all()
        airplane_employees = AirplaneEmployees.query.all()
        
        return jsonify({
            'all_employees': [employee.to_dict() for employee in all_employees],
            'airport_employees': [employee.to_dict() for employee in airport_employees],
            'airplane_employees': [employee.to_dict() for employee in airplane_employees]
        })

    @app.route('/add_employee', methods=['POST'])
    @login_required
    @admin_required
    def add_employee():
        data = request.json
        if data['employeeType'] == 'airport':
            new_employee = AirportEmployees(
                EmployeeName=data['employeeName'],
                EmployeeSalary=data['employeeSalary'],
                Designation=data['employeeDesignation'],
                Department=data['employeeDepartment']
            )
        else:
            new_employee = AirplaneEmployees(
                EmployeeName=data['employeeName'],
                EmployeeSalary=data['employeeSalary'],
                Designation=data['employeeDesignation']
            )
        
        db.session.add(new_employee)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Employee added successfully', 'employee': new_employee.to_dict()})

    @app.route('/update_employee/<int:employee_id>', methods=['PUT'])
    @login_required
    @admin_required
    def update_employee(employee_id):
        employee = Employees.query.get_or_404(employee_id)
        data = request.json
        employee.EmployeeName = data['employeeName']
        employee.EmployeeSalary = data['employeeSalary']
        employee.Designation = data['employeeDesignation']
        if isinstance(employee, AirportEmployees):
            employee.Department = data['employeeDepartment']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Employee updated successfully', 'employee': employee.to_dict()})

    @app.route('/delete_employee/<int:employee_id>', methods=['DELETE'])
    @login_required
    @admin_required
    def delete_employee(employee_id):
        employee = Employees.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Employee deleted successfully'})
    
    @app.route('/get_runways', methods=['GET'])
    @login_required
    @admin_required
    def get_runways():
        runways = Runway.query.all()
        return jsonify([{
            'RunwayNumber': runway.RunwayNumber,
            'FlightName': runway.FlightName,
            'OccupiedStatus': runway.OccupiedStatus
        } for runway in runways])

    @app.route('/get_runway/<int:runway_number>', methods=['GET'])
    @login_required
    @admin_required
    def get_runway(runway_number):
        runway = Runway.query.get_or_404(runway_number)
        return jsonify({
            'RunwayNumber': runway.RunwayNumber,
            'FlightName': runway.FlightName,
            'OccupiedStatus': runway.OccupiedStatus
        })

    @app.route('/add_runway', methods=['POST'])
    @login_required
    @admin_required
    def add_runway():
        data = request.json
        new_runway = Runway(
            RunwayNumber=data['runwayNumber'],
            FlightName=data['flightName'],
            OccupiedStatus=data['occupiedStatus'] == 'true'
        )
        db.session.add(new_runway)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Runway added successfully'})

    @app.route('/update_runway/<int:runway_number>', methods=['PUT'])
    @login_required
    @admin_required
    def update_runway(runway_number):
        runway = Runway.query.get_or_404(runway_number)
        data = request.json
        runway.FlightName = data['flightName']
        runway.OccupiedStatus = data['occupiedStatus'] == 'true'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Runway updated successfully'})

    @app.route('/delete_runway/<int:runway_number>', methods=['DELETE'])
    @login_required
    @admin_required
    def delete_runway(runway_number):
        runway = Runway.query.get_or_404(runway_number)
        db.session.delete(runway)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Runway deleted successfully'})
    
    @app.route('/get_passengers', methods=['GET'])
    @login_required
    def get_passengers():
        passengers = Passengers.query.all()
        return jsonify([passenger.to_dict() for passenger in passengers])

    @app.route('/get_passenger/<int:passenger_id>', methods=['GET'])
    @login_required
    def get_passenger(passenger_id):
        passenger = Passengers.query.get_or_404(passenger_id)
        return jsonify(passenger.to_dict())


    @app.route('/add_passenger', methods=['POST'])
    @login_required
    def add_passenger():
        data = request.json
        new_passenger = Passengers(
            PassengerName=data['passengerName'],
            PassengerAge=data['passengerAge'],
            TicketId=data['ticketId'] or None,
            LuggageId=data['luggageId'] or None
        )
        db.session.add(new_passenger)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Passenger added successfully'})

    @app.route('/update_passenger/<int:passenger_id>', methods=['PUT'])
    @login_required
    def update_passenger(passenger_id):
        passenger = Passengers.query.get_or_404(passenger_id)
        data = request.json
        passenger.PassengerName = data['passengerName']
        passenger.PassengerAge = data['passengerAge']
        passenger.TicketId = data['ticketId'] or None
        passenger.LuggageId = data['luggageId'] or None
        db.session.commit()
        return jsonify({'success': True, 'message': 'Passenger updated successfully'})


    @app.route('/delete_passenger/<int:passenger_id>', methods=['DELETE'])
    @login_required
    def delete_passenger(passenger_id):
        passenger = Passengers.query.get_or_404(passenger_id)
        db.session.delete(passenger)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Passenger deleted successfully'})


    @app.route('/get_notice_board', methods=['GET'])
    @login_required
    def get_notice_board():
        current_time = datetime.now()
        
        # Get current flights (departing within the next 2 hours)
        current_flights = Flight.query.filter(
        Flight.StartingTime.between(current_time.isoformat(), (current_time + timedelta(hours=2)).isoformat())
    ).all()
        
        # Get upcoming flights (departing after 2 hours from now)
        upcoming_flights = Flight.query.filter(
            Flight.StartingTime > (current_time + timedelta(hours=2)).isoformat()
        ).limit(10).all()
        
        def flight_to_dict(flight):
            departure_time = datetime.fromisoformat(flight.StartingTime.replace('Z', '+00:00'))
            return {
                'FlightId': flight.FlightId,
                'FlightName': flight.FlightName,
                'DepartureTime': departure_time.strftime('%Y-%m-%d %H:%M'),
                'ArrivalTime': datetime.fromisoformat(flight.ReachingTime.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M'),
                'Source': flight.Source,
                'Destination': flight.Destination,
                'Status': get_flight_status(flight, current_time)
            }
        
        return jsonify({
            'current_flights': [flight_to_dict(flight) for flight in current_flights],
            'upcoming_flights': [flight_to_dict(flight) for flight in upcoming_flights]
        })

    

    def get_flight_status(flight, current_time):
        departure_time = datetime.fromisoformat(flight.StartingTime.replace('Z', '+00:00'))
        if current_time > departure_time + timedelta(minutes=15):
            return 'Departed'
        elif current_time > departure_time:
            return 'Boarding'
        elif current_time > departure_time - timedelta(minutes=30):
            return 'Check-in'
        else:
            return 'Scheduled'



        

    @app.route('/get_luggage', methods=['GET'])
    @login_required
    def get_luggage():
        luggage = Luggage.query.all()
        return jsonify([{
            'LuggageId': l.LuggageId,
            'PassengerId': l.PassengerId,
            'FlightId': l.FlightId,
            'NoOfLuggages': l.NoOfLuggages
        } for l in luggage])

    @app.route('/get_luggage/<int:luggage_id>', methods=['GET'])
    @login_required
    def get_luggage_by_id(luggage_id):
        luggage = Luggage.query.get_or_404(luggage_id)
        return jsonify({
            'LuggageId': luggage.LuggageId,
            'PassengerId': luggage.PassengerId,
            'FlightId': luggage.FlightId,
            'NoOfLuggages': luggage.NoOfLuggages
        })

    @app.route('/add_luggage', methods=['POST'])
    @login_required
    def add_luggage():
        data = request.json
        new_luggage = Luggage(
            PassengerId=data['passengerId'],
            FlightId=data['flightId'],
            NoOfLuggages=data['noOfLuggages']
        )
        db.session.add(new_luggage)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Luggage added successfully'})

    @app.route('/update_luggage/<int:luggage_id>', methods=['PUT'])
    @login_required
    def update_luggage(luggage_id):
        luggage = Luggage.query.get_or_404(luggage_id)
        data = request.json
        luggage.PassengerId = data['passengerId']
        luggage.FlightId = data['flightId']
        luggage.NoOfLuggages = data['noOfLuggages']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Luggage updated successfully'})

    @app.route('/delete_luggage/<int:luggage_id>', methods=['DELETE'])
    @login_required
    def delete_luggage(luggage_id):
        luggage = Luggage.query.get_or_404(luggage_id)
        db.session.delete(luggage)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Luggage deleted successfully'})


    @app.route('/get_available_seats/<int:flight_id>', methods=['GET'])
    @login_required
    def get_available_seats(flight_id):
        flight = Flight.query.get_or_404(flight_id)
        booked_seats = TicketCounter.query.filter_by(FlightId=flight_id).with_entities(TicketCounter.SeatNumber).all()
        booked_seats = [seat[0] for seat in booked_seats]
        all_seats = [f"{row}{col}" for row in "ABCDEF" for col in range(1, 31)]  # assuming 30 rows, 6 seats per row
        available_seats = [seat for seat in all_seats if seat not in booked_seats]
        return jsonify(available_seats)

    @app.route('/book_ticket', methods=['POST'])
    @login_required
    def book_ticket():
        data = request.json
        flight = Flight.query.get_or_404(data['flightId'])
        
        if flight.Capacity <= 0:
            return jsonify({'success': False, 'message': 'No seats available on this flight'}), 400

        existing_ticket = TicketCounter.query.filter_by(FlightId=flight.FlightId, SeatNumber=data['seatNumber']).first()
        if existing_ticket:
            return jsonify({'success': False, 'message': 'This seat is already booked'}), 400

        new_passenger = Passengers(
            PassengerName=data['passengerName'],
            PassengerAge=data['passengerAge']
        )
        db.session.add(new_passenger)
        db.session.flush()

        new_ticket = TicketCounter(
            PassengerId=new_passenger.PassengerId,
            FlightId=flight.FlightId,
            SeatNumber=data['seatNumber'],
            Price=flight.Price,
            Source=flight.Source,
            Destination=flight.Destination
        )
        db.session.add(new_ticket)
        db.session.flush()

        new_luggage = Luggage(
            PassengerId=new_passenger.PassengerId,
            FlightId=flight.FlightId,
            NoOfLuggages=data['luggageCount']
        )
        db.session.add(new_luggage)
        db.session.flush()

        # set the TicketId and LuggageId for the passenger
        new_passenger.TicketId = new_ticket.TicketId
        new_passenger.LuggageId = new_luggage.LuggageId

        flight.Capacity -= 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Ticket booked successfully',
            'ticket': {
                'ticketId': new_ticket.TicketId,
                'passengerName': new_passenger.PassengerName,
                'flightName': flight.FlightName,
                'seatNumber': new_ticket.SeatNumber,
                'departureTime': flight.StartingTime,
                'arrivalTime': flight.ReachingTime,
                'price': new_ticket.Price,
                'luggageCount': new_luggage.NoOfLuggages
            }
        })



    @app.route('/notice_board_stream')
    def notice_board_stream():
        def generate():
            with app.app_context():
                while True:
                    data = get_notice_board_data()
                    yield f"data: {json.dumps(data)}\n\n"
                    time.sleep(60)

        return Response(generate(), mimetype='text/event-stream')


    def get_notice_board_data():
        current_time = datetime.now()
        current_flights = Flight.query.filter(
            Flight.StartingTime.between(current_time.isoformat(), (current_time + timedelta(hours=2)).isoformat())
        ).all()
        upcoming_flights = Flight.query.filter(
            Flight.StartingTime > (current_time + timedelta(hours=2)).isoformat()
        ).limit(10).all()
        
        def flight_to_dict(flight):
            departure_time = datetime.fromisoformat(flight.StartingTime.replace('Z', '+00:00'))
            return {
                'FlightId': flight.FlightId,
                'FlightName': flight.FlightName,
                'DepartureTime': departure_time.strftime('%Y-%m-%d %H:%M'),
                'ArrivalTime': datetime.fromisoformat(flight.ReachingTime.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M'),
                'Source': flight.Source,
                'Destination': flight.Destination,
                'Status': get_flight_status(flight, current_time)
            }
        
        return {
            'current_flights': [flight_to_dict(flight) for flight in current_flights],
            'upcoming_flights': [flight_to_dict(flight) for flight in upcoming_flights]
        }


    # NewsLetter
    @app.route('/subscribe_newsletter', methods=['POST'])
    def subscribe_newsletter():
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        existing_subscriber = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing_subscriber:
            return jsonify({'success': False, 'message': 'You are already subscribed to our newsletter'}), 400

        new_subscriber = NewsletterSubscriber(email=email)
        db.session.add(new_subscriber)
        db.session.commit()

        # Send welcome email
        send_welcome_email(email)

        return jsonify({'success': True, 'message': 'Thank you for subscribing to our newsletter!'})

    def send_welcome_email(email):
        mail = Mail(current_app)
        msg = Message('Welcome to AirPorter Newsletter',
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[email])
        msg.body = "Thank you for subscribing to the AirPorter newsletter. Stay tuned for the latest updates!"
        mail.send(msg)