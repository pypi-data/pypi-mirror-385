"""
⚙️ CONFIGURATION
================

Veritabanı ve API ayarları - TEK YER!

🔒 GÜVENLİK: 
- Kendi veritabanı bilgilerinizi .env dosyasında saklayın
- .env dosyası .gitignore'da olmalı (asla GitHub'a gitmemeli!)
"""

import os
from pathlib import Path

# .env dosyasını oku (varsa)
def load_env_file():
    """
    .env dosyasını yükle (python-dotenv olmadan)
    """
    env_path = Path.cwd() / '.env'
    
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# .env dosyasını yükle
load_env_file()

# Veritabanı bağlantı bilgileri (önce çevre değişkenlerinden, yoksa varsayılan)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),  # Varsayılan: localhost (kendi bilgisayarı)
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'mackolik_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Bağlantı string'i
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# API ayarları
API_CONFIG = {
    'base_url': 'https://vd.mackolik.com/livedata',
    'headers': {
        'accept': '*/*',
        'origin': 'https://arsiv.mackolik.com',
        'user-agent': 'Mozilla/5.0'
    },
    'retry_count': 3,
    'retry_delay': 60  # saniye
}

# Tablo isimleri
TABLE_NAMES = {
    'results': 'results',
    'fixtures': 'fixtures'
}
