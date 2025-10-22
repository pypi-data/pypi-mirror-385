"""
🛠️ HELPER FUNCTIONS
Yardımcı fonksiyonlar ve araçlar
"""

import pandas as pd
from typing import Dict, Set
from datetime import datetime


class ProgressPrinter:
    """İlerleme mesajlarını yazdıran yardımcı sınıf"""
    
    @staticmethod
    def print_header(title: str):
        """Başlık yazdır"""
        print("\n" + "="*80)
        print(title)
        print("="*80)
    
    @staticmethod
    def print_section(title: str):
        """Bölüm başlığı yazdır"""
        print(f"\n{'='*80}")
        print(title)
        print(f"{'='*80}")
    
    @staticmethod
    def print_info(message: str, indent: int = 0):
        """Bilgi mesajı yazdır"""
        prefix = "   " * indent
        print(f"{prefix}{message}")
    
    @staticmethod
    def print_success(message: str):
        """Başarı mesajı yazdır"""
        print(f"✅ {message}")
    
    @staticmethod
    def print_error(message: str):
        """Hata mesajı yazdır"""
        print(f"❌ {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Uyarı mesajı yazdır"""
        print(f"⚠️  {message}")
    
    @staticmethod
    def print_summary(summary: Dict):
        """Özet bilgileri yazdır"""
        ProgressPrinter.print_section("📊 ÖZET")
        for key, value in summary.items():
            print(f"   {key}: {value}")


class DataFrameHelper:
    """DataFrame işlemleri için yardımcı sınıf"""
    
    @staticmethod
    def add_match_statistics(df: pd.DataFrame, standings_by_week: Dict) -> pd.DataFrame:
        """
        Maçlara takım istatistiklerini ekle
        
        Args:
            df: Maçlar DataFrame'i
            standings_by_week: Haftalara göre puan durumu dict'i
            
        Returns:
            DataFrame: İstatistikleri eklenmiş maçlar
        """
        df = df.copy()
        
        for week in df['hafta'].unique():
            week_matches = df[df['hafta'] == week]
            
            # Önceki haftanın istatistiklerini al
            prev_week_stats = standings_by_week.get(week - 1, {})
            
            if not prev_week_stats:
                continue
            
            # Her maç için istatistikleri ekle
            for idx, match in week_matches.iterrows():
                home_id = match['home_team_id']
                away_id = match['away_team_id']
                
                # Ev sahibi istatistikleri
                df.loc[idx, 'home_rank'] = prev_week_stats.get('rank', {}).get(home_id, '-')
                df.loc[idx, 'home_played'] = prev_week_stats.get('played', {}).get(home_id, 0)
                df.loc[idx, 'home_over'] = prev_week_stats.get('over', {}).get(home_id, 0)
                df.loc[idx, 'home_under'] = prev_week_stats.get('under', {}).get(home_id, 0)
                df.loc[idx, 'home_over_ok'] = prev_week_stats.get('over_ok', {}).get(home_id, 0)
                df.loc[idx, 'home_under_ok'] = prev_week_stats.get('under_ok', {}).get(home_id, 0)
                df.loc[idx, 'home_btts'] = prev_week_stats.get('btts', {}).get(home_id, 0)
                df.loc[idx, 'home_btts_no'] = prev_week_stats.get('btts_no', {}).get(home_id, 0)
                
                # Deplasman istatistikleri
                df.loc[idx, 'away_rank'] = prev_week_stats.get('rank', {}).get(away_id, '-')
                df.loc[idx, 'away_played'] = prev_week_stats.get('played', {}).get(away_id, 0)
                df.loc[idx, 'away_over'] = prev_week_stats.get('over', {}).get(away_id, 0)
                df.loc[idx, 'away_under'] = prev_week_stats.get('under', {}).get(away_id, 0)
                df.loc[idx, 'away_over_ok'] = prev_week_stats.get('over_ok', {}).get(away_id, 0)
                df.loc[idx, 'away_under_ok'] = prev_week_stats.get('under_ok', {}).get(away_id, 0)
                df.loc[idx, 'away_btts'] = prev_week_stats.get('btts', {}).get(away_id, 0)
                df.loc[idx, 'away_btts_no'] = prev_week_stats.get('btts_no', {}).get(away_id, 0)
        
        return df
    
    @staticmethod
    def create_standings_dict(standings_df: pd.DataFrame) -> Dict:
        """
        Puan durumu DataFrame'inden dict oluştur
        
        Args:
            standings_df: Puan durumu DataFrame
            
        Returns:
            Dict: İstatistik dict'i
        """
        if standings_df is None or len(standings_df) == 0:
            return {}
        
        return {
            'rank': dict(zip(standings_df['team_id'], standings_df['Sıra'])),
            'played': dict(zip(standings_df['team_id'], standings_df['O'])),
            'over': dict(zip(standings_df['team_id'], standings_df.get('ÜST', standings_df.get('over', 0)))),
            'under': dict(zip(standings_df['team_id'], standings_df.get('ALT', standings_df.get('under', 0)))),
            'over_ok': dict(zip(standings_df['team_id'], standings_df.get('ÜST-OK', standings_df.get('over_ok', 0)))),
            'under_ok': dict(zip(standings_df['team_id'], standings_df.get('ALT-OK', standings_df.get('under_ok', 0)))),
            'btts': dict(zip(standings_df['team_id'], standings_df.get('KGVAR', standings_df.get('btts', 0)))),
            'btts_no': dict(zip(standings_df['team_id'], standings_df.get('KGYOK', standings_df.get('btts_no', 0)))),
        }
    
    @staticmethod
    def get_teams_playing_in_week(df: pd.DataFrame, week: int) -> Set[int]:
        """
        Belirli bir haftada oynayan takımları döndür
        
        Args:
            df: Maçlar DataFrame
            week: Hafta numarası
            
        Returns:
            Set: Takım ID'leri
        """
        week_matches = df[df['hafta'] == week]
        teams = set()
        
        for _, match in week_matches.iterrows():
            teams.add(match['home_team_id'])
            teams.add(match['away_team_id'])
        
        return teams
