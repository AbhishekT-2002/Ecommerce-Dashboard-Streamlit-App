import pytest
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go

# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dashboard_app import save_dataframe, load_cached_data, load_data, create_time_comparison, plot_category_distribution, create_customer_insights

# Sample DataFrame for testing
sample_data = {
    'order_id': range(1, 11),
    'transaction_date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
    'customer_id': range(1, 11),
    'customer_name': [f'Customer {i}' for i in range(1, 11)],
    'email': [f'customer{i}@example.com' for i in range(1, 11)],
    'category': ['Electronics', 'Clothing', 'Home', 'Electronics', 'Clothing', 'Home', 'Electronics', 'Clothing', 'Home', 'Electronics'],
    'product_name': ['Laptop', 'T-shirt', 'Coffee Maker', 'Smartphone', 'Jeans', 'Blender', 'Headphones', 'Sneakers', 'Vacuum Cleaner', 'Tablet'],
    'quantity': [1, 2, 1, 1, 2, 1, 1, 2, 1, 1],
    'base_price': [1000, 20, 50, 800, 40, 100, 200, 60, 150, 300],
    'discount': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'total_price': [1000, 40, 50, 800, 80, 100, 200, 120, 150, 300],
    'cost': [700, 6, 27.5, 600, 16, 50, 120, 30, 90, 195],
    'profit': [300, 34, 22.5, 200, 64, 50, 80, 90, 60, 105],
    'coupon_code': ['NONE'] * 10,
    'payment_method': ['Credit Card', 'PayPal', 'Debit Card', 'Credit Card', 'PayPal', 'Debit Card', 'Credit Card', 'PayPal', 'Debit Card', 'Credit Card'],
    'shipping_method': ['Standard', 'Express', 'Next Day', 'Standard', 'Express', 'Next Day', 'Standard', 'Express', 'Next Day', 'Standard'],
    'shipping_address': [f'Address {i}' for i in range(1, 11)],
    'ip_address': [f'192.168.0.{i}' for i in range(1, 11)]
}
sample_df = pd.DataFrame(sample_data)

def test_save_dataframe(tmp_path):
    # Define a temporary file path
    temp_file = tmp_path / "test_cached_data.csv"
    
    # Save the DataFrame to the temporary file
    save_dataframe(sample_df, filename=temp_file)
    
    # Check if the file was created
    assert os.path.exists(temp_file), "The CSV file should be created"
    
    # Check if the file is not empty
    assert os.path.getsize(temp_file) > 0, "The CSV file should not be empty"
    
    # Load the file and check if it matches the original DataFrame
    loaded_df = pd.read_csv(temp_file)
    pd.testing.assert_frame_equal(sample_df, loaded_df, check_dtype=False)

def test_load_cached_data(tmp_path):
    # Define a temporary file path
    temp_file = tmp_path / "test_cached_data.csv"
    
    # Save the DataFrame to the temporary file
    save_dataframe(sample_df, filename=temp_file)
    
    # Load the cached data
    loaded_df = load_cached_data(filename=temp_file)
    
    # Check if the loaded DataFrame matches the original DataFrame
    pd.testing.assert_frame_equal(sample_df, loaded_df, check_dtype=False)

def test_load_data(tmp_path):
    # Define a temporary file path
    temp_file = tmp_path / "test_data.csv"
    
    # Save the DataFrame to the temporary file
    sample_df.to_csv(temp_file, index=False)
    
    # Load the data
    loaded_df = load_data(file_path=temp_file)
    
    # Check if the loaded DataFrame matches the original DataFrame
    pd.testing.assert_frame_equal(sample_df, loaded_df, check_dtype=False)

def test_create_time_comparison():
    comparison = create_time_comparison(sample_df, metric='total_price', freq='D')
    
    # Check if the comparison DataFrame has the expected columns
    expected_columns = ['period', 'total_price']
    assert list(comparison.columns) == expected_columns, "The comparison DataFrame should have the expected columns"
    
    # Check if the comparison DataFrame has the correct number of records
    assert len(comparison) == 10, "The comparison DataFrame should have 10 records"

def test_plot_category_distribution():
    fig = plot_category_distribution(sample_df)
    
    # Check if the figure is a Plotly figure
    assert isinstance(fig, go.Figure), "The output should be a Plotly figure"

def test_create_customer_insights():
    insights = create_customer_insights(sample_df)
    
    # Check if the insights dictionary has the expected keys
    expected_keys = ['total_customers', 'avg_order_value', 'repeat_customers', 'top_spenders']
    assert list(insights.keys()) == expected_keys, "The insights dictionary should have the expected keys"
    
    # Check if the total number of customers is correct
    assert insights['total_customers'] == 10, "The total number of customers should be 10"
    
    # Check if the average order value is correct
    expected_avg_order_value = sample_df['total_price'].mean()
    assert insights['avg_order_value'] == expected_avg_order_value, "The average order value should be correct"
    
    # Check if the number of repeat customers is correct
    assert insights['repeat_customers'] == 0, "The number of repeat customers should be 0"
    
    # Check if the top spenders DataFrame is correct
    top_spenders = sample_df.nlargest(10, 'total_price')
    pd.testing.assert_frame_equal(insights['top_spenders'], top_spenders, check_dtype=False)

if __name__ == "__main__":
    pytest.main()