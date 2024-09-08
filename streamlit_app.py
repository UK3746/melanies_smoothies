import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests

# Define your Snowflake connection parameters
connection_parameters = {
    "account": "JPSGWSJ-OXB72419",
    "user": "UK",
    "password": "myBestRM@12345",
    "role": "SYSADMIN",
    "warehouse": "COMPUTE_WH",
    "database":  "SMOOTHIES",
    "schema":  "PUBLIC"
}

# Initialize Snowpark session
@st.cache_resource
def create_session():
    return Session.builder.configs(connection_parameters).create()

session = create_session()

# Streamlit app components
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

try:
    # Fetch data from Snowflake
    my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
    st.dataframe(data=my_dataframe.to_pandas(), use_container_width=True)

    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        options=my_dataframe.to_pandas()["FRUIT_NAME"].tolist(),
        max_selections=5
    )
    
    if ingredients_list:
        ingredients_string = ', '.join(ingredients_list)
        st.subheader(ingredients_list + 'Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/ingredients_list")
        #st.text(fruityvice_response.json())
        fv_df = st.dataframe(data=fruityvice_response.json(),use_container_width=True)
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
        """
       

        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
            
except Exception as e:
    st.error(f"An error occurred: {e}")
