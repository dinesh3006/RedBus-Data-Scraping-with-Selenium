import pandas as pd # Imports the pandas library for data handling.
import streamlit as st # Imports the streamlit library for building the web app.
import mysql.connector # Imports the connector for MySQL database access.
import time # Imports the time module for delays.
import plotly.express as px # Imports Plotly for creating interactive charts.
from PIL import Image # Imports the Image module from PIL to handle images.

# --- MySQL Configuration and Utility Functions ---

# Use st.cache_resource for the connection object
# Caches the MySQL connection object so it's created only once.
@st.cache_resource
def get_connection():
    """Establishes and returns a MySQL connection to TiDB Cloud."""
    try:
        # Attempts to connect to the MySQL database.
        connection = mysql.connector.connect(
            host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com", # Database host.
            port=4000, # Database port.
            user="g174YAijTsGambu.root", # Database username.
            # **FINAL CORRECTED PASSWORD**
            password="0d3UU1fEGvra4Dez", # Database password.
            database="Bus_details" # Database name.
        )
        return connection # Returns the successful connection.
    except mysql.connector.Error as err:
        st.error(f"Error connecting to MySQL: {err}") # Shows an error if connection fails.
        return None # Returns None on failure.

# Load all data from the database
# Caches the data for 600 seconds (10 minutes) to avoid repeated queries.
@st.cache_data(ttl=600) 
def load_data_from_db():
    """Loads bus route data, cleans it, and prepares columns for filtering."""
    conn = get_connection() # Gets the cached database connection.
    if conn is None:
        st.warning("Failed to connect to the database. Displaying empty data.") # Shows warning if no connection.
        return pd.DataFrame() # Returns an empty DataFrame.

    try:
        with st.spinner('Loading data from database...'): # Displays a loading spinner.
            # **CORRECTED SQL QUERY**
            query = """
            SELECT 
                ID, Bus_Name, Bus_Type, Departure_Time, Destination_Time, 
                Total_Duration, Ratings, Price, Seats_Available, Route_name, Route_Link 
            FROM Bus_details.bus_routes 
            """ # SQL query to fetch all route details.
            df = pd.read_sql(query, conn) # Executes the query and loads data into a DataFrame.
            conn.close() # Closes the database connection.

            # --- Data Cleaning and Preparation ---
            
            # 1. Clean Time/Duration columns
            if 'Departure_Time' in df.columns:
                # Cleans the Departure_Time string to keep only the time part.
                df['Departure_Time'] = df['Departure_Time'].apply(lambda x: str(x)[-8:] if 'days' in str(x) else str(x))

            # 2. Ensure Price, Ratings, and Seats are numeric
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce') # Converts Price to numeric (NaN on error).
            df['Ratings'] = pd.to_numeric(df['Ratings'], errors='coerce') # Converts Ratings to numeric (NaN on error).
            # Converts Seats_Available to int, filling missing values with 0.
            df['Seats_Available'] = pd.to_numeric(df['Seats_Available'], errors='coerce').fillna(0).astype(int)
            
            df.dropna(subset=['Price', 'Ratings'], inplace=True) # Removes rows with missing Price or Ratings.
            
            # 3. **ROBUST ROUTE SPLITTING FIX**
            if 'Route_name' in df.columns:
                # Replaces common delimiters with ' -> ' for consistent splitting.
                df['Route_name'] = df['Route_name'].astype(str).str.replace(' - ', ' -> ', regex=False).str.replace('-', ' -> ', regex=False)
                
                # Splits the route name into Source and Destination, limiting to one split.
                split_cols = df['Route_name'].str.split(' -> ', expand=True, n=1)
                
                # Assign Source and Destination columns safely
                if split_cols.shape[1] >= 2:
                    df['Source_City'] = split_cols[0].str.strip() # Extracts and strips Source City.
                    df['Destination_City'] = split_cols[1].str.strip() # Extracts and strips Destination City.
                elif split_cols.shape[1] == 1:
                    df['Source_City'] = split_cols[0].str.strip() # Extracts Source City.
                    df['Destination_City'] = 'Unknown Destination' # Sets destination as unknown.
                else:
                    df['Source_City'] = 'Unknown Source' # Sets source as unknown.
                    df['Destination_City'] = 'Unknown Destination' # Sets destination as unknown.
                    
                df['Source_City'] = df['Source_City'].fillna('Unknown Source') # Fills any remaining NaN sources.
                df['Destination_City'] = df['Destination_City'].fillna('Unknown Destination') # Fills any remaining NaN destinations.
            else:
                df['Source_City'] = 'N/A' # Default source if column is missing.
                df['Destination_City'] = 'N/A' # Default destination if column is missing.

        return df # Returns the cleaned DataFrame.
    except Exception as e:
        st.error(f"Failed to load data from the database: {e}") # Shows error if loading/cleaning fails.
        return pd.DataFrame() # Returns an empty DataFrame on error.


