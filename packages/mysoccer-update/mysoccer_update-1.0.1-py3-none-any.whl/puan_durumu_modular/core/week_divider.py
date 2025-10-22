"""
📅 WEEK DIVIDER
Maçları haftalara böler
"""

import pandas as pd
from typing import Optional


class WeekDivider:
    """Maçları haftalara bölen sınıf"""
    
    @staticmethod
    def divide_matches_into_weeks(df: pd.DataFrame) -> pd.DataFrame:
        """
        Maçları haftalara böl - Her takımın kaçıncı maçını oynadığına göre
        
        Args:
            df: Maç verileri DataFrame
            
        Returns:
            DataFrame: Hafta numaraları eklenmiş maç verileri
        """
        print(f"\n📅 Maçlar haftalara bölünüyor...")
        
        # DataFrame kopyası al
        df = df.copy()
        
        # Tüm takımları bul
        home_teams = set(df['home_team_id'].unique())
        away_teams = set(df['away_team_id'].unique())
        all_teams = home_teams | away_teams
        total_teams = len(all_teams)
        total_matches = len(df)
        
        print(f"   📊 Toplam {total_teams} takım bulundu")
        print(f"   ⚽ Toplam {total_matches} maç")
        
        # Beklenen hafta sayısı (çift devreli lig için)
        expected_weeks = (total_teams - 1) * 2
        matches_per_week = total_teams // 2
        
        print(f"   📅 Beklenen hafta sayısı: {expected_weeks} hafta")
        print(f"   🎯 Her haftada yaklaşık {matches_per_week} maç olmalı")
        
        # Tarihlere göre maçları sırala
        df['date_only'] = pd.to_datetime(
            df['match_date'], 
            format='%d/%m/%Y', 
            errors='coerce'
        ).dt.date
        df = df.sort_values('date_only').reset_index(drop=True)
        
        unique_dates = sorted(df['date_only'].unique())
        print(f"\n   📆 {len(unique_dates)} farklı tarihte maç oynandı")
        
        # Her takımın kaç maç oynadığını takip et
        team_match_count = {}
        
        print(f"\n   ⚙️  Her takımın maç sayısına göre hafta belirleniyor...")
        
        # Her maç için hafta numarasını belirle
        for idx, row in df.iterrows():
            home_id = row['home_team_id']
            away_id = row['away_team_id']
            
            # Bu takımların şu ana kadar kaç maç oynadığına bak
            home_count = team_match_count.get(home_id, 0)
            away_count = team_match_count.get(away_id, 0)
            
            # İki takımdan da fazla olanı al, +1 yap = bu hafta
            week_number = max(home_count, away_count) + 1
            
            # Hafta numarasını ata
            df.loc[idx, 'hafta'] = week_number
            
            # Takımların maç sayısını artır
            team_match_count[home_id] = home_count + 1
            team_match_count[away_id] = away_count + 1
        
        df['hafta'] = df['hafta'].astype(int)
        
        # En fazla maç oynayan takımı bul
        max_matches_played = max(team_match_count.values()) if team_match_count else 0
        print(f"\n   🏆 En fazla maç oynayan takım: {max_matches_played} maç")
        print(f"   📌 Son hafta: {max_matches_played}. hafta")
        
        total_weeks = max_matches_played
        
        # İstatistikler
        week_counts = df['hafta'].value_counts().sort_index()
        
        print(f"\n   ✅ {total_weeks} haftaya bölündü")
        print(f"\n   📅 Haftalara göre maç dağılımı:")
        
        WeekDivider._print_week_distribution(df, week_counts, total_weeks)
        
        # Uyarılar
        if total_weeks > expected_weeks * 1.5:
            print(f"\n   ⚠️  UYARI: Hafta sayısı beklenenin çok üstünde!")
            print(f"      Beklenen: {expected_weeks}, Gerçek: {total_weeks}")
            print(f"      Bu durum sezon henüz tamamlanmadığından olabilir")
        
        # Temizlik
        df.drop('date_only', axis=1, inplace=True)
        
        return df
    
    @staticmethod
    def _print_week_distribution(df: pd.DataFrame, week_counts: pd.Series, total_weeks: int):
        """Haftalık maç dağılımını yazdır"""
        for week in range(1, min(11, total_weeks + 1)):  # İlk 10 hafta
            if week in week_counts:
                matches_count = week_counts[week]
                week_matches = df[df['hafta'] == week]
                teams_played = set()
                for _, match in week_matches.iterrows():
                    teams_played.add(match['home_team_id'])
                    teams_played.add(match['away_team_id'])
                
                print(f"      {week}. Hafta: {matches_count} maç, {len(teams_played)} takım oynadı")
        
        if total_weeks > 10:
            print(f"      ...")
            if total_weeks in week_counts:
                matches_count = week_counts[total_weeks]
                week_matches = df[df['hafta'] == total_weeks]
                teams_played = set()
                for _, match in week_matches.iterrows():
                    teams_played.add(match['home_team_id'])
                    teams_played.add(match['away_team_id'])
                print(f"      {total_weeks}. Hafta: {matches_count} maç, {len(teams_played)} takım oynadı")
