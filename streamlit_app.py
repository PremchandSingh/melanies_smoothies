# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Streamlit app title
st.title("Example Streamlit App :balloon:")
st.write("Choose the fruit you want in your custom smoothie!")

# Input field for smoothie name
name_on_order = st.text_input("Name of the smoothie:")
st.write("Name of the smoothie will be: ", name_on_order)

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multi-select dropdown for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients',
    pd_df['FRUIT_NAME'].tolist(),  # Ensure we pass the correct list of fruit names
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)  # Combine ingredients into a string

    # Retrieve corresponding SEARCH_ON values
    search_values = [
        pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        for fruit in ingredients_list
    ]

    # Display nutrition information
    for fruit_chosen, search_on in zip(ingredients_list, search_values):
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Display the SQL insert statement
    st.write(my_insert_stmt)

    # Submit Order Button
    if "order_submitted" not in st.session_state:
        st.session_state.order_submitted = False

    if st.button('Submit Order') and not st.session_state.order_submitted:
        session.sql(my_insert_stmt).collect()  # Execute insert query
        st.session_state.order_submitted = True  # Mark as submitted
        st.success('Your Smoothie is ordered!', icon="✅")