# --- Streamlit Page Functions ---

def sign_in_page():
    """Handles the user sign-in/sign-up interface."""
    # Sets the main title using HTML for centering and styling.
    st.markdown(
        "<h1 style='text-align: center; color: #FF4500;'>Redbus Data Scraping Application🚌</h1>",
        unsafe_allow_html=True
    )
    
    # 1. Load the image
    image_path = 'C:\\Users\\hp\\OneDrive\\Pictures\\guvi certificates\\web-scraping using selenium\\Streamlit(Bus_details)\\red_bus.jpg' # Defines local image path.
    image = Image.open(image_path) # Opens the image using PIL.
    
    # 2. Center the image using columns and set a fixed width (e.g., 350px)
    col_empty1, col_img, col_empty2 = st.columns([1, 2, 1]) # Creates columns to center the image.
    with col_img:
        st.image(image, width=680) # Displays the image with a fixed width.
    
    # --- Centered Subheader ---
    st.markdown("<h3 style='text-align: center;'>Sign In</h3>", unsafe_allow_html=True) # Centers the Sign In subheader.
    
    # --- Smaller Input Boxes ---
    col_left, col_form, col_right = st.columns([1, 1, 1]) # Creates columns to center the input form.
    
    with col_form:
        name = st.text_input("Name:", "Dinesh V", key="username_input") # Text input for name.
        password = st.text_input("Password:", "Dinesh@3006", type="password", key="password_input") # Password input, masked.
        
        col_btn_in, col_btn_up = st.columns(2) # Columns to align sign-in/sign-up buttons.
        
        with col_btn_in:
            if st.button("Sign In"): # Sign In button logic.
                if name == "Dinesh V" and password == "Dinesh@3006": # Checks credentials.
                    st.session_state["signed_in"] = True # Sets session state to signed in.
                    st.success("Signed in successfully!") # Shows success message.
                    time.sleep(1) # Pauses briefly.
                    st.rerun() # Reruns the app to navigate to the main page.
                else:
                    st.error("Invalid Name or Password") # Shows error on bad credentials.
        with col_btn_up:
            st.button("Sign Up") # Sign Up button (no functionality).


