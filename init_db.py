from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

# Ініціалізація клієнта MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
applications = db.applications

# Функція для ініціалізації (повертає колекцію заявок)
def init_db():
    return applications

# Функція для додавання заявки в БД
def add_application(full_name, phone, address, tariff):
    application = {
        "full_name": full_name,
        "phone": phone,
        "address": address,
        "tariff": tariff,
        "status": "нова"
    }
    applications.insert_one(application)
