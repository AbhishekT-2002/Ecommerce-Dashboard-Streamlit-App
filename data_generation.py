import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
fake = Faker()

# Constants for data generation
PRODUCTS = {
    'Electronics': {
        'Laptop': {'min_price': 800, 'max_price': 2000, 'cost_multiplier': 0.7},
        'Smartphone': {'min_price': 500, 'max_price': 1200, 'cost_multiplier': 0.75},
        'Headphones': {'min_price': 50, 'max_price': 300, 'cost_multiplier': 0.6},
        'Tablet': {'min_price': 200, 'max_price': 800, 'cost_multiplier': 0.65}
    },
    'Clothing': {
        'T-shirt': {'min_price': 15, 'max_price': 40, 'cost_multiplier': 0.3},
        'Jeans': {'min_price': 30, 'max_price': 100, 'cost_multiplier': 0.4},
        'Sneakers': {'min_price': 50, 'max_price': 150, 'cost_multiplier': 0.5},
        'Jacket': {'min_price': 60, 'max_price': 200, 'cost_multiplier': 0.45}
    },
    'Home': {
        'Coffee Maker': {'min_price': 30, 'max_price': 200, 'cost_multiplier': 0.55},
        'Blender': {'min_price': 40, 'max_price': 150, 'cost_multiplier': 0.5},
        'Vacuum Cleaner': {'min_price': 100, 'max_price': 400, 'cost_multiplier': 0.6},
        'Microwave': {'min_price': 80, 'max_price': 300, 'cost_multiplier': 0.65}
    }
}

COUPON_CODES = ['SAVE10', 'SPRING20', 'SUMMER15', 'FLASH25', 'NONE']
PAYMENT_METHODS = ['Credit Card', 'PayPal', 'Debit Card', 'Bank Transfer']
SHIPPING_METHODS = ['Standard', 'Express', 'Next Day', 'International']
NUM_RECORDS = 100000

def generate_synthetic_data(num_records=NUM_RECORDS):
    """Generate synthetic e-commerce transaction data."""
    data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(num_records):
        category = random.choice(list(PRODUCTS.keys()))
        product = random.choice(list(PRODUCTS[category].keys()))
        product_info = PRODUCTS[category][product]
        
        base_price = round(random.uniform(product_info['min_price'], product_info['max_price']), 2)
        cost = round(base_price * product_info['cost_multiplier'], 2)
        coupon = random.choice(COUPON_CODES)
        discount = round(base_price * (0.25 if coupon != 'NONE' else 0), 2)
        total_price = round(base_price - discount, 2)
        
        days_offset = random.randint(0, 364)
        transaction_date = start_date + timedelta(days=days_offset)
        
        is_suspicious = random.random() < 0.05
        if is_suspicious:
            transaction_date = transaction_date.replace(hour=random.randint(1, 4))
            if random.random() < 0.5:
                total_price = round(total_price * random.uniform(5, 10), 2)
        
        data.append({
            'order_id': f'ORD-{i+1:06d}',
            'transaction_date': transaction_date,
            'customer_id': f'CUST-{random.randint(1, 10000):05d}',
            'customer_name': fake.name(),
            'email': fake.email(),
            'category': category,
            'product_name': product,
            'quantity': random.randint(1, 5),
            'base_price': base_price,
            'discount': discount,
            'total_price': total_price,
            'cost': cost,
            'profit': round(total_price - cost, 2),
            'coupon_code': coupon,
            'payment_method': random.choice(PAYMENT_METHODS),
            'shipping_method': random.choice(SHIPPING_METHODS),
            'shipping_address': fake.address().replace('\n', ', '),
            'ip_address': fake.ipv4()
        })
    
    return pd.DataFrame(data)

def save_data(df, filename='ecommerce_data.csv'):
    """Save DataFrame to CSV file."""
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # Generate and save synthetic data
    df = generate_synthetic_data()
    save_data(df)
