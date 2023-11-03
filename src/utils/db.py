import random
from datetime import datetime, timedelta
from typing import Optional, Union

import pandas as pd
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship
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
    def get_profile_by_name(profile_name: str):
        return session.query(CustomerProfile).filter(CustomerProfile.name == profile_name).first()

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

    @staticmethod
    def get_profile_result(
            profile_name,
            date=datetime.now()
    ) -> Optional[pd.DataFrame]:

        profile = session.query(CustomerProfile).filter(CustomerProfile.name == profile_name).first()
        if profile is None:
            return None
        if profile.profile_type == "dinamik":
            # Change 'now' to date
            sql_code = profile.sql_code.replace("now", f"{date.strftime('%Y-%m-%d')}")
            profile_result = pd.read_sql_query(sql_code, engine)
        else:
            profile_result = pd.read_json(profile.query_result)
        profile_result['date'] = date
        return profile_result

    @staticmethod
    def get_next_day_profile_result(
            profile_name,
            date=datetime.now()
    ) -> Union[int, Optional[pd.DataFrame]]:

        profile = session.query(CustomerProfile).filter(CustomerProfile.name == profile_name).first()
        if profile is None or profile.profile_exclusion_period is None or profile.profile_exclusion_period == 0:
            next_day = 0
            next_result = None
        else:
            next_day = profile.profile_exclusion_period
            next_result = pd.DataFrame()
            for current_date in pd.date_range(date, date + timedelta(days=profile.profile_exclusion_period)):
                current_day_df = CustomerProfile.get_profile_result(profile_name, current_date)
                if current_day_df is None:
                    continue
                current_day_df['date'] = current_date
                next_result = pd.concat([next_result, current_day_df])

        return next_day, next_result


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
        campaign_df = campaign_df[campaign_df['name'] != 'DoğumGünüKampanyası']
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


class FinalTarget(Base):
    __tablename__ = "final_targets"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer_name = Column(String(20))
    profile_id = Column(Integer, ForeignKey('customer_profiles.id'))
    profile_name = Column(String(20))
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    campaign_name = Column(String(20))
    current_date = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    @staticmethod
    def save_final_target(final_customer_df: pd.DataFrame, campaign: pd.Series, date=datetime.now()):
        final_customer_df['customer_id'] = final_customer_df['id']
        final_customer_df['customer_name'] = final_customer_df['name']
        profile = session.query(CustomerProfile).filter(CustomerProfile.name == campaign.campaign_profile).first()
        final_customer_df['profile_id'] = profile.id
        final_customer_df['profile_name'] = profile.name
        final_customer_df['campaign_id'] = campaign.id
        final_customer_df['campaign_name'] = campaign.name
        final_customer_df['current_date'] = date
        final_customer_df['start_date'] = final_customer_df['date']
        if profile.schedule_day is None:
            final_customer_df['end_date'] = final_customer_df['date'] + timedelta(days=0)
        else:
            final_customer_df['end_date'] = final_customer_df['date'] + timedelta(days=profile.schedule_day)

        final_customer_df = final_customer_df.drop(columns=['id', 'name', 'age', 'gender',
                                                            'city', 'birthday', 'phone', 'date',
                                                            'sms_permission', 'push_permission'])
        final_customer_df.to_sql(FinalTarget.__tablename__, engine, if_exists='append', index=False)
        return pd.read_sql_query(f"SELECT * FROM {FinalTarget.__tablename__}", engine)

    @staticmethod
    def get_all_final_targets() -> pd.DataFrame:
        final_target_df = pd.read_sql_query(f"SELECT * FROM {FinalTarget.__tablename__}", engine)
        return final_target_df

    @staticmethod
    def get_active_targets(date) -> pd.DataFrame:
        final_target_df = pd.read_sql(
            session.query(FinalTarget).filter(FinalTarget.start_date <= date, FinalTarget.end_date >= date).statement,
            session.bind
        )
        return final_target_df

    @staticmethod
    def clear_final_targets():
        session.query(FinalTarget).delete()
        session.commit()


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

customer_df = Customer.get_all_customers()
if customer_df.shape[0] == 0:
    sample_customers = Customer.create_sample_customers(40)
    session.add_all(sample_customers)
    session.commit()
