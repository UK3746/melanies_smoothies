import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests
import pandas as pd_df

# Define Snowflake connection parameters
connection_parameters = {
    "account": "JPSGWSJ-OXB72419",
    "user": "UK",
    "password": "myBestRM@12345",
    "role": "SYSADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SMOOTHIES",
    "schema": "SMOOTHIES.PUBLIC"
}

# Function to create and cache Snowpark session
@st.cache_resource
def create_session():
    return Session.builder.configs(connection_parameters).create()

# Create Snowpark session
session = create_session()

# Streamlit app components
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

try:
    # Fetch data from Snowflake
    my_DataFrame = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col("SEARCH_ON")).to_pandas()
    st.my_DataFrame(data=my_DataFrame, use_container_width=True)

    pd_df = my_DataFrame.to_pandas()
    
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        options=my_DataFrame["FRUIT_NAME"].tolist(),
        max_selections=5
    )
    
    if ingredients_list:
        ingredients_string = ', '.join(ingredients_list)
        
        for fruit in ingredients_list:

             search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
             st.write('The search value for ', fruit,' is ', search_on, '.')

             st.subheader(f'{fruit} Nutrition Information')
             # Handle Fruityvice API request
             try:
                fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit}")
                fruit_info = fruityvice_response.json()
                # Display API response as a dataframe
                fruit_df = pd.DataFrame(fruit_info, index=[0])
                st.dataframe(fruit_df, use_container_width=True)
             except requests.RequestException as e:
                st.error(f"Failed to fetch data for {fruit}: {e}")

    # SQL insert statement
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """
    
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Failed to place order: {e}")

except Exception as e:
    st.error(f"An error occurred: {e}")
