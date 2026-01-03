"""
🔄 SELF-RECOVERY MANAGER - Akıllı Hata Yönetimi
Bir yol başarısız olursa otomatik olarak alternatif yollar dener
"""

from typing import Callable, List, Dict, Any
import time
from logger import get_recovery_logger  # 📝 LOGGING

# Logger instance
log = get_recovery_logger()

class RecoveryManager:
    """
    Hata durumlarında alternatif stratejiler uygular
    """
    
    def __init__(self, max_retries=3, reporter=None):
        self.max_retries = max_retries
        self.reporter = reporter
        
        # Başarısız olan eylemler ve alternatifleri
        self.recovery_strategies = {
            "cart": self._cart_recovery_strategies,
            "add_to_cart": self._add_to_cart_recovery_strategies,
            "login": self._login_recovery_strategies,
            "search": self._search_recovery_strategies,
            "checkout": self._checkout_recovery_strategies,
        }
        
        log.info("Self-Recovery Manager aktif!")
    
    def attempt_with_recovery(self, action_type: str, primary_action: Callable, 
                            context: Dict[str, Any] = None) -> bool:
        """
        Bir eylemi dene, başarısız olursa alternatif yolları dene
        
        Args:
            action_type: Eylem tipi ("cart", "add_to_cart", etc.)
            primary_action: Ana eylem fonksiyonu
            context: Eylem için gerekli context (driver, bot, url, etc.)
        
        Returns:
            bool: Başarı durumu
        """
        context = context or {}
        
        # 1. Ana yöntemi dene
        log.info(f"Ana yöntem: {action_type}")
        if primary_action():
            log.info("Başarılı!")
            return True
        
        log.warning("Ana yöntem başarısız!")
        
        # 2. Reporter'a uyarı
        if self.reporter:
            self.reporter.log_warning(f"{action_type} ana yöntemi başarısız, alternatifler deneniyor...")
        
        # 3. Alternatif stratejileri dene
        if action_type in self.recovery_strategies:
            strategies = self.recovery_strategies[action_type](context)
            
            for i, (strategy_name, strategy_func) in enumerate(strategies, 1):
                log.info(f"Alternatif #{i}: {strategy_name}")
                
                try:
                    if strategy_func():
                        log.info(f"{strategy_name} BAŞARILI!")
                        
                        if self.reporter:
                            self.reporter.log_warning(
                                f"{action_type} alternatif yöntemle başarıldı: {strategy_name}"
                            )
                        
                        return True
                    else:
                        log.warning(f"{strategy_name} başarısız.")
                        
                except Exception as e:
                    log.error(f"{strategy_name} hata: {e}")
                
                time.sleep(1)  # Kısa bekleme
        
        # 4. Tüm yöntemler başarısız
        log.error(f"{action_type}: Tüm alternatif yöntemler tükendi!")
        
        if self.reporter:
            self.reporter.log_error(
                error_type="RecoveryFailed",
                message=f"{action_type} için tüm recovery stratejileri başarısız"
            )
        
        return False
    
    # --- RECOVERY STRATEJİLERİ ---
    
    def _cart_recovery_strategies(self, context):
        """Sepete gitmek için alternatif yollar"""
        driver = context.get("driver")
        bot = context.get("bot")
        site_url = context.get("site_url")
        
        strategies = []
        
        # Strateji 1: URL ile direkt git
        if driver and site_url:
            def url_cart():
                if "n11" in site_url:
                    driver.get("https://www.n11.com/sepetim")
                elif "hepsiburada" in site_url:
                    driver.get("https://www.hepsiburada.com/sepetim")
                elif "trendyol" in site_url:
                    driver.get("https://www.trendyol.com/sepet")
                time.sleep(2)
                return "sepet" in driver.current_url.lower() or "cart" in driver.current_url.lower()
            
            strategies.append(("URL ile direkt sepete git", url_cart))
        
        # Strateji 2: Header'da ikon ara
        if bot:
            def header_icon():
                return bot.hybrid_click([], target_text="🛒", use_recovery=False)
            
            strategies.append(("Header'daki sepet ikonuna tıkla", header_icon))
        
        # Strateji 3: Alt metinle ara (sepet yerine basket, cart)
        if bot:
            def alt_text():
                return bot.hybrid_click([], target_text="cart", use_recovery=False)
            
            strategies.append(("'cart' keyword ile ara", alt_text))
        
        return strategies
    
    def _add_to_cart_recovery_strategies(self, context):
        """Sepete ekleme için alternatif yollar"""
        bot = context.get("bot")
        driver = context.get("driver")
        
        strategies = []
        
        # 🆕 ÖNEMLI: use_recovery=False ile çağır, yoksa sonsuz döngü olur!
        
        # Strateji 1: Farklı kelimelerle ara
        if bot:
            def try_hemen_al():
                return bot.hybrid_click([], target_text="Hemen Al", use_recovery=False)
            
            strategies.append(("'Hemen Al' butonu ile dene", try_hemen_al))
        
        # Strateji 2: Sayfayı scroll et ve tekrar dene
        if bot and driver:
            def scroll_and_retry():
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(1)
                return bot.hybrid_click([], target_text="Sepete Ekle", use_recovery=False)
            
            strategies.append(("Sayfayı scroll et ve tekrar dene", scroll_and_retry))
        
        # Strateji 3: Sayfayı yenile ve tekrar dene
        if bot and driver:
            def refresh_and_retry():
                driver.refresh()
                time.sleep(2)
                return bot.hybrid_click([], target_text="Sepete Ekle", use_recovery=False)
            
            strategies.append(("Sayfayı yenile ve tekrar dene", refresh_and_retry))
        
        return strategies
    
    def _login_recovery_strategies(self, context):
        """Giriş yapmak için alternatif yollar"""
        bot = context.get("bot")
        driver = context.get("driver")
        
        strategies = []
        
        # Strateji 1: Farklı login buton metinleri
        if bot:
            def try_sign_in():
                return bot.hybrid_click([], target_text="Sign In", use_recovery=False)
            
            strategies.append(("'Sign In' ile dene", try_sign_in))
        
        # Strateji 2: URL ile direkt login sayfasına git
        if driver:
            def url_login():
                site_url = driver.current_url
                if "n11" in site_url:
                    driver.get("https://www.n11.com/giris-yap")
                elif "hepsiburada" in site_url:
                    driver.get("https://www.hepsiburada.com/giris")
                elif "trendyol" in site_url:
                    driver.get("https://www.trendyol.com/giris")
                time.sleep(2)
                return "giris" in driver.current_url.lower() or "login" in driver.current_url.lower()
            
            strategies.append(("URL ile direkt login sayfasına git", url_login))
        
        return strategies
    
    def _search_recovery_strategies(self, context):
        """Arama için alternatif yollar"""
        bot = context.get("bot")
        driver = context.get("driver")
        search_term = context.get("search_term", "laptop")
        
        strategies = []
        
        # Strateji 1: URL parametresi ile direkt ara
        if driver:
            def url_search():
                site_url = driver.current_url
                if "n11" in site_url:
                    driver.get(f"https://www.n11.com/arama?q={search_term}")
                elif "hepsiburada" in site_url:
                    driver.get(f"https://www.hepsiburada.com/ara?q={search_term}")
                elif "trendyol" in site_url:
                    driver.get(f"https://www.trendyol.com/sr?q={search_term}")
                time.sleep(3)
                return True
            
            strategies.append(("URL ile direkt arama yap", url_search))
        
        # Strateji 2: Sayfayı yenile ve tekrar ara
        if bot and driver:
            def refresh_and_search():
                driver.refresh()
                time.sleep(2)
                return bot.hybrid_type([], search_term, category="search", use_recovery=False)
            
            strategies.append(("Sayfayı yenile ve tekrar ara", refresh_and_search))
        
        return strategies
    
    def _checkout_recovery_strategies(self, context):
        """Ödeme için alternatif yollar"""
        bot = context.get("bot")
        driver = context.get("driver")
        
        strategies = []
        
        # Strateji 1: Farklı checkout metinleri
        if bot:
            def try_tamamla():
                return bot.hybrid_click([], target_text="Tamamla", use_recovery=False)
            
            strategies.append(("'Tamamla' butonu ile dene", try_tamamla))
        
        # Strateji 2: Scroll ve tekrar
        if bot and driver:
            def scroll_and_checkout():
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                return bot.hybrid_click([], target_text="Alışverişi Tamamla", use_recovery=False)
            
            strategies.append(("En alta scroll et ve dene", scroll_and_checkout))
        
        return strategies

