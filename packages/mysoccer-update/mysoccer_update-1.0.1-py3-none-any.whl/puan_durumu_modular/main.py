"""
🏆 HAFTALIK PUAN DURUMU OLUŞTURUCU - MODÜLER VERSİYON
Her hafta için puan durumu hesaplar ve Excel'e yazar

Kullanım:
    python main.py --season-id 69172
    python main.py --season-id 69172 --last-n 8
"""

import sys
import argparse
from datetime import datetime

# Modülleri içe aktar
from core import DatabaseManager, MatchLoader, WeekDivider
from calculators import StandingsCalculator
from exporters import WeeklyStandingsExporter
from utils import ProgressPrinter, DataFrameHelper


class WeeklyStandingsGenerator:
    """Haftalık puan durumu oluşturucu ana sınıf"""
    
    def __init__(self, season_id: int, last_n_matches: int = 8):
        """
        Args:
            season_id: Sezon ID'si
            last_n_matches: Son N maç formu için maç sayısı (varsayılan: 8)
        """
        self.season_id = season_id
        self.last_n_matches = last_n_matches
        
        # Bileşenleri başlat
        self.db_manager = DatabaseManager()
        self.match_loader = MatchLoader(self.db_manager)
        self.progress = ProgressPrinter()
        
        # Veri saklamak için
        self.df_all = None
        self.df_last_n = None
        self.league_name = None
        self.country = None
        self.total_weeks = 0
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.progress.print_header("🏆 HAFTALIK PUAN DURUMU OLUŞTURUCU - MODÜLER")
        self.progress.print_info(f"⏰ Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Maçları yükle
        self._load_matches()
        
        # 2. Haftalara böl
        self._divide_into_weeks()
        
        # 3. Puan durumlarını hesapla ve Excel'e aktar
        self._calculate_and_export()
        
        # 4. Özet bilgi
        self._print_final_summary()
    
    def _load_matches(self):
        """Maçları yükle"""
        self.progress.print_section("📥 1. AŞAMA: MAÇLARI YÜKLEME")
        
        # Tüm maçları yükle
        self.df_all = self.match_loader.load_matches_by_season(self.season_id)
        
        if len(self.df_all) == 0:
            self.progress.print_error(f"Season ID {self.season_id} için maç bulunamadı!")
            sys.exit(1)
        
        # Lig bilgilerini sakla
        self.league_name = self.df_all['league'].iloc[0]
        self.country = self.df_all['country'].iloc[0]
        
        # Son N maç filtresini uygula
        self.df_last_n = self.match_loader.filter_last_n_matches_per_team(
            self.df_all, 
            self.last_n_matches
        )
    
    def _divide_into_weeks(self):
        """Maçları haftalara böl"""
        self.progress.print_section("📅 2. AŞAMA: HAFTALARA BÖLME")
        
        # Tüm maçları haftalara böl
        self.progress.print_info("📊 TÜM MAÇLAR haftalara bölünüyor...")
        self.df_all = WeekDivider.divide_matches_into_weeks(self.df_all)
        
        # Son N maçları haftalara böl
        self.progress.print_info(f"\n🔥 SON {self.last_n_matches} MAÇ haftalara bölünüyor...")
        self.df_last_n = WeekDivider.divide_matches_into_weeks(self.df_last_n)
        
        self.total_weeks = self.df_all['hafta'].max()
        self.progress.print_success(f"Toplam {self.total_weeks} hafta bulundu")
    
    def _calculate_and_export(self):
        """Puan durumlarını hesapla ve Excel'e aktar"""
        self.progress.print_section("🧮 3. AŞAMA: HESAPLAMA VE EXPORT")
        
        # Excel exporter oluştur
        exporter = WeeklyStandingsExporter(
            self.season_id, 
            self.league_name, 
            self.country
        )
        
        # Tüm maçlar için hesapla
        self._calculate_all_matches(exporter)
        
        # Son N maç için hesapla
        self._calculate_last_n_matches(exporter)
        
        # Excel'e aktar
        self.summary = exporter.export_with_summary()
    
    def _calculate_all_matches(self, exporter: WeeklyStandingsExporter):
        """Tüm maçlar için puan durumu hesapla"""
        self.progress.print_info("\n📊 TÜM MAÇLAR İÇİN HESAPLANIYOR...")
        
        all_standings = []
        all_matches = []
        standings_by_week = {}
        
        # Hesaplayıcı oluştur
        calc = StandingsCalculator(self.df_all)
        
        for week in range(1, self.total_weeks + 1):
            self.progress.print_info(f"   📊 {week}. Hafta (Tüm Maçlar)...", indent=1)
            
            # Puan durumunu hesapla
            standings_df = calc.calculate(week)
            
            if standings_df is None or len(standings_df) == 0:
                continue
            
            # Season ID, League, Country, Hafta ekle
            standings_df.insert(0, 'season_id', self.season_id)
            standings_df.insert(1, 'League', self.league_name)
            standings_df.insert(2, 'Country', self.country)
            standings_df.insert(3, 'Hafta', week)
            
            all_standings.append(standings_df)
            
            # Bu haftanın istatistiklerini sakla
            standings_by_week[week] = DataFrameHelper.create_standings_dict(standings_df)
            
            # Bu haftanın maçlarını al
            week_matches = self.df_all[self.df_all['hafta'] == week].copy()
            if len(week_matches) > 0:
                # İstatistikleri ekle
                week_matches = self._add_statistics_to_matches(
                    week_matches, 
                    standings_by_week.get(week - 1, {})
                )
                all_matches.append(week_matches)
        
        # Excel'e ekle
        if all_standings:
            import pandas as pd
            combined_standings = pd.concat(all_standings, ignore_index=True)
            exporter.add_standings_sheet('Haftalık Puan Durumu', combined_standings, is_last_8=False)
        
        if all_matches:
            import pandas as pd
            combined_matches = pd.concat(all_matches, ignore_index=True)
            exporter.add_matches_sheet('Haftalık Maçlar', combined_matches, is_last_8=False)
    
    def _calculate_last_n_matches(self, exporter: WeeklyStandingsExporter):
        """Son N maç için puan durumu hesapla"""
        self.progress.print_info(f"\n🔥 SON {self.last_n_matches} MAÇ İÇİN HESAPLANIYOR...")
        
        all_standings = []
        all_matches = []
        standings_by_week = {}
        
        # Hesaplayıcı oluştur
        calc = StandingsCalculator(self.df_last_n)
        
        for week in range(1, self.total_weeks + 1):
            self.progress.print_info(f"   🔥 {week}. Hafta (Son {self.last_n_matches} Maç)...", indent=1)
            
            # Puan durumunu hesapla
            standings_df = calc.calculate(week)
            
            if standings_df is None or len(standings_df) == 0:
                continue
            
            # Season ID, League, Country, Hafta ekle
            standings_df.insert(0, 'season_id', self.season_id)
            standings_df.insert(1, 'League', self.league_name)
            standings_df.insert(2, 'Country', self.country)
            standings_df.insert(3, 'Hafta', week)
            
            all_standings.append(standings_df)
            
            # Bu haftanın istatistiklerini sakla
            standings_by_week[week] = DataFrameHelper.create_standings_dict(standings_df)
            
            # Bu haftanın maçlarını al
            week_matches = self.df_last_n[self.df_last_n['hafta'] == week].copy()
            if len(week_matches) > 0:
                # İstatistikleri ekle
                week_matches = self._add_statistics_to_matches(
                    week_matches, 
                    standings_by_week.get(week - 1, {})
                )
                all_matches.append(week_matches)
        
        # Excel'e ekle
        if all_standings:
            import pandas as pd
            combined_standings = pd.concat(all_standings, ignore_index=True)
            exporter.add_standings_sheet(f'Son {self.last_n_matches} Maç - Puan Durumu', combined_standings, is_last_8=True)
        
        if all_matches:
            import pandas as pd
            combined_matches = pd.concat(all_matches, ignore_index=True)
            exporter.add_matches_sheet(f'Son {self.last_n_matches} Maç - Maçlar', combined_matches, is_last_8=True)
    
    def _add_statistics_to_matches(self, matches_df, prev_week_stats):
        """Maçlara önceki hafta istatistiklerini ekle"""
        matches_df = matches_df.copy()
        
        if not prev_week_stats:
            return matches_df
        
        # Her maç için istatistikleri ekle
        for idx, match in matches_df.iterrows():
            home_id = match['home_team_id']
            away_id = match['away_team_id']
            
            # Ev sahibi
            matches_df.loc[idx, 'home_rank'] = prev_week_stats.get('rank', {}).get(home_id, '-')
            matches_df.loc[idx, 'home_played'] = prev_week_stats.get('played', {}).get(home_id, 0)
            matches_df.loc[idx, 'home_over'] = prev_week_stats.get('over', {}).get(home_id, 0)
            matches_df.loc[idx, 'home_under'] = prev_week_stats.get('under', {}).get(home_id, 0)
            matches_df.loc[idx, 'home_over_ok'] = prev_week_stats.get('over_ok', {}).get(home_id, 0)
            matches_df.loc[idx, 'home_under_ok'] = prev_week_stats.get('under_ok', {}).get(home_id, 0)
            matches_df.loc[idx, 'home_btts'] = prev_week_stats.get('btts', {}).get(home_id, 0)
            matches_df.loc[idx, 'home_btts_no'] = prev_week_stats.get('btts_no', {}).get(home_id, 0)
            
            # Deplasman
            matches_df.loc[idx, 'away_rank'] = prev_week_stats.get('rank', {}).get(away_id, '-')
            matches_df.loc[idx, 'away_played'] = prev_week_stats.get('played', {}).get(away_id, 0)
            matches_df.loc[idx, 'away_over'] = prev_week_stats.get('over', {}).get(away_id, 0)
            matches_df.loc[idx, 'away_under'] = prev_week_stats.get('under', {}).get(away_id, 0)
            matches_df.loc[idx, 'away_over_ok'] = prev_week_stats.get('over_ok', {}).get(away_id, 0)
            matches_df.loc[idx, 'away_under_ok'] = prev_week_stats.get('under_ok', {}).get(away_id, 0)
            matches_df.loc[idx, 'away_btts'] = prev_week_stats.get('btts', {}).get(away_id, 0)
            matches_df.loc[idx, 'away_btts_no'] = prev_week_stats.get('btts_no', {}).get(away_id, 0)
        
        return matches_df
    
    def _print_final_summary(self):
        """Son özet bilgileri yazdır"""
        self.progress.print_section("📊 ÖZET RAPOR")
        
        print(f"\n{'='*80}")
        print(f"📁 Dosya: {self.summary['filename']}")
        print(f"🏆 Lig: {self.league_name}")
        print(f"🌍 Ülke: {self.country}")
        print(f"📊 Toplam {self.total_weeks} hafta işlendi")
        print(f"\n📋 Oluşturulan Sayfalar:")
        for sheet in self.summary['sheets']:
            row_count = self.summary.get(f'{sheet}_rows', 0)
            print(f"   • {sheet}: {row_count} satır")
        print(f"\n⏰ Bitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description='Haftalık Puan Durumu Oluşturucu - Modüler Versiyon'
    )
    parser.add_argument(
        '--season-id', 
        type=int, 
        required=True,
        help='Sezon ID\'si (örn: 69172)'
    )
    parser.add_argument(
        '--last-n', 
        type=int, 
        default=8,
        help='Son N maç formu için maç sayısı (varsayılan: 8)'
    )
    
    args = parser.parse_args()
    
    # Generator oluştur ve çalıştır
    generator = WeeklyStandingsGenerator(
        season_id=args.season_id,
        last_n_matches=args.last_n
    )
    
    try:
        generator.run()
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
