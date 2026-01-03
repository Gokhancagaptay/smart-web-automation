# config.py
import os
from pathlib import Path

# --- .env DOSYASINDAN YÜKLEME ---
# python-dotenv kurulu değilse manuel yükleme yap
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Manuel .env yükleme (dotenv yoksa)
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# --- API AYARLARI ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# API Key kontrolü
if not GEMINI_API_KEY:
    print("⚠️  UYARI: GEMINI_API_KEY bulunamadı!")
    print("   Lütfen .env dosyasını oluşturun veya environment variable tanımlayın.")
    print("   Örnek: .env.example dosyasını .env olarak kopyalayın.")

# --- MODEL VE DOSYA YOLLARI ---
MODEL_PATH = "my_best_model.keras"
PROTOTYPES_DIR = "prototypes"
TEMP_SCAN_IMAGE = "temp_scan.png"

# --- PUANLAMA MOTORU AYARLARI (HEURISTICS) ---
# Varsayılan ağırlıklar (kategori bulunamazsa kullanılır)
DEFAULT_WEIGHTS = {
    "visual": 0.30,
    "semantic": 0.35,
    "location": 0.15,
    "tag": 0.20
}

# 🆕 KATEGORİ BAZLI DİNAMİK AĞIRLIKLAR
# Her kategori için optimize edilmiş ağırlıklar
CATEGORY_WEIGHTS = {
    # Input kategorileri - Semantik ve tag daha önemli
    "email": {"visual": 0.15, "semantic": 0.45, "location": 0.15, "tag": 0.25},
    "password": {"visual": 0.15, "semantic": 0.45, "location": 0.15, "tag": 0.25},
    "search": {"visual": 0.10, "semantic": 0.40, "location": 0.35, "tag": 0.15},
    "text_input": {"visual": 0.15, "semantic": 0.45, "location": 0.15, "tag": 0.25},
    "firstName": {"visual": 0.15, "semantic": 0.45, "location": 0.15, "tag": 0.25},
    "lastName": {"visual": 0.15, "semantic": 0.45, "location": 0.15, "tag": 0.25},
    "phone": {"visual": 0.15, "semantic": 0.45, "location": 0.15, "tag": 0.25},
    
    # Buton kategorileri - Görsel ve semantik dengeli
    "button": {"visual": 0.30, "semantic": 0.35, "location": 0.15, "tag": 0.20},
    "add_to_cart": {"visual": 0.25, "semantic": 0.50, "location": 0.10, "tag": 0.15},
    "cart": {"visual": 0.20, "semantic": 0.35, "location": 0.30, "tag": 0.15},
    "login_btn": {"visual": 0.20, "semantic": 0.35, "location": 0.30, "tag": 0.15},
    "checkout": {"visual": 0.25, "semantic": 0.45, "location": 0.15, "tag": 0.15},
    "signup": {"visual": 0.25, "semantic": 0.45, "location": 0.15, "tag": 0.15},
}

# 🆕 CONFIDENCE THRESHOLD SİSTEMİ
# Farklı güven seviyelerine göre davranış belirleme
CONFIDENCE_THRESHOLDS = {
    "high": 0.60,      # Direkt tıkla, doğrulama gerekmez (düşürüldü)
    "medium": 0.35,    # Tıkla ama sonucu doğrula (düşürüldü)
    "low": 0.15,       # Alternatif stratejileri de dene (düşürüldü)
    "reject": 0.05     # Bu skorun altındaki elementleri reddet (düşürüldü)
}

# Kategori bazlı minimum skor eşikleri (EVRENSEL UYUMLULUK İÇİN DÜŞÜRÜLDÜ)
CATEGORY_MIN_THRESHOLDS = {
    "email": 0.25,
    "password": 0.25,
    "search": 0.10,       # Search için çok düşük (kritik)
    "add_to_cart": 0.15,  # Düşürüldü - farklı sitelerde çalışsın
    "cart": 0.20,
    "button": 0.15,
    "checkout": 0.15,     # Düşürüldü - farklı sitelerde çalışsın
}

# Genel eşik değeri (fallback)
SCORE_THRESHOLD = 0.10  # Düşürüldü  

def get_weights_for_category(category: str) -> dict:
    """Kategori için uygun ağırlıkları döner."""
    return CATEGORY_WEIGHTS.get(category, DEFAULT_WEIGHTS)

def get_min_threshold_for_category(category: str) -> float:
    """Kategori için minimum kabul edilebilir skoru döner."""
    return CATEGORY_MIN_THRESHOLDS.get(category, SCORE_THRESHOLD)

# --- TARAYICI AYARLARI (STEALTH MODU) ---
BROWSER_OPTIONS = [
    "--start-maximized",
    "--disable-notifications",
    "--disable-popup-blocking",
    "--disable-blink-features=AutomationControlled", # En Önemli: Otomasyonu gizle
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" # Gerçek kullanıcı maskesi
]

# --- MULTI-SITE YAPILANDIRMA (EVRENSEL SİSTEM) ---
SITE_CONFIGS = {
    "n11.com": {
        "name": "N11",
        "login_btn_selector": ("CLASS_NAME", "btnSignIn"),
        "cart_hint": "myBasket",
        "checkout_hint": "btnHolder"
    },
    "trendyol.com": {
        "name": "Trendyol",
        "login_btn_selector": ("CLASS_NAME", "link account-user"),
        "cart_hint": "basket-icon",
        "checkout_hint": "btn-success"
    },
    "hepsiburada.com": {
        "name": "Hepsiburada",
        "login_btn_selector": ("ID", "myAccount"),
        "cart_hint": "sf-OldMyAccount",
        "checkout_hint": "checkoutui-BottomButtonContainer"
    }
}

def get_site_config(url):
    """
    🆕 URL'den site konfigürasyonunu döner.
    """
    for domain, config in SITE_CONFIGS.items():
        if domain in url.lower():
            return config
    return None  # Bilinmeyen site
