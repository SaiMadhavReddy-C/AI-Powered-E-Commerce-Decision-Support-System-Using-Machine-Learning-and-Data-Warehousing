import { RETAILERS } from './constants';

export function detectRetailer(input) {
  if (!input) return null;
  const lower = input.toLowerCase();
  
  for (const [key, retailer] of Object.entries(RETAILERS)) {
    if (lower.includes(retailer.domain)) return { key, ...retailer };
  }
  return null;
}

export function isURL(input) {
  try {
    const url = new URL(input);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

export function detectInputType(input) {
  if (!input || !input.trim()) return 'empty';
  if (isURL(input.trim())) return 'url';
  return 'search';
}
