"""
🚀 WEEK DIVIDER SERVICE
Tüm ligler için maçları haftalara bölen ve veritabanına kaydeden servis
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg

# Proje kök klasörünü path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import DatabaseManager
from core.match_loader import MatchLoader
from core.week_divider import WeekDivider


class WeekDividerService:
    """Tüm ligler için hafta bölme servisi"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """
        Args:
            db_manager: DatabaseManager instance (opsiyonel)
        """
        self.db_manager = db_manager or DatabaseManager()
        self.match_loader = MatchLoader(self.db_manager)
        
        # İstatistikler
        self.stats = {
            'total_leagues': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'total_matches': 0,
            'start_time': None,
            'end_time': None
        }
        
        self.failed_leagues = []
    
    def get_all_leagues(self, min_matches: int = 10) -> List[Dict[str, Any]]:
        """
        Veritabanından tüm ligleri çek
        
        Args:
            min_matches: Minimum maç sayısı (varsayılan: 10)
            
        Returns:
            List[Dict]: Lig bilgileri listesi
        """
        print("\n" + "=" * 70)
        print("📊 TÜM LİGLER ÇEKILIYOR")
        print("=" * 70)
        
        query = """
            SELECT 
                season_id,
                league,
                country,
                COUNT(*) as match_count,
                MIN(match_date) as first_match,
                MAX(match_date) as last_match
            FROM results
            WHERE status = 4
              AND ft_home IS NOT NULL
              AND ft_away IS NOT NULL
            GROUP BY season_id, league, country
            HAVING COUNT(*) >= %s
            ORDER BY country, league, season_id DESC
        """
        
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute(query, (min_matches,))
            rows = cursor.fetchall()
            cursor.close()
        
        leagues = []
        for row in rows:
            leagues.append({
                'season_id': row[0],
                'league': row[1],
                'country': row[2],
                'match_count': row[3],
                'first_match': row[4],
                'last_match': row[5]
            })
        
        print(f"\n✅ {len(leagues)} lig bulundu (minimum {min_matches} maç)")
        print(f"\n📋 İlk 5 lig:")
        for i, league in enumerate(leagues[:5], 1):
            print(f"   {i}. {league['country']} - {league['league']}")
            print(f"      Season ID: {league['season_id']}, Maç: {league['match_count']}")
        
        if len(leagues) > 5:
            print(f"\n   ... ve {len(leagues) - 5} lig daha")
        
        return leagues
    
    def create_match_weeks_table(self):
        """match_weeks tablosunu oluştur (yoksa)"""
        print("\n" + "=" * 70)
        print("🗄️  VERİTABANI TABLOSU KONTROLÜ")
        print("=" * 70)
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS match_weeks (
            id SERIAL PRIMARY KEY,
            match_id BIGINT NOT NULL,
            season_id INTEGER NOT NULL,
            league VARCHAR(255),
            country VARCHAR(255),
            week_number INTEGER NOT NULL,
            match_date VARCHAR(50),
            match_time VARCHAR(50),
            home_team_id INTEGER,
            home_team VARCHAR(255),
            away_team_id INTEGER,
            away_team VARCHAR(255),
            ht_home SMALLINT,
            ht_away SMALLINT,
            ft_home SMALLINT,
            ft_away SMALLINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_match_season UNIQUE(match_id, season_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_match_weeks_season ON match_weeks(season_id);
        CREATE INDEX IF NOT EXISTS idx_match_weeks_week ON match_weeks(week_number);
        CREATE INDEX IF NOT EXISTS idx_match_weeks_match ON match_weeks(match_id);
        """
        
        try:
            with self.db_manager as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                conn.commit()
                cursor.close()
            
            print("✅ match_weeks tablosu hazır")
        except Exception as e:
            print(f"⚠️  Tablo oluşturma hatası: {e}")
    
    def save_matches_to_database(self, matches_df, season_id: int, league: str, country: str) -> int:
        """
        Haftalara bölünmüş maçları veritabanına kaydet
        
        Args:
            matches_df: Hafta bilgili maçlar DataFrame
            season_id: Sezon ID
            league: Lig adı
            country: Ülke adı
            
        Returns:
            Kaydedilen kayıt sayısı
        """
        insert_sql = """
        INSERT INTO match_weeks (
            match_id, season_id, league, country, week_number,
            match_date, match_time, home_team_id, home_team,
            away_team_id, away_team, ht_home, ht_away, ft_home, ft_away
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (match_id, season_id) 
        DO UPDATE SET 
            week_number = EXCLUDED.week_number,
            updated_at = CURRENT_TIMESTAMP
        """
        
        saved_count = 0
        
        with self.db_manager as conn:
            cursor = conn.cursor()
            
            for _, match in matches_df.iterrows():
                try:
                    cursor.execute(insert_sql, (
                        int(match['match_id']),
                        int(season_id),
                        league,
                        country,
                        int(match['hafta']),
                        match['match_date'],
                        match.get('match_time', ''),
                        int(match['home_team_id']),
                        match['home_team'],
                        int(match['away_team_id']),
                        match['away_team'],
                        int(match['ht_home']) if match['ht_home'] is not None else None,
                        int(match['ht_away']) if match['ht_away'] is not None else None,
                        int(match['ft_home']) if match['ft_home'] is not None else None,
                        int(match['ft_away']) if match['ft_away'] is not None else None
                    ))
                    saved_count += 1
                except Exception as e:
                    print(f"      ⚠️  Kayıt hatası (match_id: {match['match_id']}): {e}")
            
            conn.commit()
            cursor.close()
        
        return saved_count
    
    def process_single_league(self, season_id: int, league: str, country: str) -> bool:
        """
        Tek bir lig için haftalara bölme işlemi yap
        
        Args:
            season_id: Sezon ID
            league: Lig adı
            country: Ülke adı
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            # Maçları yükle
            matches_df = self.match_loader.load_matches_by_season(season_id)
            
            if len(matches_df) == 0:
                print(f"      ⚠️  Maç bulunamadı")
                return False
            
            # Haftalara böl
            matches_with_weeks = WeekDivider.divide_matches_into_weeks(matches_df)
            
            total_weeks = matches_with_weeks['hafta'].max()
            
            # Veritabanına kaydet
            saved_count = self.save_matches_to_database(
                matches_with_weeks, 
                season_id, 
                league, 
                country
            )
            
            print(f"      ✅ {len(matches_df)} maç → {total_weeks} hafta → {saved_count} kayıt")
            
            self.stats['total_matches'] += len(matches_df)
            
            return True
            
        except Exception as e:
            print(f"      ❌ Hata: {e}")
            return False
    
    def process_all_leagues(self, min_matches: int = 10, limit: Optional[int] = None):
        """
        Tüm ligleri işle
        
        Args:
            min_matches: Minimum maç sayısı
            limit: İşlenecek maksimum lig sayısı (None ise hepsi)
        """
        self.stats['start_time'] = datetime.now()
        
        print("\n" + "🎯" * 35)
        print("WEEK DIVIDER SERVICE BAŞLATILDI")
        print("🎯" * 35)
        
        # Tablo kontrolü
        self.create_match_weeks_table()
        
        # Tüm ligleri getir
        all_leagues = self.get_all_leagues(min_matches)
        
        if limit:
            all_leagues = all_leagues[:limit]
            print(f"\n⚠️  İlk {limit} lig işlenecek (test modu)")
        
        self.stats['total_leagues'] = len(all_leagues)
        
        # Her ligi işle
        print("\n" + "=" * 70)
        print("🔄 LİGLER İŞLENİYOR")
        print("=" * 70)
        
        for idx, league_info in enumerate(all_leagues, 1):
            season_id = league_info['season_id']
            league = league_info['league']
            country = league_info['country']
            
            print(f"\n[{idx}/{len(all_leagues)}] 🔄 {country} - {league} (Season: {season_id})")
            
            self.stats['processed'] += 1
            
            success = self.process_single_league(season_id, league, country)
            
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
                self.failed_leagues.append({
                    'season_id': season_id,
                    'league': league,
                    'country': country
                })
            
            # Kısa bekleme (veritabanı yükünü azaltmak için)
            time.sleep(0.1)
        
        self.stats['end_time'] = datetime.now()
        
        # Özet rapor
        self.print_summary()
    
    def print_summary(self):
        """İşlem özeti yazdır"""
        print("\n" + "=" * 70)
        print("📊 İŞLEM RAPORU")
        print("=" * 70)
        
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        print(f"\n✅ Toplam İşlenen: {self.stats['processed']} lig")
        print(f"✅ Başarılı: {self.stats['successful']}")
        print(f"❌ Başarısız: {self.stats['failed']}")
        print(f"⚽ Toplam Maç: {self.stats['total_matches']:,}")
        print(f"⏱️  Toplam Süre: {minutes} dakika {seconds} saniye")
        
        if self.failed_leagues:
            print(f"\n❌ Başarısız Ligler ({len(self.failed_leagues)}):")
            for failed in self.failed_leagues[:10]:
                print(f"   • {failed['country']} - {failed['league']} (ID: {failed['season_id']})")
            
            if len(self.failed_leagues) > 10:
                print(f"   ... ve {len(self.failed_leagues) - 10} daha")
        
        print("\n" + "=" * 70)
        print("🎉 WEEK DIVIDER SERVICE TAMAMLANDI!")
        print("=" * 70)


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Week Divider Service')
    parser.add_argument('--season-id', type=int, help='Tek bir season_id işle')
    parser.add_argument('--min-matches', type=int, default=10, help='Minimum maç sayısı')
    parser.add_argument('--limit', type=int, help='İşlenecek maksimum lig sayısı')
    parser.add_argument('--test', action='store_true', help='Test modu (ilk 5 lig)')
    
    args = parser.parse_args()
    
    service = WeekDividerService()
    
    if args.season_id:
        # Tek lig işle
        print(f"\n🎯 Tek lig modu: Season ID {args.season_id}")
        
        # Lig bilgilerini al
        leagues = service.get_all_leagues(min_matches=1)
        target_league = None
        
        for league in leagues:
            if league['season_id'] == args.season_id:
                target_league = league
                break
        
        if target_league:
            service.create_match_weeks_table()
            success = service.process_single_league(
                target_league['season_id'],
                target_league['league'],
                target_league['country']
            )
            
            if success:
                print("\n✅ İşlem başarılı!")
            else:
                print("\n❌ İşlem başarısız!")
        else:
            print(f"\n❌ Season ID {args.season_id} bulunamadı!")
    
    else:
        # Tüm ligleri işle
        limit = args.limit
        if args.test:
            limit = 5
            print("\n🧪 Test modu aktif - İlk 5 lig işlenecek")
        
        service.process_all_leagues(
            min_matches=args.min_matches,
            limit=limit
        )


if __name__ == "__main__":
    main()
