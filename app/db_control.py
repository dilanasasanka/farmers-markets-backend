from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base

host = 'branded-food-database.cwa9vz5ge6cb.us-east-1.rds.amazonaws.com'
database = 'branded_food_database'
user = 'admin'
password = 'dipnys-hubne2-fItdyq'
port = 3306

DB_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

# Create engine
engine = create_engine(DB_URL)

# Create tables
Base.metadata.create_all(engine)

# Create a sessionmaker
Session = sessionmaker(bind=engine)
