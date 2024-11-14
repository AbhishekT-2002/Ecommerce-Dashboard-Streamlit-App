import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

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
num_records = 1000
def generate_synthetic_data(num_records=num_records):
    """Generate synthetic e-commerce transaction data."""
    data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(num_records):
        # Select random product and category
        category = random.choice(list(PRODUCTS.keys()))
        product = random.choice(list(PRODUCTS[category].keys()))
        product_info = PRODUCTS[category][product]
        
        # Generate base price and calculate costs
        base_price = round(random.uniform(product_info['min_price'], product_info['max_price']), 2)
        cost = round(base_price * product_info['cost_multiplier'], 2)
        
        # Generate random coupon and discount
        coupon = random.choice(COUPON_CODES)
        discount = round(base_price * (0.25 if coupon != 'NONE' else 0), 2)
        
        # Calculate final price
        total_price = round(base_price - discount, 2)
        
        # Generate transaction date
        days_offset = random.randint(0, 364)
        transaction_date = start_date + timedelta(days=days_offset)
        
        # Create suspicious patterns for some transactions (for fraud detection)
        is_suspicious = random.random() < 0.05  # 5% of transactions are suspicious
        if is_suspicious:
            # Create patterns like: multiple orders in short time, unusual payment amounts
            transaction_date = transaction_date.replace(hour=random.randint(1, 4))  # Late night orders
            if random.random() < 0.5:
                total_price = round(total_price * random.uniform(5, 10), 2)  # Unusually high amount
        
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
    return filename

def load_data(file_path):
    """Load data from CSV file."""
    df = pd.read_csv(file_path)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    return df

def create_streamlit_app():
    """Create Streamlit dashboard application."""
    st.title('E-commerce Analytics Dashboard')
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        # Sidebar filters
        st.sidebar.header('Filters')
        
        # Date range filter
        date_range = st.sidebar.date_input(
            "Select Date Range",
            [df['transaction_date'].min(), df['transaction_date'].max()],
            min_value=df['transaction_date'].min().date(),
            max_value=df['transaction_date'].max().date()
        )
        
        # Category filter
        categories = ['All'] + list(df['category'].unique())
        selected_category = st.sidebar.selectbox('Select Category', categories)
        
        # Apply filters
        mask = (df['transaction_date'].dt.date >= date_range[0]) & (df['transaction_date'].dt.date <= date_range[1])
        if selected_category != 'All':
            mask = mask & (df['category'] == selected_category)
        filtered_df = df[mask]
        
        # Daily Profit/Loss Analysis
        st.header('Daily Profit/Loss Analysis')
        daily_profits = filtered_df.groupby(filtered_df['transaction_date'].dt.date).agg({
            'profit': 'sum',
            'total_price': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        fig_profits = px.line(daily_profits, x='transaction_date', y=['profit', 'total_price', 'cost'],
                            title='Daily Profit/Loss Trends')
        st.plotly_chart(fig_profits)
        
        # Popular Products Analysis
        st.header('Popular Products Analysis')
        product_analysis = filtered_df.groupby('product_name').agg({
            'quantity': 'sum',
            'profit': 'sum',
            'total_price': 'sum'
        }).reset_index()
        
        fig_products = px.bar(product_analysis.sort_values('quantity', ascending=False).head(10),
                            x='product_name', y='quantity',
                            title='Top 10 Products by Quantity Sold')
        st.plotly_chart(fig_products)
        
        # Fraud Detection Dashboard
        st.header('Potential Fraud Detection')
        
        # Identify suspicious patterns
        suspicious_orders = filtered_df[
            (filtered_df['total_price'] > filtered_df['total_price'].quantile(0.95)) |  # Unusually high amounts
            (filtered_df['transaction_date'].dt.hour.between(1, 4)) |  # Late night orders
            (filtered_df['quantity'] > filtered_df['quantity'].quantile(0.95))  # Unusually high quantities
        ]
        
        if not suspicious_orders.empty:
            st.warning(f'Found {len(suspicious_orders)} potentially suspicious orders')
            st.dataframe(suspicious_orders[['order_id', 'transaction_date', 'total_price', 'quantity', 'ip_address']])
            
            # Visualize suspicious transactions
            fig_suspicious = px.scatter(suspicious_orders,
                                     x='transaction_date',
                                     y='total_price',
                                     color='category',
                                     title='Suspicious Transactions Distribution')
            st.plotly_chart(fig_suspicious)
        
        # Additional metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue", f"${filtered_df['total_price'].sum():,.2f}")
        with col2:
            st.metric("Total Profit", f"${filtered_df['profit'].sum():,.2f}")
        with col3:
            st.metric("Total Orders", len(filtered_df))

if __name__ == "__main__":
    # Generate and save synthetic data
    df = generate_synthetic_data(100000)
    save_data(df)
    
    # Run Streamlit app
    create_streamlit_app()