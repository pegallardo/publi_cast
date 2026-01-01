# -*- coding: utf-8 -*-
"""
PubliCast - Localization system for French and English
"""
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_config.json")

# All translations
TRANSLATIONS = {
    "fr": {
        # Main window
        "app_title": "PubliCast - Processeur Audio",
        "ready": "Prêt",
        "processing": "Traitement en cours...",
        "processing_complete": "Traitement terminé - Prêt pour un nouveau fichier",
        "logs": "Logs",
        "btn_process": "🎵 Traiter un fichier audio",
        "btn_clear_logs": "🗑️ Effacer les logs",
        "btn_quit": "❌ Quitter",
        "app_started": "Application démarrée",
        "closing": "Fermeture en cours...",
        "close_error": "Erreur lors de la fermeture",
        "processing_in_progress": "Traitement en cours",
        "confirm_quit": "Un traitement est en cours. Voulez-vous vraiment quitter?",
        "setting_changed": "Paramètre modifié",
        "language": "Langue",
        
        # Settings panel
        "settings_title": "⚙️ Paramètres de traitement",
        "compressor": "Compresseur",
        "normalize": "Normalisation",
        
        # Compressor parameters
        "threshold": "Seuil (dB)",
        "ratio": "Ratio",
        "attack": "Attack (ms)",
        "release": "Release (ms)",
        "makeup": "Makeup (dB)",
        
        # Normalize parameters
        "peak_level": "Niveau crête (dB)",
        
        # Tooltips - Compressor
        "tooltip_threshold": "Seuil de déclenchement du compresseur.\nLes sons au-dessus de ce niveau seront compressés.\nValeur typique: -18 dB pour la voix.",
        "tooltip_ratio": "Taux de compression.\nUn ratio de 4:1 signifie que pour chaque 4 dB au-dessus du seuil,\nle signal ne montera que de 1 dB.\nPlus le ratio est élevé, plus la compression est forte.",
        "tooltip_attack": "Temps d'attaque en millisecondes.\nDétermine la rapidité avec laquelle le compresseur réagit.\nUne attaque rapide (5-10ms) capture les transitoires,\nune attaque lente (30-100ms) les laisse passer.",
        "tooltip_release": "Temps de relâchement en millisecondes.\nDétermine combien de temps le compresseur reste actif\naprès que le signal soit passé sous le seuil.\nValeur typique: 100-300ms pour un son naturel.",
        "tooltip_makeup": "Gain de compensation en dB.\nPermet de remonter le niveau après compression\npour compenser la réduction de volume.",
        
        # Tooltips - Normalize
        "tooltip_peak_level": "Niveau de crête cible en dB.\nLe fichier sera normalisé pour que le pic le plus fort\natteigne ce niveau.\n-1 dB est recommandé pour éviter la saturation.",
    },
    "en": {
        # Main window
        "app_title": "PubliCast - Audio Processor",
        "ready": "Ready",
        "processing": "Processing...",
        "processing_complete": "Processing complete - Ready for next file",
        "logs": "Logs",
        "btn_process": "🎵 Process audio file",
        "btn_clear_logs": "🗑️ Clear logs",
        "btn_quit": "❌ Quit",
        "app_started": "Application started",
        "closing": "Closing...",
        "close_error": "Error while closing",
        "processing_in_progress": "Processing in progress",
        "confirm_quit": "Processing is in progress. Do you really want to quit?",
        "setting_changed": "Setting changed",
        "language": "Language",
        
        # Settings panel
        "settings_title": "⚙️ Processing settings",
        "compressor": "Compressor",
        "normalize": "Normalization",
        
        # Compressor parameters
        "threshold": "Threshold (dB)",
        "ratio": "Ratio",
        "attack": "Attack (ms)",
        "release": "Release (ms)",
        "makeup": "Makeup (dB)",
        
        # Normalize parameters
        "peak_level": "Peak level (dB)",
        
        # Tooltips - Compressor
        "tooltip_threshold": "Compressor trigger threshold.\nSounds above this level will be compressed.\nTypical value: -18 dB for voice.",
        "tooltip_ratio": "Compression ratio.\nA 4:1 ratio means for every 4 dB above threshold,\nthe signal only rises by 1 dB.\nHigher ratio = stronger compression.",
        "tooltip_attack": "Attack time in milliseconds.\nDetermines how quickly the compressor reacts.\nFast attack (5-10ms) catches transients,\nslow attack (30-100ms) lets them through.",
        "tooltip_release": "Release time in milliseconds.\nDetermines how long the compressor stays active\nafter the signal drops below threshold.\nTypical value: 100-300ms for natural sound.",
        "tooltip_makeup": "Makeup gain in dB.\nAllows boosting the level after compression\nto compensate for volume reduction.",
        
        # Tooltips - Normalize
        "tooltip_peak_level": "Target peak level in dB.\nThe file will be normalized so the loudest peak\nreaches this level.\n-1 dB is recommended to avoid clipping.",
    }
}

# Current language (default: French)
_current_lang = "fr"


def get_language():
    """Get current language."""
    global _current_lang
    # Try to load from config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                _current_lang = config.get("language", "fr")
        except Exception:
            pass
    return _current_lang


def set_language(lang):
    """Set current language and save to config."""
    global _current_lang
    if lang in TRANSLATIONS:
        _current_lang = lang
        # Save to config
        config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                pass
        config["language"] = lang
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)


def t(key):
    """Get translation for key."""
    lang = get_language()
    return TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, key)

