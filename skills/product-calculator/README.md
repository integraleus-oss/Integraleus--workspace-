# 📊 Universal Product Calculator

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=flat&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=flat&logo=javascript&logoColor=%23F7DF1E)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=flat&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)

A **universal, customizable product pricing calculator** for any business. Built as an OpenClaw skill and based on proven Alpha Platform calculator design patterns.

![Calculator Preview](docs/images/calculator-preview.png)

## ✨ Features

- 🎯 **Universal Design** — Adapt for any product line in minutes
- ⚡ **Real-time Pricing** — Live updates as users configure options
- 📱 **Fully Responsive** — Perfect on desktop, tablet, and mobile
- 🌓 **Dark/Light Theme** — Toggle with a single click
- 🧮 **Smart Calculations** — Volume discounts, regional pricing, term multipliers
- 📧 **Lead Capture** — Built-in contact form with email integration
- 🎨 **Modern UI** — Clean, professional design that converts
- ⚙️ **Easy Customization** — Change products, pricing, and styling in minutes

## 🚀 Quick Start

### 1. Download & Install

```bash
# Clone or download the repository
git clone https://github.com/your-username/product-calculator-skill.git
cd product-calculator-skill

# Copy to your web server
cp templates/calculator.html /var/www/html/
cp -r assets/ /var/www/html/
```

### 2. Customize Your Products

Edit `assets/products.js` to define your product catalog:

```javascript
const productCatalog = {
  'your-product': {
    name: 'Your Product Name',
    variants: [
      { sku: 'STARTER', quantity: 100, price: 299 },
      { sku: 'PRO', quantity: 1000, price: 999 },
      { sku: 'ENTERPRISE', quantity: 10000, price: 4999 }
    ]
  }
};
```

### 3. Style to Match Your Brand

Update CSS variables in `assets/calculator.css`:

```css
:root {
  --primary-color: #your-brand-color;
  --secondary-color: #your-accent-color;
  /* Add your logo, fonts, and styling */
}
```

### 4. Configure Backend (Optional)

Set up email delivery in `backend/config.php`:

```php
return [
    'smtp_host' => 'your-smtp-server.com',
    'from_email' => 'quotes@yourcompany.com',
    'to_email' => 'sales@yourcompany.com'
];
```

## 📋 What's Included

```
product-calculator-skill/
├── 📄 calculator.html          # Main calculator page
├── ⚙️ assets/
│   ├── products.js            # ⭐ Product definitions (customize this)
│   ├── calculator.js          # Core functionality
│   └── calculator.css         # Styling and themes
├── 🔧 backend/
│   ├── send_quote.php         # Email handler
│   └── config.php             # SMTP configuration
└── 📚 docs/
    ├── customization.md       # Detailed setup guide
    └── deployment.md          # Hosting instructions
```

## 🎯 Use Cases

Perfect for businesses selling:

- 💻 **Software & SaaS** — Different tiers, user limits, features
- 🛠️ **Professional Services** — Consulting, design, development
- 📦 **Physical Products** — Volume pricing, configurations
- 🎓 **Training & Education** — Courses, certifications, workshops
- 🏢 **B2B Solutions** — Enterprise software, hardware, services

## 🖼️ Screenshots

| Desktop View | Mobile View | Dark Theme |
|:------------:|:-----------:|:----------:|
| ![Desktop](docs/images/desktop-view.png) | ![Mobile](docs/images/mobile-view.png) | ![Dark](docs/images/dark-theme.png) |

## 🔧 Customization Examples

### Software Company
```javascript
// Perfect for SaaS pricing
const productCatalog = {
  'starter-plan': {
    name: 'Starter Plan',
    variants: [
      { sku: 'START-10', quantity: 10, price: 29 },
      { sku: 'START-50', quantity: 50, price: 99 }
    ]
  }
};
```

### Consulting Firm
```javascript
// Ideal for service-based pricing
const productCatalog = {
  'consulting-package': {
    name: 'Strategy Consulting',
    variants: [
      { sku: 'CONS-BASIC', quantity: 20, price: 5000 },
      { sku: 'CONS-PREMIUM', quantity: 80, price: 15000 }
    ]
  }
};
```

## 🌐 Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+  
- ✅ Safari 14+
- ✅ Mobile browsers with ES6 support

## 📈 Performance

- 🚀 **Lightweight** — Under 50KB total
- ⚡ **Fast Loading** — Optimized assets and minimal dependencies
- 📱 **Mobile First** — Smooth performance on all devices
- 🎯 **SEO Ready** — Clean HTML structure and meta tags

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- 📚 **Documentation**: [Customization Guide](docs/customization.md)
- 🐛 **Report Issues**: [GitHub Issues](../../issues)
- 💬 **Discussions**: [GitHub Discussions](../../discussions)
- 🌟 **OpenClaw**: [Official Website](https://openclaw.ai)

## ⭐ Show Your Support

Give a ⭐️ if this project helped you build better pricing calculators!

---

Built with ❤️ for the OpenClaw community