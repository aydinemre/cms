import random
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite://///Users/emreaydin/PycharmProjects/cms/db/simulation.db", echo=True)
Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)
    gender = Column(String(20))
    city = Column(String(20))
    phone = Column(String(20))
    birthday = Column(DateTime)
    sms_permission = Column(Integer)
    push_permission = Column(Integer)

    def __init__(self, name, age, gender, city, phone, birthday, sms_permission, push_permission):
        self.name = name
        self.age = age
        self.gender = gender
        self.city = city
        self.phone = phone
        self.birthday = birthday
        self.sms_permission = sms_permission
        self.push_permission = push_permission

    @staticmethod
    def get_all_customers() -> pd.DataFrame:
        return pd.read_sql_query(f"SELECT * FROM {Customer.__tablename__}", engine)

    @staticmethod
    def execute_sql(sql: str) -> pd.DataFrame:
        try:
            return pd.read_sql_query(sql, engine), None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def create_sample_customers(n: int) -> list:
        names = [
            ("Aslı", "Kadın"),
            ("Samet", "Erkek"),
            ("Gozde", "Kadın"),
            ("Emre", "Erkek"),
            ("Damla", "Kadın"),
            ("Bülent", "Erkek"),
            ("Tarık", "Erkek"),
            ("Serra", "Kadın"),
            ("Mehmet", "Erkek"),
            ("Hikmet", "Erkek"),
            ("Fatma", "Kadın"),
            ("Ali", "Erkek"),
            ("Veli", "Erkek"),
            ("Ahmet", "Erkek"),
            ("Merve", "Kadın"),
            ("Gökçe", "Erkek"),
            ("Cem", "Erkek"),
            ("Sabri", "Erkek"),
            ("İdil", "Kadın"),
            ("Enis", "Erkek"),
            ("Hasan", "Erkek"),
            ("Zeynep", "Kadın"),
        ]
        cities = ["İstanbul", "Ankara", "İzmir", "Trabzon", "Zonguldak"]
        current_date = datetime.now()
        customers = []
        for i in range(n):
            name = names[i % len(names)][0]
            age = random.randint(18, 65)
            birthday = current_date - timedelta(days=age * 365)
            gender = names[i % len(names)][1]
            city = random.choice(cities)
            phone_number = "05" + str(
                random.randint(10 ** 8, 10 ** 9 - 1)
            )  # 10 digit Turkish mobile phone number
            sms_permission = random.choice([0, 1])
            push_permission = random.choice([0, 1])
            customer = Customer(
                name, age, gender, city, phone_number, birthday, sms_permission, push_permission
            )
            customers.append(customer)
        return customers


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    sql_code = Column(String(1000))
    profile_type = Column(String(20))
    query_result = Column(String(1000))
    schedule_day = Column(Integer)
    profile_exclusion_period = Column(Integer)

    def __init__(self, name, sql_code, profile_type, query_result, schedule_day, profile_exclusion_period):
        self.name = name
        self.sql_code = sql_code
        self.profile_type = profile_type
        self.query_result = query_result.to_json() if query_result is not None else None
        self.schedule_day = schedule_day
        self.profile_exclusion_period = profile_exclusion_period

    @staticmethod
    def create_profile(name, sql_code, profile_type, query_result, schedule_day, profile_exclusion_period):
        customer_profile = CustomerProfile(name, sql_code, profile_type, query_result, schedule_day,
                                           profile_exclusion_period)
        session.add(customer_profile)
        session.commit()
        return customer_profile

    @staticmethod
    def get_all_profiles() -> pd.DataFrame:
        return pd.read_sql_query(f"SELECT * FROM {CustomerProfile.__tablename__}", engine)

    @staticmethod
    def delete_by_name(name: str):
        session.query(CustomerProfile).filter(CustomerProfile.name == name).delete()
        session.commit()

    @staticmethod
    def check_profile_name(name: str) -> bool:
        return session.query(CustomerProfile).filter(CustomerProfile.name == name).count() > 0


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    campaign_type = Column(String(20))
    campaign_order = Column(Integer)
    campaign_profile = Column(String(100))

    def __init__(self, name, start_date, end_date, campaign_type, campaign_order, campaign_profile):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.campaign_type = campaign_type
        self.campaign_order = campaign_order
        self.campaign_profile = campaign_profile

    @staticmethod
    def __preprocess_campaign_df(campaign_df):
        campaign_df['start_date'] = pd.to_datetime(campaign_df['start_date'])
        campaign_df['end_date'] = pd.to_datetime(campaign_df['end_date'])
        campaign_df = campaign_df.sort_values(by=['campaign_order', 'campaign_type', 'start_date'])
        return campaign_df

    @staticmethod
    def get_all_campaigns() -> pd.DataFrame:
        campaign_df = pd.read_sql_query(f"SELECT * FROM {Campaign.__tablename__}", engine)
        return Campaign.__preprocess_campaign_df(campaign_df)

    @staticmethod
    def get_active_campaigns(date) -> pd.DataFrame:
        # SQL Alchemy query
        campaign_df = pd.read_sql(
            session.query(Campaign).filter(Campaign.start_date <= date, Campaign.end_date >= date).statement,
            session.bind
        )

        return Campaign.__preprocess_campaign_df(campaign_df)

    @staticmethod
    def create(name, start_date, end_date, campaign_type, campaign_order, campaign_profile):
        campaign = Campaign(name, start_date, end_date, campaign_type, campaign_order, campaign_profile)
        session.add(campaign)
        session.commit()
        return campaign


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

customer_df = Customer.get_all_customers()
if customer_df.shape[0] == 0:
    sample_customers = Customer.create_sample_customers(40)
    session.add_all(sample_customers)
    session.commit()
