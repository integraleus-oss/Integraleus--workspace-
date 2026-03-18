# Product Calculator Skill

Universal product pricing calculator with customizable products, variants, and add-ons. Based on the proven Alpha Platform calculator design but made generic for any product line.

## Features

- **Multi-product support** — Different product categories with variants
- **Flexible pricing** — SKU-based pricing with term multipliers
- **Add-on system** — Additional modules, clients, services
- **Responsive design** — Works on desktop and mobile
- **Email integration** — Send quotes via PHP backend
- **Theme support** — Light/dark mode toggle

## Structure

### Calculator Components
- **Product selector** — Radio buttons with product details
- **Parameter controls** — Sliders, dropdowns, checkboxes
- **Real-time pricing** — Live updates as user changes options
- **Result panel** — Summary with total price and details
- **Contact form** — Lead capture integration

### Wizard Mode
- **Multi-step form** — Category → Details → Contacts → Summary
- **Progress tracking** — Visual step indicator
- **Data validation** — Required fields and format checking
- **Success handling** — Confirmation and ticket generation

## Usage

The skill provides a complete calculator template that can be customized for any product line by:

1. **Editing product definitions** in JavaScript
2. **Updating pricing tables** with your SKUs
3. **Customizing design** via CSS variables
4. **Configuring email backend** for quote delivery

## Files Structure

```
skills/product-calculator/
├── SKILL.md              # This documentation
├── templates/
│   ├── calculator.html   # Main calculator page
│   ├── wizard.html       # Multi-step wizard version
│   └── embed.html        # Embeddable widget version
├── assets/
│   ├── calculator.css    # Styling
│   ├── calculator.js     # Core functionality
│   └── products.js       # Product definitions (customize this)
├── backend/
│   ├── send_quote.php    # Email handler
│   └── config.php        # Backend configuration
└── docs/
    ├── README.md         # Setup instructions
    ├── customization.md  # How to adapt for your products
    └── deployment.md     # Hosting and integration guide
```

## Customization

See `docs/customization.md` for detailed instructions on adapting the calculator for your specific products and pricing structure.

## Requirements

- Modern web browser (ES6+ support)
- PHP 7.4+ (for email functionality)
- Web server (Apache/Nginx)

## License

Open source - adapt and use freely for commercial and non-commercial purposes.