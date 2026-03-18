# Deployment Guide

How to deploy the Universal Product Calculator to various hosting platforms.

## 🚀 Quick Deployment Options

### 1. Static Hosting (Simplest)

Perfect for GitHub Pages, Netlify, Vercel:

```bash
# Just deploy the files as-is
./templates/calculator.html    # Main page
./assets/                      # CSS, JS, and config
```

⚠️ **Note**: Email functionality requires server-side processing (PHP/Node.js)

### 2. Shared Hosting (PHP)

For cPanel, shared hosting with PHP support:

```bash
# Upload to your web root
calculator.html                # Main page
assets/calculator.css         # Styles
assets/calculator.js          # Functionality  
assets/products.js            # Your product config
backend/send_quote.php        # Email handler
backend/config.php            # SMTP settings
```

### 3. VPS/Dedicated Server

Full control with Apache/Nginx + PHP:

```bash
# Apache setup
cp templates/calculator.html /var/www/html/
cp -r assets/ /var/www/html/
cp -r backend/ /var/www/html/

# Nginx + PHP-FPM
cp templates/calculator.html /usr/share/nginx/html/
cp -r assets/ /usr/share/nginx/html/
cp -r backend/ /usr/share/nginx/html/
```

## 📋 Platform-Specific Instructions

### GitHub Pages

1. **Create repository** on GitHub
2. **Upload files** to main branch
3. **Enable Pages** in repository settings
4. **Set source** to main branch
5. **Access** via `https://username.github.io/repository-name`

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/deploy-pages@v1
        with:
          artifact_name: github-pages
```

⚠️ **Limitation**: No email functionality (static hosting)

### Netlify

1. **Connect repository** to Netlify
2. **Set build settings**:
   - Build command: (leave empty)
   - Publish directory: `/`
3. **Deploy automatically** on push

**With Netlify Functions** (for email):

```javascript
// netlify/functions/send-quote.js
exports.handler = async (event, context) => {
  // Handle form submission
  const { name, email, product } = JSON.parse(event.body);
  
  // Send email via SendGrid/Mailgun
  await sendEmail(name, email, product);
  
  return {
    statusCode: 200,
    body: JSON.stringify({ success: true })
  };
};
```

### Vercel

```json
// vercel.json
{
  "functions": {
    "api/send-quote.js": {
      "runtime": "nodejs18.x"
    }
  }
}
```

```javascript
// api/send-quote.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const { name, email, product } = req.body;
  
  // Process form submission
  await sendEmail(name, email, product);
  
  res.status(200).json({ success: true });
}
```

### AWS S3 + CloudFront

**Static hosting** (no email):

```bash
# Upload to S3 bucket
aws s3 sync . s3://your-bucket-name --exclude "backend/*"

# Create CloudFront distribution
aws cloudfront create-distribution --distribution-config file://distribution.json
```

**With Lambda** (for email):

```javascript
// lambda/send-quote.js
exports.handler = async (event) => {
  const { name, email, product } = JSON.parse(event.body);
  
  // Use AWS SES for email
  const ses = new AWS.SES();
  await ses.sendEmail(params).promise();
  
  return {
    statusCode: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ success: true })
  };
};
```

### Traditional Web Hosting

**cPanel/Shared Hosting**:

1. **Upload files** via File Manager or FTP
2. **Configure email** in `backend/config.php`
3. **Test form submission**

**Apache .htaccess** (optional):

```apache
# .htaccess
RewriteEngine On

# Clean URLs
RewriteRule ^calculator/?$ calculator.html [L]

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
```

## 🔧 Configuration

### Environment Variables

For different environments:

```javascript
// assets/config.js (create this)
const CONFIG = {
  API_ENDPOINT: process.env.NODE_ENV === 'production' 
    ? '/backend/send_quote.php'
    : '/api/send-quote',
  
  ANALYTICS_ID: process.env.GOOGLE_ANALYTICS_ID || '',
  
  CONTACT_EMAIL: 'sales@yourcompany.com'
};
```

### Email Configuration

**PHP (traditional hosting)**:

```php
// backend/config.php
<?php
return [
    'smtp_host' => $_ENV['SMTP_HOST'] ?? 'localhost',
    'smtp_port' => $_ENV['SMTP_PORT'] ?? 587,
    'smtp_username' => $_ENV['SMTP_USERNAME'] ?? '',
    'smtp_password' => $_ENV['SMTP_PASSWORD'] ?? '',
    'from_email' => $_ENV['FROM_EMAIL'] ?? 'noreply@yoursite.com',
    'to_email' => $_ENV['TO_EMAIL'] ?? 'sales@yoursite.com'
];
?>
```

**Node.js (Vercel/Netlify)**:

```javascript
// Use environment variables
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransporter({
  host: process.env.SMTP_HOST,
  port: process.env.SMTP_PORT,
  auth: {
    user: process.env.SMTP_USERNAME,
    pass: process.env.SMTP_PASSWORD
  }
});
```

## 🔒 Security Considerations

### Production Checklist

- [ ] **Remove debug code** from JavaScript
- [ ] **Set up HTTPS** (SSL certificate)
- [ ] **Configure CORS** properly for API endpoints
- [ ] **Validate all inputs** on backend
- [ ] **Rate limit** form submissions
- [ ] **Sanitize user data** before processing
- [ ] **Hide error details** in production
- [ ] **Use environment variables** for sensitive config

### Content Security Policy

```html
<!-- Add to calculator.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               style-src 'self' 'unsafe-inline'; 
               script-src 'self';
               img-src 'self' data:;">
```

## 📊 Analytics & Monitoring

### Google Analytics

```html
<!-- Add to calculator.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Custom Events

```javascript
// Track calculator interactions
function trackCalculatorEvent(action, product, value) {
  gtag('event', action, {
    'custom_parameter': product,
    'value': value
  });
}

// Usage
trackCalculatorEvent('product_selected', 'basic-plan', 299);
trackCalculatorEvent('quote_requested', 'pro-plan', 999);
```

## 🚀 Performance Optimization

### File Optimization

```bash
# Minify CSS
npx clean-css-cli assets/calculator.css -o assets/calculator.min.css

# Minify JavaScript  
npx terser assets/calculator.js -o assets/calculator.min.js

# Optimize images
npx imagemin assets/images/* --out-dir=assets/images-optimized
```

### CDN Setup

```html
<!-- Use CDN for common libraries -->
<link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" as="style">
```

## 🧪 Testing in Production

### Smoke Tests

```bash
# Test main functionality
curl -f https://yourdomain.com/calculator.html
curl -f https://yourdomain.com/assets/calculator.js
curl -f https://yourdomain.com/assets/calculator.css

# Test form submission
curl -X POST https://yourdomain.com/backend/send_quote.php \
  -d "name=Test&email=test@test.com&product=basic"
```

### Load Testing

```bash
# Simple load test with Apache Bench
ab -n 100 -c 10 https://yourdomain.com/calculator.html
```

## 📞 Troubleshooting

**Common Issues**:

1. **CSS/JS not loading** → Check file paths
2. **Email not sending** → Verify SMTP configuration  
3. **CORS errors** → Configure server headers
4. **Mobile layout broken** → Test responsive design
5. **Form submission fails** → Check backend logs

---

Choose the deployment method that best fits your infrastructure and requirements. Static hosting is simplest but lacks email functionality, while VPS deployment gives you full control.