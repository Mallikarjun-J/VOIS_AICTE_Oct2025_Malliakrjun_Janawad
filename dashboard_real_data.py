"""
Streamlit Dashboard for Real Air BNB Dataset
Adapted for your actual Airbnb_dataset.csv
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Air BNB Data Analysis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (minimal - keeping clean)
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_csv('Airbnb_dataset.csv')
    # Clean price if needed
    if df['price'].dtype == 'object':
        df['price'] = df['price'].str.replace('$', '').str.replace(',', '').astype(float)
    # Handle missing values
    df['reviews_per_month'].fillna(0, inplace=True)
    return df

def add_bar_borders(fig):
    """Add white borders to bar charts to separate bars"""
    fig.update_traces(marker=dict(line=dict(color='white', width=2)))
    return fig

# Main app
def main():
    st.markdown("""
        <h1 style='text-align: center; 
                   color: #FF5A5F; 
                   font-size: 50px; 
                   font-weight: bold; 
                   padding: 30px;
                   text-shadow: 3px 3px 6px rgba(0,0,0,0.15);
                   letter-spacing: 3px;'>
            🏠 Air BNB Data Analysis Dashboard
        </h1>
    """, unsafe_allow_html=True)
    
    try:
        df = load_data()
        
        # Sidebar
        st.sidebar.title("🎛️ Filters")
        
        # Neighbourhood group filter
        if 'neighbourhood_group' in df.columns:
            neighbourhood_groups = ['All'] + sorted(df['neighbourhood_group'].unique().tolist())
            selected_ng = st.sidebar.multiselect(
                "Neighbourhood Group",
                neighbourhood_groups,
                default=['All']
            )
            if 'All' not in selected_ng and selected_ng:
                df = df[df['neighbourhood_group'].isin(selected_ng)]
        
        # Room type filter
        room_types = ['All'] + sorted(df['room_type'].unique().tolist())
        selected_room = st.sidebar.multiselect(
            "Room Type",
            room_types,
            default=['All']
        )
        if 'All' not in selected_room and selected_room:
            df = df[df['room_type'].isin(selected_room)]
        
        # Price range filter
        price_min = int(df['price'].min())
        price_max = int(df['price'].max())
        price_range = st.sidebar.slider(
            "Price Range ($)",
            price_min,
            min(price_max, 1000),
            (price_min, min(500, price_max))
        )
        df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
        
        # Minimum nights filter
        min_nights_max = int(df['minimum_nights'].quantile(0.95))
        min_nights_range = st.sidebar.slider(
            "Minimum Nights",
            1,
            min(min_nights_max, 30),
            (1, min(7, min_nights_max))
        )
        df = df[(df['minimum_nights'] >= min_nights_range[0]) & (df['minimum_nights'] <= min_nights_range[1])]
        
        st.sidebar.markdown(f"**Showing {len(df):,} listings**")
        
        # Key Metrics with custom styling
        st.header("📊 Key Metrics")
        
        # Custom CSS for metric cards
        st.markdown("""
        <style>
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
        }
        div[data-testid="stMetric"] > label {
            color: white !important;
            font-weight: 600;
            font-size: 14px;
        }
        div[data-testid="stMetric"] > div {
            color: white !important;
            font-size: 28px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Listings", f"{len(df):,}")
        with col2:
            st.metric("Avg Price", f"${df['price'].mean():.2f}")
        with col3:
            st.metric("Median Price", f"${df['price'].median():.2f}")
        with col4:
            st.metric("Total Reviews", f"{df['number_of_reviews'].sum():,}")
        with col5:
            st.metric("Unique Hosts", f"{df['host_id'].nunique():,}")
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Overview", 
            "💰 Price Analysis", 
            "🗺️ Location", 
            "⭐ Reviews", 
            "📅 Availability"
        ])
        
        with tab1:
            show_overview(df)
        
        with tab2:
            show_price_analysis(df)
        
        with tab3:
            show_location_analysis(df)
        
        with tab4:
            show_reviews_analysis(df)
        
        with tab5:
            show_availability_analysis(df)
            
    except FileNotFoundError:
        st.error("❌ Could not find Airbnb_dataset.csv. Please ensure the file is in the same directory.")
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")

