import { createContext, useContext, useState } from 'react';

const I18nContext = createContext();

const translations = {
  en: {
    Overview: 'Overview',
    'Live Feeds': 'Live Feeds',
    'Floor Plan': 'Floor Plan',
    Alerts: 'Alerts',
    Sensors: 'Sensors',
    Communicate: 'Communicate',
    'Real-time security intelligence': 'Real-time security intelligence'
  },
  es: {
    Overview: 'Resumen',
    'Live Feeds': 'Cámaras',
    'Floor Plan': 'Plano',
    Alerts: 'Alertas',
    Sensors: 'Sensores',
    Communicate: 'Comunicar',
    'Real-time security intelligence': 'Inteligencia de seguridad en tiempo real'
  }
};

export function I18nProvider({ children }) {
  const [lang, setLang] = useState('en');
  
  const t = (key) => translations[lang]?.[key] || key;
  
  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
