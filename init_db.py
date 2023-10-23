import random
from datetime import datetime, timedelta

from src.utils.db_manager import db_manager


def create_random_musteri(c, n=1):
    isimler = [
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
    sehirler = ["İstanbul", "Ankara", "İzmir", "Trabzon", "Zonguldak"]
    current_date = datetime.now()

    for i in range(n):
        isim = isimler[i % len(isimler)][0]
        yas = random.randint(18, 65)
        dogum_tarihi = current_date - timedelta(days=yas * 365)
        cinsiyet = isimler[i % len(isimler)][1]
        sehir = random.choice(sehirler)
        telefon = "05" + str(
            random.randint(10**8, 10**9 - 1)
        )  # 10 digit Turkish mobile phone number
        sms_izin = random.choice([0, 1])
        push_izin = random.choice([0, 1])
        c.execute(
            """
            INSERT INTO musteriler (isim, yas, dogum_tarihi, cinsiyet, sehir, telefon, sms_izin, push_izin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (isim, yas, dogum_tarihi, cinsiyet, sehir, telefon, sms_izin, push_izin),
        )


def initialize_database():
    c = db_manager.conn_customers.cursor()
    create_random_musteri(c, 20)  # for example, create 10000 random customers
    db_manager.conn_customers.commit()
    db_manager.close()


if __name__ == "__main__":
    initialize_database()
