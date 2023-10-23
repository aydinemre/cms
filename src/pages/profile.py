import pandas as pd
import streamlit as st

from src.pages.base import BasePage
from src.utils.db import Customer, CustomerProfile


class ProfilePage(BasePage):
    def show(self):
        st.title("Profil Tanımlama Ekranı")

        # Show the list of customers
        st.subheader("'customers' Veritabanı")
        st.dataframe(Customer.get_all_customers())

        # Create a new customer and show the list of customers
        st.subheader("Yeni Profil Ekle")
        profile_name = st.text_input("Profil Adı:")
        sql_code = st.text_area("SQL Kodu:")
        profile_type = st.selectbox("Tanımlama Tipi:", ["dinamik", "statik"])
        profile_exclusion_period = st.number_input(
            "Bu müşteri kitlesine bir kampanya uygulanmadan önceki kaç gün "
            "boyunca başka bir kampanya uygulanmamalıdır?(gün):", min_value=0, max_value=365, value=0
        )
        schedule_day = st.number_input(
            "Çalışma Frekansı(gün):", min_value=1, max_value=365, value=7
        )

        if st.button("Test Et ve Ekle"):
            # Check if the profile name is already in the database
            if CustomerProfile.check_profile_name(profile_name):
                st.error(f"'{profile_name}' zaten mevcut. Lütfen başka bir ad girin.")
                return
            sonuc, hata = Customer.execute_sql(sql_code)
            if hata is None:
                displayed_sonuc = sonuc
                if profile_type == "dinamik":
                    sonuc = None
                if profile_type == "statik":
                    profile_exclusion_period = None
                    schedule_day = None
                if CustomerProfile.create_profile(
                    name=profile_name,
                    sql_code=sql_code,
                    profile_type=profile_type,
                    profile_exclusion_period=profile_exclusion_period,
                    schedule_day=schedule_day,
                    query_result=sonuc,
                ):
                    st.success(f"'{profile_name}' başarıyla eklendi!")
                    st.dataframe(displayed_sonuc)
                else:
                    st.error(f"'{profile_name}' zaten mevcut. Lütfen başka bir ad girin.")
            else:
                st.error(f"SQL Hatası: {hata}")

        # Eski profil tanımlamalarını göster
        st.subheader("Eski Tanımlamalar")
        profiles = CustomerProfile.get_all_profiles()
        for index, profile in profiles.iterrows():
            if st.button(f"Sil - {profile['name']}"):
                CustomerProfile.delete_by_name(profile["name"])
                st.success(f"{profile['name']} silindi!")

        profiles = CustomerProfile.get_all_profiles()
        st.dataframe(profiles)
