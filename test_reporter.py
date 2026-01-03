"""
🎯 TEST REPORTER - Excel/CSV Raporlama Sistemi
Tüm test sonuçlarını otomatik olarak kaydet ve analiz et
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import statistics

class TestReporter:
    """
    Test sonuçlarını kaydet ve rapor oluştur
    """
    
    def __init__(self, test_name="test", output_dir="reports"):
        self.test_name = test_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Test başlangıç zamanı
        self.start_time = datetime.now()
        
        # Test verileri
        self.interactions = []  # Her bir etkileşim
        self.errors = []        # Hatalar
        self.warnings = []      # Uyarılar
        self.cache_hits = 0     # Cache kullanım sayısı
        self.total_scans = 0    # Toplam tarama sayısı
        
        # Timing verileri
        self.timings = {
            "scan": [],
            "interact": [],
            "wait": []
        }
        
        print(f"📊 Test Reporter başlatıldı: {test_name}")
    
    def log_interaction(self, action_type: str, category: str, element_info: Dict, 
                       score: float, success: bool, duration: float):
        """Bir etkileşimi kaydet"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "category": category,
            "element_id": element_info.get("id", "N/A"),
            "element_class": element_info.get("class", "N/A"),
            "element_tag": element_info.get("tag", "N/A"),
            "score": round(score, 3),
            "success": success,
            "duration_ms": round(duration * 1000, 2)
        }
        self.interactions.append(interaction)
        
        # Timing kaydet
        self.timings["interact"].append(duration)
    
    def log_scan(self, category: str, elements_found: int, 
                 best_score: float, duration: float, cache_hit: bool = False):
        """Bir taramayı kaydet"""
        if cache_hit:
            self.cache_hits += 1
        else:
            self.total_scans += 1
            self.timings["scan"].append(duration)
        
        scan_info = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "elements_found": elements_found,
            "best_score": round(best_score, 3),
            "duration_ms": round(duration * 1000, 2),
            "cache_hit": cache_hit
        }
        self.interactions.append(scan_info)
    
    def log_error(self, error_type: str, message: str, element_info: Dict = None):
        """Bir hatayı kaydet"""
        error = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "element": element_info
        }
        self.errors.append(error)
    
    def log_warning(self, message: str):
        """Bir uyarıyı kaydet"""
        warning = {
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        self.warnings.append(warning)
    
    def log_wait(self, wait_type: str, duration: float, success: bool):
        """Bir beklemeyi kaydet"""
        self.timings["wait"].append(duration)
        wait_info = {
            "timestamp": datetime.now().isoformat(),
            "type": wait_type,
            "duration_ms": round(duration * 1000, 2),
            "success": success
        }
        self.interactions.append(wait_info)
    
    def generate_report(self):
        """Test sonunda rapor oluştur"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # --- 1. CSV RAPORU (Detaylı Log) ---
        csv_path = self.output_dir / f"{self.test_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}_details.csv"
        self._write_csv_report(csv_path)
        
        # --- 2. JSON RAPORU (Machine-readable) ---
        json_path = self.output_dir / f"{self.test_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}_full.json"
        self._write_json_report(json_path, total_duration)
        
        # --- 3. ÖZET RAPORU (Human-readable) ---
        summary_path = self.output_dir / f"{self.test_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}_summary.txt"
        self._write_summary_report(summary_path, total_duration)
        
        print("\n" + "="*70)
        print("📊 TEST RAPORU OLUŞTURULDU!")
        print("="*70)
        print(f"📄 Detaylı Log: {csv_path}")
        print(f"📦 JSON Rapor: {json_path}")
        print(f"📋 Özet Rapor: {summary_path}")
        print("="*70)
        
        return {
            "csv": str(csv_path),
            "json": str(json_path),
            "summary": str(summary_path)
        }
    
    def _write_csv_report(self, path: Path):
        """CSV formatında detaylı log"""
        with open(path, 'w', newline='', encoding='utf-8') as f:
            if self.interactions:
                # Tüm key'leri topla
                all_keys = set()
                for item in self.interactions:
                    all_keys.update(item.keys())
                
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(self.interactions)
    
    def _write_json_report(self, path: Path, total_duration: float):
        """JSON formatında tam rapor"""
        report = {
            "test_name": self.test_name,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_duration_seconds": round(total_duration, 2),
            "interactions": self.interactions,
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": self._calculate_statistics()
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    def _write_summary_report(self, path: Path, total_duration: float):
        """Human-readable özet rapor"""
        stats = self._calculate_statistics()
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write(f"🎯 TEST ÖZET RAPORU: {self.test_name}\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"⏱️  SÜRE BİLGİLERİ:\n")
            f.write(f"   Toplam Süre: {total_duration:.2f}s\n")
            f.write(f"   Başlangıç: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"   Bitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"📊 İSTATİSTİKLER:\n")
            f.write(f"   Toplam Etkileşim: {stats['total_interactions']}\n")
            f.write(f"   Başarılı: {stats['successful_interactions']} ✅\n")
            f.write(f"   Başarısız: {stats['failed_interactions']} ❌\n")
            f.write(f"   Başarı Oranı: {stats['success_rate']:.1f}%\n\n")
            
            f.write(f"🔍 TARAMA BİLGİLERİ:\n")
            f.write(f"   Toplam Tarama: {self.total_scans}\n")
            f.write(f"   Cache Kullanımı: {self.cache_hits}\n")
            f.write(f"   Cache Hit Rate: {stats['cache_hit_rate']:.1f}%\n")
            f.write(f"   Ort. Tarama Süresi: {stats['avg_scan_time']:.0f}ms\n\n")
            
            f.write(f"⚡ PERFORMANS:\n")
            f.write(f"   Ort. Etkileşim Süresi: {stats['avg_interact_time']:.0f}ms\n")
            f.write(f"   Ort. Bekleme Süresi: {stats['avg_wait_time']:.0f}ms\n")
            f.write(f"   En Hızlı Etkileşim: {stats['min_interact_time']:.0f}ms\n")
            f.write(f"   En Yavaş Etkileşim: {stats['max_interact_time']:.0f}ms\n\n")
            
            if self.errors:
                f.write(f"❌ HATALAR ({len(self.errors)}):\n")
                for err in self.errors:
                    f.write(f"   [{err['timestamp']}] {err['type']}: {err['message']}\n")
                f.write("\n")
            
            if self.warnings:
                f.write(f"⚠️  UYARILAR ({len(self.warnings)}):\n")
                for warn in self.warnings:
                    f.write(f"   [{warn['timestamp']}] {warn['message']}\n")
                f.write("\n")
            
            f.write("="*70 + "\n")
        
        # Konsola da yazdır
        print(f"\n📋 ÖZET:")
        print(f"   Toplam Süre: {total_duration:.2f}s")
        print(f"   Başarı Oranı: {stats['success_rate']:.1f}%")
        print(f"   Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
        print(f"   Ort. Tarama: {stats['avg_scan_time']:.0f}ms")
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """İstatistikleri hesapla"""
        successful = sum(1 for i in self.interactions if i.get('success') == True)
        failed = sum(1 for i in self.interactions if i.get('success') == False)
        total = successful + failed
        
        # Timing istatistikleri
        scan_times = self.timings["scan"]
        interact_times = self.timings["interact"]
        wait_times = self.timings["wait"]
        
        return {
            "total_interactions": len(self.interactions),
            "successful_interactions": successful,
            "failed_interactions": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            
            "total_scans": self.total_scans,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": (self.cache_hits / (self.total_scans + self.cache_hits) * 100) 
                             if (self.total_scans + self.cache_hits) > 0 else 0,
            
            "avg_scan_time": statistics.mean(scan_times) * 1000 if scan_times else 0,
            "avg_interact_time": statistics.mean(interact_times) * 1000 if interact_times else 0,
            "avg_wait_time": statistics.mean(wait_times) * 1000 if wait_times else 0,
            
            "min_interact_time": min(interact_times) * 1000 if interact_times else 0,
            "max_interact_time": max(interact_times) * 1000 if interact_times else 0,
        }

