# Product Calculator Skill

A universal, customizable product pricing calculator based on the proven Alpha Platform calculator design.

## Quick Start

1. **Copy the skill** to your OpenClaw workspace:
   ```bash
   cp -r skills/product-calculator/ /path/to/your/openclaw/skills/
   ```

2. **Customize your products** in `assets/products.js`:
   - Edit `productCatalog` with your products and pricing
   - Modify `addonCatalog` for additional services
   - Adjust `pricingRules` for discounts and terms

3. **Deploy to web server**:
   ```bash
   cp templates/calculator.html /var/www/html/
   cp -r assets/ /var/www/html/
   ```

4. **Configure backend** (optional):
   - Set up `backend/send_quote.php` for email functionality
   - Update `backend/config.php` with your SMTP settings

## File Structure

```
skills/product-calculator/
├── SKILL.md              # Skill documentation
├── templates/
│   ├── calculator.html   # Main calculator page
│   ├── wizard.html       # Multi-step wizard (planned)
│   └── embed.html        # Embeddable widget (planned)
├── assets/
│   ├── products.js       # ⭐ CUSTOMIZE THIS - Your product definitions
│   ├── calculator.js     # Core calculator functionality
│   └── calculator.css    # Styling (customize colors/branding)
├── backend/
│   ├── send_quote.php    # Email handler
│   └── config.php        # Backend configuration
└── docs/
    ├── README.md         # This file
    ├── customization.md  # Detailed customization guide
    └── deployment.md     # Hosting and integration
```

## Key Features

- ✅ **Real-time pricing** updates as user changes options
- ✅ **Responsive design** works on desktop and mobile
- ✅ **Theme support** with light/dark mode toggle
- ✅ **Product variants** with quantity-based SKU selection
- ✅ **Add-on system** for additional services and modules
- ✅ **Contact integration** for lead capture
- ✅ **Volume discounts** and regional pricing support
- ✅ **Clean, modern UI** based on proven design patterns

## Customization

### Products (`assets/products.js`)
```javascript
const productCatalog = {
  'your-product': {
    name: 'Your Product Name',
    variants: [
      { sku: 'SKU-1', quantity: 100, price: 1000 },
      { sku: 'SKU-2', quantity: 500, price: 4000 }
    ]
  }
};
```

### Styling (`assets/calculator.css`)
- Update CSS custom properties for colors and branding
- Modify component styles to match your design system
- Add your logo and brand elements

### Backend (`backend/`)
- Configure SMTP settings in `config.php`
- Customize email templates in `send_quote.php`
- Add CRM integration if needed

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers with ES6 support

## License

Open source - adapt freely for commercial and non-commercial use.

See `docs/customization.md` for detailed setup instructions.