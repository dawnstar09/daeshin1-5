import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase 설정
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'your_supabase_project_url')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your_supabase_anon_key')
    
    # Flask 설정
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 데이터베이스 설정
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///users.db')
