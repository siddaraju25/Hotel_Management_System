// API_BASE_URL is now relative, as the frontend and backend are served from the same Flask app
const API_BASE_URL = '/api'; 

async function bookRoom() {
    const name = document.getElementById("guestName").value.trim();
    const type = document.getElementById("roomType").value;

    if (name === "") {
        alert("Please enter guest name.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/bookings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ guestName: name, roomType: type }),
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            displayBookings();
            document.getElementById("guestName").value = "";
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        console.error('Error booking room:', error);
        alert('Could not connect to the server or a network error occurred. Please ensure the backend is running and accessible.');
    }
}

async function checkAvailability() {
    const type = document.getElementById("checkRoomType").value;

    try {
        const response = await fetch(`${API_BASE_URL}/availability/${type}`);
        const data = await response.json();

        if (response.ok) {
            alert(`${data.available} ${data.roomType} room(s) available (out of ${data.total}).`);
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        console.error('Error checking availability:', error);
        alert('Could not connect to the server or a network error occurred.');
    }
}

async function displayBookings() {
    const list = document.getElementById("bookingList");
    list.innerHTML = "";

    try {
        const response = await fetch(`${API_BASE_URL}/bookings`);
        const bookings = await response.json();

        if (response.ok) {
            if (bookings.length === 0) {
                list.innerHTML = '<p>No bookings yet.</p>';
                return;
            }
            bookings.forEach((booking, index) => {
                const div = document.createElement("div");
                div.className = "booking";
                const bookingDate = new Date(booking.booking_date).toLocaleString();
                div.innerText = `${index + 1}. ${booking.guest_name} - ${booking.room_type} (Booked on: ${bookingDate})`;
                list.appendChild(div);
            });
        } else {
            list.innerHTML = `<p>Error fetching bookings: ${bookings.message}</p>`;
        }
    } catch (error) {
        console.error('Error fetching bookings:', error);
        list.innerHTML = '<p>Could not load bookings. Server might be down or a network error occurred.</p>';
    }
}

document.addEventListener('DOMContentLoaded', displayBookings);
