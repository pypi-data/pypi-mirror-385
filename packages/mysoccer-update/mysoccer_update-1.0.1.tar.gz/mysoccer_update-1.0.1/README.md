# MySoccer Update

🚀 Mackolik.com API'den futbol maç verilerini çeken profesyonel Python kütüphanesi.

## 📦 Kurulum
```bash
pip install mysoccer-update
```

## 🚀 Hızlı Başlangıç
```python
from mysoccer_update import ResultsAPI, FixturesAPI

# Sonuçları güncelle
results = ResultsAPI()
results.auto_update()  # Dün + Bugün + Yarın

# Fikstürleri çek
fixtures = FixturesAPI()
data = fixtures.get_next_3_days()
```

## ✨ Özellikler
- ✅ **Modüler Yapı** - Temiz ve genişletilebilir
- ✅ **Hızlı** - BULK INSERT ile saniyede 1000+ maç
- ✅ **Güvenilir** - Otomatik retry mekanizması
- ✅ **Kolay Kullanım** - 3 satır kod yeterli
- ✅ **Status Filtresi** - Status < 13 (0-12 arası tüm maçlar)

## 📚 Dokümantasyon

### Sonuçlar (Maçlar)
```python
from mysoccer_update import ResultsAPI

results = ResultsAPI()

# Bugünü güncelle
results.update_today()

# Tarih aralığı
results.update_date_range('01/01/2025', '31/12/2025')

# Tek tarih
results.update_single_date('15/10/2025')

# Otomatik (Dün + Bugün + Yarın)
results.auto_update()
```

### Fikstürler (Gelecek Maçlar)
```python
from mysoccer_update import FixturesAPI

fixtures = FixturesAPI()

# 3 günlük fikstür
data = fixtures.get_next_3_days()

# Veritabanına kaydet
fixtures.save_to_database(data)

# Excel'e aktar
fixtures.export_to_excel(data, 'fixtures.xlsx')
```

## ⚙️ Yapılandırma

### 🔒 Güvenli Yöntem: .env Dosyası (Önerilen)
```bash
# .env dosyası oluştur
DB_HOST=your-host.com
DB_PORT=5432
DB_NAME=mackolik_db
DB_USER=your_user
DB_PASSWORD=your_password
```

```python
from mysoccer_update import ResultsAPI

# .env dosyasından otomatik okur!
results = ResultsAPI()
results.update_today()
```

## 📊 Status Filtresi
- **Status < 13**: 0-12 arası tüm maçlar (oynanacak, oynanan, biten)
- Otomatik filtreleme yapılır

## 🔄 Versiyon 1.0.1
- ✅ Status filtresi güncellendi (status < 13)
- ✅ Tüm maç durumları destekleniyor

## 📄 Lisans
MIT License

## 🔗 Bağlantılar
- PyPI: https://pypi.org/project/mysoccer-update
