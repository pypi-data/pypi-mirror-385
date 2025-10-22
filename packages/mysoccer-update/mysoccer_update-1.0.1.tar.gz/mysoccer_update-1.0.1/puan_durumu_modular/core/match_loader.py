"""
⚽ MATCH LOADER
Veritabanından maç verilerini yükler
"""

import pandas as pd
from typing import Optional
from .database import DatabaseManager

class MatchLoader:
    """Maç verilerini yükleyen sınıf"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """
        Args:
            db_manager: DatabaseManager instance (opsiyonel)
        """
        self.db_manager = db_manager or DatabaseManager()
    
    def load_matches_by_season(self, season_id):
        """
        Sezona göre maçları yükle
        
        Args:
            season_id: Sezon ID'si
            
        Returns:
            DataFrame: Maç verileri
        """
        print(f"🔍 Season ID: {season_id} için maçlar çekiliyor...")
        
        query = """
            SELECT 
                match_id,
                season_id,
                league,
                country,
                home_team_id,
                home_team,
                away_team_id,
                away_team,
                ht_home,
                ht_away,
                ft_home,
                ft_away,
                match_date,
                match_time,
                status,
                home_odd,
                draw_odd,
                away_odd
            FROM results
            WHERE season_id = %s
              AND status = 4
              AND ft_home IS NOT NULL
              AND ft_away IS NOT NULL
            ORDER BY match_date, match_time
        """

        with self.db_manager as conn:
            df = pd.read_sql_query(query, conn, params=(season_id,))
        
        if len(df) == 0:
            print(f"❌ Season ID {season_id} için maç bulunamadı!")
            return df
        
        print(f"✅ {len(df)} maç bulundu")
        print(f"📍 Lig: {df['league'].iloc[0]}")
        print(f"🌍 Ülke: {df['country'].iloc[0]}")
        
        return df
    
    def filter_last_n_matches_per_team(self, df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
        """
        Her takımın son N maçını filtrele
        
        Args:
            df: Maç verileri DataFrame
            n: Son kaç maç alınacak (varsayılan: 8)
            
        Returns:
            DataFrame: Filtrelenmiş maç verileri
        """
        print(f"\n🔥 Her takımın son {n} maçı filtreleniyor...")
        
        # Tüm takımları bul
        all_teams = set(df['home_team_id'].tolist() + df['away_team_id'].tolist())
        print(f"   📊 Toplam {len(all_teams)} takım bulundu")
        
        # Her takımın son N maçını topla
        all_last_n_matches = []
        
        for team_id in all_teams:
            # Bu takımın tüm maçlarını al (ev + deplasman)
            team_home = df[df['home_team_id'] == team_id].copy()
            team_away = df[df['away_team_id'] == team_id].copy()
            
            # Ev ve deplasman maçlarını birleştir ve tarihe göre sırala
            team_home['is_home'] = True
            team_away['is_home'] = False
            team_all_matches = pd.concat([team_home, team_away])
            team_all_matches['date_only'] = pd.to_datetime(
                team_all_matches['match_date'], 
                format='%d/%m/%Y', 
                errors='coerce'
            ).dt.date
            team_all_matches = team_all_matches.sort_values('date_only').reset_index(drop=True)
            
            # Son N maçı al
            last_n = team_all_matches.tail(n).copy()
            
            # is_home ve date_only kolonlarını kaldır
            last_n = last_n.drop(['is_home', 'date_only'], axis=1)
            
            all_last_n_matches.append(last_n)
        
        # Tüm son N maçları birleştir
        last_n_df = pd.concat(all_last_n_matches, ignore_index=True)
        
        # Duplikasyonları kaldır
        last_n_df = last_n_df.drop_duplicates(subset=['match_id']).reset_index(drop=True)
        
        print(f"   ✅ Son {n} maç filtresi: {len(df)} maç → {len(last_n_df)} maç")
        
        return last_n_df
