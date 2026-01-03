# 🤖 YTMA - AI-Powered E-Commerce Automation

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/TensorFlow-2.x-orange.svg" alt="TensorFlow">
  <img src="https://img.shields.io/badge/Selenium-4.x-green.svg" alt="Selenium">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

<p align="center">
  <b>Yapay Zeka Destekli E-Ticaret Otomasyon Sistemi</b><br>
  <i>Self-Learning | Multi-Site | Pure AI Element Detection</i>
</p>

---

## 🎯 Proje Özeti

YTMA (Yakari Test & Model Automation), geleneksel web otomasyonunun ötesine geçen, **yapay zeka tabanlı** bir e-ticaret otomasyon sistemidir. Sistem, sabit ID/Class selector'lara bağlı kalmak yerine, **görsel analiz** ve **semantik anlama** kullanarak web elementlerini tespit eder.

### 🌟 Temel Özellikler

- 🧠 **AI-Powered Element Detection**: CNN tabanlı görsel tanıma
- 🔄 **Self-Learning System**: Her etkileşimden öğrenir
- 📸 **Auto Reference Capture**: Yüksek güvenli elementleri otomatik kaydeder
- 🔍 **Duplicate Detection**: Aynı referansları tekrar kaydetmez
- 🌐 **Multi-Site Support**: N11, Trendyol, Hepsiburada, Amazon ve daha fazlası
- 📊 **Detailed Reporting**: JSON, CSV ve özet raporlar

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                    YTMA ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Selenium   │───▶│   SmartBot   │───▶│  AI Brain    │  │
│  │   WebDriver  │    │   (Core)     │    │  (VisualBrain│  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Heuristics  │    │   Learning   │    │ Auto-Capture │  │
│  │   Engine     │    │   System     │    │   System     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         └───────────────────┼────────────────────┘          │
│                             ▼                               │
│                    ┌──────────────┐                         │
│                    │   Reports    │                         │
│                    │   & Logs     │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Proje Yapısı

```
YTMA/
├── 🧠 AI & Core
│   ├── ai_model.py           # VisualBrain - CNN model wrapper
│   ├── smart_bot.py          # Ana SmartBot sınıfı
│   ├── heuristics_engine.py  # Kural tabanlı element analizi
│   └── my_best_model.keras   # Eğitilmiş Keras modeli
│
├── 📚 Learning & Memory
│   ├── learning_system.py    # Pattern öğrenme sistemi
│   ├── auto_capture.py       # Otomatik referans yakalama
│   └── knowledge/            # Öğrenilen pattern'lar
│
├── 🔧 Utilities
│   ├── config.py             # Konfigürasyon ayarları
│   ├── logger.py             # Loglama sistemi
│   ├── recovery_manager.py   # Hata kurtarma
│   └── test_reporter.py      # Rapor üretici
│
├── 🧪 Test Senaryoları
│   ├── full_shopping_scenario.py  # N11 tam senaryo
│   ├── trendyol_test.py          # Trendyol testi
│   ├── hepsiburada_test.py       # Hepsiburada testi
│   ├── amazon_test.py            # Amazon testi
│   └── mega_site_test.py         # 10 site mega test
│
├── 📊 Outputs
│   ├── prototypes/           # Referans görseller
│   │   └── auto_captured/    # Otomatik yakalananlar
│   ├── reports/              # Test raporları
│   └── evidence/             # Ekran görüntüleri
│
└── 📄 Documentation
    ├── README.md             # Bu dosya
    ├── ARTICLE_INFO.md       # Makale bilgileri
    └── requirements.txt      # Python bağımlılıkları
```

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.11+
- Chrome Browser
- ChromeDriver

### Adımlar

```bash
# 1. Repository'yi klonla
git clone https://github.com/username/ytma.git
cd ytma

# 2. Virtual environment oluştur
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Environment dosyasını ayarla
cp .env.example .env
# .env dosyasını düzenle

# 5. Test çalıştır
python full_shopping_scenario.py
```

---

## 💡 Kullanım

### Basit Kullanım

```python
from selenium import webdriver
from smart_bot import SmartBot

driver = webdriver.Chrome()
bot = SmartBot(driver)

# Siteye git
driver.get("https://www.n11.com")

# AI ile element bul ve etkileşim kur
bot.interact("search", text="laptop", target_text="Ara")
bot.interact("add_to_cart", target_text="Sepete Ekle")
bot.interact("cart", target_text="Sepetim")
```

### Desteklenen Kategoriler

| Kategori | Açıklama | Örnek Elementler |
|----------|----------|------------------|
| `email` | E-posta input alanları | Login formu email |
| `password` | Şifre input alanları | Login formu şifre |
| `search` | Arama kutuları | Site arama |
| `button` | Genel butonlar | Giriş yap, Devam et |
| `add_to_cart` | Sepete ekle butonları | Sepete Ekle |
| `cart` | Sepet bağlantıları | Sepetim |
| `checkout` | Ödeme butonları | Satın Al |

---

## 📈 Performans Sonuçları

### Multi-Site Test Sonuçları

| Site | Search | Product | AddCart | Cart | Başarı |
|------|--------|---------|---------|------|--------|
| **N11** | ✅ 0.99 | ✅ | ✅ 0.25 | ✅ 0.68 | **100%** |
| **Trendyol** | ⚠️ | ✅ | ✅ 0.24 | ✅ 0.53 | **75%** |
| **Boyner** | ⚠️ | ✅ | ✅ 0.21 | ✅ 0.68 | **75%** |
| **Decathlon** | ✅ 0.97 | ✅ | ✅ 0.21 | ⚠️ | **75%** |
| **MediaMarkt** | ✅ 0.97 | ⚠️ | ✅ 0.15 | ⚠️ | **50%** |

### Öğrenme Sistemi İstatistikleri

```
✅ Toplam Pattern: 15+
✅ Toplam Başarı: 270/270
✅ Ortalama Başarı Oranı: 100%
✅ Cross-Site Learning: Aktif
```

---

## 🧠 AI Model Detayları

### Model Mimarisi

```
Input Layer: 64x64x3 (RGB Image)
    ↓
Conv2D(32, 3x3) + ReLU + MaxPooling
    ↓
Conv2D(64, 3x3) + ReLU + MaxPooling
    ↓
Conv2D(128, 3x3) + ReLU + MaxPooling
    ↓
Flatten + Dense(256) + Dropout(0.5)
    ↓
Output: Similarity Score (0-1)
```

### Skorlama Sistemi

Her element için hesaplanan skorlar:

| Skor | Ağırlık | Açıklama |
|------|---------|----------|
| **V** (Visual) | 40% | CNN görsel benzerlik |
| **S** (Semantic) | 25% | Metin analizi |
| **L** (Location) | 20% | Konum skoru |
| **T** (Tag) | 10% | HTML tag uyumu |
| **P** (Proximity) | 5% | Yakınlık bonusu |

**Final Skor** = V×0.4 + S×0.25 + L×0.2 + T×0.1 + P×0.05

---

## 🔄 Self-Learning Mekanizması

### 1. Auto-Capture System

```python
# %70-95 güvenli elementler otomatik kaydedilir
if 0.70 <= confidence <= 0.95:
    auto_capture.capture_element(element, category, site)
```

### 2. Duplicate Detection

```python
# Evrensel kontrol - tüm sitelerde aynı element tekrar kaydedilmez
existing_refs = [f for f in os.listdir() if f.startswith(f"{category}_auto_")]
if similarity > 0.95:
    return "Duplicate - Skip"
```

### 3. Fallback Reference System

```python
# Düşük skor durumunda auto_captured referanslar kullanılır
if winner_score < 0.7 and auto_refs:
    rescan_with_additional_refs()
```

---

## 📊 Raporlama

Her test sonrası üretilen raporlar:

- `*_details.csv` - Detaylı etkileşim logları
- `*_full.json` - Tam JSON rapor
- `*_summary.txt` - Özet rapor

### Örnek Rapor Çıktısı

```
📋 ÖZET:
   Toplam Süre: 92.64s
   Başarı Oranı: 100.0%
   Cache Hit Rate: 22.2%
   Ort. Tarama: 1548ms
```

---

## 🛠️ Konfigürasyon

### config.py

```python
# Model ayarları
MODEL_PATH = "my_best_model.keras"
PROTOTYPES_DIR = "prototypes"
TEMP_SCAN_IMAGE = "temp_scan.png"

# Threshold'lar
CONFIDENCE_THRESHOLD = 0.10
HIGH_CONFIDENCE = 0.70
VISUAL_WEIGHT = 0.40
```

### .env

```bash
# Site credentials (opsiyonel)
N11_EMAIL=your_email@example.com
N11_PASSWORD=your_password
```

---

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit'leyin (`git commit -m 'Add amazing feature'`)
4. Push'layın (`git push origin feature/amazing`)
5. Pull Request açın

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

---

## 👥 Ekip

- **Geliştirici**: Cagaptay
- **Proje Tipi**: Akademik / Araştırma

---

## 📞 İletişim

- **Email**: cagaptay09@gmail.com
- **GitHub**: [github.com/username/ytma](https://github.com/username/ytma)

---

<p align="center">
  <b>🚀 AI-Powered Web Automation for the Future 🚀</b>
</p>
