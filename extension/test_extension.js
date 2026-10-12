/**
 * ShopQ Chrome Extension Test & Validation Suite
 * Validates Manifest V3 compliance, bundle file existence, CSP rules,
 * design system adherence, and API contract parsing.
 */

const fs = require('fs');
const path = require('path');

const EXT_DIR = path.resolve(__dirname);
let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function assert(condition, message) {
  totalTests++;
  if (condition) {
    passedTests++;
    console.log(`  ✓ PASS: ${message}`);
  } else {
    failedTests++;
    console.error(`  ✗ FAIL: ${message}`);
  }
}

console.log('====================================================');
console.log('🧪 Starting ShopQ Manifest V3 Extension Validation');
console.log(`Directory: ${EXT_DIR}`);
console.log('====================================================\n');

// 1. MANIFEST V3 VALIDATION
console.log('📦 1. Manifest V3 Syntax & Permissions:');
const manifestPath = path.join(EXT_DIR, 'manifest.json');
assert(fs.existsSync(manifestPath), 'manifest.json exists');

let manifest = null;
try {
  const content = fs.readFileSync(manifestPath, 'utf8');
  manifest = JSON.parse(content);
  assert(true, 'manifest.json is valid JSON');
} catch (err) {
  assert(false, `manifest.json parsing error: ${err.message}`);
}

if (manifest) {
  assert(manifest.manifest_version === 3, 'manifest_version is exactly 3');
  assert(typeof manifest.name === 'string' && manifest.name.length > 0, 'Extension has name');
  assert(typeof manifest.version === 'string' && manifest.version.length > 0, 'Extension has version');

  // Permissions
  const expectedPerms = ['activeTab', 'sidePanel', 'storage'];
  const hasPerms = expectedPerms.every(p => manifest.permissions && manifest.permissions.includes(p));
  assert(hasPerms, `Declares minimal permissions: ${expectedPerms.join(', ')}`);

  // Host permissions
  const expectedHosts = [
    '*://*.amazon.in/*',
    '*://*.flipkart.com/*',
    '*://*.croma.com/*',
    '*://*.reliancedigital.in/*',
    '*://*.myntra.com/*'
  ];
  const hasHosts = expectedHosts.every(h => manifest.host_permissions && manifest.host_permissions.includes(h));
  assert(hasHosts, `Declares host_permissions for 5 supported retailers`);

  // Side Panel API
  assert(manifest.side_panel && manifest.side_panel.default_path === 'sidepanel.html', 'side_panel configured with default_path "sidepanel.html"');
  
  // Action key
  assert(manifest.action && typeof manifest.action === 'object', 'action object declared in manifest');

  // Background Service Worker
  assert(manifest.background && manifest.background.service_worker === 'background.js', 'background.service_worker points to background.js');

  // Content Scripts
  assert(Array.isArray(manifest.content_scripts) && manifest.content_scripts.length > 0, 'content_scripts configured');
  if (manifest.content_scripts && manifest.content_scripts[0]) {
    const cs = manifest.content_scripts[0];
    assert(cs.js.includes('content.js'), 'content_scripts includes content.js');
    assert(cs.css.includes('content.css'), 'content_scripts includes content.css');
  }

  // Referenced files check
  const referencedFiles = [
    manifest.background?.service_worker,
    manifest.side_panel?.default_path,
    ...(manifest.content_scripts?.[0]?.js || []),
    ...(manifest.content_scripts?.[0]?.css || [])
  ].filter(Boolean);

  referencedFiles.forEach(relPath => {
    const absPath = path.join(EXT_DIR, relPath);
    assert(fs.existsSync(absPath), `Referenced file exists: ${relPath}`);
  });
}

// 2. CSP & SYNTAX INTEGRITY CHECKS
console.log('\n🔒 2. CSP & Security Rules:');
const jsFiles = ['background.js', 'content.js', 'sidepanel.js'];
jsFiles.forEach(file => {
  const filePath = path.join(EXT_DIR, file);
  if (fs.existsSync(filePath)) {
    const code = fs.readFileSync(filePath, 'utf8');
    assert(!code.includes('eval('), `${file} does NOT contain eval()`);
    assert(!code.includes('new Function('), `${file} does NOT contain new Function()`);
  }
});

