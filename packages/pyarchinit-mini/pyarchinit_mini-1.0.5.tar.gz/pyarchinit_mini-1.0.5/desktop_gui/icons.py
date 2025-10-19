#!/usr/bin/env python3
"""
Icon management for PyArchInit-Mini navigation toolbar
Creates simple text-based icons using Unicode symbols
"""

class Icons:
    """Unicode symbols for navigation toolbar"""
    
    # Navigation icons
    HOME = "🏠"
    SITE = "🏛️"
    US = "📋"
    INVENTORY = "📦"
    HARRIS = "🔀"
    PDF = "📄"
    MEDIA = "🖼️"
    SETTINGS = "⚙️"
    
    # Action icons
    NEW = "➕"
    EDIT = "✏️"
    DELETE = "🗑️"
    SAVE = "💾"
    SEARCH = "🔍"
    REFRESH = "🔄"
    EXPORT = "📤"
    IMPORT = "📥"
    
    # Navigation arrows
    FIRST = "⏮️"
    PREV = "◀️"
    NEXT = "▶️"
    LAST = "⏭️"
    
    # Status icons
    OK = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    
    @classmethod
    def get_text_icons(cls):
        """Get simple text representations for systems without emoji support"""
        return {
            "HOME": "[H]",
            "SITE": "[S]",
            "US": "[U]",
            "INVENTORY": "[I]",
            "HARRIS": "[M]",
            "PDF": "[P]",
            "MEDIA": "[MD]",
            "SETTINGS": "[ST]",
            "NEW": "[+]",
            "EDIT": "[E]",
            "DELETE": "[D]",
            "SAVE": "[SV]",
            "SEARCH": "[SR]",
            "REFRESH": "[R]",
            "EXPORT": "[EX]",
            "IMPORT": "[IM]",
            "FIRST": "[<<]",
            "PREV": "[<]",
            "NEXT": "[>]",
            "LAST": "[>>]",
            "OK": "[OK]",
            "ERROR": "[ER]",
            "WARNING": "[!]",
            "INFO": "[i]"
        }