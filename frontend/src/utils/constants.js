export const RECOMMENDATION_TYPES = {
  BUY: {
    key: 'buy',
    type: 'BUY',
    emoji: '🛒',
    label: 'Buy it',
    category: 'buy',
    color: 'positive',
    message: "I'd buy this one."
  },
  GRAB: {
    key: 'grab',
    type: 'BUY',
    emoji: '🔥',
    label: 'Grab it now',
    category: 'buy',
    color: 'positive',
    message: 'This is a really good moment to buy.'
  },
  WAIT: {
    key: 'wait',
    type: 'WAIT',
    emoji: '⏳',
    label: 'Wait a little',
    category: 'wait',
    color: 'warning',
    message: "I'd hold off for now."
  },
  WAIT_SALE: {
    key: 'wait_sale',
    type: 'WAIT',
    emoji: '🎯',
    label: 'Wait for a sale',
    category: 'wait',
    color: 'warning',
    message: "I'd wait for a better deal."
  },
  CHECK_ALT: {
    key: 'check_alt',
    type: 'CHANGE',
    emoji: '👀',
    label: 'Check another',
    category: 'change',
    color: 'accent',
    message: 'I found a better option.'
  },
  CAUTION: {
    key: 'caution',
    type: 'CHANGE',
    emoji: '⚠️',
    label: 'Proceed with caution',
    category: 'change',
    color: 'warning',
    message: "The price looks good, but I'd be careful here."
  },
  DONT_RUSH: {
    key: 'dont_rush',
    type: 'WAIT',
    emoji: '🚫',
    label: "Don't rush",
    category: 'wait',
    color: 'danger',
    message: 'This looks expensive right now.'
  },
  YOUR_CALL: {
    key: 'your_call',
    type: 'UNCERTAIN',
    emoji: '🤷',
    label: 'Your call',
    category: 'uncertain',
    color: 'neutral',
    message: "This is a reasonable price, but I don't see a strong reason to buy now or wait."
  },
  NO_DECISION: {
    key: 'no_decision',
    type: 'UNCERTAIN',
    emoji: '❓',
    label: 'No decision',
    category: 'uncertain',
    color: 'neutral',
    message: "I couldn't verify enough to give you a reliable recommendation."
  },
};

// Backward-compatible aliases
RECOMMENDATION_TYPES.CHECK_SELLER = RECOMMENDATION_TYPES.CAUTION;
RECOMMENDATION_TYPES.NO_DATA = RECOMMENDATION_TYPES.NO_DECISION;
RECOMMENDATION_TYPES.UNCERTAIN = RECOMMENDATION_TYPES.NO_DECISION;

export const RECOMMENDATION_STATES = {
  BUY: 'BUY',
  GRAB: 'GRAB',
  WAIT: 'WAIT',
  WAIT_SALE: 'WAIT_SALE',
  CHECK_ALT: 'CHECK_ALT',
  CAUTION: 'CAUTION',
  DONT_RUSH: 'DONT_RUSH',
  YOUR_CALL: 'YOUR_CALL',
  NO_DECISION: 'NO_DECISION',
  // Backward compatibility
  CHECK_SELLER: 'CAUTION',
  NO_DATA: 'NO_DECISION',
  UNCERTAIN: 'NO_DECISION',
};

export const WATCHLIST_STATUS = {
  BUY_SIGNAL: { key: 'buy_signal', emoji: '🔥', label: 'BUY SIGNAL', category: 'buy' },
  WAITING: { key: 'waiting', emoji: '⏳', label: 'WAITING', category: 'wait' },
  WATCHING: { key: 'watching', emoji: '👀', label: 'WATCHING', category: 'watch' },
  NEEDS_ATTENTION: { key: 'needs_attention', emoji: '⚠️', label: 'NEEDS ATTENTION', category: 'attention' },
};

export const RETAILERS = {
  amazon: { name: 'Amazon', domain: 'amazon.in', color: '#FF9900' },
  flipkart: { name: 'Flipkart', domain: 'flipkart.com', color: '#2874F0' },
  croma: { name: 'Croma', domain: 'croma.com', color: '#0F7D39' },
  reliance: { name: 'Reliance Digital', domain: 'reliancedigital.in', color: '#003DA5' },
  myntra: { name: 'Myntra', domain: 'myntra.com', color: '#FF3F6C' },
};

// String mapping ensures React can safely render {confText} directly without child object crash
export const CONFIDENCE_LEVELS = {
  HIGH: "I'm pretty confident.",
  MEDIUM: "I'm reasonably confident.",
  LOW: "I'm not confident enough to recommend strongly.",
  high: "I'm pretty confident.",
  medium: "I'm reasonably confident.",
  low: "I'm not confident enough to recommend strongly.",
};

export const CONFIDENCE_DETAILS = {
  HIGH: { key: 'high', label: "I'm pretty confident.", icon: '👍' },
  MEDIUM: { key: 'medium', label: "I'm reasonably confident.", icon: '👌' },
  LOW: { key: 'low', label: "I'm not confident enough to recommend strongly.", icon: '🤔' },
};

export const SELLER_RELIABILITY = {
  RELIABLE: { key: 'reliable', label: 'Looks reliable', icon: '🛡️' },
  MODERATE: { key: 'moderate', label: "I'd double-check the seller.", icon: '⚠️' },
  RISKY: { key: 'risky', label: "I'd avoid this listing.", icon: '🚫' },
  UNKNOWN: { key: 'unknown', label: 'Seller not verified.', icon: '❓' },
};

export const TREND_TYPES = {
  FALLING: { key: 'falling', label: 'Falling', icon: '↓', color: 'positive' },
  RISING: { key: 'rising', label: 'Rising', icon: '↑', color: 'danger' },
  STABLE: { key: 'stable', label: 'Stable', icon: '→', color: 'neutral' },
  VOLATILE: { key: 'volatile', label: 'Volatile', icon: '↕', color: 'warning' },
};
