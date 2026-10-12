/**
 * ShopQ Background Service Worker (Manifest V3)
 * Manages native chrome.sidePanel lifecycle, action badges, and message coordination.
 * Ephemeral architecture: state is persisted strictly in chrome.storage.local.
 */

const SUPPORTED_DOMAINS = [
  'amazon.in',
  'flipkart.com',
  'croma.com',
  'reliancedigital.in',
  'myntra.com'
];

/**
 * Utility to verify if a given URL belongs to a supported retailer domain.
 */
function isSupportedRetailer(url) {
  if (!url) return false;
  try {
    const parsed = new URL(url);
    return SUPPORTED_DOMAINS.some(domain => parsed.hostname === domain || parsed.hostname.endsWith(`.${domain}`));
  } catch {
    return false;
  }
}

// 1. Extension Installation & Defaults
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('[ShopQ Background] Installed reason:', details.reason);

  // Configure side panel behavior to open on action click if API supported
  if (chrome.sidePanel?.setPanelBehavior) {
    try {
      await chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
    } catch (err) {
      console.warn('[ShopQ Background] setPanelBehavior not supported or failed:', err);
    }
  }

  // Initialize persistent default configuration in chrome.storage.local
  const stored = await chrome.storage.local.get(['backendUrl', 'webAppUrl', 'watchlist']);
  const defaults = {};

  if (!stored.backendUrl) {
    defaults.backendUrl = 'http://localhost:8000';
  }
  if (!stored.webAppUrl) {
    defaults.webAppUrl = 'http://localhost:5173';
  }
  if (!stored.watchlist) {
    defaults.watchlist = [];
  }

  if (Object.keys(defaults).length > 0) {
    await chrome.storage.local.set(defaults);
  }
});

// 2. Action Click Listener (Reliable Fallback for opening SidePanel)
chrome.action.onClicked.addListener(async (tab) => {
  if (!tab?.windowId) return;

  try {
    if (chrome.sidePanel?.open) {
      await chrome.sidePanel.open({ windowId: tab.windowId });
    }
  } catch (err) {
    console.error('[ShopQ Background] Error opening side panel on action click:', err);
  }
});

// 3. Message Routing between Content Script & Side Panel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message || !message.type) return false;

  (async () => {
    try {
      switch (message.type) {
        case 'OPEN_SIDE_PANEL': {
          // Store detected product metadata in chrome.storage.local for sidepanel to read
          const activeProduct = {
            url: message.url || sender.tab?.url || '',
            title: message.title || sender.tab?.title || '',
            retailer: message.retailer || '',
            price: message.price || null,
            tabId: sender.tab?.id || null,
            windowId: sender.tab?.windowId || null,
            timestamp: Date.now()
          };

          await chrome.storage.local.set({ activeProduct });

          // Open the native side panel for the sender window
          const targetWindowId = sender.tab?.windowId;
          if (targetWindowId && chrome.sidePanel?.open) {
            await chrome.sidePanel.open({ windowId: targetWindowId });
          }

          // Set active badge on the tab
          if (sender.tab?.id) {
            await chrome.action.setBadgeText({ tabId: sender.tab.id, text: 'Q' });
            await chrome.action.setBadgeBackgroundColor({ tabId: sender.tab.id, color: '#C96B7A' });
          }

          sendResponse({ success: true, activeProduct });
          break;
        }

        case 'PDP_DETECTED': {
          // Content script found a valid PDP, show indicator badge on extension action
          if (sender.tab?.id) {
            await chrome.action.setBadgeText({ tabId: sender.tab.id, text: 'Q' });
            await chrome.action.setBadgeBackgroundColor({ tabId: sender.tab.id, color: '#C96B7A' });
            await chrome.action.setTitle({
              tabId: sender.tab.id,
              title: `ShopQ ready: ${message.retailer || 'Product'} detected`
            });
          }
          sendResponse({ success: true });
          break;
        }

        case 'GET_CURRENT_PRODUCT': {
          const data = await chrome.storage.local.get('activeProduct');
          sendResponse({ success: true, activeProduct: data.activeProduct || null });
          break;
        }

        case 'CLEAR_BADGE': {
          if (sender.tab?.id) {
            await chrome.action.setBadgeText({ tabId: sender.tab.id, text: '' });
          }
          sendResponse({ success: true });
          break;
        }

        default:
          sendResponse({ error: `Unknown message type: ${message.type}` });
      }
    } catch (err) {
      console.error('[ShopQ Background] Error handling message:', message.type, err);
      sendResponse({ success: false, error: err.message });
    }
  })();

  return true; // Keep message channel open for asynchronous sendResponse
});

// 4. Tab Navigation Management (clean up badge when navigating away from supported retailers)
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete' || !tab?.url) return;

  if (!isSupportedRetailer(tab.url)) {
    try {
      await chrome.action.setBadgeText({ tabId, text: '' });
      await chrome.action.setTitle({ tabId, title: 'ShopQ - Check Before You Buy' });
    } catch {
      // Ignore errors for discarded or protected tabs
    }
  }
});
