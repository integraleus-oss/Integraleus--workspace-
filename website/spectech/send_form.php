<?php
/**
 * send_form.php — secure form handler for specialtechnology.ru contact form
 * Protection: rate-limit (IP), honeypot, referer check, input sanitization
 */

// --- Config ---
error_reporting(0);
ini_set('display_errors', 0);

$MAIL_TO   = 'sales@special-tech.ru';
$MAIL_CC   = 'info@special-tech.ru';
$MAIL_FROM = 'noreply@specialtechnology.ru';
$RATE_DIR  = __DIR__ . '/.rate_limit';
$RATE_MAX  = 3;
$RATE_WINDOW = 300;

// --- Only POST ---
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /');
    exit;
}

// --- Referer check ---
$referer = $_SERVER['HTTP_REFERER'] ?? '';
if (!$referer || !preg_match('#^https?://(www\.)?specialtechnology\.ru/#i', $referer)) {
    header('Location: /');
    exit;
}

// --- Honeypot check ---
if (!empty($_POST['website'])) {
    header('Location: /?sent=ok');
    exit;
}

// --- Rate limiting by IP ---
$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
$ipHash = md5($ip);

if (!is_dir($RATE_DIR)) {
    @mkdir($RATE_DIR, 0700, true);
    @file_put_contents($RATE_DIR . '/.htaccess', "Deny from all\n");
}

$rateFile = $RATE_DIR . '/' . $ipHash;
$now = time();
$attempts = [];

if (file_exists($rateFile)) {
    $raw = @file_get_contents($rateFile);
    $attempts = $raw ? json_decode($raw, true) : [];
    if (!is_array($attempts)) $attempts = [];
    $attempts = array_filter($attempts, function($t) use ($now, $RATE_WINDOW) {
        return ($now - $t) < $RATE_WINDOW;
    });
}

if (count($attempts) >= $RATE_MAX) {
    header('Location: /?error=rate');
    exit;
}

$attempts[] = $now;
@file_put_contents($rateFile, json_encode(array_values($attempts)));

// --- Cleanup old rate files (1 in 20 chance) ---
if (mt_rand(1, 20) === 1) {
    $files = @glob($RATE_DIR . '/*');
    if ($files) {
        foreach ($files as $f) {
            if (basename($f)[0] === '.') continue;
            if ($now - filemtime($f) > $RATE_WINDOW * 2) @unlink($f);
        }
    }
}

// --- Sanitize inputs ---
function clean($val, $maxLen = 500) {
    $val = trim($val ?? '');
    $val = mb_substr($val, 0, $maxLen, 'UTF-8');
    $val = htmlspecialchars($val, ENT_QUOTES, 'UTF-8');
    return $val;
}

$name     = clean($_POST['name'] ?? '', 200);
$company  = clean($_POST['company'] ?? '', 200);
$email    = clean($_POST['email'] ?? '', 200);
$phone    = clean($_POST['phone'] ?? '', 50);
$industry = clean($_POST['industry'] ?? '', 100);
$scale    = clean($_POST['scale'] ?? '', 100);
$message  = clean($_POST['message'] ?? '', 3000);

// --- Validate ---
$rawEmail = trim($_POST['email'] ?? '');
if (!$name || !$rawEmail || !filter_var($rawEmail, FILTER_VALIDATE_EMAIL)) {
    header('Location: /#contact');
    exit;
}

// --- Build email ---
$subject = "Заявка с сайта — $name ($company)";

$body = "Новая заявка с сайта specialtechnology.ru\n";
$body .= "========================================\n\n";
$body .= "Имя:      $name\n";
$body .= "Компания: $company\n";
$body .= "Email:    $email\n";
if ($phone) $body .= "Телефон:  $phone\n";
if ($industry) $body .= "Отрасль:  $industry\n";
if ($scale) $body .= "Масштаб:  $scale\n";
if ($message) $body .= "\nСообщение:\n$message\n";

$body .= "\n----------------------------------------\n";
$body .= "IP: $ip\n";
$body .= "Дата: " . date('Y-m-d H:i:s') . " MSK\n";
$body .= "Referer: $referer\n";

// --- Send ---
$headers  = "From: $MAIL_FROM\r\n";
$headers .= "Cc: $MAIL_CC\r\n";
$headers .= "Reply-To: $rawEmail\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "X-Mailer: SpecTech-Form/1.0\r\n";

$sent = @mail($MAIL_TO, "=?UTF-8?B?" . base64_encode($subject) . "?=", $body, $headers);

// --- Log ---
$logFile = __DIR__ . '/.form_log';
$logLine = date('Y-m-d H:i:s') . " | $ip | $name | $company | $rawEmail | " . ($sent ? 'OK' : 'FAIL') . "\n";
@file_put_contents($logFile, $logLine, FILE_APPEND | LOCK_EX);

// --- Redirect back ---
header('Location: /#contact');
exit;
