"""
📅 FIXTURES API
===============

Gelecek maçları (fikstür) çeker ve veritabanına kaydeder.
Status filtresi YOK - tüm maçları çeker (başlamış, başlamamış, biten hepsi).
"""

import psycopg
import pandas as pd
from datetime import datetime, timedelta
from .api_client import MackolikAPIClient
from .config import DB_URL, TABLE_NAMES


class FixturesAPI:
    """Fikstür verilerini yöneten API"""
    
    def __init__(self):
        self.client = MackolikAPIClient()
        self.table_name = TABLE_NAMES['fixtures']
    
    def fetch_fixtures_by_date(self, date: str) -> pd.DataFrame:
        """
        Belirli bir tarihteki TÜM maçları çek (status filtresi YOK)
        
        Args:
            date (str): 'DD/MM/YYYY' formatında tarih
            
        Returns:
            DataFrame: Tüm maçlar
        """
        data = self.client.fetch_and_process(date, status_filter=None)
        
        status_counts = data['status'].value_counts().to_dict()
        print(f'✓ {len(data)} maç bulundu (Status: {status_counts})')
        
        return data
    
    def get_next_3_days(self) -> pd.DataFrame:
        """
        Bugün, yarın, öbür gün - 3 günlük fikstürü topla
        
        Returns:
            DataFrame: 3 günlük tüm maçlar
        """
        today = datetime.now()
        
        print('📅 3 GÜNLÜK FİKSTÜR TOPLANIYOR')
        print('=' * 60)
        
        all_fixtures = []
        
        for i in range(3):
            current_date = today + timedelta(days=i)
            date_str = current_date.strftime('%d/%m/%Y')
            
            if i == 0:
                day_name = 'BUGÜN'
            elif i == 1:
                day_name = 'YARIN'
            else:
                day_name = 'ÖBÜR GÜN'
            
            print(f'\n{day_name}: {date_str}')
            
            try:
                fixtures = self.fetch_fixtures_by_date(date_str)
                all_fixtures.append(fixtures)
            except Exception as e:
                print(f'❌ {date_str} hatası: {e}')
        
        # Tüm günleri birleştir
        if all_fixtures:
            combined = pd.concat(all_fixtures, ignore_index=True)
            
            # Mükerrer match_id varsa temizle
            duplicates_count = combined.duplicated(subset=['match_id'], keep='last').sum()
            if duplicates_count > 0:
                print(f'\n⚠️ {duplicates_count} mükerrer match_id temizlendi')
                combined = combined.drop_duplicates(subset=['match_id'], keep='last').reset_index(drop=True)
            
            # SIRALAMA: Tarih → Saat (gün bazlı gruplama)
            combined['match_date_sort'] = pd.to_datetime(combined['match_date'], format='%d/%m/%Y')
            combined = combined.sort_values(by=['match_date_sort', 'match_time'], ascending=[True, True])
            combined = combined.drop(columns=['match_date_sort']).reset_index(drop=True)
            
            print('=' * 60)
            print(f'✓ TOPLAM: {len(combined)} maç')
            print(f'📊 Status dağılımı: {combined["status"].value_counts().to_dict()}')
            print(f'📅 Tarih aralığı: {combined["match_date"].min()} - {combined["match_date"].max()}')
            print('=' * 60)
            
            return combined
        else:
            print('❌ Hiç veri çekilemedi!')
            return pd.DataFrame()
    
    def save_to_database(self, data: pd.DataFrame) -> dict:
        """
        Fikstürleri veritabanına kaydet (TRUNCATE + INSERT)
        
        Args:
            data (DataFrame): Fikstür verileri
            
        Returns:
            dict: İstatistikler
        """
        if len(data) == 0:
            print('⚠️ Kaydedilecek veri yok')
            return {'inserted': 0}
        
        # Veritabanına eklerken de sırala (Tarih → Saat)
        data_sorted = data.copy()
        data_sorted['match_date_sort'] = pd.to_datetime(data_sorted['match_date'], format='%d/%m/%Y')
        data_sorted = data_sorted.sort_values(by=['match_date_sort', 'match_time'], ascending=[True, True])
        data_sorted = data_sorted.drop(columns=['match_date_sort']).reset_index(drop=True)
        
        conn = psycopg.connect(DB_URL)
        cur = conn.cursor()
        
        # Önce tabloyu temizle (her çalıştırmada yeni fikstür)
        cur.execute(f"TRUNCATE TABLE {self.table_name}")
        print(f'🗑️ {self.table_name} tablosu temizlendi')
        
        # Tüm verileri TOPLU EKLE (sıralı olarak)
        values = [tuple(row) for _, row in data_sorted.iterrows()]
        columns = ', '.join(data_sorted.columns)
        
        with cur.copy(f"COPY {self.table_name} ({columns}) FROM STDIN") as copy:
            for row in values:
                copy.write_row(row)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f'✓ {len(data)} maç {self.table_name} tablosuna eklendi')
        
        return {'inserted': len(data)}
    
    def export_to_excel(self, data: pd.DataFrame, filename: str = 'fixtures_3gun.xlsx') -> None:
        """
        Fikstürleri Excel'e aktar
        
        Args:
            data (DataFrame): Fikstür verileri
            filename (str): Dosya adı
        """
        if len(data) == 0:
            print('⚠️ Kaydedilecek veri yok')
            return
        
        data.to_excel(filename, index=False, engine='openpyxl')
        print(f'✓ Fikstürler {filename} dosyasına kaydedildi')
    
    def update_fixtures(self, save_to_db: bool = True, export_excel: bool = False) -> pd.DataFrame:
        """
        3 günlük fikstürü çek ve kaydet (all-in-one)
        
        Args:
            save_to_db (bool): Veritabanına kaydet
            export_excel (bool): Excel'e aktar
            
        Returns:
            DataFrame: Fikstür verileri
        """
        fixtures = self.get_next_3_days()
        
        if len(fixtures) > 0:
            if save_to_db:
                self.save_to_database(fixtures)
            
            if export_excel:
                self.export_to_excel(fixtures)
        
        return fixtures
