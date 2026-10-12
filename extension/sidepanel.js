/**
 * ShopQ Side Panel Controller (Manifest V3)
 * Consumes FastAPI POST /api/analyze contract: { product, decision, best_offer }.
 * Renders ShopQ light mode UI with humanized pre-purchase recommendations.
 */

(function () {
  'use strict';

  // State
  let config = {
    backendUrl: 'http://localhost:8000',
    webAppUrl: 'http://localhost:5173'
  };

  let currentTargetUrl = '';
  let currentAnalysisData = null;
  let isWatchingCurrentItem = false;

  // DOM Elements
  const elements = {
    // Views
    idleView: document.getElementById('idleView'),
    thinkingView: document.getElementById('thinkingView'),
    resultView: document.getElementById('resultView'),
    errorView: document.getElementById('errorView'),

    // Header & Settings
    refreshBtn: document.getElementById('refreshBtn'),
    settingsToggleBtn: document.getElementById('settingsToggleBtn'),
    settingsPanel: document.getElementById('settingsPanel'),
    backendUrlInput: document.getElementById('backendUrlInput'),
    webAppUrlInput: document.getElementById('webAppUrlInput'),
    saveSettingsBtn: document.getElementById('saveSettingsBtn'),
    cancelSettingsBtn: document.getElementById('cancelSettingsBtn'),

    // Context Bar
    contextBar: document.getElementById('contextBar'),
    contextRetailerBadge: document.getElementById('contextRetailerBadge'),
    contextTitle: document.getElementById('contextTitle'),

    // Idle View
    manualUrlForm: document.getElementById('manualUrlForm'),
    manualUrlInput: document.getElementById('manualUrlInput'),
    sampleChips: document.querySelectorAll('.sample-chip'),

    // Thinking Steps
    step1: document.getElementById('step1'),
    step2: document.getElementById('step2'),
    step3: document.getElementById('step3'),

    // Result View
    resultBrand: document.getElementById('resultBrand'),
    resultName: document.getElementById('resultName'),
    resultCurrentPrice: document.getElementById('resultCurrentPrice'),
    resultRetailer: document.getElementById('resultRetailer'),

    verdictCard: document.getElementById('verdictCard'),
    verdictBadge: document.getElementById('verdictBadge'),
    verdictEmoji: document.getElementById('verdictEmoji'),
    verdictLabel: document.getElementById('verdictLabel'),
    confidenceBadge: document.getElementById('confidenceBadge'),
    verdictHeadline: document.getElementById('verdictHeadline'),
    primaryReason: document.getElementById('primaryReason'),
    secondaryReasonsList: document.getElementById('secondaryReasonsList'),

    buyPointCard: document.getElementById('buyPointCard'),
    buyPointPrice: document.getElementById('buyPointPrice'),
    buyPointAdvice: document.getElementById('buyPointAdvice'),
    watchBtn: document.getElementById('watchBtn'),
    watchBtnIcon: document.getElementById('watchBtnIcon'),
    watchBtnText: document.getElementById('watchBtnText'),

    bestOfferCard: document.getElementById('bestOfferCard'),
    bestOfferRetailer: document.getElementById('bestOfferRetailer'),
    bestOfferPrice: document.getElementById('bestOfferPrice'),
    bestOfferMeta: document.getElementById('bestOfferMeta'),
    bestOfferLink: document.getElementById('bestOfferLink'),

    sellerStatus: document.getElementById('sellerStatus'),
    sellerReturn: document.getElementById('sellerReturn'),

    openWebAppBtn: document.getElementById('openWebAppBtn'),

    // Error View
    errorMessage: document.getElementById('errorMessage'),
    retryBtn: document.getElementById('retryBtn'),
    errorSettingsBtn: document.getElementById('errorSettingsBtn')
  };

  /**
   * Currency formatter for Indian Rupee (INR).
   */
  function formatPrice(amount) {
    if (amount === undefined || amount === null || isNaN(amount)) {
      return '₹--';
    }
    try {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
      }).format(amount);
    } catch {
      return `₹${Number(amount).toLocaleString('en-IN')}`;
    }
  }

  /**
   * Switch active sidepanel view.
   */
  function showView(viewName) {
    elements.idleView.classList.add('hidden');
    elements.thinkingView.classList.add('hidden');
    elements.resultView.classList.add('hidden');
    elements.errorView.classList.add('hidden');

    switch (viewName) {
      case 'idle':
        elements.idleView.classList.remove('hidden');
        break;
      case 'thinking':
        elements.thinkingView.classList.remove('hidden');
        resetThinkingSteps();
        break;
      case 'result':
        elements.resultView.classList.remove('hidden');
        break;
      case 'error':
        elements.errorView.classList.remove('hidden');
        break;
    }
  }

  /**
   * Thinking animation state machine.
   */
  function resetThinkingSteps() {
    [elements.step1, elements.step2, elements.step3].forEach((step, idx) => {
      step.className = 'step-item';
      step.querySelector('.step-icon').textContent = '⏳';
    });
    elements.step1.classList.add('active');
  }

  function advanceThinkingStep(stepNum) {
    if (stepNum === 1) {
      elements.step1.className = 'step-item done';
      elements.step1.querySelector('.step-icon').textContent = '✓';
      elements.step2.className = 'step-item active';
    } else if (stepNum === 2) {
      elements.step2.className = 'step-item done';
      elements.step2.querySelector('.step-icon').textContent = '✓';
      elements.step3.className = 'step-item active';
    } else if (stepNum === 3) {
      elements.step3.className = 'step-item done';
      elements.step3.querySelector('.step-icon').textContent = '✓';
    }
  }

  /**
   * Load configuration from chrome.storage.local.
   */
  async function loadConfig() {
    const data = await chrome.storage.local.get(['backendUrl', 'webAppUrl']);
    if (data.backendUrl) config.backendUrl = data.backendUrl;
    if (data.webAppUrl) config.webAppUrl = data.webAppUrl;

    elements.backendUrlInput.value = config.backendUrl;
    elements.webAppUrlInput.value = config.webAppUrl;
  }

  /**
   * Save configuration to chrome.storage.local.
   */
  async function saveConfig() {
    const backend = elements.backendUrlInput.value.trim() || 'http://localhost:8000';
    const webApp = elements.webAppUrlInput.value.trim() || 'http://localhost:5173';

    config.backendUrl = backend;
    config.webAppUrl = webApp;

    await chrome.storage.local.set({
      backendUrl: backend,
      webAppUrl: webApp
    });

    elements.settingsPanel.classList.add('hidden');
  }

  /**
   * Detect Retailer name from URL.
   */
  function getRetailerNameFromUrl(url) {
    if (!url) return 'Retailer';
    if (url.includes('amazon.in')) return 'Amazon';
    if (url.includes('flipkart.com')) return 'Flipkart';
    if (url.includes('croma.com')) return 'Croma';
    if (url.includes('reliancedigital.in')) return 'Reliance Digital';
    if (url.includes('myntra.com')) return 'Myntra';
    return 'Retailer';
  }

  /**
   * Update Context Bar on top of side panel.
   */
  function setContextBar(retailer, title) {
    if (!retailer && !title) {
      elements.contextBar.classList.add('hidden');
      return;
    }
    elements.contextRetailerBadge.textContent = retailer || 'Store';
    elements.contextTitle.textContent = title || 'Active Listing';
    elements.contextBar.classList.remove('hidden');
  }

  /**
   * Main API Caller: requests POST /api/analyze to backend.
   */
  async function analyzeProduct(queryOrUrl) {
    if (!queryOrUrl || !queryOrUrl.trim()) return;

    currentTargetUrl = queryOrUrl.trim();
    showView('thinking');

    // Step 1 animation
    setTimeout(() => advanceThinkingStep(1), 300);

    try {
      const endpoint = `${config.backendUrl.replace(/\/+$/, '')}/api/analyze`;
      
      const payload = {
        url: currentTargetUrl,
        input: currentTargetUrl
      };

      // Step 2 animation
      setTimeout(() => advanceThinkingStep(2), 650);

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}: ${response.statusText}`);
      }

      // Step 3 animation
      advanceThinkingStep(3);

      const data = await response.json();
      currentAnalysisData = data;

      // Small pause to let user see step 3 completion, then render
      setTimeout(() => {
        renderAnalysis(data);
        showView('result');
      }, 350);

    } catch (err) {
      console.error('[ShopQ Sidepanel] Analysis error:', err);
      elements.errorMessage.textContent = `Could not reach ShopQ backend (${config.backendUrl}). Error: ${err.message}. Ensure the FastAPI server is running.`;
      showView('error');
    }
  }

  /**
   * Render structured analysis JSON into UI components.
   */
  function renderAnalysis(data) {
    const product = data.product || {};
    const decision = data.decision || {};
    const bestOffer = data.best_offer || data.bestOffer || null;

    // 1. Context & Product Header
    const retailer = product.retailer || getRetailerNameFromUrl(currentTargetUrl);
    setContextBar(retailer, product.name || 'Analyzed Product');

    elements.resultBrand.textContent = product.brand || 'Product';
    elements.resultName.textContent = product.name || 'Selected Item';
    
    const priceVal = product.current_price ?? product.currentPrice;
    elements.resultCurrentPrice.textContent = formatPrice(priceVal);
    elements.resultRetailer.textContent = `on ${retailer}`;

    // 2. Verdict Badge & Card
    const decType = (decision.decision || 'WAIT').toUpperCase();
    const confLevel = (decision.confidence_level || decision.confidence || 'HIGH').toUpperCase();

    // Reset card classes
    elements.verdictCard.className = 'card verdict-card';
    elements.verdictBadge.className = 'verdict-badge';

    let emoji = '⏳';
    let label = 'WAIT A LITTLE';
    let headline = "I'd hold off for now.";
    let cardClass = 'type-wait';
    let badgeClass = 'badge-warning';

    if (decType === 'BUY' || decType === 'GRAB') {
      emoji = decType === 'GRAB' ? '🔥' : '🛒';
      label = decType === 'GRAB' ? 'GRAB IT NOW' : 'BUY IT';
      headline = 'This is a really good moment to buy.';
      cardClass = 'type-buy';
      badgeClass = 'badge-positive';
    } else if (decType === 'WAIT' || decType === 'WAIT_SALE') {
      emoji = decType === 'WAIT_SALE' ? '🎯' : '⏳';
      label = decType === 'WAIT_SALE' ? 'WAIT FOR A SALE' : 'WAIT A LITTLE';
      headline = "I'd hold off for now.";
      cardClass = 'type-wait';
      badgeClass = 'badge-warning';
    } else if (decType === 'CAUTION' || decType === 'DONT_RUSH') {
      emoji = decType === 'DONT_RUSH' ? '🚫' : '⚠️';
      label = decType === 'DONT_RUSH' ? "DON'T RUSH" : 'PROCEED WITH CAUTION';
      headline = "The price looks good, but I'd be careful here.";
      cardClass = 'type-caution';
      badgeClass = 'badge-danger';
    } else if (decType === 'CHECK_ALT') {
      emoji = '👀';
      label = 'CHECK ANOTHER OPTION';
      headline = 'I found a better option.';
      cardClass = 'type-wait';
      badgeClass = 'badge-warning';
    } else {
      emoji = '🤷';
      label = 'YOUR CALL';
      headline = 'Reasonable price, but no urgent signal.';
      cardClass = 'type-neutral';
      badgeClass = 'badge-neutral';
    }

    elements.verdictCard.classList.add(cardClass);
    elements.verdictBadge.classList.add(badgeClass);
    elements.verdictEmoji.textContent = emoji;
    elements.verdictLabel.textContent = label;

    // Confidence
    let confText = 'Pretty confident';
    if (confLevel === 'MEDIUM') confText = 'Reasonably confident';
    if (confLevel === 'LOW') confText = 'Low confidence';
    elements.confidenceBadge.textContent = confText;

    // Headline & Primary Reason
    elements.verdictHeadline.textContent = headline;
    elements.primaryReason.textContent = decision.primary_reason || product.explanation || 'Verified market signals and pricing patterns.';

    // Secondary Reasons
    elements.secondaryReasonsList.innerHTML = '';
    const reasons = decision.secondary_reasons || product.reasons || [];
    if (Array.isArray(reasons) && reasons.length > 0) {
      reasons.forEach(r => {
        const li = document.createElement('li');
        li.textContent = r;
        elements.secondaryReasonsList.appendChild(li);
      });
      elements.secondaryReasonsList.classList.remove('hidden');
    } else {
      elements.secondaryReasonsList.classList.add('hidden');
    }

    // 3. Buy Point Target
    const buyPointVal = decision.buy_point ?? product.buy_point ?? product.buyPoint;
    if (buyPointVal) {
      elements.buyPointPrice.textContent = formatPrice(buyPointVal);
      elements.buyPointAdvice.textContent = `I'd reconsider around ${formatPrice(buyPointVal)}.`;
      elements.buyPointCard.classList.remove('hidden');
    } else {
      elements.buyPointCard.classList.add('hidden');
    }

    // Check watch status
    checkWatchStatus(product.id || currentTargetUrl);

    // 4. Best Offer Card
    if (bestOffer && bestOffer.price) {
      elements.bestOfferRetailer.textContent = bestOffer.retailer || 'Alternative Retailer';
      elements.bestOfferPrice.textContent = formatPrice(bestOffer.price);
      
      const sellerStat = bestOffer.seller_status || 'Verified Seller';
      elements.bestOfferMeta.textContent = `🛡️ ${sellerStat} · In Stock`;

      if (bestOffer.url) {
        elements.bestOfferLink.href = bestOffer.url;
        elements.bestOfferLink.classList.remove('hidden');
      } else {
        elements.bestOfferLink.classList.add('hidden');
      }

      elements.bestOfferCard.classList.remove('hidden');
    } else {
      elements.bestOfferCard.classList.add('hidden');
    }

    // 5. Seller Status
    const sellerObj = product.seller || {};
    const sellerRel = sellerObj.reliability || (typeof sellerObj === 'string' ? sellerObj : 'RELIABLE');
    elements.sellerStatus.textContent = sellerRel === 'RELIABLE' ? '🛡️ Looks reliable' : '⚠️ Double check';
    elements.sellerReturn.textContent = sellerObj.return_policy || '7-day replacement';

    // 6. Web App CTA Link
    const productId = product.id || encodeURIComponent(currentTargetUrl);
    const webAppUrl = `${config.webAppUrl.replace(/\/+$/, '')}/analyze/${productId}`;
    elements.openWebAppBtn.href = webAppUrl;
  }

  /**
   * Watchlist storage management.
   */
  async function checkWatchStatus(itemId) {
    const data = await chrome.storage.local.get('watchlist');
    const watchlist = Array.isArray(data.watchlist) ? data.watchlist : [];
    isWatchingCurrentItem = watchlist.some(w => w.id === itemId || w.url === currentTargetUrl);

    updateWatchBtnUI();
  }

  function updateWatchBtnUI() {
    if (isWatchingCurrentItem) {
      elements.watchBtnIcon.textContent = '✓';
      elements.watchBtnText.textContent = 'Watching in ShopQ';
      elements.watchBtn.classList.remove('btn-secondary');
      elements.watchBtn.classList.add('btn-primary');
    } else {
      elements.watchBtnIcon.textContent = '🔔';
      elements.watchBtnText.textContent = 'Watch this item in ShopQ';
      elements.watchBtn.classList.remove('btn-primary');
      elements.watchBtn.classList.add('btn-secondary');
    }
  }

  async function toggleWatchItem() {
    if (!currentAnalysisData) return;

    const product = currentAnalysisData.product || {};
    const decision = currentAnalysisData.decision || {};
    const itemId = product.id || currentTargetUrl;

    const data = await chrome.storage.local.get('watchlist');
    let watchlist = Array.isArray(data.watchlist) ? data.watchlist : [];

    if (isWatchingCurrentItem) {
      watchlist = watchlist.filter(w => w.id !== itemId && w.url !== currentTargetUrl);
      isWatchingCurrentItem = false;
    } else {
      watchlist.push({
        id: itemId,
        name: product.name || 'Watched Product',
        currentPrice: product.current_price ?? product.currentPrice,
        buyPoint: decision.buy_point ?? product.buy_point,
        url: currentTargetUrl,
        addedAt: Date.now()
      });
      isWatchingCurrentItem = true;
    }

    await chrome.storage.local.set({ watchlist });
    updateWatchBtnUI();
  }

  /**
   * Check active tab on sidepanel launch.
   */
  async function checkActiveTabForProduct() {
    // 1. Check storage if content script already staged an activeProduct
    const stored = await chrome.storage.local.get('activeProduct');
    if (stored.activeProduct && stored.activeProduct.url) {
      // If detected in last 10 minutes, prioritize it
      const age = Date.now() - (stored.activeProduct.timestamp || 0);
      if (age < 10 * 60 * 1000) {
        setContextBar(stored.activeProduct.retailer, stored.activeProduct.title);
        analyzeProduct(stored.activeProduct.url);
        return;
      }
    }

    // 2. Query the current active browser tab
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab?.url) {
        const supportedRetailers = ['amazon.in', 'flipkart.com', 'croma.com', 'reliancedigital.in', 'myntra.com'];
        const isSupported = supportedRetailers.some(domain => tab.url.includes(domain));

        if (isSupported) {
          const retailer = getRetailerNameFromUrl(tab.url);
          setContextBar(retailer, tab.title);
          analyzeProduct(tab.url);
          return;
        }
      }
    } catch (err) {
      console.warn('[ShopQ Sidepanel] Could not query active tab:', err);
    }

    // 3. Fallback: Show Idle view
    showView('idle');
  }

  /**
   * Event Listeners Registration.
   */
  function initListeners() {
    // Header actions
    elements.refreshBtn.addEventListener('click', () => {
      if (currentTargetUrl) {
        analyzeProduct(currentTargetUrl);
      } else {
        checkActiveTabForProduct();
      }
    });

    elements.settingsToggleBtn.addEventListener('click', () => {
      elements.settingsPanel.classList.toggle('hidden');
    });

    elements.saveSettingsBtn.addEventListener('click', saveConfig);
    elements.cancelSettingsBtn.addEventListener('click', () => {
      elements.settingsPanel.classList.add('hidden');
    });

    // Idle View: Manual Search
    elements.manualUrlForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = elements.manualUrlInput.value.trim();
      if (val) {
        analyzeProduct(val);
      }
    });

    // Idle View: Sample Chips
    elements.sampleChips.forEach(chip => {
      chip.addEventListener('click', () => {
        const query = chip.getAttribute('data-query');
        if (query) {
          analyzeProduct(query);
        }
      });
    });

    // Watch Button
    elements.watchBtn.addEventListener('click', toggleWatchItem);

    // Error View Actions
    elements.retryBtn.addEventListener('click', () => {
      if (currentTargetUrl) {
        analyzeProduct(currentTargetUrl);
      } else {
        checkActiveTabForProduct();
      }
    });

    elements.errorSettingsBtn.addEventListener('click', () => {
      elements.settingsPanel.classList.remove('hidden');
    });

    // Listen for storage changes from background or other tabs
    chrome.storage.onChanged.addListener((changes, area) => {
      if (area === 'local' && changes.activeProduct?.newValue) {
        const newProduct = changes.activeProduct.newValue;
        if (newProduct.url && newProduct.url !== currentTargetUrl) {
          setContextBar(newProduct.retailer, newProduct.title);
          analyzeProduct(newProduct.url);
        }
      }
    });
  }

  // Initialization Entry Point
  document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    initListeners();
    await checkActiveTabForProduct();
  });
})();
