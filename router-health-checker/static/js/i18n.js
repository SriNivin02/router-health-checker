/**
 * i18n Engine: Locale loading, text interpolation, RTL direction, and persistence.
 */

const RTL_LANGUAGES = new Set(['ar', 'ur']);

class I18nEngine {
  constructor() {
    this.currentLang = localStorage.getItem('rhc_language') || this.detectBrowserLang();
    this.translations = {};
    this.fallbackTranslations = {};
  }

  detectBrowserLang() {
    const navLang = (navigator.language || navigator.userLanguage || 'en').split('-')[0].toLowerCase();
    const supported = ['en', 'hi', 'ta', 'te', 'kn', 'ml', 'bn', 'mr', 'ur', 'ar', 'es', 'fr'];
    return supported.includes(navLang) ? navLang : 'en';
  }

  async init() {
    // Always load English as primary fallback
    try {
      const resEn = await fetch('/static/locales/en.json');
      this.fallbackTranslations = await resEn.json();
    } catch (e) {
      this.fallbackTranslations = {};
    }

    await this.setLanguage(this.currentLang);
  }

  async setLanguage(langCode) {
    this.currentLang = langCode;
    localStorage.setItem('rhc_language', langCode);

    if (langCode === 'en') {
      this.translations = this.fallbackTranslations;
    } else {
      try {
        const res = await fetch(`/static/locales/${langCode}.json`);
        if (res.ok) {
          this.translations = await res.json();
        } else {
          this.translations = this.fallbackTranslations;
        }
      } catch (e) {
        this.translations = this.fallbackTranslations;
      }
    }

    // Set document direction
    const isRtl = RTL_LANGUAGES.has(langCode);
    document.documentElement.dir = isRtl ? 'rtl' : 'ltr';
    document.documentElement.lang = langCode;

    this.applyToDOM();

    // Trigger language change event
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: langCode } }));
  }

  t(key, params = {}) {
    let str = this.translations[key] || this.fallbackTranslations[key] || key;
    for (const [k, v] of Object.entries(params)) {
      str = str.replace(new RegExp(`{${k}}`, 'g'), v);
    }
    return str;
  }

  applyToDOM() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (key) {
        el.textContent = this.t(key);
      }
    });

    const placeholderEls = document.querySelectorAll('[data-i18n-placeholder]');
    placeholderEls.forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (key) {
        el.setAttribute('placeholder', this.t(key));
      }
    });
  }
}

export const i18n = new I18nEngine();
