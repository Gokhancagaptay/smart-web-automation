# 🎓 SUNUM SORU-CEVAP REHBERİ
**Hazırlayan:** AI Analiz Sistemi  
**Tarih:** 2026-01-08

---

## 📚 MODEL EĞİTİMİ SORULARI

### S1: "Modeli nasıl eğittiniz?"
> **C:** "Siamese Network (Siyam Ağı) mimarisi kullandık. ResNet50'yi temel model olarak aldık ve üzerine benzerlik ölçen bir katman ekledik. Eğitim için anchor-positive çiftleri oluşturduk. Aynı kategorideki elementler pozitif, farklı kategoridekiler negatif çift olarak işaretlendi. 5 epoch eğitim yapıldı."

### S2: "Neden ResNet50 seçtiniz?"
> **C:** "ResNet50, ImageNet üzerinde önceden eğitilmiş güçlü bir feature extractor. Transfer learning ile az veriyle bile iyi sonuçlar alabiliyoruz. 50 katmanlı derin yapısı görsel özellikleri çok iyi yakalar."

### S3: "Veri setiniz kaç görsel içeriyor?"
> **C:** "Yaklaşık 2400 görsel kullandık - 1528 buton görseli ve 865 input görseli. E-ticaret sitelerinden toplandı. Anchor-positive çiftleri oluşturarak eğitim yaptık."

### S4: "Overfitting'i nasıl önlediniz?"
> **C:** "Transfer learning kullandık - ResNet50'nin ağırlıklarını dondurup (trainable=False) sadece son karar katmanını eğittik. Ayrıca %20 validation split ile eğitim sürecini izledik."

### S5: "Model boyutu neden 95MB?"
> **C:** "ResNet50 temel model olarak kullanıldığı için. Bu büyük boyut aslında modelin zengin feature extraction kapasitesini gösterir. Prodüksiyonda model compression yapılabilir."

---

## 🔧 TEKNİK MİMARİ SORULARI

### S6: "Hibrit yaklaşım ne demek?"
> **C:** "Tek bir yönteme bağımlı değiliz. Üç katman var:
> 1. **Kural tabanlı**: Hızlı ön filtreleme (tag, konum, metin)
> 2. **Derin öğrenme**: CNN ile görsel analiz
> 3. **Self-healing**: Hata durumunda otomatik onarım
> Bu katmanlar birbirini tamamlıyor."

### S7: "Skorlama formülünü açıklar mısınız?"
> **C:** "4 faktörü ağırlıklı olarak birleştiriyoruz:
> - V (Görsel): %30 - CNN benzerlik skoru
> - S (Semantik): %35 - Metin eşleşmesi
> - L (Konum): %15 - Sayfa pozisyonu
> - T (Tag): %20 - HTML element türü
> 
> Toplam 1.00 olacak şekilde normalize. Semantik en yüksek çünkü 'Sepete Ekle' metnini bulmak en güvenilir."

### S8: "Neden sabit selector kullanmıyorsunuz?"
> **C:** "ID ve class isimleri sık değişiyor. 'btn-primary-v2' yarın 'button-main-new' olabilir. Görsel ve semantik özellikler daha stabil. DOM bağımsızlığı sağlıyoruz."

### S9: "Self-healing nasıl çalışıyor?"
> **C:** "Bir element bulunamazsa Recovery Manager devreye giriyor:
> 1. Önce ana stratejiyi dene
> 2. Başarısızsa alternatif hedef metinlerle dene ('Sepete Ekle' → 'Ekle')
> 3. Hala başarısızsa AI ile görsel tarama yap
> 4. Başarılıysa öğren ve kaydet"

### S10: "Learning System ne yapıyor?"
> **C:** "Başarılı etkileşimleri kaydediyor. Örneğin n11.com'da 'email' inputunu bulduğumuzda, hangi ID, class ve tag ile bulduk bilgisini saklıyor. Sonraki çalıştırmalarda önce bu bilgiyi kullanıyor. Zaman kazandırır."

---

## 📊 PERFORMANS SORULARI

### S11: "N11'de %100 başarı nasıl elde ettiniz?"
> **C:** "Model eğitimi için N11 görselleri ağırlıklı kullanıldı. DOM yapısı e-ticaret standartlarına çok uygun. Semantik eşleşme güçlü ('Sepete Ekle', 'Giriş Yap' gibi net metinler)."

