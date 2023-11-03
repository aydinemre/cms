import streamlit as st

from src.pages.page_factory import pages


def main():
    # Define sidebar
    st.sidebar.title("Kampanya Önceliklendirme Simülasyonu")
    page = st.sidebar.selectbox("Sayfa Seçiniz", list(pages.keys()), index=2)
    pages[page].show()


if __name__ == "__main__":
    main()
