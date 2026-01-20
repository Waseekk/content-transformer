/**
 * Language Detection Utility
 * Detects if text is primarily Bengali or English
 */

// Bengali Unicode range: U+0980 to U+09FF
const BENGALI_RANGE_START = 0x0980;
const BENGALI_RANGE_END = 0x09FF;

/**
 * Check if a character is Bengali
 */
export const isBengaliChar = (char: string): boolean => {
  const code = char.charCodeAt(0);
  return code >= BENGALI_RANGE_START && code <= BENGALI_RANGE_END;
};

/**
 * Count Bengali characters in text
 */
export const countBengaliChars = (text: string): number => {
  return Array.from(text).filter(isBengaliChar).length;
};

/**
 * Count alphabetic (Latin) characters in text
 */
export const countLatinChars = (text: string): number => {
  return Array.from(text).filter(char => /[a-zA-Z]/.test(char)).length;
};

/**
 * Detect the primary language of the text
 * @returns 'bn' for Bengali, 'en' for English, 'mixed' for mixed content
 */
export const detectLanguage = (text: string): 'bn' | 'en' | 'mixed' => {
  if (!text || text.trim().length === 0) return 'en';

  const bengaliCount = countBengaliChars(text);
  const latinCount = countLatinChars(text);
  const totalLetters = bengaliCount + latinCount;

  if (totalLetters === 0) return 'en'; // No letters, assume English

  const bengaliRatio = bengaliCount / totalLetters;
  const latinRatio = latinCount / totalLetters;

  // If more than 70% is Bengali, it's Bengali
  if (bengaliRatio > 0.7) return 'bn';

  // If more than 70% is Latin, it's English
  if (latinRatio > 0.7) return 'en';

  // Otherwise it's mixed
  return 'mixed';
};

/**
 * Get language display info
 */
export const getLanguageInfo = (language: 'bn' | 'en' | 'mixed') => {
  switch (language) {
    case 'bn':
      return {
        code: 'bn',
        name: 'Bengali',
        nativeName: 'বাংলা',
        flag: '🇧🇩',
        description: 'Detected as Bengali text',
      };
    case 'en':
      return {
        code: 'en',
        name: 'English',
        nativeName: 'English',
        flag: '🇬🇧',
        description: 'Detected as English text',
      };
    case 'mixed':
      return {
        code: 'mixed',
        name: 'Mixed',
        nativeName: 'Mixed',
        flag: '🌐',
        description: 'Contains both Bengali and English',
      };
  }
};
