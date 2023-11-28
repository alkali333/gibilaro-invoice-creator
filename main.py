import streamlit as st
import requests

from functions import fetch_pdf, append_text_to_pdf

st.set_page_config(
    page_title="Gibilaro Design Invoice Creator",
    page_icon=":open_file_folder:",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image("images/logo.gif")
st.header(":open_file_folder: Invoice Creator")

# User input for the product URL
product_url = st.text_input(
    "Enter the product URL",
    value="https://gibilarodesign.co.uk/shop/small-wrought-fire-basket-in-the-dutch-manner/",
)
text = st.text_area(
    "Enter the text to add", value="Price: $999\n(including installation)"
)
submit_button = st.button("Get Invoice")

if product_url and submit_button:
    try:
        with st.spinner("Loading... "):
            pdf_bytes, file_name = fetch_pdf(product_url)

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching the PDF: {e}")
        # Additional error handling can go here
    else:
        # Specify the text and position here (you can adjust x and y as needed)
        text_to_append = text
        x_position = 300
        y_position = 250

        # Append text to the PDF outside of the try block
        pdf_bytes = append_text_to_pdf(
            pdf_bytes, text_to_append, x_position, y_position
        )

        # Display download button with the PDF file
        st.download_button(
            label="Download Invoice",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/octet-stream",
        )

        # st.image(
        #     "images/jesse.jpg",
        #     caption="Gibilaro Design: Quality Fire Grates, made with love",
        # )