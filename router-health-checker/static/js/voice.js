/**
 * Voice input (SpeechRecognition) and Speech Output (SpeechSynthesis) module.
 */

const LANG_CODE_MAP = {
  en: 'en-US',
  hi: 'hi-IN',
  ta: 'ta-IN',
  te: 'te-IN',
  kn: 'kn-IN',
  ml: 'ml-IN',
  bn: 'bn-IN',
  mr: 'mr-IN',
  ur: 'ur-PK',
  ar: 'ar-SA',
  es: 'es-ES',
  fr: 'fr-FR'
};

class VoiceManager {
  constructor() {
    this.synth = window.speechSynthesis;
    this.recognition = null;
    this.isListening = false;
    this.voices = [];
    this.currentUtterance = null;
    this.initRecognition();
    this.initVoices();
  }

  initVoices() {
    if (!this.synth) return;
    const loadVoices = () => {
      this.voices = this.synth.getVoices();
    };
    loadVoices();
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = loadVoices;
    }
  }

  initRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec) {
      this.recognition = new SpeechRec();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
    }
  }

  startListening(langCode, onResult, onEnd, onError) {
    if (!this.recognition) {
      if (onError) onError('SPEECH_RECOGNITION_NOT_SUPPORTED');
      return;
    }
    try {
      this.recognition.lang = LANG_CODE_MAP[langCode] || 'en-US';
      this.isListening = true;

      this.recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        if (onResult) onResult(transcript);
      };

      this.recognition.onerror = (e) => {
        this.isListening = false;
        if (onError) onError(e.error);
      };

      this.recognition.onend = () => {
        this.isListening = false;
        if (onEnd) onEnd();
      };

      this.recognition.start();
    } catch (err) {
      this.isListening = false;
      if (onError) onError(err);
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }

  speak(text, langCode = 'en', rate = 1.0, onEnd = null) {
    if (!this.synth) return;
    this.stopSpeaking();

    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = rate;
    const targetTag = LANG_CODE_MAP[langCode] || 'en-US';
    utter.lang = targetTag;

    // Best matching voice
    const voice = this.voices.find(v => v.lang.replace('_', '-') === targetTag || v.lang.startsWith(langCode));
    if (voice) {
      utter.voice = voice;
    }

    if (onEnd) {
      utter.onend = onEnd;
      utter.onerror = onEnd;
    }

    this.currentUtterance = utter;
    this.synth.speak(utter);
  }

  stopSpeaking() {
    if (this.synth && (this.synth.speaking || this.synth.pending)) {
      this.synth.cancel();
    }
  }
}

export const voiceManager = new VoiceManager();
