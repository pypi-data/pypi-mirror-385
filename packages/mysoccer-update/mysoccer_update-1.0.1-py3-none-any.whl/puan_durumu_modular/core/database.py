"""
🗄️ DATABASE MANAGER
Veritabanı bağlantısını yönetir
"""

import psycopg
from typing import Dict, Any


class DatabaseManager:
    """Veritabanı bağlantı yöneticisi"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Args:
            config: Veritabanı yapılandırması (host, port, dbname, user, password)
        """
        self.config = config or self._default_config()
        self._connection = None
    
    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """Varsayılan veritabanı yapılandırması"""
        return {
            'host': '167.71.74.229',
            'port': 5432,
            'dbname': 'mackolik_db',
            'user': 'mackolik_user',
            'password': 'GucluSifre123!'
        }
    
    def connect(self):
        """Veritabanına bağlan"""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg.connect(**self.config)
        return self._connection
    
    def disconnect(self):
        """Bağlantıyı kapat"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    def get_connection(self):
        """Aktif bağlantıyı döndür (yoksa oluştur)"""
        return self.connect()
    
    def __enter__(self):
        """Context manager - with bloğu için"""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - otomatik kapanış"""
        self.disconnect()
