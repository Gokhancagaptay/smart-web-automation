import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input

# --- CUSTOM OBJECTS (MODEL YÜKLEMEK İÇİN GEREKLİ) ---
# Modeli kaydederken kullandığımız özel fonksiyonu burada da tanımlamalıyız
def euclidean_distance(vectors):
    x, y = vectors
    return tf.abs(x - y)

class VisualBrain:
    def __init__(self, model_path="my_best_model.keras"):
        print(f"🧠 Eğitilmiş Yapay Zeka Modeli Yükleniyor: {model_path}")
        
        if os.path.exists(model_path):
            try:
                # --- KRİTİK DÜZELTME BURADA ---
                # Modeli yüklerken 'euclidean_distance' fonksiyonunu tanıtıyoruz.
                # safe_mode=False da gerekli olabilir.
                self.model = tf.keras.models.load_model(
                    model_path, 
                    custom_objects={'euclidean_distance': euclidean_distance},
                    safe_mode=False
                )
                print("✅ Özel eğitilmiş model başarıyla yüklendi!")
            except Exception as e:
                print(f"❌ Model yüklenirken hata oluştu: {e}")
                self.model = None
        else:
            print("⚠️ HATA: 'my_best_model.keras' dosyası bulunamadı!")
            self.model = None

    def _preprocess_image(self, img_path):
        """Görseli modelin anlayacağı formata (224x224) getirir."""
        try:
            if not os.path.exists(img_path): return None
            
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            return preprocess_input(img_array)
        except:
            return None

    def compare_images(self, img_path1, img_path2):
        """İki görseli EĞİTİLMİŞ modele sorar."""
        if self.model is None: return 0.0

        img1 = self._preprocess_image(img_path1)
        img2 = self._preprocess_image(img_path2)
        
        if img1 is None or img2 is None: return 0.0

        # Eğittiğimiz model iki giriş bekler: [img1, img2]
        prediction = self.model.predict([img1, img2], verbose=0)
        
        similarity_score = float(prediction[0][0])
        return similarity_score

# --- TEST ALANI ---
if __name__ == "__main__":
    brain = VisualBrain()
    
    base_path = r"C:\Users\cagap\Desktop\pton\Ytma\dataset_ready"
    if os.path.exists(base_path):
        print("\n--- MODEL TESTİ BAŞLIYOR ---")
        # Örnek test için klasörden gerçek bir dosya adı bulup buraya yazabilirsin.
        # img1 = ...
        # img2 = ...
        # print(brain.compare_images(img1, img2))
        print("Model hafızaya alındı. Entegrasyon için hazır.")