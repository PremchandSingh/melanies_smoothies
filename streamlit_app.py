# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
# from snowflake.snowpark.context import get_active_session

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)

# cnx = st.connection("Snowflake")
# session =cnx.session()

# Write directly to the app
st.title("Example Streamlit App :balloon:")
st.write(
    f""" Choose the fruit you want in your custom smootihie!    
    """
)

name_on_order = st.text_input("Name of the smoothie:")
st.write("Name of the smoothie will be: ", name_on_order)
   
# session = get_active_session()

cnx = st.connection("snowflake")
session =cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'))
# st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'choose up to 5 ingredients'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:

    ingredients_string =''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    

    st.write(my_insert_stmt)
    # st.stop()
    time_to_insert = st.button('Submit Order')

    if ingredients_string:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

    





