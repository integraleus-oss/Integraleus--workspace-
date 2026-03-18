# Customization Guide

How to adapt the Product Calculator for your specific needs.

## 1. Product Configuration

### Basic Product Setup

Edit `assets/products.js` to define your products:

```javascript
const productCatalog = {
  'my-software': {
    name: 'My Software',
    variants: [
      { sku: 'SW-STARTER', quantity: 10, price: 299 },
      { sku: 'SW-PRO', quantity: 100, price: 999 },
      { sku: 'SW-ENTERPRISE', quantity: 1000, price: 4999 }
    ]
  },
  'my-service': {
    name: 'Consulting Service',
    variants: [
      { sku: 'CONS-BASIC', quantity: 10, price: 2000 },
      { sku: 'CONS-PREMIUM', quantity: 40, price: 6000 }
    ]
  }
};
```

### Add-ons Configuration

```javascript
const addonCatalog = {
  'training': { 
    name: 'Training Package', 
    price: 1500, 
    type: 'service' 
  },
  'support': { 
    name: 'Annual Support', 
    price: 500, 
    type: 'annual' 
  }
};
```

### Pricing Rules

```javascript
const pricingRules = {
  termMultipliers: {
    'perpetual': 1.0,    // Full price for perpetual
    'annual': 0.35,      // 35% of perpetual for annual
    'monthly': 0.08      // 8% of perpetual for monthly
  },
  
  volumeDiscounts: [
    { threshold: 5000, discount: 0.05 },   // 5% off $5k+
    { threshold: 25000, discount: 0.10 }   // 10% off $25k+
  ]
};
```

## 2. UI Customization

### Update Product Cards

Edit the HTML in `templates/calculator.html`:

```html
<div class="product-option">
  <input type="radio" name="product" id="my-product" value="my-product">
  <label for="my-product" class="product-card">
    <div class="product-header">
      <h3>My Product Name</h3>
      <p class="product-description">Description of your product</p>
    </div>
    <div class="product-features">
      <ul>
        <li>Feature 1</li>
        <li>Feature 2</li>
        <li>Feature 3</li>
      </ul>
    </div>
    <div class="product-pricing">
      Starting at <strong>$299</strong>
    </div>
  </label>
</div>
```

### Customize Styling

Update CSS variables in `assets/calculator.css`:

```css
:root {
  --primary-color: #your-brand-color;
  --secondary-color: #your-secondary-color;
  --background: #your-background;
  --text-color: #your-text-color;
  --border-color: #your-border-color;
}
```

### Add Your Branding

```css
.nav-brand h1::before {
  content: '';
  background: url('your-logo.png') no-repeat;
  width: 32px;
  height: 32px;
  display: inline-block;
  margin-right: 10px;
}
```

## 3. Functionality Changes

### Custom Quantity Logic

Modify the quantity slider behavior in `assets/calculator.js`:

```javascript
function updateQuantityDisplay() {
  const slider = document.getElementById('quantity');
  const value = parseInt(slider.value);
  
  // Your custom quantity mapping
  const quantities = [10, 50, 100, 500, 1000, 5000, 10000];
  const actualQuantity = quantities[value];
  
  document.querySelector('.quantity-display').textContent = 
    `${actualQuantity.toLocaleString()} units`;
}
```

### Custom Calculations

Add special pricing logic:

```javascript
function calculatePrice() {
  let basePrice = getBasePriceForProduct();
  
  // Your custom business logic
  if (isEarlyBird()) {
    basePrice *= 0.8; // 20% early bird discount
  }
  
  if (hasReferral()) {
    basePrice *= 0.9; // 10% referral discount
  }
  
  return basePrice;
}
```

## 4. Backend Integration

### Email Configuration

Edit `backend/config.php`:

```php
<?php
return [
    'smtp_host' => 'your-smtp-server.com',
    'smtp_port' => 587,
    'smtp_username' => 'your-email@company.com',
    'smtp_password' => 'your-password',
    'from_email' => 'quotes@company.com',
    'from_name' => 'Your Company Name',
    'to_email' => 'sales@company.com'
];
?>
```

### CRM Integration

Add to `backend/send_quote.php`:

```php
// Send to CRM
$crm_data = [
    'name' => $_POST['name'],
    'email' => $_POST['email'],
    'product' => $_POST['product'],
    'total' => $_POST['total']
];

// Example: HubSpot integration
$hubspot = new HubSpot\Client($api_key);
$hubspot->contacts()->create($crm_data);
```

## 5. Advanced Features

### Multi-Language Support

Add language switching:

```javascript
const translations = {
  en: {
    'calculator.title': 'Product Calculator',
    'product.basic': 'Basic Package'
  },
  es: {
    'calculator.title': 'Calculadora de Productos',
    'product.basic': 'Paquete Básico'
  }
};
```

### Regional Pricing

```javascript
function getRegionalPrice(basePrice, region) {
  const multipliers = {
    'US': 1.0,
    'EU': 1.2,    // Include VAT
    'ASIA': 0.8   // Lower pricing for developing markets
  };
  
  return basePrice * (multipliers[region] || 1.0);
}
```

### A/B Testing

```javascript
function getVariant() {
  return Math.random() < 0.5 ? 'variant-a' : 'variant-b';
}

if (getVariant() === 'variant-b') {
  // Show different pricing or UI
  document.body.classList.add('variant-b');
}
```

## 6. Analytics Integration

### Google Analytics

```html
<!-- Add to calculator.html -->
<script>
gtag('event', 'calculator_interaction', {
  'product': selectedProduct,
  'quantity': selectedQuantity,
  'total_value': calculatedPrice
});
</script>
```

### Custom Tracking

```javascript
function trackCalculatorEvent(action, product, value) {
  fetch('/api/analytics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: action,
      product: product,
      value: value,
      timestamp: Date.now()
    })
  });
}
```

## Testing

1. **Test all product combinations**
2. **Verify pricing calculations**
3. **Test on mobile devices**
4. **Check email delivery**
5. **Validate form submissions**
6. **Test theme switching**

## Performance Tips

- Minimize recalculations
- Debounce slider updates
- Optimize images and assets
- Use CSS for animations
- Cache pricing data if complex