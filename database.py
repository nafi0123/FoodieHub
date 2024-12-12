from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
URL_DATABASE = "mysql+pymysql://root:@127.0.0.1:3306/foodiehub"
engine=create_engine(URL_DATABASE)
sessonlocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base=declarative_base()
