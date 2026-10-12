/**
 * ShopQ Content Script (Manifest V3)
 * Detects supported retailer PDP (Product Detail Page) URLs.
 * Injects a small, unintrusive ShopQ floating indicator using Shadow DOM.
 * 
 * PRIVACY GUARANTEE:
 * Does NOT automatically stream browsing activity to any external server.
 * Operates purely locally on the page DOM until user explicitly clicks the badge.
 */

(function () {
  'use strict';

  // Retailer domain identifiers
  const RETAILER_CONFIGS = [
    {
      id: 'amazon',
      name: 'Amazon',
      domain: 'amazon.in',
      isPdp: (url) => /\/(dp|gp\/product|d|gp\/aw\/d)\/[A-Z0-9]{10}/i.test(url),
      getTitle: () => document.getElementById('productTitle')?.textContent?.trim() || '',
      getPrice: () => {
        const whole = document.querySelector('.a-price-whole')?.textContent?.replace(/[,.]/g, '');
        return whole ? parseFloat(whole) : null;
      }
    },
    {
      id: 'flipkart',
      name: 'Flipkart',
      domain: 'flipkart.com',
      isPdp: (url) => /\/p\/[a-z0-9]+/i.test(url) || url.includes('?pid=') || url.includes('&pid='),
      getTitle: () => document.querySelector('h1.VU-ZEz, span.B_NuCI, h1._6EBuvd')?.textContent?.trim() || '',
      getPrice: () => {
        const text = document.querySelector('div.Nx9bqj._4b5DiR, div._30jeq3._16J063')?.textContent?.replace(/[^0-9]/g, '');
        return text ? parseFloat(text) : null;
      }
    },
    {
      id: 'croma',
      name: 'Croma',
      domain: 'croma.com',
      isPdp: (url) => /\/p\/[0-9]+/i.test(url),
      getTitle: () => document.querySelector('h1.pd-title, h1.product-title')?.textContent?.trim() || '',
      getPrice: () => {
        const text = document.querySelector('span.amount, span.new-price')?.textContent?.replace(/[^0-9]/g, '');
        return text ? parseFloat(text) : null;
      }
    },
    {
      id: 'reliance',
      name: 'Reliance Digital',
      domain: 'reliancedigital.in',
      isPdp: (url) => /\/p\/[0-9a-zA-Z_-]+/i.test(url) || url.includes('/p/'),
      getTitle: () => document.querySelector('h1.pdp__title')?.textContent?.trim() || '',
      getPrice: () => {
        const text = document.querySelector('span.pdp__offerPrice')?.textContent?.replace(/[^0-9]/g, '');
        return text ? parseFloat(text) : null;
      }
    },
    {
      id: 'myntra',
      name: 'Myntra',
      domain: 'myntra.com',
      isPdp: (url) => /\/[0-9]+\/buy/i.test(url) || (url.includes('/buy') && !url.includes('/checkout/')),
      getTitle: () => {
        const brand = document.querySelector('h1.pdp-title')?.textContent?.trim() || '';
        const name = document.querySelector('h1.pdp-name')?.textContent?.trim() || '';
        return `${brand} ${name}`.trim();
      },
      getPrice: () => {
        const text = document.querySelector('span.pdp-price')?.textContent?.replace(/[^0-9]/g, '');
        return text ? parseFloat(text) : null;
      }
    },
    {
      id: 'tatacliq',
      name: 'Tata CLiQ',
      domain: 'tatacliq.com',
      isPdp: (url) => /\/p-mp[0-9]+/i.test(url) || url.includes('/p-'),
      getTitle: () => document.querySelector('h1.ProductDescriptionPage__productName, h1')?.textContent?.trim() || '',
      getPrice: () => {
        const text = document.querySelector('h3.ProductDescriptionPage__price, span.ProductDescriptionPage__discountPrice')?.textContent?.replace(/[^0-9]/g, '');
        return text ? parseFloat(text) : null;
      }
    },
    {
      id: 'ajio',
      name: 'AJIO',
      domain: 'ajio.com',
      isPdp: (url) => /\/p\/[0-9]+/i.test(url),
      getTitle: () => document.querySelector('h1.prod-title, div.prod-name')?.textContent?.trim() || '',
      getPrice: () => {
        const text = document.querySelector('span.prod-sp, div.prod-cp')?.textContent?.replace(/[^0-9]/g, '');
        return text ? parseFloat(text) : null;
      }
    },
    {
      id: 'meesho',
      name: 'Meesho',
      domain: 'meesho.com',
      isPdp: (url) => /\/p\/[0-9a-zA-Z]+/i.test(url) || url.includes('/s/p/'),
      getTitle: () => document.querySelector('h1')?.textContent?.trim() || '',
      getPrice: () => {
        const text = document.querySelector('h4, span.Text__StyledText')?.textContent?.replace(/[^0-9]/g, '');
        return text ? parseFloat(text) : null;
      }
    },
    {
      id: 'jiomart',
      name: 'JioMart',
      domain: 'jiomart.com',
      isPdp: (url) => /\/p\/[a-z0-9_-]+\/[0-9]+/i.test(url) || url.includes('/p/'),
      getTitle: () => document.querySelector('div.pdp-title, h1')?.textContent?.trim() || '',
      getPrice: () => {
        const text = document.querySelector('span.jm-heading-xxs, div.price-box')?.textContent?.replace(/[^0-9]/g, '');
        return text ? parseFloat(text) : null;
      }
    },
    {
      id: 'nykaa',
      name: 'Nykaa',
      domain: 'nykaa.com',
      isPdp: (url) => /\/p\/[0-9]+/i.test(url),
      getTitle: () => document.querySelector('h1.css-1gc4x7i, h1')?.textContent?.trim() || '',
      getPrice: () => {
        const text = document.querySelector('span.css-11122p1, span.css-1725288')?.textContent?.replace(/[^0-9]/g, '');
        return text ? parseFloat(text) : null;
      }
    }
  ];

  let currentRetailer = null;
  let isDismissedForUrl = false;
  let lastCheckedUrl = '';

  /**
   * Determine whether current window location is a product detail page.
   */
  function detectProductPage() {
    const url = window.location.href;
    const hostname = window.location.hostname;

    for (const config of RETAILER_CONFIGS) {
      if (hostname.includes(config.domain)) {
        if (config.isPdp(url)) {
          return config;
        }
      }
    }

    // Generic schema.org fallback
    try {
      const isProductMeta = document.querySelector('meta[property="og:type"][content="product"]') !== null;
      const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
      for (const script of jsonLdScripts) {
        if (script.textContent.includes('"@type":"Product"') || script.textContent.includes('"@type": "Product"')) {
          return {
            id: 'generic',
            name: hostname.replace('www.', ''),
            domain: hostname,
            getTitle: () => document.title || '',
            getPrice: () => null
          };
        }
      }
      if (isProductMeta) {
        return {
          id: 'generic',
          name: hostname.replace('www.', ''),
          domain: hostname,
          getTitle: () => document.title || '',
          getPrice: () => null
        };
      }
    } catch {
      // Ignore parser errors
    }

    return null;
  }

  /**
   * Injects the isolated ShopQ indicator badge using Shadow DOM.
   */
  function injectShopQBadge(retailer) {
    if (document.getElementById('shopq-indicator-host')) {
      return; // Already present
    }

    const host = document.createElement('div');
    host.id = 'shopq-indicator-host';

    const shadow = host.attachShadow({ mode: 'open' });

    // Styles matching ShopQ Design System (#FAF8F5, #FFFFFF, #C96B7A accent)
    const style = document.createElement('style');
    style.textContent = `
      :host {
        all: initial;
        display: block;
      }
      
      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }

      .shopq-badge-container {
        display: flex;
        align-items: center;
        background-color: #FFFFFF;
        border: 1px solid #E8E4E0;
        border-radius: 24px;
        padding: 6px 12px 6px 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.04);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #1A1A1A;
        font-size: 13px;
        font-weight: 500;
        line-height: 1;
        cursor: pointer;
        user-select: none;
        transition: transform 0.2s cubic-bezier(0.2, 0, 0, 1), box-shadow 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;
        animation: shopqSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }

      .shopq-badge-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(201, 107, 122, 0.18), 0 2px 6px rgba(0, 0, 0, 0.06);
        border-color: #C96B7A;
        background-color: #FAF8F5;
      }

      .shopq-emblem {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background-color: #C96B7A;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 700;
        margin-right: 8px;
        flex-shrink: 0;
        letter-spacing: -0.5px;
      }

      .shopq-text-group {
        display: flex;
        flex-direction: column;
        gap: 2px;
        margin-right: 8px;
      }

      .shopq-title {
        font-size: 13px;
        font-weight: 600;
        color: #1A1A1A;
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .shopq-subtitle {
        font-size: 10px;
        font-weight: 400;
        color: #6B6B6B;
      }

      .shopq-arrow {
        color: #C96B7A;
        font-size: 14px;
        margin-left: 2px;
        transition: transform 0.15s ease;
      }

      .shopq-badge-container:hover .shopq-arrow {
        transform: translateX(2px);
      }

      .shopq-dismiss-btn {
        background: transparent;
        border: none;
        color: #8A8A8A;
        font-size: 16px;
        line-height: 1;
        cursor: pointer;
        padding: 4px;
        margin-left: 6px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: color 0.15s ease, background-color 0.15s ease;
      }

      .shopq-dismiss-btn:hover {
        color: #1A1A1A;
        background-color: #E8E4E0;
      }

      @keyframes shopqSlideIn {
        from {
          opacity: 0;
          transform: translateY(12px) scale(0.95);
        }
        to {
          opacity: 1;
          transform: translateY(0) scale(1);
        }
      }

      @media (max-width: 480px) {
        .shopq-subtitle {
          display: none;
        }
        .shopq-badge-container {
          padding: 6px 10px 6px 6px;
        }
      }
    `;

    const badge = document.createElement('div');
    badge.className = 'shopq-badge-container';
    badge.setAttribute('role', 'button');
    badge.setAttribute('tabindex', '0');
    badge.setAttribute('aria-label', 'Open ShopQ analysis');

    badge.innerHTML = `
      <div class="shopq-emblem">Q</div>
      <div class="shopq-text-group">
        <div class="shopq-title">
          <span>ShopQ</span>
          <span style="font-weight: 400; color: #6B6B6B;">· Check Price</span>
        </div>
        <div class="shopq-subtitle">Advice before you buy</div>
      </div>
      <div class="shopq-arrow">→</div>
      <button class="shopq-dismiss-btn" title="Dismiss for now" aria-label="Dismiss ShopQ indicator">×</button>
    `;

    // Handle badge click -> Open side panel
    badge.addEventListener('click', (e) => {
      // If user clicked dismiss button, ignore badge trigger
      if (e.target.closest('.shopq-dismiss-btn')) return;

      const title = retailer.getTitle ? retailer.getTitle() : document.title;
      const price = retailer.getPrice ? retailer.getPrice() : null;

      const titleEl = badge.querySelector('.shopq-title');
      if (titleEl) {
        titleEl.textContent = 'Opening ShopQ...';
      }

      // Notify background service worker to open native chrome.sidePanel
      chrome.runtime.sendMessage(
        {
          type: 'OPEN_SIDE_PANEL',
          url: window.location.href,
          retailer: retailer.name,
          title: title || document.title,
          price: price
        },
        () => {
          setTimeout(() => {
            if (titleEl) {
              titleEl.innerHTML = `<span>ShopQ</span><span style="font-weight: 400; color: #6B6B6B;">· Check Price</span>`;
            }
          }, 1500);
        }
      );
    });

    // Handle dismiss button
    const dismissBtn = badge.querySelector('.shopq-dismiss-btn');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        isDismissedForUrl = true;
        host.remove();
      });
    }

    shadow.appendChild(style);
    shadow.appendChild(badge);

    document.documentElement.appendChild(host);

    // Notify background script that PDP is active (so action icon badge updates to 'Q')
    chrome.runtime.sendMessage({
      type: 'PDP_DETECTED',
      retailer: retailer.name
    }).catch(() => {});
  }

  /**
   * Removes injected badge if user navigates away from PDP.
   */
  function removeShopQBadge() {
    const host = document.getElementById('shopq-indicator-host');
    if (host) {
      host.remove();
    }
  }

  /**
   * Main evaluator triggered on document ready and SPA route changes.
   */
  function evaluatePage() {
    const currentUrl = window.location.href;

    if (currentUrl !== lastCheckedUrl) {
      lastCheckedUrl = currentUrl;
      isDismissedForUrl = false;
    }

    if (isDismissedForUrl) {
      return;
    }

    const detected = detectProductPage();
    if (detected) {
      currentRetailer = detected;
      injectShopQBadge(detected);
    } else {
      currentRetailer = null;
      removeShopQBadge();
    }
  }

  // Initial evaluation when DOM content is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', evaluatePage);
  } else {
    evaluatePage();
  }

  // Periodic and event-based checks for client-side SPA navigation
  window.addEventListener('popstate', () => setTimeout(evaluatePage, 200));
  window.addEventListener('hashchange', () => setTimeout(evaluatePage, 200));

  // Secondary observer to catch dynamic DOM transitions (common in Flipkart & Myntra)
  let checkTimer = null;
  const observer = new MutationObserver(() => {
    if (window.location.href !== lastCheckedUrl) {
      if (checkTimer) clearTimeout(checkTimer);
      checkTimer = setTimeout(evaluatePage, 300);
    }
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: false
  });
})();