def show_overview(df):
    st.subheader("📈 Overview")
    
    # Row 1: Room Type & Neighbourhood
    col1, col2 = st.columns(2)
    
    with col1:
        # Room type distribution
        room_counts = df['room_type'].value_counts()
        fig = px.pie(
            values=room_counts.values,
            names=room_counts.index,
            title="Room Type Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
                font=dict(size=12, color="black")
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Neighbourhood group distribution
        if 'neighbourhood_group' in df.columns:
            ng_counts = df['neighbourhood_group'].value_counts()
            fig = px.bar(
                x=ng_counts.index,
                y=ng_counts.values,
                title="Listings by Neighbourhood Group",
                color=ng_counts.values,
                color_continuous_scale='Viridis'
            )
            fig = add_bar_borders(fig)
            fig.update_layout(xaxis_title="Neighbourhood Group", yaxis_title="Count", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Price Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution histogram
        fig = px.histogram(
            df,
            x='price',
            nbins=50,
            title="Price Distribution",
            color_discrete_sequence=['#FF5A5F']
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Price ($)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price box plot by room type
        fig = px.box(
            df,
            x='room_type',
            y='price',
            title="Price Distribution by Room Type",
            color='room_type'
        )
        fig.update_layout(xaxis_title="Room Type", yaxis_title="Price ($)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Reviews & Availability
    col1, col2 = st.columns(2)
    
    with col1:
        # Reviews distribution
        fig = px.histogram(
            df,
            x='number_of_reviews',
            nbins=50,
            title="Reviews Distribution",
            color_discrete_sequence=['#00A699']
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Number of Reviews", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Availability distribution
        fig = px.histogram(
            df,
            x='availability_365',
            nbins=50,
            title="Availability Distribution (Days/Year)",
            color_discrete_sequence=['#FFB400']
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Availability (days)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 4: Top Neighbourhoods
    st.markdown("### 🏘️ Top 15 Neighbourhoods by Listings")
    top_neighbourhoods = df['neighbourhood'].value_counts().head(15)
    fig = px.bar(
        x=top_neighbourhoods.values,
        y=top_neighbourhoods.index,
        orientation='h',
        title="Top 15 Neighbourhoods",
        color=top_neighbourhoods.values,
        color_continuous_scale='Blues'
    )
    fig = add_bar_borders(fig)
    fig.update_layout(xaxis_title="Number of Listings", yaxis_title="Neighbourhood", showlegend=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

def show_price_analysis(df):
    st.subheader("💰 Price Analysis")
    
    # Row 1: Room Type & Neighbourhood Group
    col1, col2 = st.columns(2)
    
    with col1:
        # Price by room type
        price_by_room = df.groupby('room_type')['price'].agg(['mean', 'median', 'count']).reset_index()
        fig = px.bar(
            price_by_room,
            x='room_type',
            y='mean',
            title="Average Price by Room Type",
            color='mean',
            color_continuous_scale='Reds',
            text='mean'
        )
        fig = add_bar_borders(fig)
        fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        fig.update_layout(xaxis_title="Room Type", yaxis_title="Average Price ($)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price by neighbourhood group
        if 'neighbourhood_group' in df.columns:
            price_by_ng = df.groupby('neighbourhood_group')['price'].mean().sort_values()
            fig = px.bar(
                x=price_by_ng.values,
                y=price_by_ng.index,
                orientation='h',
                title="Average Price by Neighbourhood Group",
                color=price_by_ng.values,
                color_continuous_scale='Blues'
            )
            fig = add_bar_borders(fig)
            fig.update_layout(xaxis_title="Average Price ($)", yaxis_title="Neighbourhood Group", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Top Expensive Neighbourhoods & Median Price Comparison
    col1, col2 = st.columns(2)
    
    with col1:
        # Top expensive neighbourhoods
        top_neighbourhoods = df.groupby('neighbourhood')['price'].mean().sort_values(ascending=False).head(15)
        fig = px.bar(
            x=top_neighbourhoods.values,
            y=top_neighbourhoods.index,
            orientation='h',
            title="Top 15 Most Expensive Neighbourhoods",
            color=top_neighbourhoods.values,
            color_continuous_scale='Oranges'
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Average Price ($)", yaxis_title="Neighbourhood", showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Median price by room type
        fig = px.bar(
            price_by_room,
            x='room_type',
            y='median',
            title="Median Price by Room Type",
            color='median',
            color_continuous_scale='Greens',
            text='median'
        )
        fig = add_bar_borders(fig)
        fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        fig.update_layout(xaxis_title="Room Type", yaxis_title="Median Price ($)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Minimum nights vs price
        df_filtered = df[(df['minimum_nights'] <= 30) & (df['price'] <= 1000)]
        sample_df = df_filtered.sample(min(1000, len(df_filtered)))
        fig = px.scatter(
            sample_df,
            x='minimum_nights',
            y='price',
            color='room_type',
            title="Price vs Minimum Nights",
            opacity=0.5
        )
        fig.update_layout(xaxis_title="Minimum Nights", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Scatter Plots
    col1, col2 = st.columns(2)
    
    with col1:
        # Price vs reviews scatter
        sample_df = df.sample(min(1000, len(df)))
        fig = px.scatter(
            sample_df,
            x='number_of_reviews',
            y='price',
            color='room_type',
            title="Price vs Number of Reviews",
            opacity=0.6
        )
        fig.update_layout(xaxis_title="Number of Reviews", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price vs availability
        sample_df = df.sample(min(1000, len(df)))
        fig = px.scatter(
            sample_df,
            x='availability_365',
            y='price',
            color='room_type',
            title="Price vs Availability",
            opacity=0.6
        )
        fig.update_layout(xaxis_title="Availability (days/year)", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)

def show_location_analysis(df):
    st.subheader("🗺️ Location Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Map
        sample_df = df.sample(min(5000, len(df)))
        
        if 'neighbourhood_group' in df.columns:
            fig = px.scatter_mapbox(
                sample_df,
                lat='latitude',
                lon='longitude',
                color='neighbourhood_group',
                size='price',
                hover_data=['name', 'price', 'room_type'],
                title="Listings Map",
                zoom=10,
                height=600
            )
        else:
            fig = px.scatter_mapbox(
                sample_df,
                lat='latitude',
                lon='longitude',
                color='price',
                size='price',
                hover_data=['name', 'price', 'room_type'],
                title="Listings Map",
                zoom=10,
                height=600,
                color_continuous_scale='Viridis'
            )
        
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top neighbourhoods by count
        top_neighbourhoods = df['neighbourhood'].value_counts().head(15)
        fig = px.bar(
            x=top_neighbourhoods.values,
            y=top_neighbourhoods.index,
            orientation='h',
            title="Top 15 Neighbourhoods",
            color=top_neighbourhoods.values,
            color_continuous_scale='Greens'
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Count", yaxis_title="Neighbourhood", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary stats
        st.markdown("### 📍 Location Stats")
        if 'neighbourhood_group' in df.columns:
            st.write(f"**Neighbourhood Groups:** {df['neighbourhood_group'].nunique()}")
        st.write(f"**Neighbourhoods:** {df['neighbourhood'].nunique()}")
        st.write(f"**Latitude Range:** {df['latitude'].min():.4f} to {df['latitude'].max():.4f}")
        st.write(f"**Longitude Range:** {df['longitude'].min():.4f} to {df['longitude'].max():.4f}")

def show_reviews_analysis(df):
    st.subheader("⭐ Reviews Analysis")
    
    # Row 1: Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Reviews distribution histogram
        fig = px.histogram(
            df,
            x='number_of_reviews',
            nbins=50,
            title="Reviews Distribution",
            color_discrete_sequence=['#FF5A5F']
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Number of Reviews", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Reviews per month distribution
        df_reviews = df[df['reviews_per_month'] > 0]
        fig = px.histogram(
            df_reviews,
            x='reviews_per_month',
            nbins=50,
            title="Reviews per Month Distribution",
            color_discrete_sequence=['#00A699']
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Reviews per Month", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: By Room Type & Categories
    col1, col2 = st.columns(2)
    
    with col1:
        # Reviews distribution by room type (box plot)
        fig = px.box(
            df,
            x='room_type',
            y='number_of_reviews',
            title="Reviews Distribution by Room Type",
            color='room_type'
        )
        fig.update_layout(xaxis_title="Room Type", yaxis_title="Number of Reviews", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Review categories
        review_categories = pd.cut(
            df['number_of_reviews'],
            bins=[0, 1, 10, 50, 100, 1000],
            labels=['0', '1-10', '11-50', '51-100', '100+']
        )
        review_cat_counts = review_categories.value_counts().sort_index()
        fig = px.bar(
            x=review_cat_counts.index,
            y=review_cat_counts.values,
            title="Listings by Review Count Category",
            color=review_cat_counts.values,
            color_continuous_scale='Teal'
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Review Range", yaxis_title="Count", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: By Location
    col1, col2 = st.columns(2)
    
    with col1:
        # Average reviews by neighbourhood group
        if 'neighbourhood_group' in df.columns:
            avg_reviews = df.groupby('neighbourhood_group')['number_of_reviews'].mean().sort_values()
            fig = px.bar(
                x=avg_reviews.values,
                y=avg_reviews.index,
                orientation='h',
                title="Average Reviews by Neighbourhood Group",
                color=avg_reviews.values,
                color_continuous_scale='Purples'
            )
            fig = add_bar_borders(fig)
            fig.update_layout(xaxis_title="Average Reviews", yaxis_title="Neighbourhood Group", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average reviews by room type
        avg_reviews_room = df.groupby('room_type')['number_of_reviews'].mean().sort_values()
        fig = px.bar(
            x=avg_reviews_room.index,
            y=avg_reviews_room.values,
            title="Average Reviews by Room Type",
            color=avg_reviews_room.values,
            color_continuous_scale='Oranges'
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Room Type", yaxis_title="Average Reviews", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 4: Top Reviewed Neighbourhoods
    st.markdown("### 🏆 Top 15 Most Reviewed Neighbourhoods")
    top_reviewed = df.groupby('neighbourhood')['number_of_reviews'].sum().sort_values(ascending=False).head(15)
    fig = px.bar(
        x=top_reviewed.values,
        y=top_reviewed.index,
        orientation='h',
        title="Top 15 Neighbourhoods by Total Reviews",
        color=top_reviewed.values,
        color_continuous_scale='Viridis'
    )
    fig = add_bar_borders(fig)
    fig.update_layout(xaxis_title="Total Reviews", yaxis_title="Neighbourhood", showlegend=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
        
    # Reviews summary with custom styling
    st.markdown("### 📊 Reviews Summary")
    st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reviews", f"{df['number_of_reviews'].sum():,}")
    with col2:
        st.metric("Avg Reviews/Listing", f"{df['number_of_reviews'].mean():.1f}")
    with col3:
        listings_no_reviews = (df['number_of_reviews'] == 0).sum()
        st.metric("No Reviews", f"{listings_no_reviews:,}")
    with col4:
        listings_many_reviews = (df['number_of_reviews'] >= 100).sum()
        st.metric("100+ Reviews", f"{listings_many_reviews:,}")

def show_availability_analysis(df):
    st.subheader("📅 Availability Analysis")
    
    # Row 1: Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Availability distribution
        fig = px.histogram(
            df,
            x='availability_365',
            nbins=50,
            title="Availability Distribution",
            color_discrete_sequence=['#00A699']
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Days Available per Year", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Availability categories
        avail_categories = pd.cut(
            df['availability_365'],
            bins=[0, 30, 90, 180, 300, 365],
            labels=['0-30', '31-90', '91-180', '181-300', '301-365']
        )
        avail_cat_counts = avail_categories.value_counts().sort_index()
        fig = px.bar(
            x=avail_cat_counts.index,
            y=avail_cat_counts.values,
            title="Listings by Availability Range",
            color=avail_cat_counts.values,
            color_continuous_scale='YlOrRd'
        )
        fig = add_bar_borders(fig)
        fig.update_layout(xaxis_title="Availability Range (days)", yaxis_title="Count", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: By Room Type & Neighbourhood
    col1, col2 = st.columns(2)
    
    with col1:
        # Availability by room type
        fig = px.box(
            df,
            x='room_type',
            y='availability_365',
            title="Availability Distribution by Room Type",
            color='room_type'
        )
        fig.update_layout(xaxis_title="Room Type", yaxis_title="Availability (days)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average availability by neighbourhood group
        if 'neighbourhood_group' in df.columns:
            avg_avail = df.groupby('neighbourhood_group')['availability_365'].mean().sort_values()
            fig = px.bar(
                x=avg_avail.values,
                y=avg_avail.index,
                orientation='h',
                title="Average Availability by Neighbourhood Group",
                color=avg_avail.values,
                color_continuous_scale='Blues'
            )
            fig = add_bar_borders(fig)
            fig.update_layout(xaxis_title="Average Availability (days)", yaxis_title="Neighbourhood Group", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Correlations
    col1, col2 = st.columns(2)
    
    with col1:
        # Availability vs Price
        sample_df = df.sample(min(1000, len(df)))
        fig = px.scatter(
            sample_df,
            x='availability_365',
            y='price',
            color='room_type',
            title="Availability vs Price",
            opacity=0.6
        )
        fig.update_layout(xaxis_title="Availability (days/year)", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Availability vs Reviews
        sample_df = df.sample(min(1000, len(df)))
        fig = px.scatter(
            sample_df,
            x='availability_365',
            y='number_of_reviews',
            color='room_type',
            title="Availability vs Number of Reviews",
            opacity=0.6
        )
        fig.update_layout(xaxis_title="Availability (days/year)", yaxis_title="Number of Reviews")
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 4: Average Availability by Room Type
    st.markdown("### 📊 Availability Statistics")
    avg_avail_room = df.groupby('room_type')['availability_365'].agg(['mean', 'median', 'count']).reset_index()
    fig = px.bar(
        avg_avail_room,
        x='room_type',
        y='mean',
        title="Average Availability by Room Type",
        color='mean',
        color_continuous_scale='Greens',
        text='mean'
    )
    fig = add_bar_borders(fig)
    fig.update_traces(texttemplate='%{text:.1f} days', textposition='outside')
    fig.update_layout(xaxis_title="Room Type", yaxis_title="Average Availability (days)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Availability summary with custom styling
    st.markdown("### 📊 Availability Summary")
    st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Availability", f"{df['availability_365'].mean():.0f} days")
    with col2:
        always_available = (df['availability_365'] == 365).sum()
        st.metric("Always Available", f"{always_available:,}")
    with col3:
        never_available = (df['availability_365'] == 0).sum()
        st.metric("Never Available", f"{never_available:,}")
    with col4:
        high_availability = (df['availability_365'] >= 300).sum()
        st.metric("300+ Days", f"{high_availability:,}")

if __name__ == "__main__":
    main()
