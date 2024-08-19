from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base

host = 'xxxxx'
database = 'branded_food_database'
user = 'admin'
password = 'xxxxx'
port = 3306

DB_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

# Create engine
engine = create_engine(DB_URL)

# Create tables
Base.metadata.create_all(engine)

# Create a sessionmaker
Session = sessionmaker(bind=engine)
