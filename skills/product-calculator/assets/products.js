/* ─── PRODUCT DEFINITIONS ─── */
// Customize these definitions for your product line

const productCatalog = {
  'product-basic': {
    name: 'Basic Package',
    variants: [
      { sku: 'BASIC-S', quantity: 100, price: 1000 },
      { sku: 'BASIC-M', quantity: 500, price: 4000 },
      { sku: 'BASIC-L', quantity: 1000, price: 7500 },
      { sku: 'BASIC-XL', quantity: 5000, price: 30000 }
    ]
  },
  'product-professional': {
    name: 'Professional Package',
    variants: [
      { sku: 'PRO-S', quantity: 100, price: 2000 },
      { sku: 'PRO-M', quantity: 500, price: 8000 },
      { sku: 'PRO-L', quantity: 1000, price: 15000 },
      { sku: 'PRO-XL', quantity: 5000, price: 60000 }
    ]
  },
  'product-enterprise': {
    name: 'Enterprise Package',
    variants: [
      { sku: 'ENT-S', quantity: 1000, price: 20000 },
      { sku: 'ENT-M', quantity: 5000, price: 80000 },
      { sku: 'ENT-L', quantity: 10000, price: 150000 },
      { sku: 'ENT-XL', quantity: 50000, price: 600000 }
    ]
  }
};

/* ─── ADDON DEFINITIONS ─── */
const addonCatalog = {
  // Support packages
  'support-basic': { name: 'Basic Support', price: 500, type: 'annual' },
  'support-premium': { name: 'Premium Support', price: 1500, type: 'annual' },
  
  // Additional modules
  'module-analytics': { name: 'Analytics Module', price: 2000, type: 'onetime' },
  'module-reporting': { name: 'Reporting Module', price: 3000, type: 'onetime' },
  'module-integration': { name: 'API Integration', price: 4000, type: 'onetime' },
  
  // User licenses
  'users-5': { name: '5 Additional Users', price: 1000, type: 'onetime' },
  'users-10': { name: '10 Additional Users', price: 1800, type: 'onetime' },
  'users-25': { name: '25 Additional Users', price: 4000, type: 'onetime' },
  
  // Services
  'setup-basic': { name: 'Basic Setup', price: 2000, type: 'service' },
  'setup-advanced': { name: 'Advanced Setup', price: 5000, type: 'service' },
  'training': { name: 'Training Package', price: 3000, type: 'service' }
};

/* ─── PRICING RULES ─── */
const pricingRules = {
  // License term multipliers
  termMultipliers: {
    'perpetual': 1.0,
    'annual': 0.4,
    'triennial': 0.85
  },
  
  // Volume discounts
  volumeDiscounts: [
    { threshold: 10000, discount: 0.05 },   // 5% off orders over $10k
    { threshold: 50000, discount: 0.10 },   // 10% off orders over $50k
    { threshold: 100000, discount: 0.15 }   // 15% off orders over $100k
  ],
  
  // Regional multipliers
  regionalMultipliers: {
    'us': 1.0,
    'eu': 1.1,
    'asia': 0.9,
    'other': 1.0
  }
};

/* ─── HELPER FUNCTIONS ─── */
function findBestVariant(product, targetQuantity) {
  const variants = productCatalog[product]?.variants || [];
  const suitable = variants.filter(v => v.quantity >= targetQuantity);
  return suitable.length > 0 ? suitable[0] : variants[variants.length - 1];
}

function calculateDiscount(basePrice) {
  for (let tier of pricingRules.volumeDiscounts.reverse()) {
    if (basePrice >= tier.threshold) {
      return tier.discount;
    }
  }
  return 0;
}

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0
  }).format(amount);
}

/* ─── EXPORT ─── */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    productCatalog,
    addonCatalog, 
    pricingRules,
    findBestVariant,
    calculateDiscount,
    formatCurrency
  };
}