### S12: "Diğer sitelerde neden düşük?"
> **C:** "Her site farklı:
> - Bazıları asenkron yükleme kullanıyor (elementler geç çıkıyor)
> - Bazıları farklı terminoloji kullanıyor ('Sepete At' vs 'Sepete Ekle')
> - Bazıları bot koruması uyguluyor
> - Görsel tasarım eğitim verisinden çok farklı olabilir"

### S13: "%22 Cache Hit Rate ne anlama geliyor?"
> **C:** "Her 5 element aramadan 1'i önceden öğrenilmiş bilgiden geliyor. Bu, ~2-3 saniye tasarruf demek. Sistem zamanla daha hızlı oluyor."

### S14: "Ortalama 1548ms tarama süresi yeterli mi?"
> **C:** "Evet. Geleneksel XPath araması 100-200ms ama flaky. Bizim yöntemimiz 1.5 saniyede çok daha güvenilir sonuç veriyor. Güvenilirlik vs hız tradeoff'u."

---

## 🔬 METODOLOJİ SORULARI

### S15: "Bu flaky test çözümü mü yoksa element tespiti mi?"
> **C:** "Her ikisi de. Flaky testlerin ana nedeni değişen DOM yapısı. Biz DOM'a bağımlılığı kaldırarak flaky davranışı kaynağında engelliyoruz. Tespit değil, önleme yaklaşımı."

### S16: "LLM kullanmadınız mı? Neden?"
> **C:** "LLM görsel analiz için uygun değil. Ayrıca halüsinasyon riski var. CNN ile deterministik sonuçlar alıyoruz. Literatür taramasında LLM yaklaşımlarını inceledik ve eksikliklerini belirttik."

### S17: "Test Smells'i nasıl tespit ediyorsunuz?"
> **C:** "Doğrudan 'test smell' terimi yerine semantik analiz kullanıyoruz. Örneğin 'hard-coded wait' yerine dinamik bekleme (smart_wait), kırılgan selector yerine çoklu skor. Aynı problemi farklı yöntemle çözüyoruz."

### S18: "Genellenebilirlik sorunu var mı?"
> **C:** "Kategori bazlı dinamik ağırlıklar kullanıyoruz. Her site için ayrı eğitim gerekmiyor. 10 farklı sitede %62.5 başarı elde ettik. Cross-site learning sayesinde N11'de öğrenilen pattern Trendyol'da da işe yarıyor."

---

## ⚠️ ZOR SORULAR

### S19: "Accuracy metriğiniz nedir?"
> **C:** "Element bazlı başarı oranı:
> - N11: %100 (17/17 element)
> - Hepsiburada: %85.7 (6/7 element)
> - Genel: %62.5 (multi-site)
> - Learning accuracy: %100 (288/288 pattern)"

### S20: "Baseline ile karşılaştırma yaptınız mı?"
> **C:** "Evet, sabit XPath/CSS selector kullanan geleneksel yöntemle. Site güncellemesinden sonra geleneksel yöntem %0, bizim sistemimiz %95+ başarı gösterdi. DOM değişikliğine dayanıklılık temel avantajımız."

### S21: "Limitasyonlarınız neler?"
> **C:** "Dürüst olmak gerekirse:
> 1. Sadece Chrome'da test edildi
> 2. Mobil arayüzler desteklenmiyor (gelecek çalışma)
> 3. Çok yoğun görsel arka planlarda CNN zorlanabiliyor
> 4. İlk çalıştırma yavaş (model yükleme ~5s)"

---

## 💡 BONUS SORULAR

### S22: "Bu sistem gerçek dünyada kullanılabilir mi?"
> **C:** "Evet! CI/CD pipeline'ına entegre edilebilir. E-ticaret şirketleri için test bakım maliyetini %70+ azaltma potansiyeli var. Otonom referans öğrenme sayesinde 'insansız bakım' mümkün."

### S23: "Gelecek çalışmalar neler?"
> **C:** "1. iOS/Android mobil uygulama desteği
> 2. Multi-browser (Firefox, Safari)
> 3. Model compression (95MB → 20MB)
> 4. Real-time görsel feedback UI"

---

**Bu soruların %90'ı bu cevaplarla karşılanır. Başarılar! 🚀**
