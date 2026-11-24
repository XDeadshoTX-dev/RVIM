import { useState, useEffect } from 'react';

/**
 * Хук для збереження стану в localStorage (вимога ЛР2)
 * @param {string} key - ключ у localStorage
 * @param {*} initialValue - значення за замовчуванням
 */
export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item !== null ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('localStorage write error:', error);
    }
  }, [key, value]);

  return [value, setValue];
}