def home_page():
    # Sets custom CSS for background, text, and an animated header.
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("file:///C:/Users/hp/OneDrive/Pictures/guvi%20certificates/web-scraping%20using%20selenium/Streamlit(Bus_details)/Plain-white-background-image.jpg");
            background-size: cover;
        }
        .content {
            background-color: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 10px;
            color: #000000;
            font-weight: bold;
        }
        .centered-text {
            text-align: center;
            color: #000000;
            font-size: 2em;
            font-weight: bold;
            animation: vertical-move 3s linear infinite;
        }
        h4 {
            color: #FF4500;
        }
        p, ul {
            color: #000000;
        }
        h2, h3 {
            color: #FF4500;
        }
        @keyframes vertical-move {
            0% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
            100% { transform: translateY(0); }
        }
        </style>
        <div class="content">
            <div class="centered-text">
                <h2 style="text-align:center;">Redbus Data Scraping with Selenium & Dynamic Filtering using Streamlit</h2>
                <h3 style="text-align:center;">Domain: Transportation</h3>
            </div>
            <div>
            <h4>Objectives:</h4>
            <ul>
                <li>Automate Data Collection: Use Selenium to scrape bus data from Redbus, including routes, schedules, prices, and seat availability.</li>
                <li>Store Data Efficiently: Save the scraped data in a SQL database with a well-structured schema.</li>
                <li>Develop a Streamlit App: Create an interactive Streamlit application for visualizing and filtering bus data.</li>
                <li>Implement Filters: Allow users to filter data by bus type, route, price range, star rating, and seat availability.</li>
                <li>Ensure Usability: Make the application user-friendly and responsive to enhance the overall user experience.</li>
                <li>Analyze and Report: Evaluate the accuracy of data scraping, effectiveness of the database, and usability of the application.</li>
            </ul>
            <h4>Overview:</h4>
            <p>The project aims to enhance the transportation industry by using Selenium to automatically collect detailed bus travel data from Redbus, such as routes, schedules, prices, and seat availability. This data will be stored in a SQL database and visualized through a Streamlit application. Users will be able to filter and analyze the data easily. The goal is to provide a comprehensive tool for improving operational efficiency, market analysis, and customer service in the transportation sector.</p>
        </div>
        </div>
        """,
        unsafe_allow_html=True # Allows rendering of HTML/CSS.
    )


def bus_routes_page_mysql():
    """Displays the data table with dynamic sidebar filters, using whole numbers for the Ratings filter."""
    st.title("🚌 Bus Routes Explorer") # Page title.
    st.markdown("Use the sidebar filters to refine the list of available bus routes.") # Instructions.

    df = load_data_from_db() # Loads the bus data.

    if df.empty:
        return # Stops if data is empty.

    # --- Sidebar Filters ---
    st.sidebar.header("Filter Options") # Sidebar header.

    # 1. Route Filter (Source City)
    all_source = sorted(df['Source_City'].unique()) # Gets unique source cities.
    selected_source = st.sidebar.selectbox("Source City", ["All"] + list(all_source)) # Source city filter.
    
    # 2. Bus Operator Filter
    all_operators = sorted(df['Bus_Name'].unique()) # Gets unique operator names.
    selected_operator = st.sidebar.selectbox("Bus Operator", ["All"] + list(all_operators)) # Operator filter.

    # 3. Bus Type Filter
    bus_types = sorted(df['Bus_Type'].unique()) # Gets unique bus types.
    selected_bus_type = st.sidebar.selectbox("Bus Type", ["All"] + list(bus_types)) # Bus type filter.

    # 4. Price Range Filter
    min_p, max_p = df['Price'].min(), df['Price'].max() # Gets min/max price.
    price_range = st.sidebar.slider(
        "Price Range (₹)", min_value=float(min_p), max_value=float(max_p), 
        value=(float(min_p), float(max_p)), step=50.0 # Price range slider.
    )

    # 5. Rating Filter (MODIFIED FOR WHOLE NUMBER SLIDER)
    min_rating_ui = int(df['Ratings'].min() // 1) # Calculates min integer rating.
    max_rating_ui = int(df['Ratings'].max() // 1) + 1 # Calculates max integer rating (rounded up).
    
    min_rating_ui = max(1, min_rating_ui) # Ensures min rating is at least 1.
    max_rating_ui = min(5, max_rating_ui) # Ensures max rating is at most 5.
    
    rating_cutoff = st.sidebar.slider(
        "Minimum Rating (Stars)", 
        min_value=0.0,   # Set minimum to 0
        max_value=5.0,   # Set maximum to 5
        value=0.0,       # Set default value to 0 (shows all buses)
        step=1.0         # Step by 1.0 (whole numbers)
    )

    # 6. Seats Available Filter
    seats_filter = st.sidebar.checkbox("Show only buses with seats available", value=False) # Checkbox filter for seats.
    
    # --- Apply Filters ---
    filtered_df = df.copy() # Starts with a copy of the data.

    # Applies Source City Filter
    if selected_source != "All":
        filtered_df = filtered_df[filtered_df['Source_City'] == selected_source]

    # Applies Bus Operator Filter
    if selected_operator != "All":
        filtered_df = filtered_df[filtered_df['Bus_Name'] == selected_operator]
    
    # Applies Bus Type Filter
    if selected_bus_type != "All":
        filtered_df = filtered_df[filtered_df['Bus_Type'] == selected_bus_type]
    
    # Applies Price Filter
    filtered_df = filtered_df[
        (filtered_df['Price'] >= price_range[0]) & (filtered_df['Price'] <= price_range[1])
    ]
    
    # Applies Rating Filter
    filtered_df = filtered_df[filtered_df['Ratings'] >= rating_cutoff]
    
    # Applies Seats Filter
    if seats_filter:
        filtered_df = filtered_df[filtered_df['Seats_Available'] > 0] # Filters for buses with > 0 seats.

    # --- Display Results ---
    st.header(f"Total Buses Found: {len(filtered_df)}") # Displays the count of results.
    
    if filtered_df.empty:
        st.warning("No buses match the current filter criteria.") # Warning if no buses match filters.
    else:
        # Define the professional column order
        professional_columns = [
            'Route_name', 
            'Bus_Name', 
            'Bus_Type', 
            'Departure_Time', 
            'Destination_Time', 
            'Total_Duration', 
            'Price', 
            'Ratings', 
            'Seats_Available' 
        ] 
                
        # Selects columns and renames one for display.
        display_df = filtered_df[professional_columns].rename(columns={'Bus_Name': 'Bus Operator'})

        st.dataframe(
            display_df,
            use_container_width=True # Displays the filtered data table.
        )


def charts_page():
    """Displays professional and attractive data visualizations using Plotly."""
    st.title("📈 Data Visualization & Analysis") # Page title.
    st.markdown("Explore key trends and insights from the Redbus data through interactive charts.") # Instructions.

    df = load_data_from_db() # Loads the data.
    
    if df.empty:
        st.warning("No data available to generate charts. Please check the database connection or filters.")
        return # Stops if data is empty.

    # --- Chart 1: Price Distribution by Bus Type ---
    st.subheader("Price Distribution by Bus Type 💰") # Subheader for chart 1.
    st.markdown("Understanding how prices vary across different bus types.")
    
    try:
        # Creates an interactive box plot for price distribution.
        fig_price = px.box(
            df, 
            x='Bus_Type', 
            y='Price', 
            color='Bus_Type', 
            title='<b>Bus Ticket Price Distribution by Bus Type</b>',
            labels={'Bus_Type': 'Bus Type', 'Price': 'Ticket Price (₹)'},
            color_discrete_sequence=px.colors.qualitative.Pastel, 
            hover_name="Bus_Name" 
        )
        # Updates layout for better appearance.
        fig_price.update_layout(
            xaxis_title="Bus Type",
            yaxis_title="Price (₹)",
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)', 
            font=dict(family="Arial", size=12, color="#333"),
            hovermode="x unified", 
            margin=dict(l=40, r=40, t=80, b=40)
        )
        fig_price.update_traces(marker_line_width=1, marker_line_color='black') # Adds border to boxes.
        st.plotly_chart(fig_price, use_container_width=True) # Displays chart 1.
    except Exception as e:
        st.error(f"Error generating Price Distribution chart: {e}")

    st.markdown("---") # Separator.

    # --- Chart 2: Average Rating per Bus Operator (Top 10) ---
    st.subheader("Top Bus Operators by Average Rating ⭐") # Subheader for chart 2.
    st.markdown("See which operators are highly rated by passengers.")

    try:
        valid_ratings_df = df.dropna(subset=['Ratings']) # Filters out rows with missing ratings.
        # Calculates average rating per operator, sorted descending.
        avg_rating_operator = valid_ratings_df.groupby('Bus_Name')['Ratings'].mean().sort_values(ascending=False).reset_index()
        
        top_n_operators = avg_rating_operator.head(10) # Takes the top 10.

        # Creates a bar chart for top operator ratings.
        fig_rating = px.bar(
            top_n_operators, 
            x='Bus_Name', 
            y='Ratings', 
            color='Ratings', 
            title='<b>Top 10 Bus Operators by Average Customer Rating</b>',
            labels={'Bus_Name': 'Bus Operator', 'Ratings': 'Average Rating (Stars)'},
            color_continuous_scale=px.colors.sequential.Sunsetdark, 
            text='Ratings' 
        )
        fig_rating.update_traces(texttemplate='%{text:.2s}', textposition='outside') # Formats text on bars.
        # Updates layout for better appearance.
        fig_rating.update_layout(
            xaxis_title="Bus Operator",
            yaxis_title="Average Rating",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12, color="#333"),
            hovermode="x unified",
            margin=dict(l=40, r=40, t=80, b=40)
        )
        # Adjusts Y-axis limits dynamically.
        fig_rating.update_yaxes(range=[valid_ratings_df['Ratings'].min() * 0.9, valid_ratings_df['Ratings'].max() * 1.1]) 
        st.plotly_chart(fig_rating, use_container_width=True) # Displays chart 2.
    except Exception as e:
        st.error(f"Error generating Average Rating chart: {e}")

    st.markdown("---") # Separator.

    # --- Chart 3: Count of Buses by Route (Top 10) ---
    st.subheader("Most Popular Bus Routes 🗺️") # Subheader for chart 3.
    st.markdown("See the routes with the highest number of available buses.")

    try:
        route_counts = df['Route_name'].value_counts().head(10).reset_index() # Counts top 10 routes.
        route_counts.columns = ['Route_name', 'Count'] # Renames columns.
        
        # Creates a donut chart for route frequency.
        fig_routes = px.pie(
            route_counts, 
            values='Count', 
            names='Route_name',
            title='<b>Top 10 Most Frequent Bus Routes</b>',
            color_discrete_sequence=px.colors.sequential.RdBu, 
            hole=0.3 # Makes it a donut chart.
        )
        # Sets text to show percentage and label, and 'explodes' the largest slice.
        fig_routes.update_traces(
            textinfo='percent+label', 
            pull=[0.05 if i == route_counts['Count'].idxmax() else 0 for i in range(len(route_counts))] 
        )
        # Updates layout for better appearance.
        fig_routes.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12, color="#333"),
            margin=dict(l=40, r=40, t=80, b=40),
            showlegend=True,
            legend_title_text="Routes"
        )
        st.plotly_chart(fig_routes, use_container_width=True) # Displays chart 3.
    except Exception as e:
        st.error(f"Error generating Route Count chart: {e}")


# --- Main Execution ---

def main():
    """Main function to run the Streamlit application."""
    # Sets page configuration (title, layout, sidebar state).
    st.set_page_config(page_title="Redbus Dashboard", layout="wide", initial_sidebar_state="expanded")

    if "signed_in" not in st.session_state:
        st.session_state["signed_in"] = False # Initializes the signed_in status.

    if not st.session_state["signed_in"]:
        sign_in_page() # Shows sign-in page if not signed in.
    else:
        st.sidebar.header("Navigation") # Sidebar header for navigation.
        if st.sidebar.button("Sign Out"): # Sign Out button logic.
            st.session_state["signed_in"] = False # Resets signed_in status.
            st.rerun() # Reruns to show sign-in page.

        page = st.sidebar.selectbox("Select Page", ["Home", "Bus Routes", "Charts"]) # Page selector.
            
        if page == "Home":
            home_page() # Shows the Home page.
        elif page == "Bus Routes":
            bus_routes_page_mysql() # Shows the Bus Routes page with filters.
        elif page == "Charts":
            charts_page() # Shows the Charts page.


if __name__ == "__main__":

    main() # Executes the main function when the script starts.
