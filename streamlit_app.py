import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Snowflake connection parameters
snowflake_config = {
    "account": "<your_account>",
    "user": "<your_username>",
    "password": "<your_password>",
    "role": "<your_role>",
    "warehouse": "<your_warehouse>",
    "database": "<your_database>",
    "schema": "<your_schema>"
}

# Initialize Snowflake session
session = Session.builder.configs(snowflake_config).create()

# Streamlit app code
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

# User input for the smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Load fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
st.dataframe(data=my_dataframe.to_pandas(), use_container_width=True)

# Convert Snowflake dataframe to pandas dataframe
pd_df = my_dataframe.to_pandas()

# User selects ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get search value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        # Fetch and display nutrition information
        st.subheader(fruit_chosen + ' Nutrition Information')
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
            fruityvice_response.raise_for_status()  # Raise error for bad responses
            fv_data = fruityvice_response.json()
            st.json(fv_data)
        except requests.RequestException as e:
            st.error(f"Error fetching nutrition information for {fruit_chosen}: {e}")

# Prepare SQL statement to insert order
my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                     VALUES (%s, %s)"""

# Handle order submission
if st.button('Submit Order'):
    try:
        session.sql(my_insert_stmt, (ingredients_string, name_on_order)).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
    except Exception as e:
        st.error(f"Error submitting order: {e}")
