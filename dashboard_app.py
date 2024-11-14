import streamlit as st
import pandas as pd
import plotly.express as px

def load_data(file_path):
    """Load data from CSV file."""
    df = pd.read_csv(file_path)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    return df

def create_dashboard(df):
    """Create Streamlit dashboard application."""
    st.title('E-commerce Analytics Dashboard')
    
    # Sidebar filters
    st.sidebar.header('Filters')
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [df['transaction_date'].min(), df['transaction_date'].max()],
        min_value=df['transaction_date'].min().date(),
        max_value=df['transaction_date'].max().date()
    )
    
    categories = ['All'] + list(df['category'].unique())
    selected_category = st.sidebar.selectbox('Select Category', categories)
    
    mask = (df['transaction_date'].dt.date >= date_range[0]) & (df['transaction_date'].dt.date <= date_range[1])
    if selected_category != 'All':
        mask = mask & (df['category'] == selected_category)
    filtered_df = df[mask]
    
    st.header('Daily Profit/Loss Analysis')
    daily_profits = filtered_df.groupby(filtered_df['transaction_date'].dt.date).agg({
        'profit': 'sum',
        'total_price': 'sum',
        'cost': 'sum'
    }).reset_index()
    
    fig_profits = px.line(daily_profits, x='transaction_date', y=['profit', 'total_price', 'cost'],
                          title='Daily Profit/Loss Trends')
    st.plotly_chart(fig_profits)
    
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
    
    st.header('Potential Fraud Detection')
    suspicious_orders = filtered_df[
        (filtered_df['total_price'] > filtered_df['total_price'].quantile(0.95)) |
        (filtered_df['transaction_date'].dt.hour.between(1, 4)) |
        (filtered_df['quantity'] > filtered_df['quantity'].quantile(0.95))
    ]
    
    if not suspicious_orders.empty:
        st.warning(f'Found {len(suspicious_orders)} potentially suspicious orders')
        st.dataframe(suspicious_orders[['order_id', 'transaction_date', 'total_price', 'quantity', 'ip_address']])
        
        fig_suspicious = px.scatter(suspicious_orders,
                                    x='transaction_date',
                                    y='total_price',
                                    color='category',
                                    title='Suspicious Transactions Distribution')
        st.plotly_chart(fig_suspicious)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"${filtered_df['total_price'].sum():,.2f}")
    with col2:
        st.metric("Total Profit", f"${filtered_df['profit'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", len(filtered_df))

# Main Streamlit app
st.title("E-commerce Data Dashboard")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df = load_data(uploaded_file)
    create_dashboard(df)
