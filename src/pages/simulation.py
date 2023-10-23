from time import sleep

import streamlit as st
import pandas as pd

from src.pages.base import BasePage
from src.utils.db import Campaign, Customer


class SimulationPage(BasePage):
    def run_simulation(self, simulation_start_date, simulation_end_date):
        result = {}
        for current_date in pd.date_range(simulation_start_date, simulation_end_date):
            st.write(f"## {current_date.date()}")
            st.write(
                f"""
                ### {current_date.date()} tarihindeki kampanyalar:
                """
            )
            current_campaigns = Campaign.get_active_campaigns(current_date)
            st.dataframe(current_campaigns)
            result[current_date.date()] = {}
        print(result)

    def show(self):
        all_campaigns = Campaign.get_all_campaigns()
        if len(all_campaigns) == 0:
            st.error(
                "Tanımlı kampanya bulunamadı. Lütfen kampanya tanımlama sayfasından kampanya tanımlayınız."
            )
            return
        st.write(
            """
                 # Kampanya Önceliği Simülasyonu
                 ## Mevcut Kampanyalar:
                 """
        )
        st.dataframe(all_campaigns)
        st.write(
            """
                 # Kampanya Önceliği Simülasyonu
                 ## Mevcut Müşteri Veritabanı:
                 """
        )
        st.dataframe(Customer.get_all_customers())

        simulation_start_date = all_campaigns['start_date'].min()
        simulation_end_date = all_campaigns['end_date'].max()
        st.write(
            f"""
                    - Simülasyon başlangıç Tarihi: {simulation_start_date}
                    (Kampayaların başlangıç tarihleri arasında en erken olanı)

                    - Simülasyon bitiş Tarihi: {simulation_end_date}
                    (Kampayaların bitiş tarihleri arasında en geç olanı)
                    
                """
        )
        # Simülasyon başlat butonu
        if st.button("Simülasyonu Başlat"):
            self.run_simulation(simulation_start_date, simulation_end_date)
