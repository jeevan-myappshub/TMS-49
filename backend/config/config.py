from dotenv import load_dotenv 
import os 

load_dotenv()

# MYSQL_HOST=os.getenv('MYSQL_HOST')
# MYSQL_USER=os.getenv('MYSQL_USER')
# MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD')
# MYSQL_DB=os.getenv('MYSQL_DB')
# MYSQL_PORT=int(os.getenv('MYSQL_PORT',3306))

# SQLALCHEMY_DATABASE_URI = (
#     f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
# )

# POSTGRES_HOST = os.getenv('POSTGRES_HOST')
# POSTGRES_USER = os.getenv('POSTGRES_USER')
# POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
# POSTGRES_DB = os.getenv('POSTGRES_DB')
# POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))

# SQLALCHEMY_DATABASE_URI = (
#     f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
# )

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:939252@localhost:5432/timesheet"


SQLALCHEMY_TRACK_MODIFICATIONS = False


