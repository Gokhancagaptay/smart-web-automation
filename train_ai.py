import os
import numpy as np
import random
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Flatten, Dense, Dropout, Lambda
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.optimizers import Adam

# --- AYARLAR ---
# Veri seti yolunu kendi bilgisayarına göre ayarla
DATASET_PATH = r"C:\Users\cagap\Desktop\pton\Ytma\dataset_ready" 
MODEL_SAVE_PATH = "my_best_model.keras" 
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 5 

def load_image(img_path):
    """Resmi yükler ve modelin anlayacağı formata çevirir."""
    try:
        img = image.load_img(img_path, target_size=IMG_SIZE)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        return preprocess_input(img_array)[0]
    except:
        return None

def create_pairs(dataset_path):
    """Veri setinden Çiftler (Pairs) oluşturur."""
    pairs = []
    labels = []
    
    for category in os.listdir(dataset_path):
        cat_path = os.path.join(dataset_path, category)
        if not os.path.isdir(cat_path): continue
        
        all_files = os.listdir(cat_path)
        anchors = [f for f in all_files if 'anchor' in f]
        
        print(f"📂 '{category}' kategorisinde {len(anchors)} veri işleniyor...")

        for anchor_file in anchors:
            unique_id = anchor_file.split('_')[0]
            positive_file = f"{unique_id}_positive.png"
            
            if positive_file in all_files:
                anchor_path = os.path.join(cat_path, anchor_file)
                pos_path = os.path.join(cat_path, positive_file)
                
                try:
                    img_a = load_image(anchor_path)
                    img_p = load_image(pos_path)
                    
                    if img_a is None or img_p is None: continue

                    # Pozitif Çift
                    pairs.append([img_a, img_p])
                    labels.append(1.0) 
                    
                    # Negatif Çift
                    neg_file = random.choice(anchors)
                    while neg_file == anchor_file:
                        neg_file = random.choice(anchors)
                    
                    neg_path = os.path.join(cat_path, neg_file)
                    img_n = load_image(neg_path)
                    
                    if img_n is not None:
                        pairs.append([img_a, img_n])
                        labels.append(0.0) 
                except:
                    continue

    return np.array(pairs), np.array(labels)

def build_siamese_model():
    """Siyam Ağı mimarisini kurar."""
    # 1. Temel Model (ResNet50)
    base_cnn = ResNet50(weights="imagenet", include_top=False, input_shape=IMG_SIZE + (3,), pooling="avg")
    
    for layer in base_cnn.layers:
        layer.trainable = False

    # 2. İki Giriş Kapısı
    input_1 = Input(IMG_SIZE + (3,))
    input_2 = Input(IMG_SIZE + (3,))

    # 3. İkisi de aynı beyinden geçiyor
    feat_1 = base_cnn(input_1)
    feat_2 = base_cnn(input_2)

    # 4. Mesafe Hesaplama (Lambda Sorununu Çözen Kısım)
    def euclidean_distance(vectors):
        x, y = vectors
        return tf.abs(x - y)

    distance = Lambda(euclidean_distance)([feat_1, feat_2])

    # 5. Karar Katmanı
    prediction = Dense(1, activation='sigmoid')(distance)

    model = Model(inputs=[input_1, input_2], outputs=prediction)
    return model

# --- EĞİTİMİ BAŞLAT ---
if __name__ == "__main__":
    if not os.path.exists(DATASET_PATH):
        print(f"❌ HATA: Veri seti klasörü bulunamadı: {DATASET_PATH}")
        exit()

    print("🚀 Veriler hazırlanıyor... (Bu biraz sürebilir)")
    pairs, labels = create_pairs(DATASET_PATH)
    
    if len(pairs) == 0:
        print("❌ HATA: Hiç veri çifti oluşturulamadı! Klasörleri kontrol et.")
        exit()
        
    print(f"✅ Toplam {len(pairs)} adet eğitim çifti oluşturuldu.")

    print("🧠 Model inşa ediliyor...")
    model = build_siamese_model()
    model.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

    print("🔥 EĞİTİM BAŞLIYOR! (Kahveni al, arkana yaslan)")
    history = model.fit(
        [pairs[:, 0], pairs[:, 1]], labels,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_split=0.2 
    )

    print(f"💾 Model kaydediliyor: {MODEL_SAVE_PATH}")
    model.save(MODEL_SAVE_PATH)
    print("🎉 TEBRİKLER! Kendi Yapay Zeka modelini eğittin.")