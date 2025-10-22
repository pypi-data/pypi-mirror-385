"""
🏆 STANDINGS CALCULATOR
Puan durumu hesaplamaları
"""

import pandas as pd
from typing import Optional, Set
from .base_calculator import BaseCalculator
from .stats_calculator import StatsCalculator


class StandingsCalculator(BaseCalculator):
    """Puan durumu hesaplayan sınıf"""
    
    def calculate(self, week_num: Optional[int] = None) -> pd.DataFrame:
        """
        Belirli bir haftaya kadar olan kümülatif puan durumu hesapla
        
        Args:
            week_num: Hangi haftaya kadar hesaplanacak (None ise tüm sezon)
            
        Returns:
            DataFrame: Puan durumu tablosu
        """
        # İlgili haftaya kadar olan maçları al
        if week_num is not None and 'hafta' in self.df.columns:
            matches = self.df[self.df['hafta'] <= week_num].copy()
        else:
            matches = self.df.copy()
        
        if len(matches) == 0:
            return None
        
        # Tüm takımları bul
        all_teams = self.get_all_teams()
        
        # İstatistik hesaplayıcı oluştur
        stats_calc = StatsCalculator(matches)
        
        # Her takım için istatistikler hesapla
        standings = []
        
        for _, team in all_teams.iterrows():
            team_id = team['team_id']
            team_name = team['team_name']
            
            # Bu takımın maçları
            team_matches_dict = self.get_team_matches(team_id)
            home_matches = matches[matches['home_team_id'] == team_id].copy()
            away_matches = matches[matches['away_team_id'] == team_id].copy()
            
            total_matches = len(home_matches) + len(away_matches)
            
            # Eğer bu takım henüz hiç oynamadıysa atla
            if total_matches == 0:
                continue
            
            # Temel istatistikler
            basic_stats = self._calculate_basic_stats(home_matches, away_matches)
            
            # Detaylı istatistikler (StatsCalculator kullanarak)
            detailed_stats = stats_calc.calculate(team_id)
            
            # Takım bilgilerini birleştir
            team_row = {
                'team_id': team_id,
                'Sıra': 0,  # Sıralama sonra yapılacak
                'Takım': team_name,
                **basic_stats,
                **detailed_stats
            }
            
            standings.append(team_row)
        
        # DataFrame'e çevir ve sırala
        standings_df = pd.DataFrame(standings)
        
        if len(standings_df) == 0:
            return None
        
        # Türkçe kolon isimleri ekle (Excel export ve görüntüleme için)
        if 'over' in standings_df.columns:
            standings_df['ÜST'] = standings_df['over']
        if 'under' in standings_df.columns:
            standings_df['ALT'] = standings_df['under']
        if 'btts' in standings_df.columns:
            standings_df['KGVAR'] = standings_df['btts']
        if 'btts_no' in standings_df.columns:
            standings_df['KGYOK'] = standings_df['btts_no']
        if 'over_ok' in standings_df.columns:
            standings_df['ÜST-OK'] = standings_df['over_ok']
        if 'under_ok' in standings_df.columns:
            standings_df['ALT-OK'] = standings_df['under_ok']
        if 'ht_over' in standings_df.columns:
            standings_df['İY-OVER'] = standings_df['ht_over']
        if 'ht_under' in standings_df.columns:
            standings_df['İY-UNDER'] = standings_df['ht_under']
        if 'ht_btts' in standings_df.columns:
            standings_df['İY-KGVAR'] = standings_df['ht_btts']
        if 'cleansheet' in standings_df.columns:
            standings_df['CS'] = standings_df['cleansheet']
        
        # Sıralama: Puan → Averaj → Attığı Gol
        standings_df = standings_df.sort_values(
            by=['P', 'AV', 'A'], 
            ascending=[False, False, False]
        ).reset_index(drop=True)
        
        # Sıra numarası ekle
        standings_df['Sıra'] = range(1, len(standings_df) + 1)
        
        # Kolon sırasını düzenle
        cols = self._get_column_order()
        standings_df = standings_df[[col for col in cols if col in standings_df.columns]]
        
        return standings_df
    
    def _calculate_basic_stats(self, home_matches: pd.DataFrame, away_matches: pd.DataFrame) -> dict:
        """Temel puan durumu istatistiklerini hesapla"""
        
        # Ev sahibi istatistikleri
        home_wins = len(home_matches[home_matches['ft_home'] > home_matches['ft_away']])
        home_draws = len(home_matches[home_matches['ft_home'] == home_matches['ft_away']])
        home_losses = len(home_matches[home_matches['ft_home'] < home_matches['ft_away']])
        home_gf = int(home_matches['ft_home'].sum())
        home_ga = int(home_matches['ft_away'].sum())
        
        # Deplasman istatistikleri
        away_wins = len(away_matches[away_matches['ft_away'] > away_matches['ft_home']])
        away_draws = len(away_matches[away_matches['ft_away'] == away_matches['ft_home']])
        away_losses = len(away_matches[away_matches['ft_away'] < away_matches['ft_home']])
        away_gf = int(away_matches['ft_away'].sum())
        away_ga = int(away_matches['ft_home'].sum())
        
        # Toplam
        total_matches = len(home_matches) + len(away_matches)
        wins = home_wins + away_wins
        draws = home_draws + away_draws
        losses = home_losses + away_losses
        gf = home_gf + away_gf
        ga = home_ga + away_ga
        gd = gf - ga
        
        # Puan hesapla
        points = (wins * 3) + draws
        
        return {
            'O': total_matches,
            'G': wins,
            'B': draws,
            'M': losses,
            'A': gf,
            'Y': ga,
            'AV': gd,
            'P': points,
            'EV-O': len(home_matches),
            'DEP-O': len(away_matches)
        }
    
    def _get_column_order(self) -> list:
        """Kolon sırasını döndür"""
        return [
            'team_id', 'Sıra', 'Takım', 'O', 'G', 'B', 'M', 'A', 'Y', 'AV', 'P',
            'ÜST', 'ALT', 'ÜST-OK', 'ALT-OK', 'KGVAR', 'KGYOK',
            'İY-OVER', 'İY-UNDER', 'İY-KGVAR', 'CS',
            'EV-O', 'DEP-O',
            'over', 'under', 'over_ok', 'under_ok', 'btts', 'btts_no',
            'ht_over', 'ht_under', 'ht_btts', 'ht2_over',
            'scored', 'conceded', 'cleansheet',
            'home_matches', 'away_matches', 'total_matches'
        ]
    
    def calculate_for_specific_teams(self, week_num: int, team_ids: Set[int]) -> pd.DataFrame:
        """
        Sadece belirli takımlar için puan durumu hesapla
        
        Args:
            week_num: Hangi haftaya kadar
            team_ids: Hesaplanacak takım ID'leri
            
        Returns:
            DataFrame: Sadece belirtilen takımların puan durumu
        """
        # Tam puan durumunu hesapla
        full_standings = self.calculate(week_num)
        
        if full_standings is None or len(full_standings) == 0:
            return None
        
        # Sadece istenen takımları filtrele
        filtered_standings = full_standings[full_standings['team_id'].isin(team_ids)].copy()
        
        # Sıralamayı yeniden yap
        filtered_standings = filtered_standings.sort_values(
            by=['P', 'AV', 'A'], 
            ascending=[False, False, False]
        ).reset_index(drop=True)
        
        filtered_standings['Sıra'] = range(1, len(filtered_standings) + 1)
        
        return filtered_standings
