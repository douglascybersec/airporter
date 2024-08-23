document.addEventListener('DOMContentLoaded', function() {
    // Register form validation
    const registerForm = document.querySelector('#register-form');
    const loginForm = document.querySelector('#login-form');


    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            const password = document.querySelector('#password').value;
            const confirmPassword = document.querySelector('#confirm-password').value;

            if (password !== confirmPassword) {
                event.preventDefault();
                alert('Passwords do not match!');
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', function(event){
            // Client-side validation for login can be added here
        });
    }

    // Airport management delete confirmation
    const deleteForms = document.querySelectorAll('form[action*="delete_airport"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const confirmDelete = confirm('Are you sure you want to delete this airport?');
            if (!confirmDelete) {
                e.preventDefault();
            }
        });
    });

    // Flight Details functionality
    const flightForm = document.getElementById('flightForm');
    const flightTable = document.getElementById('flightTable').getElementsByTagName('tbody')[0];

    if (flightForm) {
        fetchFlights();

        flightForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(flightForm);
            const flightData = Object.fromEntries(formData.entries());
            const flightId = flightData.FlightId;

            const url = flightId ? `/update_flight/${flightId}` : '/add_flight';
            const method = flightId ? 'PUT' : 'POST';

            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(flightData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    flightForm.reset();
                    fetchFlights();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }

    function fetchFlights() {
        fetch('/get_flights')
            .then(response => response.json())
            .then(flights => {
                flightTable.innerHTML = '';
                flights.forEach(flight => addFlightToTable(flight));
            })
            .catch(error => console.error('Error:', error));
    }

    function addFlightToTable(flight) {
        const row = flightTable.insertRow();
        row.innerHTML = `
            <td>${flight.FlightName}</td>
            <td>${flight.Capacity}</td>
            <td>${flight.StartingTime}</td>
            <td>${flight.ReachingTime}</td>
            <td>${flight.Source}</td>
            <td>${flight.Destination}</td>
            <td>${flight.Price}</td>
            <td>
                <button onclick="editFlight(${flight.FlightId})">Edit</button>
                <button onclick="deleteFlight(${flight.FlightId})">Delete</button>
            </td>
        `;
    }

    window.editFlight = function(flightId) {
        fetch(`/get_flights`)
            .then(response => response.json())
            .then(flights => {
                const flight = flights.find(f => f.FlightId === flightId);
                if (flight) {
                    document.getElementById('FlightId').value = flight.FlightId;
                    document.getElementById('FlightName').value = flight.FlightName;
                    document.getElementById('Capacity').value = flight.Capacity;
                    document.getElementById('StartingTime').value = flight.StartingTime.slice(0, 16);
                    document.getElementById('ReachingTime').value = flight.ReachingTime.slice(0, 16);
                    document.getElementById('Source').value = flight.Source;
                    document.getElementById('Destination').value = flight.Destination;
                    document.getElementById('Price').value = flight.Price;
                }
            })
            .catch(error => console.error('Error:', error));
    }

    window.deleteFlight = function(flightId) {
        if (confirm('Are you sure you want to delete this flight?')) {
            fetch(`/delete_flight/${flightId}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        fetchFlights();
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }

    
});



// Employee Management functionality
document.addEventListener('DOMContentLoaded', function() {
    const addEmployeeBtn = document.getElementById('addEmployeeBtn');
    const addEmployeeModal = document.getElementById('addEmployeeModal');
    const closeBtn = addEmployeeModal.querySelector('.close');
    const addEmployeeForm = document.getElementById('addEmployeeForm');
    const employeeType = document.getElementById('employeeType');
    const departmentGroup = document.getElementById('departmentGroup');

    // Open modal
    addEmployeeBtn.onclick = function() {
        addEmployeeModal.style.display = 'block';
    }

    // Close modal
    closeBtn.onclick = function() {
        addEmployeeModal.style.display = 'none';
    }

    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target == addEmployeeModal) {
            addEmployeeModal.style.display = 'none';
        }
    }

    // Show/hide department field based on employee type
    employeeType.onchange = function() {
        if (this.value === 'airport') {
            departmentGroup.style.display = 'block';
        } else {
            departmentGroup.style.display = 'none';
        }
    }

    // Handle form submission
    addEmployeeForm.onsubmit = function(e) {
        e.preventDefault();
        const formData = new FormData(addEmployeeForm);
        const employeeData = Object.fromEntries(formData.entries());
        
        fetch('/add_employee', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(employeeData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                addEmployeeModal.style.display = 'none';
                addEmployeeForm.reset();
                fetchEmployees();
            } else {
                alert('Error adding employee');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    // Fetch and display employees
    function fetchEmployees() {
        fetch('/get_employees')
        .then(response => response.json())
        .then(data => {
            populateTable('allEmployeesTable', data.all_employees);
            populateTable('airportEmployeesTable', data.airport_employees, true);
            populateTable('airplaneEmployeesTable', data.airplane_employees);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function populateTable(tableId, data, includeAirportFields = false) {
        const table = document.getElementById(tableId);
        const tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = '';
        data.forEach(employee => {
            const row = tbody.insertRow();
            row.insertCell().textContent = employee.EmployeeId;
            row.insertCell().textContent = employee.EmployeeName;
            row.insertCell().textContent = employee.EmployeeSalary;
            row.insertCell().textContent = employee.Designation;
            if (includeAirportFields) {
                row.insertCell().textContent = employee.Department;
            }
            const actionsCell = row.insertCell();
            actionsCell.innerHTML = `
                <button onclick="editEmployee(${employee.EmployeeId})">Edit</button>
                <button onclick="deleteEmployee(${employee.EmployeeId})">Delete</button>
            `;
        });
    }

    // Initial fetch
    fetchEmployees();
});

function editEmployee(id) {
    // Implement edit functionality
    console.log(`Editing employee with id ${id}`);
    // You can implement a modal or form to edit employee details
}

function deleteEmployee(id) {
    if (confirm('Are you sure you want to delete this employee?')) {
        fetch(`/delete_employee/${id}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                fetchEmployees();
            } else {
                alert('Error deleting employee');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}

function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}


// Runway functionality

document.addEventListener('DOMContentLoaded', function() {
    const runwayForm = document.getElementById('runwayForm');
    const runwayTable = document.getElementById('runwayTable').getElementsByTagName('tbody')[0];

    // Fetch and display runways
    function fetchRunways() {
        fetch('/get_runways')
            .then(response => response.json())
            .then(data => {
                runwayTable.innerHTML = '';
                data.forEach(runway => {
                    addRunwayToTable(runway);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    // Add runway to table
    function addRunwayToTable(runway) {
        const row = runwayTable.insertRow();
        row.innerHTML = `
            <td>${runway.RunwayNumber}</td>
            <td>${runway.FlightName || ''}</td>
            <td>${runway.OccupiedStatus ? 'Occupied' : 'Not Occupied'}</td>
            <td>
                <button onclick="editRunway(${runway.RunwayNumber})">Edit</button>
                <button onclick="deleteRunway(${runway.RunwayNumber})">Delete</button>
            </td>
        `;
    }

    // Handle form submission
    runwayForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(runwayForm);
        const runwayData = Object.fromEntries(formData.entries());
        
        const url = runwayData.runwayId ? `/update_runway/${runwayData.runwayId}` : '/add_runway';
        const method = runwayData.runwayId ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(runwayData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                runwayForm.reset();
                fetchRunways();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    // Edit runway
    window.editRunway = function(runwayNumber) {
        fetch(`/get_runway/${runwayNumber}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('runwayId').value = data.RunwayNumber;
                document.getElementById('runwayNumber').value = data.RunwayNumber;
                document.getElementById('flightName').value = data.FlightName || '';
                document.getElementById('occupiedStatus').value = data.OccupiedStatus.toString();
            })
            .catch(error => console.error('Error:', error));
    }

    // Delete runway
    window.deleteRunway = function(runwayNumber) {
        if (confirm('Are you sure you want to delete this runway?')) {
            fetch(`/delete_runway/${runwayNumber}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        fetchRunways();
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }

    // Initial fetch
    fetchRunways();
});


// Passenger Details Functionality
document.addEventListener('DOMContentLoaded', function() {
    const passengerForm = document.getElementById('passengerForm');
    const passengerTable = document.getElementById('passengerTable').getElementsByTagName('tbody')[0];

    // Fetch and display passengers
    function fetchPassengers() {
        fetch('/get_passengers')
            .then(response => response.json())
            .then(data => {
                passengerTable.innerHTML = '';
                data.forEach(passenger => {
                    addPassengerToTable(passenger);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    // Add passenger to table
    function addPassengerToTable(passenger) {
        const row = passengerTable.insertRow();
        row.innerHTML = `
            <td>${passenger.PassengerId}</td>
            <td>${passenger.PassengerName}</td>
            <td>${passenger.PassengerAge}</td>
            <td>${formatTicketDetails(passenger.TicketDetails)}</td>
            <td>${formatLuggageDetails(passenger.LuggageDetails)}</td>
            <td>
                <button onclick="editPassenger(${passenger.PassengerId})">Edit</button>
                <button onclick="deletePassenger(${passenger.PassengerId})">Delete</button>
            </td>
        `;
    }
    
    function formatTicketDetails(ticket) {
        if (!ticket) return 'No ticket';
        return `Flight: ${ticket.FlightId}, Seat: ${ticket.SeatNumber}`;
    }
    
    function formatLuggageDetails(luggage) {
        if (!luggage) return 'No luggage';
        return `Luggage Count: ${luggage.NoOfLuggages}`;
    }
    
    
    window.editPassenger = function(passengerId) {
        fetch(`/get_passenger/${passengerId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('passengerId').value = data.PassengerId;
                document.getElementById('passengerName').value = data.PassengerName;
                document.getElementById('passengerAge').value = data.PassengerAge;
                document.getElementById('ticketId').value = data.TicketId || '';
                document.getElementById('luggageId').value = data.LuggageId || '';
            })
            .catch(error => console.error('Error:', error));
    }

    // Delete passenger
    window.deletePassenger = function(passengerId) {
        if (confirm('Are you sure you want to delete this passenger?')) {
            fetch(`/delete_passenger/${passengerId}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        fetchPassengers();
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }

    // Initial fetch
    fetchPassengers();
});


// Notice Board functionality
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('noticeBoard')) {
        // Initial load of notice board data
        fetchNoticeBoard();

        // Set up server-sent events
        const evtSource = new EventSource("/notice_board_stream");
        evtSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateNoticeBoardTables(data);
        };
    }
});

function fetchNoticeBoard() {
    fetch('/get_notice_board')
        .then(response => response.json())
        .then(data => updateNoticeBoardTables(data))
        .catch(error => console.error('Error:', error));
}

function updateNoticeBoardTables(data) {
    updateTable('currentFlightsTable', data.current_flights);
    updateTable('upcomingFlightsTable', data.upcoming_flights);
}

function updateTable(tableId, flights) {
    const tbody = document.getElementById(tableId).getElementsByTagName('tbody')[0];
    tbody.innerHTML = '';
    flights.forEach(flight => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${flight.FlightName}</td>
            <td>${flight.DepartureTime}</td>
            <td>${flight.ArrivalTime}</td>
            <td>${flight.Source}</td>
            <td>${flight.Destination}</td>
            <td class="status-${flight.Status.toLowerCase()}">${flight.Status}</td>
        `;
    });
}


// Refresh notice board every 5 minutes
setInterval(fetchNoticeBoard, 300000);



// Luggage Details functionality
document.addEventListener('DOMContentLoaded', function() {
    const luggageForm = document.getElementById('luggageForm');
    const luggageTable = document.getElementById('luggageTable').getElementsByTagName('tbody')[0];

    if (luggageForm) {
        fetchLuggage();

        luggageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(luggageForm);
            const luggageData = Object.fromEntries(formData.entries());
            
            const url = luggageData.luggageId ? `/update_luggage/${luggageData.luggageId}` : '/add_luggage';
            const method = luggageData.luggageId ? 'PUT' : 'POST';

            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(luggageData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    luggageForm.reset();
                    document.getElementById('luggageId').value = '';
                    fetchLuggage();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }

    function fetchLuggage() {
        fetch('/get_luggage')
            .then(response => response.json())
            .then(data => {
                luggageTable.innerHTML = '';
                data.forEach(luggage => {
                    addLuggageToTable(luggage);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    function addLuggageToTable(luggage) {
        const row = luggageTable.insertRow();
        row.innerHTML = `
            <td>${luggage.LuggageId}</td>
            <td>${luggage.PassengerId}</td>
            <td>${luggage.FlightId}</td>
            <td>${luggage.NoOfLuggages}</td>
            <td>
                <button onclick="editLuggage(${luggage.LuggageId})">Edit</button>
                <button onclick="deleteLuggage(${luggage.LuggageId})">Delete</button>
            </td>
        `;
    }

    window.editLuggage = function(luggageId) {
        fetch(`/get_luggage/${luggageId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('luggageId').value = data.LuggageId;
                document.getElementById('passengerId').value = data.PassengerId;
                document.getElementById('flightId').value = data.FlightId;
                document.getElementById('noOfLuggages').value = data.NoOfLuggages;
            })
            .catch(error => console.error('Error:', error));
    }

    window.deleteLuggage = function(luggageId) {
        if (confirm('Are you sure you want to delete this luggage record?')) {
            fetch(`/delete_luggage/${luggageId}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        fetchLuggage();
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }
});


// ticket counter functionality
document.addEventListener('DOMContentLoaded', function() {
    const ticketForm = document.getElementById('ticketForm');
    const flightSelect = document.getElementById('flightSelect');
    const seatNumber = document.getElementById('seatNumber');
    let selectedFlightCapacity = 0;

    // Fetch available flights
    fetch('/get_flights')
        .then(response => response.json())
        .then(flights => {
            flights.forEach(flight => {
                const option = document.createElement('option');
                option.value = flight.FlightId;
                option.textContent = `${flight.FlightName} - ${flight.Source} to ${flight.Destination} (Capacity: ${flight.Capacity})`;
                option.dataset.capacity = flight.Capacity;
                flightSelect.appendChild(option);
            });
        });

    // Update selected flight capacity when a flight is selected
    flightSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        selectedFlightCapacity = parseInt(selectedOption.dataset.capacity);
    });

    // Handle form submission
    ticketForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = {
            flightId: flightSelect.value,
            passengerName: document.getElementById('passengerName').value,
            passengerAge: document.getElementById('passengerAge').value,
            seatNumber: seatNumber.value,
            luggageCount: document.getElementById('luggageCount').value
        };

        // Validate seat number
        if (!isValidSeatNumber(formData.seatNumber, selectedFlightCapacity)) {
            alert('Invalid seat number. Please enter a valid seat (e.g., A1, B2) within the flight capacity.');
            return;
        }

        fetch('/book_ticket', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayTicketDetails(data.ticket);
                ticketForm.reset();
            } else {
                alert('Error booking ticket: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    function isValidSeatNumber(seatNumber, capacity) {
        const match = seatNumber.match(/^([A-F])(\d+)$/);
        if (!match) return false;

        const row = match[1].charCodeAt(0) - 65; // A=0, B=1, etc.
        const col = parseInt(match[2]) - 1;
        const seatIndex = row * 30 + col; // Assuming 30 seats per row

        return seatIndex >= 0 && seatIndex < capacity;
    }

    function displayTicketDetails(ticket) {
        document.getElementById('detailTicketId').textContent = ticket.ticketId;
        document.getElementById('detailPassengerName').textContent = ticket.passengerName;
        document.getElementById('detailFlightName').textContent = ticket.flightName;
        document.getElementById('detailSeat').textContent = ticket.seatNumber;
        document.getElementById('detailDeparture').textContent = ticket.departureTime;
        document.getElementById('detailArrival').textContent = ticket.arrivalTime;
        document.getElementById('detailPrice').textContent = ticket.price;
        document.getElementById('detailLuggage').textContent = ticket.luggageCount;
        document.getElementById('ticketDetails').style.display = 'block';
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Newsletter subscription
    const newsletterForm = document.getElementById('newsletter-form');
    const newsletterMessage = document.getElementById('newsletter-message');

    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('newsletter-email').value;

            fetch('/subscribe_newsletter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    newsletterMessage.textContent = data.message;
                    newsletterMessage.style.color = 'green';
                    newsletterForm.reset();
                } else {
                    newsletterMessage.textContent = data.message;
                    newsletterMessage.style.color = 'red';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                newsletterMessage.textContent = 'An error occurred. Please try again later.';
                newsletterMessage.style.color = 'red';
            });
        });
    }
});


// latest flight details
document.addEventListener('DOMContentLoaded', function() {
    // Fetch and display latest flight information
    fetch('/get_notice_board')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const flightInfoTable = document.getElementById('flightInfoTable');
            if (data.current_flights && data.current_flights.length > 0) {
                let tableHTML = '<table><thead><tr><th>Flight</th><th>Departure</th><th>Arrival</th><th>Status</th></tr></thead><tbody>';
                
                data.current_flights.forEach(flight => {
                    tableHTML += `<tr>
                        <td>${flight.FlightName}</td>
                        <td>${flight.DepartureTime}</td>
                        <td>${flight.ArrivalTime}</td>
                        <td class="status-${flight.Status.toLowerCase()}">${flight.Status}</td>
                    </tr>`;
                });
                
                tableHTML += '</tbody></table>';
                flightInfoTable.innerHTML = tableHTML;
            } else {
                flightInfoTable.innerHTML = '<p>No current flights available.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching flight information:', error);
            document.getElementById('flightInfoTable').innerHTML = '<p>Error loading flight information. Please try again later.</p>';
        });

    // Handle newsletter form submission
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            // Here you would typically send this email to your server
            console.log('Newsletter signup:', email);
            alert('Thank you for subscribing to our newsletter!');
            this.reset();
        });
    }
});


// hover effect
document.addEventListener('DOMContentLoaded', function() {
    const logo = document.querySelector('.logo a');
    const navItems = document.querySelectorAll('.nav-item');
    
    function handleHover(event) {
        event.target.style.color = '#007bff';
    }

    function handleMouseOut(event) {
        event.target.style.color = 'white';
    }

    logo.addEventListener('mouseover', handleHover);
    logo.addEventListener('mouseout', handleMouseOut);

    navItems.forEach(item => {
        item.addEventListener('mouseover', handleHover);
        item.addEventListener('mouseout', handleMouseOut);
    });
});


