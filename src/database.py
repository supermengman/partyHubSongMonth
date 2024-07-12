from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///tokens.db'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserToken(Base):
    __tablename__ = 'user_tokens'

    user_id = Column(String, primary_key=True, index=True)
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_type = Column(String)
    expires_in = Column(String)
    scope = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
    
init_db()