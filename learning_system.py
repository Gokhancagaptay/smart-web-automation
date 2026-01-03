"""
🧠 LEARNING SYSTEM - Öğrenen AI Sistemi
Başarılı etkileşimleri kaydeder ve sonraki testlerde öncelik verir
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from logger import get_learning_logger  # 📝 LOGGING

# Logger instance
log = get_learning_logger()

class LearningSystem:
    """
    Başarılı element etkileşimlerini öğrenir ve sonraki testlerde kullanır
    """
    
    def __init__(self, knowledge_file="knowledge/learned_patterns.json"):
        self.knowledge_file = Path(knowledge_file)
        self.knowledge_file.parent.mkdir(exist_ok=True)
        
        # Öğrenilmiş bilgi deposu
        self.knowledge_base = self._load_knowledge()
        
        # Bu oturumda öğrenilenler
        self.session_learnings = []
        
        log.info("Learning System aktif!")
        log.info(f"Bilgi Deposu: {len(self.knowledge_base)} öğrenilmiş pattern")
    
    def _load_knowledge(self) -> Dict:
        """Önceki öğrenmeleri yükle"""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                log.warning("Bilgi deposu okunamadı, yeni oluşturuluyor...")
                return {}
        return {}
    
    def _save_knowledge(self):
        """Öğrenmeleri diske kaydet"""
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
    
    def learn_success(self, site: str, action_type: str, category: str, 
                     element_info: Dict[str, str], score: float):
        """
        Başarılı bir etkileşimi öğren
        
        Args:
            site: Hangi site (n11, hepsiburada, etc.)
            action_type: CLICK veya TYPE
            category: Element kategorisi (email, password, cart, etc.)
            element_info: Element bilgisi (id, class, tag, text)
            score: AI skoru
        """
        # Pattern key oluştur
        pattern_key = f"{site}_{category}"
        
        # Eğer bu pattern yoksa oluştur
        if pattern_key not in self.knowledge_base:
            self.knowledge_base[pattern_key] = {
                "site": site,
                "category": category,
                "attempts": 0,
                "successes": 0,
                "best_selectors": [],
                "last_updated": None
            }
        
        pattern = self.knowledge_base[pattern_key]
        
        # İstatistikleri güncelle
        pattern["attempts"] += 1
        pattern["successes"] += 1
        pattern["last_updated"] = datetime.now().isoformat()
        
        # Bu selector'ı ekle/güncelle
        selector_info = {
            "id": element_info.get("id"),
            "class": element_info.get("class"),
            "tag": element_info.get("tag"),
            "text": element_info.get("text", "")[:50],  # İlk 50 karakter
            "score": round(score, 3),
            "action_type": action_type,
            "success_count": 1,
            "last_used": datetime.now().isoformat()
        }
        
        # Mevcut selector'lar arasında var mı kontrol et
        found = False
        for sel in pattern["best_selectors"]:
            if (sel.get("id") == selector_info["id"] and 
                sel.get("class") == selector_info["class"]):
                sel["success_count"] += 1
                sel["last_used"] = selector_info["last_used"]
                sel["score"] = max(sel["score"], selector_info["score"])
                found = True
                break
        
        if not found:
            pattern["best_selectors"].append(selector_info)
        
        # En başarılı 5'i tut
        pattern["best_selectors"].sort(key=lambda x: x["success_count"], reverse=True)
        pattern["best_selectors"] = pattern["best_selectors"][:5]
        
        # Başarı oranını hesapla
        pattern["success_rate"] = pattern["successes"] / pattern["attempts"]
        
        # Session learning'e ekle
        self.session_learnings.append({
            "pattern_key": pattern_key,
            "element_info": element_info,
            "score": score,
            "timestamp": datetime.now().isoformat()
        })
        
        log.debug(f"Öğrenildi: {pattern_key} (Başarı: {pattern['successes']}/{pattern['attempts']})")
    
    def get_learned_selector(self, site: str, category: str) -> Dict[str, Any]:
        """
        Öğrenilmiş bir selector getir (varsa)
        
        Returns:
            Öğrenilmiş selector bilgisi veya None
        """
        pattern_key = f"{site}_{category}"
        
        if pattern_key in self.knowledge_base:
            pattern = self.knowledge_base[pattern_key]
            
            if pattern["best_selectors"]:
                # En başarılısını döndür
                best = pattern["best_selectors"][0]
                log.info(f"Öğrenilmiş pattern bulundu: {pattern_key}")
                log.debug(f"ID: {best.get('id', 'N/A')}, Class: {best.get('class', 'N/A')[:30]}")
                log.debug(f"Başarı: {best['success_count']} kez, Skor: {best['score']}")
                return best
        
        return None
    
    def get_stats(self) -> Dict:
        """İstatistikleri al"""
        total_patterns = len(self.knowledge_base)
        total_successes = sum(p["successes"] for p in self.knowledge_base.values())
        total_attempts = sum(p["attempts"] for p in self.knowledge_base.values())
        
        avg_success_rate = (total_successes / total_attempts * 100) if total_attempts > 0 else 0
        
        # En başarılı patternler
        top_patterns = sorted(
            self.knowledge_base.items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )[:5]
        
        return {
            "total_patterns": total_patterns,
            "total_successes": total_successes,
            "total_attempts": total_attempts,
            "avg_success_rate": round(avg_success_rate, 1),
            "top_patterns": [
                {
                    "key": k,
                    "successes": v["successes"],
                    "attempts": v["attempts"],
                    "rate": round(v["success_rate"] * 100, 1)
                }
                for k, v in top_patterns
            ],
            "session_learnings": len(self.session_learnings)
        }
    
    def save_and_report(self):
        """Öğrenmeleri kaydet ve rapor ver"""
        self._save_knowledge()
        
        stats = self.get_stats()
        
        log.info("=" * 50)
        log.info("LEARNING SYSTEM RAPORU")
        log.info(f"Toplam Pattern: {stats['total_patterns']}")
        log.info(f"Toplam Başarı: {stats['total_successes']}/{stats['total_attempts']}")
        log.info(f"Ortalama Başarı Oranı: {stats['avg_success_rate']}%")
        log.info(f"Bu Oturumda Öğrenilen: {stats['session_learnings']} pattern")
        
        if stats['top_patterns']:
            log.info("EN BAŞARILI PATTERNLER:")
            for i, p in enumerate(stats['top_patterns'], 1):
                log.info(f"#{i}: {p['key']} - {p['rate']}% ({p['successes']}/{p['attempts']})")
        
        log.info("=" * 50)
        log.info(f"Bilgi deposu kaydedildi: {self.knowledge_file}")
        
        return stats
    
    def should_try_learned_first(self, site: str, category: str) -> bool:
        """Bu pattern için öğrenilmiş bilgi kullanılmalı mı?"""
        pattern_key = f"{site}_{category}"
        
        if pattern_key in self.knowledge_base:
            pattern = self.knowledge_base[pattern_key]
            # Başarı oranı %70'in üzerindeyse öğrenileni önce dene
            return pattern.get("success_rate", 0) > 0.7
        
        return False

