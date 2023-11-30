import streamlit as st
import requests

from functions import fetch_pdf, append_text_to_pdf, find_string_coordinates

st.set_page_config(
    page_title="Gibilaro Design Info Sheet Maker",
    page_icon=":open_file_folder:",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image("images/logo.gif")
st.header(":open_file_folder: Info Sheet Maker")

# User input for the product URL
product_url = st.text_input(
    "Enter the product URL",
    # value="https://gibilarodesign.co.uk/shop/small-wrought-fire-basket-in-the-dutch-manner/",
)
text = st.text_area(
    "Enter the text to add",
    #   value="Price: $999\n(including installation)"
)
submit_button = st.button("Generate Information Sheet")

if product_url and submit_button:
    try:
        with st.spinner("Loading... "):
            pdf_bytes, file_name = fetch_pdf(product_url)

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching the PDF: {e}")
    else:
        text_to_append = text

        # the PDFs can be different lengths, so put the text relative to
        # additional information string
        x, y = find_string_coordinates(pdf_bytes, "Additional Information")

        x_position = x + 100
        y_position = y - 56

        # Append text to the PDF outside of the try block
        pdf_bytes = append_text_to_pdf(
            pdf_bytes, text_to_append, x_position, y_position
        )

        st.success("Information sheet created")
        # Display download button with the PDF file
        st.download_button(
            label="Download Information Sheet",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/octet-stream",
        )

        st.image(
            "images/jesse.jpg",
            caption="Gibilaro Design: Quality Fire Grates, made with love",
        )
