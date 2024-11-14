import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os
import json
import base64

# Set page configuration
st.set_page_config(page_title="E-commerce Analytics", page_icon="🛍️", layout="wide")

# Custom CSS 
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
        background-color: #1D1C63;
    }
    .stMetric {
        background-color: rgba(20, 87, 221, 0.9);
        padding: 10px;
        border-radius: 5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    /* Customize other elements for dark background */
    .stMarkdown, .stTitle, h1, h2, h3 {
        color: white !important;
    }
    .stTab {
        color: white !important;
    }
    div[data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
    }
    div[data-baseweb="tab"] {
        color: white !important;
    }
    div[data-testid="stMarkdownContainer"] > p {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Cache directory setup
CACHE_DIR = "dashboard_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def save_dataframe(df, filename="cached_data.csv"):
    """Save DataFrame to cache."""
    cache_path = os.path.join(CACHE_DIR, filename)
    df.to_csv(cache_path, index=False)
    return cache_path

def load_cached_data(filename="cached_data.csv"):
    """Load DataFrame from cache."""
    cache_path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(cache_path):
        df = pd.read_csv(cache_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        return df
    return None

def load_data(file_path):
    """Load data from CSV file."""
    df = pd.read_csv(file_path)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    # Save to cache
    save_dataframe(df)
    return df

def create_time_comparison(df, metric, freq='M'):
    """Create time comparison for selected metric."""
    df['period'] = df['transaction_date'].dt.to_period(freq)
    comparison = df.groupby('period')[metric].sum().reset_index()
    comparison['period'] = comparison['period'].astype(str)
    return comparison

def plot_category_distribution(df):
    """Create category distribution plot."""
    category_data = df.groupby('category').agg({
        'total_price': 'sum',
        'profit': 'sum',
        'order_id': 'count'
    }).reset_index()
    
    fig = px.sunburst(df, 
                      path=['category', 'product_name'], 
                      values='total_price',
                      title='Product Category Distribution',
                      color='profit',
                      color_continuous_scale='RdYlBu')
    return fig

def create_customer_insights(df):
    """Generate customer insights."""
    customer_data = df.groupby('customer_id').agg({
        'order_id': 'count',
        'total_price': 'sum',
        'profit': 'sum'
    }).reset_index()
    
    return {
        'total_customers': len(customer_data),
        'avg_order_value': customer_data['total_price'].mean(),
        'repeat_customers': len(customer_data[customer_data['order_id'] > 1]),
        'top_spenders': customer_data.nlargest(10, 'total_price')
    }

def create_dashboard(df):
    """Create enhanced Streamlit dashboard application."""
    plot_template = "plotly_dark" # because dark theme is superior
    
    # Header with logo and title
    st.title('🛍️ Advanced E-commerce Analytics Dashboard')
    
    # Add data source indicator
    if st.session_state.get('data_source'):
        st.caption(f"Current Data Source: {st.session_state.data_source}")
    
    # Sidebar filters
    with st.sidebar:
        st.header('Dashboard Filters')
        
        # Clear data button
        if st.button('Clear Current Data'):
            if os.path.exists(os.path.join(CACHE_DIR, "cached_data.csv")):
                os.remove(os.path.join(CACHE_DIR, "cached_data.csv"))
            st.session_state.data = None
            st.session_state.data_source = None
            st.rerun()
        
         # Date filter
        date_range = st.date_input(
            "Select Date Range",
            [df['transaction_date'].min(), df['transaction_date'].max()],
            min_value=df['transaction_date'].min().date(),
            max_value=df['transaction_date'].max().date()
        )
        
        # Category and product filters
        categories = ['All'] + list(df['category'].unique())
        selected_category = st.selectbox('Select Category', categories)
        
        products = ['All'] + list(df['product_name'].unique())
        selected_product = st.selectbox('Select Product', products)
        
        # Payment and shipping method filters
        payment_methods = ['All'] + list(df['payment_method'].unique())
        selected_payment = st.selectbox('Payment Method', payment_methods)
        
        shipping_methods = ['All'] + list(df['shipping_method'].unique())
        selected_shipping = st.selectbox('Shipping Method', shipping_methods)

        # Price range filter
        price_range = st.slider(
            'Price Range ($)',
            float(df['total_price'].min()),
            float(df['total_price'].max()),
            (float(df['total_price'].min()), float(df['total_price'].max()))
        )
    
    # Update all plotly figures to use dark template
    def update_fig_template(fig):
        fig.update_layout(
            template=plot_template,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            font_color='white'
        )
        return fig
    
        # Apply filters
    mask = (
        (df['transaction_date'].dt.date >= date_range[0]) & 
        (df['transaction_date'].dt.date <= date_range[1]) &
        (df['total_price'].between(price_range[0], price_range[1]))
    )
    if selected_category != 'All':
        mask &= (df['category'] == selected_category)
    if selected_product != 'All':
        mask &= (df['product_name'] == selected_product)
    if selected_payment != 'All':
        mask &= (df['payment_method'] == selected_payment)
    if selected_shipping != 'All':
        mask &= (df['shipping_method'] == selected_shipping)
    
    filtered_df = df[mask]
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${filtered_df['total_price'].sum():,.2f}",
                 delta=f"{(filtered_df['total_price'].sum() / df['total_price'].sum() * 100):.1f}% of total")
    with col2:
        st.metric("Total Profit", f"${filtered_df['profit'].sum():,.2f}",
                 delta=f"{(filtered_df['profit'].sum() / filtered_df['total_price'].sum() * 100):.1f}% margin")
    with col3:
        st.metric("Total Orders", f"{len(filtered_df):,}",
                 delta=f"{len(filtered_df) / len(df) * 100:.1f}% of total")
    with col4:
        avg_order = filtered_df['total_price'].mean()
        st.metric("Avg Order Value", f"${avg_order:,.2f}")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Analysis", "🎯 Product Insights", 
                                     "👥 Customer Analytics", "⚠️ Fraud Detection"])
    
    with tab1:
        st.header('Sales and Profit Analysis')
        
        # Time series analysis
        daily_metrics = filtered_df.groupby(filtered_df['transaction_date'].dt.date).agg({
            'profit': 'sum',
            'total_price': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        fig_metrics = go.Figure()
        fig_metrics.add_trace(go.Scatter(x=daily_metrics['transaction_date'], 
                                       y=daily_metrics['total_price'],
                                       name='Revenue',
                                       line=dict(color='#2E86C1')))
        fig_metrics.add_trace(go.Scatter(x=daily_metrics['transaction_date'], 
                                       y=daily_metrics['profit'],
                                       name='Profit',
                                       line=dict(color='#28B463')))
        fig_metrics.update_layout(title='Daily Revenue and Profit Trends',
                                xaxis_title='Date',
                                yaxis_title='Amount ($)',
                                hovermode='x unified')
        st.plotly_chart(fig_metrics, use_container_width=True)
        
        # Payment and shipping analysis
        col1, col2 = st.columns(2)
        with col1:
            payment_analysis = filtered_df.groupby('payment_method').agg({
                'total_price': 'sum',
                'order_id': 'count'
            }).reset_index()
            fig_payment = px.pie(payment_analysis, values='total_price', names='payment_method',
                               title='Revenue by Payment Method')
            st.plotly_chart(fig_payment, use_container_width=True)
        
        with col2:
            shipping_analysis = filtered_df.groupby('shipping_method').agg({
                'total_price': 'sum',
                'order_id': 'count'
            }).reset_index()
            fig_shipping = px.pie(shipping_analysis, values='order_id', names='shipping_method',
                                title='Orders by Shipping Method')
            st.plotly_chart(fig_shipping, use_container_width=True)
    
    with tab2:
        st.header('Product and Category Analysis')
        
        # Category distribution
        fig_category = plot_category_distribution(filtered_df)
        st.plotly_chart(fig_category, use_container_width=True)
        
        # Product performance
        product_analysis = filtered_df.groupby('product_name').agg({
            'quantity': 'sum',
            'profit': 'sum',
            'total_price': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        with col1:
            fig_products = px.bar(product_analysis.nlargest(10, 'quantity'),
                                x='product_name', y='quantity',
                                title='Top 10 Products by Quantity Sold')
            st.plotly_chart(fig_products, use_container_width=True)
        
        with col2:
            fig_profit = px.bar(product_analysis.nlargest(10, 'profit'),
                              x='product_name', y='profit',
                              title='Top 10 Products by Profit')
            st.plotly_chart(fig_profit, use_container_width=True)
    
    with tab3:
        st.header('Customer Insights')
        
        # Customer analysis
        customer_insights = create_customer_insights(filtered_df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Customers", f"{customer_insights['total_customers']:,}")
        with col2:
            st.metric("Avg Customer Value", f"${customer_insights['avg_order_value']:,.2f}")
        with col3:
            st.metric("Repeat Customers", f"{customer_insights['repeat_customers']:,}")
        
        st.subheader("Top Spenders")
        st.dataframe(customer_insights['top_spenders'].style.format({
            'total_price': '${:,.2f}',
            'profit': '${:,.2f}'
        }))
    
    with tab4:
        st.header('Fraud Detection Dashboard')
        
        # Enhanced fraud detection
        suspicious_threshold = st.slider('Suspicious Amount Threshold (percentile)', 90, 99, 95)
        
        suspicious_orders = filtered_df[
            (filtered_df['total_price'] > filtered_df['total_price'].quantile(suspicious_threshold/100)) |
            (filtered_df['transaction_date'].dt.hour.between(1, 4)) |
            (filtered_df['quantity'] > filtered_df['quantity'].quantile(0.95))
        ]
        
        # IP address analysis
        ip_counts = filtered_df.groupby('ip_address')['order_id'].count().reset_index()
        suspicious_ips = ip_counts[ip_counts['order_id'] > ip_counts['order_id'].quantile(0.95)]
        suspicious_ip_orders = filtered_df[filtered_df['ip_address'].isin(suspicious_ips['ip_address'])]
        
        col1, col2 = st.columns(2)
        with col1:
            st.warning(f'Found {len(suspicious_orders)} potentially suspicious orders')
            fig_suspicious = px.scatter(suspicious_orders,
                                     x='transaction_date',
                                     y='total_price',
                                     color='category',
                                     size='quantity',
                                     title='Suspicious Transactions Distribution')
            st.plotly_chart(fig_suspicious, use_container_width=True)
        
        with col2:
            st.warning(f'Found {len(suspicious_ip_orders)} orders from suspicious IPs')
            fig_ip = px.scatter(suspicious_ip_orders,
                              x='transaction_date',
                              y='total_price',
                              color='ip_address',
                              size='quantity',
                              title='Orders from Suspicious IPs')
            st.plotly_chart(fig_ip, use_container_width=True)
        
        # Detailed suspicious order data
        st.subheader("Suspicious Order Details")
        suspicious_data = pd.concat([suspicious_orders, suspicious_ip_orders]).drop_duplicates()
        st.dataframe(suspicious_data[['order_id', 'transaction_date', 'total_price', 
                                    'quantity', 'ip_address', 'payment_method']].sort_values('total_price', ascending=False))
# Main Streamlit app
if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.data_source = None

# Load cached data on startup if available
if st.session_state.data is None:
    cached_data = load_cached_data()
    if cached_data is not None:
        st.session_state.data = cached_data
        st.session_state.data_source = "Cached Data"

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    # Check if this is a new file
    file_contents = uploaded_file.getvalue()
    file_hash = base64.b64encode(file_contents).decode()
    
    if 'current_file_hash' not in st.session_state or st.session_state.current_file_hash != file_hash:
        df = load_data(uploaded_file)
        st.session_state.data = df
        st.session_state.current_file_hash = file_hash
        st.session_state.data_source = uploaded_file.name
        st.rerun()

if st.session_state.data is not None:
    create_dashboard(st.session_state.data)
else:
    st.info("Please upload a CSV file to begin analysis.")

# Add download button for current data
if st.session_state.data is not None:
    csv = st.session_state.data.to_csv(index=False)
    st.download_button(
        label="Download Current Data as CSV",
        data=csv,
        file_name="ecommerce_data.csv",
        mime="text/csv"
    )