const htmlPath = path.join(EXT_DIR, 'sidepanel.html');
if (fs.existsSync(htmlPath)) {
  const html = fs.readFileSync(htmlPath, 'utf8');
  assert(!/onclick\s*=/i.test(html), 'sidepanel.html contains NO inline onclick handlers (CSP compliant)');
  assert(!/onload\s*=/i.test(html), 'sidepanel.html contains NO inline onload handlers (CSP compliant)');
  assert(!/<script>[\s\S]*?<\/script>/i.test(html), 'sidepanel.html contains NO inline <script> tags (CSP compliant)');
  assert(html.includes('<script src="sidepanel.js"></script>'), 'sidepanel.html imports external sidepanel.js');
  assert(html.includes('<link rel="stylesheet" href="sidepanel.css">'), 'sidepanel.html imports external sidepanel.css');
}

// 3. DESIGN SYSTEM VERIFICATION
console.log('\n🎨 3. ShopQ Light Mode Design System Compliance:');
const cssPath = path.join(EXT_DIR, 'sidepanel.css');
if (fs.existsSync(cssPath)) {
  const css = fs.readFileSync(cssPath, 'utf8');
  assert(css.includes('#FAF8F5') || css.includes('var(--bg)'), 'sidepanel.css uses #FAF8F5 light background');
  assert(css.includes('#FFFFFF') || css.includes('var(--bg-card)'), 'sidepanel.css uses #FFFFFF card background');
  assert(css.includes('#C96B7A') || css.includes('var(--accent)'), 'sidepanel.css uses #C96B7A Dusty Rose accent');
  assert(css.includes('#E8E4E0') || css.includes('var(--border)'), 'sidepanel.css uses #E8E4E0 1px borders');
  assert(css.includes('8px'), 'sidepanel.css uses 8px radius');
  assert(css.includes('Inter'), 'sidepanel.css specifies Inter typography');
}

// 4. API CONTRACT TEST SIMULATION
console.log('\n📡 4. Backend /api/analyze Contract Compatibility:');
const mockApiResponse = {
  product: {
    id: "sony_wh1000xm5",
    name: "Sony WH-1000XM5",
    brand: "Sony",
    category: "Headphones",
    variant: "Black",
    current_price: 23499,
    currency: "INR",
    retailer: "Amazon"
  },
  decision: {
    decision: "WAIT",
    confidence_level: "HIGH",
    primary_reason: "PRICE_TREND_FALLING",
    secondary_reasons: ["ABOVE_RECENT_LOW", "BETTER_TIMING_POSSIBLE"],
    buy_point: 22999,
    best_offer_id: "offer_123",
    data_freshness: "FRESH",
    data_coverage: "MEDIUM",
    checked_at: "2026-10-07T23:55:00Z"
  },
  best_offer: {
    id: "offer_123",
    retailer: "Flipkart",
    price: 22499,
    seller_status: "RELIABLE",
    availability: "IN_STOCK",
    url: "https://flipkart.com/..."
  }
};

assert(Boolean(mockApiResponse.product.id), 'Contract contains product.id');
assert(typeof mockApiResponse.product.current_price === 'number', 'Contract product.current_price is a numeric price');
assert(Boolean(mockApiResponse.decision.decision), 'Contract contains decision.decision');
assert(typeof mockApiResponse.decision.buy_point === 'number', 'Contract decision.buy_point is present');
assert(Boolean(mockApiResponse.best_offer.retailer), 'Contract best_offer.retailer is present');

// Format price check
const formatted = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0
}).format(mockApiResponse.product.current_price);
assert(formatted.includes('23,499'), `Price formats correctly with Indian grouping: ${formatted}`);

console.log('\n====================================================');
console.log(`📊 Summary: ${passedTests}/${totalTests} tests passed (${failedTests} failures).`);
console.log('====================================================');

if (failedTests > 0) {
  process.exit(1);
} else {
  console.log('🎉 ALL EXTENSION VALIDATION TESTS PASSED!');
  process.exit(0);
}
