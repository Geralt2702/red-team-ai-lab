"""
🐬 Model Manager - Zarządzanie modelami Ollama
Pozwala na dynamiczne pobieranie i testowanie modelów
bez zajmowania RAM
"""

import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Dict

class OllamaModelManager:
    """Zarządzanie modelami Ollama - pobieranie, czyszczenie, listing"""
    
    # Predefiniowane modele dla pentestingu
    PENTESTING_MODELS = [
        {
            'name': '🐬 Dolphin Llama3 8B',
            'id': 'dolphin-llama3:8b',
            'size': '5GB',
            'vram': '5GB',
            'ram': '8GB',
            'purpose': 'Uncensored - Red Teaming, Jailbreak Tests',
            'best_for': 'Testowanie bezpieczeństwa AI'
        },
        {
            'name': '🤖 Mistral 7B',
            'id': 'mistral:7b',
            'size': '4.4GB',
            'vram': '4GB',
            'ram': '8GB',
            'purpose': 'Baseline Security Model',
            'best_for': 'Porównanie z innymi modelami'
        },
        {
            'name': '💬 Neural Chat',
            'id': 'neural-chat:latest',
            'size': '4.1GB',
            'vram': '4GB',
            'ram': '8GB',
            'purpose': 'Medium Security',
            'best_for': 'Szybkie testy'
        },
        {
            'name': '💎 Gemma3',
            'id': 'gemma3:latest',
            'size': '3.3GB',
            'vram': '3GB',
            'ram': '6GB',
            'purpose': 'High Security',
            'best_for': 'Szybkie, bezpieczne testy'
        },
    ]
    
    def __init__(self):
        self.available_models = self.PENTESTING_MODELS
        self._verify_ollama_installed()
    
    def _verify_ollama_installed(self):
        """Sprawdzenie czy Ollama jest zainstalowana"""
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Ollama nie znaleziona - zainstaluj z https://ollama.com")
        except FileNotFoundError:
            raise Exception("Ollama nie zainstalowana!")
    
    def get_installed_models(self) -> List[Dict]:
        """Pobierz listę zainstalowanych modeli"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:]  # Pomiń nagłówek
            installed = []
            
            for line in lines:
                if line.strip() and 'NAME' not in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        installed.append({
                            'name': parts[0],
                            'digest': parts[1] if len(parts) > 1 else 'unknown',
                            'size': parts[2] if len(parts) > 2 else 'unknown'
                        })
            return installed
        except Exception as e:
            print(f"❌ Błąd podczas pobierania listy: {e}")
            return []
    
    def pull_model(self, model_id: str) -> Tuple[bool, str]:
        """Pobierz model (z progressbar)"""
        try:
            print(f"\n⏳ Pobieranie {model_id}...")
            result = subprocess.run(
                ['ollama', 'pull', model_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, f"✅ Model {model_id} pobrany pomyślnie!"
            else:
                return False, result.stderr or "Nieznany błąd"
        except Exception as e:
            return False, str(e)
    
    def is_model_available(self, model_id: str) -> bool:
        """Sprawdzenie czy model jest pobrany"""
        installed = self.get_installed_models()
        base_name = model_id.split(':')[0]
        return any(m['name'].startswith(base_name) for m in installed)
    
    def remove_model(self, model_id: str) -> Tuple[bool, str]:
        """Usuń model"""
        try:
            result = subprocess.run(['ollama', 'rm', model_id], capture_output=True, text=True)
            if result.returncode == 0:
                return True, f"✅ Model {model_id} usunięty"
            else:
                return False, result.stderr or "Błąd usuwania"
        except Exception as e:
            return False, str(e)
    
    def get_model_info(self, model_id: str) -> Dict:
        """Pobierz informacje o modelu"""
        for model in self.available_models:
            if model['id'] == model_id:
                return model
        return {}
    
    def estimate_ram_usage(self, model_id: str) -> str:
        """Szacunkowe zużycie RAM"""
        info = self.get_model_info(model_id)
        return info.get('ram', 'unknown')
    
    def is_compatible_with_system(self, model_id: str, available_ram_gb: int = 12) -> bool:
        """Sprawdzenie kompatybilności z systemem"""
        info = self.get_model_info(model_id)
        required_ram = int(info.get('ram', '0').replace('GB', ''))
        return available_ram_gb >= required_ram


# Test
if __name__ == '__main__':
    try:
        manager = OllamaModelManager()
        print("✅ Ollama Manager inicjalizowany\n")
        
        print("📚 Dostępne modele:")
        for i, model in enumerate(manager.available_models, 1):
            print(f"{i}. {model['name']:<30} ({model['size']}) - {model['best_for']}")
        
        print("\n📋 Zainstalowane modele:")
        installed = manager.get_installed_models()
        if installed:
            for model in installed:
                print(f"  ✓ {model['name']} ({model['size']})")
        else:
            print("  Brak zainstalowanych modeli")
            
        print("\n💾 Kompatybilność z Twoim systemem (12GB RAM):")
        for model in manager.available_models:
            compat = "✅" if manager.is_compatible_with_system(model['id'], 12) else "❌"
            print(f"  {compat} {model['name']:<30} ({model['ram']} wymagane)")
            
    except Exception as e:
        print(f"❌ Błąd: {e}")
