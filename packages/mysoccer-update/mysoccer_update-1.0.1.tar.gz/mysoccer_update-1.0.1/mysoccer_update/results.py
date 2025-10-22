"""
⚽ RESULTS API
==============

Maçları çeker ve veritabanına kaydeder.
Status < 13 filtresi uygulanır (0-12 arası tüm maçlar).
"""

import psycopg
import pandas as pd
from datetime import datetime, timedelta
import time
from .api_client import MackolikAPIClient
from .config import DB_URL, TABLE_NAMES, API_CONFIG


class ResultsAPI:
    """Biten maçları yöneten API"""
    
    def __init__(self):
        self.client = MackolikAPIClient()
        self.table_name = TABLE_NAMES['results']
        self.retry_count = API_CONFIG['retry_count']
        self.retry_delay = API_CONFIG['retry_delay']
    
    def fetch_results_by_date(self, date: str) -> pd.DataFrame:
        """
        Belirli bir tarihteki maçları çek (status < 13)
        
        Args:
            date (str): 'DD/MM/YYYY' formatında tarih
            
        Returns:
            DataFrame: Maçlar (status < 13)
        """
        data = self.client.fetch_and_process(date, status_filter=13)
        print(f'✓ {len(data)} maç bulundu')
        return data
    
    def save_to_database(self, data: pd.DataFrame) -> dict:
        """
        Verileri veritabanına kaydet (BULK INSERT - çok hızlı)
        
        Args:
            data (DataFrame): Kaydedilecek veri
            
        Returns:
            dict: İstatistikler (inserted, deleted)
        """
        if len(data) == 0:
            print('⚠️ Kaydedilecek veri yok')
            return {'inserted': 0, 'deleted': 0}
        
        # Mükerrer match_id kontrolü (API'den gelen veride)
        duplicates_count = data.duplicated(subset=['match_id'], keep='last').sum()
        if duplicates_count > 0:
            print(f'⚠️ {duplicates_count} mükerrer match_id temizlendi')
            data = data.drop_duplicates(subset=['match_id'], keep='last').reset_index(drop=True)
        
        conn = psycopg.connect(DB_URL)
        cur = conn.cursor()
        
        # 1. Bu maçların match_id'lerini SİL (güncelleme için)
        match_ids = tuple(data['match_id'].tolist())
        if len(match_ids) == 1:
            cur.execute(f"DELETE FROM {self.table_name} WHERE match_id = %s", (match_ids[0],))
        else:
            placeholders = ','.join(['%s'] * len(match_ids))
            cur.execute(f"DELETE FROM {self.table_name} WHERE match_id IN ({placeholders})", match_ids)
        deleted = cur.rowcount
        
        # 2. Tüm verileri TOPLU EKLE (COPY - çok hızlı)
        values = [tuple(row) for _, row in data.iterrows()]
        columns = ', '.join(data.columns)
        
        with cur.copy(f"COPY {self.table_name} ({columns}) FROM STDIN") as copy:
            for row in values:
                copy.write_row(row)
        
        conn.commit()
        cur.close()
        conn.close()
        
        inserted = len(data)
        if deleted > 0:
            print(f'✓ PostgreSQL: {inserted} eklendi ({deleted} eski silindi)')
        else:
            print(f'✓ PostgreSQL: {inserted} yeni eklendi')
        
        return {'inserted': inserted, 'deleted': deleted}
    
    def update_single_date(self, date: str, retry_count: int = 0) -> dict:
        """
        Tek tarih için güncelleme yap (retry mekanizması ile)
        
        Args:
            date (str): 'DD/MM/YYYY' formatında tarih
            retry_count (int): Mevcut deneme sayısı
            
        Returns:
            dict: İstatistikler
        """
        try:
            print(f'📅 Tarih: {date}')
            data = self.fetch_results_by_date(date)
            
            if len(data) == 0:
                print('⚠️ Bu tarihte maç bulunamadı')
                return {'date': date, 'total': 0, 'inserted': 0, 'deleted': 0}
            
            stats = self.save_to_database(data)
            stats['date'] = date
            stats['total'] = len(data)
            
            return stats
        
        except Exception as e:
            if retry_count < self.retry_count:
                print(f'❌ {date} hatası: {e}')
                print(f'⏳ {self.retry_delay} saniye bekleniyor... (Deneme {retry_count + 1}/{self.retry_count})')
                time.sleep(self.retry_delay)
                print(f'🔄 {date} tekrar deneniyor...')
                return self.update_single_date(date, retry_count + 1)
            else:
                print(f'❌ {date} başarısız! {self.retry_count} deneme sonrası hala hata: {e}')
                return {'date': date, 'total': 0, 'inserted': 0, 'deleted': 0, 'error': str(e)}
    
    def update_date_range(self, start_date: str, end_date: str) -> dict:
        """
        Tarih aralığı için güncelleme yap
        
        Args:
            start_date (str): Başlangıç tarihi 'DD/MM/YYYY'
            end_date (str): Bitiş tarihi 'DD/MM/YYYY'
            
        Returns:
            dict: Toplam istatistikler
        """
        start = datetime.strptime(start_date, '%d/%m/%Y')
        end = datetime.strptime(end_date, '%d/%m/%Y')
        
        if start > end:
            print('❌ Başlangıç tarihi bitiş tarihinden büyük olamaz!')
            return None
        
        print(f'📅 Tarih Aralığı: {start_date} - {end_date}')
        print('=' * 60)
        
        total_matches = 0
        total_inserted = 0
        total_deleted = 0
        daily_stats = []
        
        current = start
        while current <= end:
            date_str = current.strftime('%d/%m/%Y')
            
            result = self.update_single_date(date_str)
            total_matches += result['total']
            total_inserted += result.get('inserted', 0)
            total_deleted += result.get('deleted', 0)
            daily_stats.append(result)
            
            current += timedelta(days=1)
        
        print('=' * 60)
        print(f'✓ TOPLAM: {total_inserted} maç eklendi ({total_deleted} eski silindi)')
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_matches': total_matches,
            'total_inserted': total_inserted,
            'total_deleted': total_deleted,
            'daily_stats': daily_stats
        }
    
    def update_today(self) -> dict:
        """Bugünü güncelle"""
        today = datetime.now().strftime('%d/%m/%Y')
        return self.update_single_date(today)
    
    def update_yesterday(self) -> dict:
        """Dünü güncelle"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
        return self.update_single_date(yesterday)
    
    def auto_update(self) -> dict:
        """
        Otomatik güncelleme - Dün, Bugün, Yarın
        Veri kaçırılmasını önler
        """
        print('🔄 OTOMATİK GÜNCELLEME BAŞLATILDI')
        print('=' * 60)
        
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        print(f'📆 Dün: {yesterday.strftime("%d/%m/%Y")}')
        print(f'📆 Bugün: {today.strftime("%d/%m/%Y")}')
        print(f'📆 Yarın: {tomorrow.strftime("%d/%m/%Y")}')
        print('=' * 60)
        
        results = {}
        total_matches = 0
        total_inserted = 0
        total_deleted = 0
        
        # Dün
        print('\n📅 DÜN verileri çekiliyor...')
        results['yesterday'] = self.update_single_date(yesterday.strftime('%d/%m/%Y'))
        total_matches += results['yesterday']['total']
        total_inserted += results['yesterday'].get('inserted', 0)
        total_deleted += results['yesterday'].get('deleted', 0)
        
        # Bugün
        print('\n📅 BUGÜN verileri çekiliyor...')
        results['today'] = self.update_single_date(today.strftime('%d/%m/%Y'))
        total_matches += results['today']['total']
        total_inserted += results['today'].get('inserted', 0)
        total_deleted += results['today'].get('deleted', 0)
        
        # Yarın
        print('\n📅 YARIN verileri çekiliyor...')
        results['tomorrow'] = self.update_single_date(tomorrow.strftime('%d/%m/%Y'))
        total_matches += results['tomorrow']['total']
        total_inserted += results['tomorrow'].get('inserted', 0)
        total_deleted += results['tomorrow'].get('deleted', 0)
        
        print('=' * 60)
        print(f'✓ TOPLAM: {total_inserted} maç eklendi ({total_deleted} eski silindi)')
        print('✓ OTOMATİK GÜNCELLEME TAMAMLANDI')
        
        results['total_matches'] = total_matches
        results['total_inserted'] = total_inserted
        results['total_deleted'] = total_deleted
        
        return results
