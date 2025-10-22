"""
Testi interfaccia PyPrestaScan GUI - SOLO ITALIANO
"""


class TranslationManager:
    """Gestione testi interfaccia - SOLO ITALIANO"""

    # Testi interfaccia SOLO ITALIANO
    TEXTS = {
        # === HEADER ===
        "app_title": "PyPrestaScan - Analisi SEO PrestaShop",
        "app_subtitle": "Analisi SEO PrestaShop",

        # === TABS ===
        "tab_config": "⚙️ Configurazione",
        "tab_progress": "📈 Progress & Log",
        "tab_results": "📊 Risultati",
        "tab_fixes": "🔧 Fix Suggeriti",
        "tab_help": "❓ Aiuto",

        # === BUTTONS ===
        "btn_start_scan": "▶️ Avvia Scansione",
        "btn_stop_scan": "⏹️ Ferma Scansione",
        "btn_export_excel": "📊 Esporta Report Excel",
        "btn_export_csv": "📥 Esporta Issues CSV",
        "btn_view_report": "📊 Visualizza Report HTML Completo",
        "btn_open_folder": "📁 Apri Cartella Report",
        "btn_generate_fixes": "🔧 Genera Fix Suggeriti",

        # === LABELS ===
        "label_url": "URL Target:",
        "label_project": "Nome Progetto:",
        "label_max_pages": "Max Pagine:",
        "label_max_depth": "Profondità Max:",
        "label_concurrency": "Concorrenza:",
        "label_delay": "Delay (ms):",
        "label_language": "🌐 Lingua:",

        # === GROUPS ===
        "group_basic": "Configurazione Base",
        "group_advanced": "Opzioni Avanzate",
        "group_ai": "🤖 AI Fix Avanzati (Opzionale)",
        "group_progress": "📊 Progresso Scansione",
        "group_log": "📝 Log Attività",
        "group_stats": "📋 Riepilogo Statistiche",
        "group_actions": "🎯 Azioni Disponibili",

        # === CHECKBOXES ===
        "check_sitemap": "Usa sitemap.xml",
        "check_robots": "Rispetta robots.txt",
        "check_external": "Segui link esterni",
        "check_javascript": "Esegui JavaScript",
        "check_ai_enable": "✨ Abilita AI",

        # === STATUS MESSAGES ===
        "status_ready": "Pronto per la scansione",
        "status_scanning": "Scansione in corso...",
        "status_completed": "Scansione completata",
        "status_error": "Errore durante la scansione",

        # === STATISTICS ===
        "stat_pages_scanned": "Pagine scansionate:",
        "stat_pages_failed": "Pagine fallite:",
        "stat_issues_found": "Issues trovati:",
        "stat_images_no_alt": "Immagini senza ALT:",
        "stat_total_pages": "📄 Pagine totali:",
        "stat_success_rate": "✅ Tasso successo:",
        "stat_avg_score": "⭐ Score medio:",
        "stat_critical_issues": "🔴 Issues critici:",

        # === MESSAGES ===
        "msg_scan_success": "Scansione completata con successo!",
        "msg_export_success": "Export completato",
        "msg_no_data": "Nessun dato",
        "msg_confirm_close": "Conferma chiusura",
        "msg_scan_running": "La scansione è in corso. Vuoi interromperla?",

        # === TOOLTIPS ===
        "tooltip_theme_toggle": "Cambia tema (Light/Dark)",
        "tooltip_language": "Seleziona lingua interfaccia",

        # === AI SECTION ===
        "ai_provider": "Provider AI:",
        "ai_api_key": "API Key:",
        "ai_model": "Modello:",

        # === THEME ===
        "theme_changed": "🎨 Tema cambiato in:",
        "theme_light": "Light Mode",
        "theme_dark": "Dark Mode",
    }

    def t(self, key: str) -> str:
        """
        Ottieni testo italiano per chiave

        Args:
            key: Chiave testo (es. "app_title")

        Returns:
            str: Testo in ITALIANO
        """
        return self.TEXTS.get(key, f"[{key}]")


# Istanza globale singleton
_translation_manager = None


def get_translation_manager() -> TranslationManager:
    """Ottieni istanza globale TranslationManager (singleton)"""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager()
    return _translation_manager


def t(key: str) -> str:
    """
    Shortcut per ottenere testo italiano

    Usage:
        from pyprestascan.gui.i18n import t
        label = QLabel(t("app_title"))
    """
    return get_translation_manager().t(key)
