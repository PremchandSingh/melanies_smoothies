# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
# from snowflake.snowpark.context import get_active_session
import requests
import pandas as pd_df

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

my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'),col ('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)

# ----------comment

pd_df= my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'choose up to 5 ingredients'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:
    ingredients_string =''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen +'Nutrition information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+fruit_chosen)
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
                
    # st.write(ingredients_string)
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    st.write(my_insert_stmt)
    # st.stop()
    time_to_insert = st.button('Submit Order')

    if ingredients_string:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")



# st.text(smoothiefroot_response.json())
    





