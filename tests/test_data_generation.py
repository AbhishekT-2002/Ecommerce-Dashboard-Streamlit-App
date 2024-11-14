import pytest
import pandas as pd
import os
import sys
from pathlib import Path

# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from data_generation import generate_synthetic_data, save_data

def test_generate_synthetic_data():
    # Test if the function returns a DataFrame
    df = generate_synthetic_data(num_records=100)
    assert isinstance(df, pd.DataFrame), "The output should be a pandas DataFrame"
    
    # Test if the DataFrame has the correct number of records
    assert len(df) == 100, "The DataFrame should have 100 records"
    
    # Test if the DataFrame has the expected columns
    expected_columns = [
        'order_id', 'transaction_date', 'customer_id', 'customer_name', 'email',
        'category', 'product_name', 'quantity', 'base_price', 'discount',
        'total_price', 'cost', 'profit', 'coupon_code', 'payment_method',
        'shipping_method', 'shipping_address', 'ip_address'
    ]
    assert list(df.columns) == expected_columns, "The DataFrame should have the expected columns"

def test_save_data(tmp_path):
    # Generate a small sample DataFrame
    df = generate_synthetic_data(num_records=10)
    
    # Convert transaction_date to string format before saving
    df['transaction_date'] = df['transaction_date'].astype(str)
    
    # Define a temporary file path
    temp_file = tmp_path / "test_ecommerce_data.csv"
    
    # Save the DataFrame to the temporary file
    save_data(df, filename=temp_file)
    
    # Check if the file was created
    assert os.path.exists(temp_file), "The CSV file should be created"
    
    # Check if the file is not empty
    assert os.path.getsize(temp_file) > 0, "The CSV file should not be empty"
    
    # Load the file and convert transaction_date back to datetime format
    loaded_df = pd.read_csv(temp_file)
    loaded_df['transaction_date'] = pd.to_datetime(loaded_df['transaction_date'])
    
    # Convert the original DataFrame's transaction_date back to datetime format for comparison
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Check if the loaded DataFrame matches the original DataFrame
    pd.testing.assert_frame_equal(df, loaded_df, check_dtype=False)

if __name__ == "__main__":
    pytest.main()