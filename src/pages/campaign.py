import streamlit as st

from src.utils.db import Campaign, CustomerProfile


class CampaignPage:
    def show(self):
        st.title("Kampanya Tanımlama & Önceliklendirme Ekranı")

        # Form to get the user input
        with st.form(key="kampanya_form"):
            campaign_name = st.text_input("Kampanya Adı")
            start_date = st.date_input("Başlangıç Tarihi")
            end_date = st.date_input("Bitiş Tarihi")
            order = st.number_input("Öncelik", min_value=1, max_value=1000, value=3)
            campaign_type = st.selectbox(
                "Kategori", ["akaryakıt", "market", "akaryakıt+market"]
            )
            campaign_profile = st.selectbox("Hedef Kitle", CustomerProfile.get_all_profiles()['name'].tolist())

            submit_button = st.form_submit_button(label="Kampanya Oluştur")
            if submit_button:
                try:
                    Campaign.create(
                        name=campaign_name,
                        start_date=start_date,
                        end_date=end_date,
                        campaign_order=order,
                        campaign_type=campaign_type,
                        campaign_profile=campaign_profile
                    )
                except Exception as e:
                    st.error(f"Error creating: {e}")

        # List of existing kampanyalar
        st.subheader("Mevcut Kampanyalar")
        campaign_df = Campaign.get_all_campaigns()
        st.dataframe(campaign_df)

