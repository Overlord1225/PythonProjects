rooms = {
    1: {'room_number': 101, 'room_type': 'Standard Room', "status": 'available', 'price': 1800},
    2: {'room_number': 102, 'room_type': 'Deluxe Room', "status": 'available', 'price': 2800},
    3: {'room_number': 103, 'room_type': 'Premium Room', "status": 'available', 'price': 3800},
}


def check_in():
    print("Available rooms:")
    for key, room in rooms.items():
        if room["status"] == 'available':
            print(f"{key}. {room['room_type']} - Php{room['price']} per night")

    room_choice = int(input("Select a room by entering the corresponding number: "))
    
    if room_choice in rooms:
        print(f"You have selected {rooms[room_choice]['room_type']} at Php{rooms[room_choice]['price']} per night.")
        name = input("Enter your name: ")
        guests = int(input("Enter the number of guests: "))
        check_in_date = input("Enter your check-in date (YYYY-MM-DD): ")
        nights = int(input("Enter the number of nights you want to stay: "))
        total_cost = rooms[room_choice]['price'] * nights
        print(f"Total cost for your stay: Php{total_cost}")
        rooms[room_choice]['status'] = 'booked'
        print(f"Thank you, {name}! Your booking for {rooms[room_choice]['room_type']} has been confirmed.")
    else:
        print("Invalid choice. Please try again.")   
def check_out():
    print("Check-out process initiated. Please provide your details.")
    name = input("Enter your name: ")
    check_out_date = input("Enter your check-out date (YYYY-MM-DD): ")
    room_choice = int(input("Enter the room number: "))
    print(f"Check-out for {name} on {check_out_date} has been completed.")
    rooms[room_choice]['status'] = 'available'

while True:
    print("\nWelcome to the Hotel Booking System!")
    print("-" * 40)
    print("Available rooms:")
    for key, room in rooms.items():
        if room["status"] == 'available':
            print(f"{key}. {room['room_type']} - Php{room['price']} per night")
    print("-" * 40)
    print("1. Check In")
    print("2. Check Out")
    print("3. Exit")
    
    choice = int(input("Please select an option: "))
    
    if choice == 1:
        check_in()
    elif choice == 2:
        check_out()
    elif choice == 3:
        print("Thank you for using the Hotel Booking System. Goodbye!")
        break
    else:
        print("Invalid option. Please try again.")