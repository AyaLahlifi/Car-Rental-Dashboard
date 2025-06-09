import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="KECH Car Rental Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #1E3A8A;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .card {
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
        background-color: white;
    }
    .kpi-container {
        padding: 0.5rem;
        text-align: center;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0;
    }
    .kpi-label {
        font-size: 1rem;
        color: #4B5563;
        margin-top: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Page header
st.markdown("<h1 class='main-header'> KECH Car Rental Agency Dashboard</h1>", unsafe_allow_html=True)

# Function to load data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    try:
        # Try to load from the provided Excel files
        vehicles_df = pd.read_excel("C:/Users/ayala/Downloads/sfe_2/vehicles .xlsx")
        rentals_df = pd.read_excel("C:/Users/ayala/Downloads/sfe_2/rentals .xlsx")
    except FileNotFoundError:
        # If files not found, use sample data
        st.warning("Excel files not found. Using sample data instead.")
        
        # Create sample vehicles data
        vehicles_data = {
            'vehicle_id': list(range(1, 21)),
            'brand': np.random.choice(['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Hyundai'], 20),
            'model': np.random.choice(['Sedan', 'SUV', 'Compact', 'Luxury', 'Van'], 20),
            'year': np.random.choice(range(2018, 2023), 20),
            'category': np.random.choice(['Economy', 'Standard', 'Premium', 'Luxury'], 20),
            'daily_rate': np.random.uniform(30, 150, 20).round(2),
            'status': np.random.choice(['Available', 'Rented', 'Maintenance'], 20, p=[0.6, 0.3, 0.1]),
            'mileage': np.random.uniform(10000, 80000, 20).round(0),
            'last_maintenance': pd.date_range(start='2023-01-01', periods=20),
            'condition_score': np.random.uniform(3, 5, 20).round(1)
        }
        vehicles_df = pd.DataFrame(vehicles_data)
        
        # Create sample rentals data
        today = datetime.now()
        num_rentals = 200
        start_dates = pd.date_range(end=today, periods=365).tolist()
        
        rentals_data = {
            'rental_id': list(range(1, num_rentals + 1)),
            'vehicle_id': np.random.choice(vehicles_df['vehicle_id'], num_rentals),
            'client_name': np.random.choice(['John Smith', 'Mary Johnson', 'Robert Williams', 'Sarah Davis', 
                                             'Michael Brown', 'Jennifer Miller', 'David Garcia', 'Lisa Wilson',
                                             'James Moore', 'Patricia Taylor'], num_rentals),
            'start_date': np.random.choice(start_dates, num_rentals),
            'rental_days': np.random.choice(range(1, 15), num_rentals),
            'total_price': np.random.uniform(100, 2000, num_rentals).round(2),
            'payment_method': np.random.choice(['Credit Card', 'Debit Card', 'Cash', 'Online Payment'], num_rentals),
            'status': np.random.choice(['Completed', 'Active', 'Reserved'], num_rentals, p=[0.7, 0.2, 0.1]),
            'return_delay_days': np.random.choice(range(0, 5), num_rentals, p=[0.8, 0.1, 0.05, 0.03, 0.02]),
            'customer_rating': np.random.choice([None, 3, 4, 5], num_rentals, p=[0.2, 0.1, 0.3, 0.4])
        }
        rentals_df = pd.DataFrame(rentals_data)
        
        # Calculate end dates based on start_date and rental_days
        rentals_df['end_date'] = rentals_df.apply(lambda x: x['start_date'] + timedelta(days=x['rental_days']), axis=1)
        
    # Process and clean the data
    rentals_df['start_date'] = pd.to_datetime(rentals_df['start_date'])
    if 'end_date' not in rentals_df.columns:
        rentals_df['end_date'] = rentals_df.apply(lambda x: x['start_date'] + timedelta(days=x['rental_days']), axis=1)
    
    # Add month and year columns for time-based analysis
    rentals_df['month'] = rentals_df['start_date'].dt.month_name()
    rentals_df['year'] = rentals_df['start_date'].dt.year
    rentals_df['month_year'] = rentals_df['start_date'].dt.strftime('%b %Y')
    
    # Merge dataframes for comprehensive analysis
    merged_df = pd.merge(rentals_df, vehicles_df, on='vehicle_id', how='left')
    
    return vehicles_df, rentals_df, merged_df

# Load the data
vehicles_df, rentals_df, merged_df = load_data()

# Sidebar for filters
st.sidebar.header("Filters")

# Date range filter
min_date = rentals_df['start_date'].min().date()
max_date = rentals_df['start_date'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_rentals = rentals_df[(rentals_df['start_date'].dt.date >= start_date) & 
                                 (rentals_df['start_date'].dt.date <= end_date)]
    filtered_merged = merged_df[(merged_df['start_date'].dt.date >= start_date) & 
                               (merged_df['start_date'].dt.date <= end_date)]
else:
    filtered_rentals = rentals_df
    filtered_merged = merged_df

# Vehicle category filter
all_categories = ['All'] + sorted(vehicles_df['vehicle_type'].unique().tolist())
selected_category = st.sidebar.selectbox("Vehicle Category", all_categories)

if selected_category != 'All':
    filtered_vehicles = vehicles_df[vehicles_df['vehicle_type'] == selected_category]
    vehicle_ids = filtered_vehicles['vehicle_id'].tolist()
    filtered_rentals = filtered_rentals[filtered_rentals['vehicle_id'].isin(vehicle_ids)]
    filtered_merged = filtered_merged[filtered_merged['vehicle_type'] == selected_category]
else:
    filtered_vehicles = vehicles_df

# Vehicle status filter
all_statuses = ['All'] + sorted(vehicles_df['status'].unique().tolist())
selected_status = st.sidebar.selectbox("Vehicle Status", all_statuses)

if selected_status != 'All':
    filtered_vehicles = filtered_vehicles[filtered_vehicles['status'] == selected_status]

# Vehicle brand filter
all_brands = ['All'] + sorted(vehicles_df['make'].unique().tolist())
selected_brand = st.sidebar.selectbox("Vehicle Brand", all_brands)

if selected_brand != 'All':
    filtered_vehicles = filtered_vehicles[filtered_vehicles['make'] == selected_brand]
    filtered_merged = filtered_merged[filtered_merged['make'] == selected_brand]

# Main dashboard content
# KPIs section
st.markdown("<h2 class='sub-header'>📊 Key Performance Indicators</h2>", unsafe_allow_html=True)

# Calculate KPIs
total_rentals = len(filtered_rentals)
total_revenue = filtered_rentals['total_price'].sum()
avg_rental_price = filtered_rentals['total_price'].mean() if total_rentals > 0 else 0
# Ensure dates are datetime objects
filtered_rentals["start_date"] = pd.to_datetime(filtered_rentals["start_date"])
filtered_rentals["end_date"] = pd.to_datetime(filtered_rentals["end_date"])

# Calculate rental duration
filtered_rentals["rental_days"] = (filtered_rentals["end_date"] - filtered_rentals["start_date"]).dt.days

# Now calculate average rental duration
avg_rental_days = filtered_rentals['rental_days'].mean() if total_rentals > 0 else 0

avg_rating = filtered_rentals['customer_rating'].mean() if total_rentals > 0 else 0
total_available = len(filtered_vehicles[filtered_vehicles['status'] == 'Available'])
total_rented = len(filtered_vehicles[filtered_vehicles['status'] == 'Rented'])
total_maintenance = len(filtered_vehicles[filtered_vehicles['status'] == 'Maintenance'])

# Display KPIs in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='kpi-container' style='background-color: #EFF6FF;color: black;'>
        <p class='kpi-value'>{}</p>
        <p class='kpi-label'>Total Rentals</p>
    </div>
    """.format(total_rentals), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='kpi-container' style='background-color: #ECFDF5;color: black;'>
        <p class='kpi-value'> {:.2f} MAD</p>
        <p class='kpi-label'>Total Revenue</p>
    </div>
    """.format(total_revenue), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='kpi-container' style='background-color: #F3F4F6;color: black;'>
        <p class='kpi-value'> {:.2f} MAD</p>
        <p class='kpi-label'>Avg. Rental Price</p>
    </div>
    """.format(avg_rental_price), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='kpi-container' style='background-color: #FEF3C7;color: black;'>
        <p class='kpi-value'>{:.1f} ⭐</p>
        <p class='kpi-label'>Avg. Customer Rating</p>
    </div>
    """.format(avg_rating), unsafe_allow_html=True)

# Vehicle status summary
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='kpi-container' style='background-color: #DCFCE7;color: black;'>
        <p class='kpi-value'>{}</p>
        <p class='kpi-label'>Available Vehicles</p>
    </div>
    """.format(total_available), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='kpi-container' style='background-color: #DBEAFE;color: black;'>
        <p class='kpi-value'>{}</p>
        <p class='kpi-label'>Rented Vehicles</p>
    </div>
    """.format(total_rented), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='kpi-container' style='background-color: #FEE2E2;color: black;'>
        <p class='kpi-value'>{}</p>
        <p class='kpi-label'>Vehicles in Maintenance</p>
    </div>
    """.format(total_maintenance), unsafe_allow_html=True)

# Time series analysis
st.markdown("<h2 class='sub-header'>📈 Rental Trends</h2>", unsafe_allow_html=True)

# Prepare time series data - group by month
monthly_rentals = filtered_rentals.groupby('month_year').size().reset_index(name='count')
monthly_revenue = filtered_rentals.groupby('month_year').agg({'total_price': 'sum'}).reset_index()

# Ensure chronological order
all_months = pd.date_range(start=min_date, end=max_date, freq='MS').strftime('%b %Y').tolist()
monthly_rentals['month_year'] = pd.Categorical(monthly_rentals['month_year'], categories=all_months, ordered=True)
monthly_rentals = monthly_rentals.sort_values('month_year')

monthly_revenue['month_year'] = pd.Categorical(monthly_revenue['month_year'], categories=all_months, ordered=True)
monthly_revenue = monthly_revenue.sort_values('month_year')

# Create tabs for different time series visualizations
trend_tabs = st.tabs(["Rentals Over Time", "Revenue Over Time", "Combined View"])

with trend_tabs[0]:
    fig_rentals = px.line(
        monthly_rentals, 
        x='month_year', 
        y='count',
        markers=True,
        title='Number of Rentals by Month',
        labels={'count': 'Number of Rentals', 'month_year': 'Month'},
        template='plotly_white'
    )
    fig_rentals.update_layout(height=400)
    st.plotly_chart(fig_rentals, use_container_width=True)

with trend_tabs[1]:
    fig_revenue = px.line(
        monthly_revenue, 
        x='month_year', 
        y='total_price',
        markers=True,
        title='Revenue by Month',
        labels={'total_price': 'Revenue (MAD)', 'month_year': 'Month'},
        template='plotly_white'
    )
    fig_revenue.update_layout(height=400)
    st.plotly_chart(fig_revenue, use_container_width=True)

with trend_tabs[2]:
    # Create a figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=monthly_rentals['month_year'], 
            y=monthly_rentals['count'],
            name="Number of Rentals",
            mode='lines+markers',
            line=dict(color='#3B82F6')
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=monthly_revenue['month_year'], 
            y=monthly_revenue['total_price'],
            name="Revenue (MAD)",
            mode='lines+markers',
            line=dict(color='#10B981')
        ),
        secondary_y=True
    )
    
    # Set titles
    fig.update_layout(
        title_text="Rentals and Revenue by Month",
        template='plotly_white',
        height=400
    )
    
    # Set x-axis title
    fig.update_xaxes(title_text="Month")
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Number of Rentals", secondary_y=False)
    fig.update_yaxes(title_text="Revenue (MAD)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)

# Vehicle performance section
st.markdown("<h2 class='sub-header'>🚙 Vehicle Performance</h2>", unsafe_allow_html=True)

# Create two columns for this section
col1, col2 = st.columns(2)

with col1:
    # Vehicle category performance
    category_perf = filtered_merged.groupby('vehicle_type').agg({
        'rental_id': 'count',
        'total_price': 'sum',
        'customer_rating': 'mean'
    }).reset_index()
    
    category_perf.columns = ['Category', 'Number of Rentals', 'Total Revenue', 'Avg Rating']
    category_perf['Avg Rating'] = category_perf['Avg Rating'].round(1)
    
    fig_category = px.bar(
        category_perf,
        x='Category',
        y='Number of Rentals',
        color='Total Revenue',
        text='Number of Rentals',
        title='Rentals by Vehicle Category',
        color_continuous_scale='Blues',
        template='plotly_white'
    )
    fig_category.update_layout(height=400)
    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    # Vehicle brand performance
    brand_perf = filtered_merged.groupby('make').agg({
        'rental_id': 'count',
        'total_price': 'sum',
        'customer_rating': 'mean'
    }).reset_index()
    
    brand_perf.columns = ['Brand', 'Number of Rentals', 'Total Revenue', 'Avg Rating']
    brand_perf['Avg Rating'] = brand_perf['Avg Rating'].round(1)
    brand_perf = brand_perf.sort_values('Number of Rentals', ascending=False)
    
    fig_brand = px.bar(
        brand_perf.head(10),
        x='Brand',
        y='Number of Rentals',
        color='Total Revenue',
        text='Number of Rentals',
        title='Top 10 Vehicle Brands by Rental Count',
        color_continuous_scale='Greens',
        template='plotly_white'
    )
    fig_brand.update_layout(height=400)
    st.plotly_chart(fig_brand, use_container_width=True)

# Vehicle status and condition visualizations
col1, col2 = st.columns(2)

with col1:
    # Vehicle status distribution
    status_counts = filtered_vehicles['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig_status = px.pie(
        status_counts, 
        values='Count', 
        names='Status',
        title='Vehicle Status Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4,
        template='plotly_white'
    )
    fig_status.update_layout(height=400)
    st.plotly_chart(fig_status, use_container_width=True)

with col2:
    # Vehicle condition score distribution
    if 'condition_score' in filtered_vehicles.columns:
        fig_condition = px.histogram(
            filtered_vehicles,
            x='condition_score',
            nbins=10,
            title='Vehicle Condition Score Distribution',
            color_discrete_sequence=['#3B82F6'],
            template='plotly_white'
        )
        fig_condition.update_layout(height=400)
        st.plotly_chart(fig_condition, use_container_width=True)

# Client insights section
st.markdown("<h2 class='sub-header'>👥 Client Insights</h2>", unsafe_allow_html=True)

# Create tabs for different client insights
client_tabs = st.tabs(["Top Clients", "Return Delay Analysis", "Customer Ratings"])

with client_tabs[0]:
    # Top clients by rental frequency
    top_clients = filtered_rentals['client_name'].value_counts().reset_index()
    top_clients.columns = ['Client Name', 'Number of Rentals']
    top_clients = top_clients.head(10)
    
    fig_top_clients = px.bar(
        top_clients,
        x='Client Name',
        y='Number of Rentals',
        title='Top 10 Clients by Rental Frequency',
        color='Number of Rentals',
        color_continuous_scale='Blues',
        template='plotly_white'
    )
    fig_top_clients.update_layout(height=400)
    st.plotly_chart(fig_top_clients, use_container_width=True)

with client_tabs[1]:
    st.markdown("### ⏱️ Return Delay Analysis")
    # Return delay analysis
    delay_counts = filtered_rentals['return_delay_days'].value_counts().reset_index()
    delay_counts.columns = ['Delay Days', 'Count']
    delay_counts = delay_counts.sort_values('Delay Days')
    
    fig_delay = px.bar(
        delay_counts,
        x='Delay Days',
        y='Count',
        title='Return Delay Distribution',
        color='Count',
        color_continuous_scale='Reds',
        template='plotly_white'
    )
    fig_delay.update_layout(height=400)
    st.plotly_chart(fig_delay, use_container_width=True)
    
    # Calculate average delay
    avg_delay = filtered_rentals['return_delay_days'].mean()
    st.info(f"Average Return Delay: {avg_delay:.2f} days")
    # Total delayed rentals
    delayed_rentals = filtered_rentals[filtered_rentals['return_delay_days'] > 0]
    percent_delayed = (len(delayed_rentals) / len(filtered_rentals)) * 100 if len(filtered_rentals) > 0 else 0

    # Show KPIs
    col1, col2 = st.columns(2)
    col1.metric("📦 Delayed Rentals", len(delayed_rentals))
    col2.metric("📊 % of Delayed Rentals", f"{percent_delayed:.1f}%")

    # Pie chart of delayed vs on-time
    delay_pie = pd.DataFrame({
        "Status": ["On Time", "Delayed"],
        "Count": [
            (filtered_rentals['return_delay_days'] == 0).sum(),
            (filtered_rentals['return_delay_days'] > 0).sum()
        ]
    })

    fig_pie = px.pie(
        delay_pie,
        names="Status",
        values="Count",
        title="Rental Return Timeliness",
        color_discrete_sequence=["#10B981", "#EF4444"],
        hole=0.4,
        template='plotly_white'
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

with client_tabs[2]:
    # Customer ratings analysis
    valid_ratings = filtered_rentals.dropna(subset=['customer_rating'])
    rating_counts = valid_ratings['customer_rating'].value_counts().reset_index()
    rating_counts.columns = ['Rating', 'Count']
    rating_counts = rating_counts.sort_values('Rating')
    
    fig_ratings = px.bar(
        rating_counts,
        x='Rating',
        y='Count',
        title='Customer Rating Distribution',
        color='Rating',
        color_continuous_scale='YlGn',
        template='plotly_white'
    )
    fig_ratings.update_layout(height=400)
    st.plotly_chart(fig_ratings, use_container_width=True)
    
    # Calculate percentage of 4+ ratings
    high_ratings = valid_ratings[valid_ratings['customer_rating'] >= 4]['customer_rating'].count()
    rating_percentage = (high_ratings / len(valid_ratings)) * 100 if len(valid_ratings) > 0 else 0
    st.info(f"Percentage of 4+ Star Ratings: {rating_percentage:.2f}%")

# Advanced analytics section
st.markdown("<h2 class='sub-header'>🔍 Advanced Analytics</h2>", unsafe_allow_html=True)

# Create two columns
col1, col2 = st.columns(2)
# 📌 Ensure clean data for Plotly chart
# Remove rows with missing rental_days or total_price
safe_data = filtered_rentals.dropna(subset=["rental_days", "total_price"])

# Optional: Remove entries with 0 or negative rental days
safe_data = safe_data[safe_data["rental_days"] > 0]


with col1:
    # Rental duration vs. price relationship
    fig_duration_price = px.scatter(
        safe_data,
        x='rental_days',
        y='total_price',
        color='return_delay_days',
        size='rental_days',
        title='Rental Duration vs. Price',
        labels={'rental_days': 'Rental Duration (days)', 'total_price': 'Total Price (MAD)', 'return_delay_days': 'Return Delay (days)'},
        template='plotly_white'
    )
    fig_duration_price.update_layout(height=400)
    st.plotly_chart(fig_duration_price, use_container_width=True)

with col2:
    # Revenue by payment method
    payment_revenue = filtered_rentals.groupby('payment_method').agg({
        'total_price': 'sum',
        'rental_id': 'count'
    }).reset_index()
    
    payment_revenue.columns = ['Payment Method', 'Total Revenue', 'Number of Rentals']
    
    fig_payment = px.pie(
        payment_revenue,
        values='Total Revenue',
        names='Payment Method',
        title='Revenue by Payment Method',
        hover_data=['Number of Rentals'],
        template='plotly_white'
    )
    fig_payment.update_layout(height=400)
    st.plotly_chart(fig_payment, use_container_width=True)

# Vehicle details table
st.markdown("<h2 class='sub-header'>🚗 Vehicle Fleet Details</h2>", unsafe_allow_html=True)

# Create an expander for this section
with st.expander("View Vehicle Fleet Details"):
    # Prepare the data for display
    display_cols = ['vehicle_id', 'make', 'model', 'year', 'vehicle_type', 'fuel_type', 'color', 'rental_price_per_day', 'status']

    vehicle_table = filtered_vehicles[display_cols].copy()
    
    # Rename columns for better display
    vehicle_table.columns = ['ID', 'Brand', 'Model', 'Year', 'Category', 'Daily Rate (MAD)', 'Status', 'Mileage', 'Condition Score']
    
    # Display the table
    st.dataframe(vehicle_table, use_container_width=True)

# Recent rentals table
st.markdown("<h2 class='sub-header'>📝 Recent Rentals</h2>", unsafe_allow_html=True)

# Create an expander for this section
with st.expander("View Recent Rentals"):
    # Prepare the data for display
    display_cols = ['rental_id', 'vehicle_id', 'client_name', 'start_date', 'end_date', 'rental_days', 'total_price', 'status', 'return_delay_days', 'customer_rating']
    recent_rentals = filtered_rentals.sort_values('start_date', ascending=False).head(20)
    rentals_table = recent_rentals[display_cols].copy()
    
    # Rename columns for better display
    rentals_table.columns = ['ID', 'Vehicle ID', 'Client', 'Start Date', 'End Date', 'Duration (days)', 'Price (MAD)', 'Status', 'Delay (days)', 'Rating']
    
    # Format dates
    rentals_table['Start Date'] = rentals_table['Start Date'].dt.strftime('%Y-%m-%d')
    rentals_table['End Date'] = rentals_table['End Date'].dt.strftime('%Y-%m-%d')
    
    # Display the table
    st.dataframe(rentals_table, use_container_width=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 1rem; background-color: #F3F4F6; border-radius: 5px;color:black;">
    <p style="margin-bottom: 0.5rem;">Car Rental Agency Dashboard</p>
    <p style="margin-top: 0; font-size: 0.8rem; color: #6B7280;">Data updates automatically when Excel files are modified</p>
</div>
""", unsafe_allow_html=True)