from time import sleep

import streamlit as st
import pandas as pd

from src.pages.base import BasePage
from src.utils.db import Campaign, Customer, CustomerProfile, FinalTarget


class SimulationPage(BasePage):
    def run_simulation(self, simulation_start_date, simulation_end_date):
        FinalTarget.clear_final_targets()
        for current_date in pd.date_range(simulation_start_date, simulation_end_date):
            current_active_campaigns = Campaign.get_active_campaigns(current_date)
            for campaign_type in current_active_campaigns['campaign_type'].unique():
                st.write(
                    f"""
                    # :arrow_forward: {current_date.date()}
                    """
                )
                st.write(
                    f"""
                    ## :four_leaf_clover: {current_date.date()} tarihindeki {campaign_type} Kampanyaları:
                    """
                )
                campaign_type_campaigns = current_active_campaigns[
                    current_active_campaigns['campaign_type'] == campaign_type]
                st.dataframe(campaign_type_campaigns)
                for index, campaign in campaign_type_campaigns.iterrows():
                    profile_result = CustomerProfile.get_profile_result(campaign['campaign_profile'], current_date)
                    st.write(
                        f"""
                        ### :sparkle: {campaign['name']} için {current_date} tarihinde oluşan profil aşağıdaki gibidir:
                        """
                    )
                    st.dataframe(profile_result)

                    if profile_result is None:
                        st.error(
                            f"""
                            ### :sparkle: {campaign['name']} için {campaign['campaign_profile']} profil tanımlı değil.
                            """
                        )
                        continue

                    next_day, next_result = CustomerProfile.get_next_day_profile_result(
                        campaign['campaign_profile'],
                        current_date
                    )
                    if next_day != 0:
                        st.write(
                            f"""
                            ### :sparkle: {campaign['name']} için önümüzdeki {next_day} gün içinde oluşacak profil aşağıdaki gibidir:
                            """
                        )
                        st.dataframe(next_result)

                    final_df = profile_result if next_result is None else pd.concat([profile_result, next_result])
                    st.write(
                        f"""
                        ### :sparkle: Aktif kampanya tanımı bulunan kişiler çıkarıldıktan sonra {campaign['name']} için oluşan profil aşağıdaki gibidir:
                        """
                    )
                    active_targets = FinalTarget.get_active_targets(current_date)
                    final_df = final_df[~final_df['id'].isin(active_targets['customer_id'])]
                    st.dataframe(final_df)

                    all_targets = FinalTarget.save_final_target(final_df, campaign)
                    st.write(f"""
                        :earth_asia: Final Hedef Tablo:
                    """)
                    st.dataframe(all_targets)

            # Separate days with a line
            sleep(5)
            st.write("---")

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
