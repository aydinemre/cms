import sqlite3

import pandas as pd


class DatabaseManager:
    def __init__(self):
        self.conn_customers = sqlite3.connect("db/customers.db", check_same_thread=False)
        self.conn_profile = sqlite3.connect("db/profiles.db", check_same_thread=False)
        self.conn_campaign = sqlite3.connect("db/campaigns.db", check_same_thread=False)
        self.conn_final_target = sqlite3.connect("db/final_target.db", check_same_thread=False)

        self.create_tables()

    def create_tables(self):
        # Create table for customers
        self.conn_customers.execute(
            """
        CREATE TABLE IF NOT EXISTS customers (
            _id INTEGER PRIMARY KEY,
            customer_name TEXT,
            last_name TEXT,
            age INTEGER,
            gender TEXT,
            birthday DATE,
            city TEXT,
            phone TEXT,
            sms_permission INTEGER,
            push_permission INTEGER
        )
        """
        )
        self.conn_customers.commit()

        # Create table for profiles
        self.conn_profile.execute(
            """
        CREATE TABLE IF NOT EXISTS profiles (
            profile_name TEXT PRIMARY KEY,
            sql_code TEXT,
            profile_type TEXT,
            result TEXT,
            gun_degeri INTEGER
        )
        """
        )
        self.conn_profile.commit()

        # Create table for campaigns
        self.conn_campaign.execute(
            """
        CREATE TABLE IF NOT EXISTS kampanyalar (
            ad TEXT PRIMARY KEY,
            baslangic_tarihi DATE,
            bitis_tarihi DATE,
            oncelik INTEGER,
            kategori TEXT,
            hedef_kitle TEXT
        )
        """
        )
        self.conn_campaign.commit()

        # Create table for final target audience
        self.conn_final_target.execute(
            """
                CREATE TABLE IF NOT EXISTS final_hedef_kitle (
                    _id INTEGER PRIMARY KEY,
                    MUSTERI_ID INTEGER,
                    MUSTERI_AD TEXT,
                    KITLE_AD TEXT,
                    FAYDA_TUR TEXT,
                    TARIH DATE,
                    BASLANGIC_TARIHI DATE,
                    BITIS_TARIHI DATE
                )
                    
            """
        )
        self.conn_final_target.commit()

    def close(self):
        self.conn_customers.close()
        self.conn_profile.close()
        self.conn_campaign.close()

    def get_kampanyalar(self):
        all_campaigns = pd.read_sql_query(
            "SELECT * FROM kampanyalar", self.conn_campaign
        )
        all_campaigns["baslangic_tarihi"] = pd.to_datetime(
            all_campaigns["baslangic_tarihi"]
        )

        all_campaigns["bitis_tarihi"] = pd.to_datetime(all_campaigns["bitis_tarihi"])

        return all_campaigns.sort_values(by=["kategori", "oncelik", "bitis_tarihi"])

    def get_active_campaigns(self, current_date=pd.Timestamp.now()):
        all_campaigns = self.get_kampanyalar()
        return (
            all_campaigns[all_campaigns.bitis_tarihi >= current_date]
            .sort_values(by=["kategori", "oncelik", "bitis_tarihi"])
            .reset_index(drop=True)
        )

    def get_tanimlamalar(self):
        return pd.read_sql_query(
            "SELECT ad FROM tanimlamalar", self.conn_profile
        ).ad.tolist()

    def get_final_hedef_kitle(self):
        df = pd.read_sql_query(
            "SELECT * FROM final_hedef_kitle", self.conn_final_target
        )

        df["TARIH"] = pd.to_datetime(df["TARIH"])
        df["BASLANGIC_TARIHI"] = pd.to_datetime(df["BASLANGIC_TARIHI"])
        df["BITIS_TARIHI"] = pd.to_datetime(df["BITIS_TARIHI"])
        return df

    def get_hedef_kitle_tanimi_with_name(self, hedef_kitle_adi):
        return pd.read_sql_query(
            f"SELECT * FROM tanimlamalar WHERE ad='{hedef_kitle_adi}'",
            self.conn_profile,
        ).iloc[0]

    def get_hedef_kitle(self, hedef_kitle_adi, run_date=pd.Timestamp.now()):
        hedef_kitle_tanimi = self.get_hedef_kitle_tanimi_with_name(hedef_kitle_adi)
        # Execute SQL code
        if hedef_kitle_tanimi.tip == "dinamik":
            hedef_kitle = pd.read_sql_query(
                hedef_kitle_tanimi.sql_kodu, self.conn_customers
            )
        else:
            hedef_kitle = pd.read_json(hedef_kitle_tanimi.statik_sonuc)

        return hedef_kitle

    def get_all_customers(self):
        return pd.read_sql_query("SELECT * FROM musteriler", self.conn_customers)

    def add_final_hedef_kitle(self, hedef_kitle, hedef_kitle_tanimi, campaign, date):
        hedef_kitle_df = pd.DataFrame()
        hedef_kitle_df["MUSTERI_AD"] = hedef_kitle["isim"]
        hedef_kitle_df["MUSTERI_ID"] = hedef_kitle["_id"]

        hedef_kitle_df["KITLE_AD"] = hedef_kitle_tanimi["ad"]

        hedef_kitle_df["TARIH"] = date
        hedef_kitle_df["BASLANGIC_TARIHI"] = campaign.baslangic_tarihi
        hedef_kitle_df["BITIS_TARIHI"] = campaign.bitis_tarihi
        hedef_kitle_df["KITLE_AD"] = campaign.hedef_kitle
        hedef_kitle_df["FAYDA_TUR"] = campaign.kategori

        current_final_hedef_kitle = self.get_final_hedef_kitle()
        customer_exists_query = hedef_kitle_df.MUSTERI_ID.isin(
            current_final_hedef_kitle.MUSTERI_ID.tolist()
        )
        not_exists_hedef_kitle = hedef_kitle_df[~customer_exists_query]
        existing_hedef_kitle = hedef_kitle_df[customer_exists_query]
        existing_hedef_kitle = existing_hedef_kitle[
            existing_hedef_kitle.BITIS_TARIHI <= date
            ]
        pd.concat([not_exists_hedef_kitle, existing_hedef_kitle]).to_sql(
            "final_hedef_kitle",
            self.conn_final_target,
            if_exists="append",
            index=False,
        )

    # SQL kodunu çalıştırma
    def execute_sql(self, sql_kodu):
        try:
            return pd.read_sql_query(sql_kodu, db_manager.conn_customers), None
        except Exception as e:
            return None, str(e)


db_manager = DatabaseManager()
