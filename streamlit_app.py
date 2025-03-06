import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd_df

st.title("Example Streamlit App :balloon:")
st.write("Choose the fruit you want in your custom smoothie!")

name_on_order = st.text_input("Name of the smoothie:")
st.write("Name of the smoothie will be: ", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'choose up to 5 ingredients',
    pd_df['FRUIT_NAME'].tolist(),  # Use pandas Series to get the list
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    st.write(f"Ingredients chosen: {ingredients_string}")

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(fruit_chosen + ' Nutrition information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        try:
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except Exception as e:
            st.error(f"Error fetching nutrition data for {fruit_chosen}: {e}")

    time_to_insert = st.button('Submit Order')

    if time_to_insert:  # Only execute when the button is pressed
        if ingredients_string and name_on_order:
            my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            try:
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie is ordered!', icon="✅")
            except Exception as e:
                st.error(f"Error inserting order: {e}")
        else:
            st.warning("Please enter a name and select ingredients.")
