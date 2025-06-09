import csv
import random
from datetime import datetime, timedelta

# Vehicle data generation
vehicles = [
    ["vehicle_id", "make", "model", "year", "vehicle_type", "fuel_type", "color", "rental_price_per_day", "status"]
]

makes = ["Renault", "Dacia", "Peugeot", "Citroen", "Ford"]
models = {
    "Renault": ["Clio", "Megane", "Captur"],
    "Dacia": ["Logan", "Sandero", "Duster"],
    "Peugeot": ["208", "308", "3008"],
    "Citroen": ["C3", "C4", "C5"],
    "Ford": ["Focus", "Fiesta", "Kuga"]
}
vehicle_types = ["Sedan", "SUV", "Hatchback", "Truck"]
fuel_types = ["Petrol", "Diesel", "Hybrid", "Electric"]
colors = ["Red", "White", "Black", "Blue", "Silver", "Grey"]
statuses = ["Available", "Under Maintenance", "Rented"]

for i in range(1, 22):  # 21 vehicles
    make = random.choice(makes)
    model = random.choice(models[make])
    year = random.randint(2015, 2023)
    v_type = random.choice(vehicle_types)
    fuel = random.choice(fuel_types)
    color = random.choice(colors)
    price = round(random.uniform(150, 500), 2)  # MAD price range
    status = random.choice(statuses)
    vehicles.append([
        f"VEH{str(i).zfill(3)}", make, model, year, v_type, fuel, color, price, status
    ])

# Write vehicles to CSV
with open("vehicles.csv", "w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(vehicles)

# Rentals data generation
rentals = [
    ["rental_id", "vehicle_id", "start_date", "end_date", "total_price", "status", "customer_rating", "client_name", "return_delay_days", "payment_method"]
]

statuses_rental = ["Completed", "Cancelled", "Ongoing"]
payment_methods = ["cash", "credit card", "debit card", "online payment"]
client_names = ["Aya", "Salma", "Koki", "Chadi", "Imad", "Sana", "Amine", "Laila", "Youssef", "Fatima"]

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

start_range = datetime.strptime("2023-01-01", "%Y-%m-%d")
end_range = datetime.strptime("2023-12-31", "%Y-%m-%d")

for i in range(1, 251):  # 250 rentals
    vehicle_id = f"VEH{random.randint(1,21):03d}"
    start_date = random_date(start_range, end_range)
    rental_days = random.randint(1, 14)
    end_date = start_date + timedelta(days=rental_days)
    price_per_day = next(v[7] for v in vehicles if v[0] == vehicle_id)
    total_price = round(price_per_day * rental_days, 2)
    status = random.choice(statuses_rental)
    rating = round(random.uniform(1, 5), 1) if status == "Completed" else ""
    client = random.choice(client_names)
    delay = random.randint(0, 10) if status == "Completed" else ""
    payment = random.choice(payment_methods) if status == "Completed" else ""
    rentals.append([
        f"RENT{str(i).zfill(4)}",
        vehicle_id,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        total_price,
        status,
        rating,
        client,
        delay,
        payment
    ])

# Write rentals to CSV
with open("rentals.csv", "w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(rentals)

print("CSV files 'vehicles.csv' and 'rentals.csv' generated successfully.")
