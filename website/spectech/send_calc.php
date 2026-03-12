<?php
/**
 * send_calc.php — secure form handler for specialtechnology.ru calculator
 * Protection: rate-limit (IP), honeypot, referer check, timestamp check, input sanitization
 */

// --- Config ---
error_reporting(0);
ini_set('display_errors', 0);
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

$MAIL_TO   = 'sales@special-tech.ru';
$MAIL_CC   = 'info@special-tech.ru';
$MAIL_FROM = 'noreply@specialtechnology.ru';
$RATE_DIR  = __DIR__ . '/.rate_limit';
$RATE_MAX  = 3;       // max requests per window
$RATE_WINDOW = 300;   // 5 minutes in seconds
$MIN_TIME  = 3;       // minimum seconds between page load and submit

// --- Only POST ---
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Method not allowed']);
    exit;
}

// --- Referer check ---
$referer = $_SERVER['HTTP_REFERER'] ?? '';
if (!$referer || !preg_match('#^https?://(www\.)?specialtechnology\.ru/#i', $referer)) {
    http_response_code(403);
    echo json_encode(['ok' => false, 'error' => 'Invalid origin']);
    exit;
}

// --- Honeypot check (hidden field "website" must be empty) ---
if (!empty($_POST['website'])) {
    // Bot filled the honeypot — pretend success
    echo json_encode(['ok' => true, 'tid' => $_POST['tid'] ?? '']);
    exit;
}

// --- Timestamp check (form must be open at least MIN_TIME seconds) ---
$formTs = intval($_POST['_ts'] ?? 0);
if ($formTs > 0 && (time() - $formTs) < $MIN_TIME) {
    // Too fast — likely bot, pretend success
    echo json_encode(['ok' => true, 'tid' => $_POST['tid'] ?? '']);
    exit;
}

// --- Rate limiting by IP ---
$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
$ipHash = md5($ip);

if (!is_dir($RATE_DIR)) {
    @mkdir($RATE_DIR, 0700, true);
    // Protect directory with .htaccess
    @file_put_contents($RATE_DIR . '/.htaccess', "Deny from all\n");
}

$rateFile = $RATE_DIR . '/' . $ipHash;
$now = time();
$attempts = [];

if (file_exists($rateFile)) {
    $raw = @file_get_contents($rateFile);
    $attempts = $raw ? json_decode($raw, true) : [];
    if (!is_array($attempts)) $attempts = [];
    // Keep only attempts within window
    $attempts = array_filter($attempts, function($t) use ($now, $RATE_WINDOW) {
        return ($now - $t) < $RATE_WINDOW;
    });
}

if (count($attempts) >= $RATE_MAX) {
    http_response_code(429);
    echo json_encode(['ok' => false, 'error' => 'Слишком много запросов. Попробуйте через 5 минут.']);
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

$tid      = clean($_POST['tid'] ?? '', 20);
$product  = clean($_POST['product'] ?? '', 100);
$name     = clean($_POST['name'] ?? '', 200);
$email    = clean($_POST['email'] ?? '', 200);
$phone    = clean($_POST['phone'] ?? '', 50);
$comment  = clean($_POST['comment'] ?? '', 2000);
$sku      = clean($_POST['sku'] ?? '', 100);
$tags     = clean($_POST['tags'] ?? '', 50);
$term     = clean($_POST['term'] ?? '', 50);
$reserve  = clean($_POST['reserve'] ?? '', 10);
$historian = clean($_POST['historian'] ?? '', 200);
$reports  = clean($_POST['reports'] ?? '', 200);
$addons   = clean($_POST['addons'] ?? '', 2000);

// --- Validate email ---
$rawEmail = trim($_POST['email'] ?? '');
if (!$rawEmail || !filter_var($rawEmail, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(['ok' => false, 'error' => 'Некорректный email']);
    exit;
}

// --- Validate required fields ---
if (!$name || !$product) {
    echo json_encode(['ok' => false, 'error' => 'Заполните обязательные поля']);
    exit;
}

// --- Build email ---
$subject = "КП $tid — $product";
$body = "Заявка на коммерческое предложение\n";
$body .= "========================================\n\n";
$body .= "Тикет:    $tid\n";
$body .= "Продукт:  $product\n";
$body .= "Артикул:  $sku\n";
$body .= "Теги:     $tags\n";
$body .= "Лицензия: $term\n";

if ($reserve)   $body .= "Резерв:   Да\n";
if ($historian)  $body .= "Historian: $historian\n";
if ($reports)    $body .= "Reports:  $reports\n";

if ($addons) {
    $body .= "\nДополнения:\n$addons\n";
}

$body .= "\n----------------------------------------\n";
$body .= "Контакт:\n";
$body .= "  Имя:    $name\n";
$body .= "  Email:  $email\n";
if ($phone) $body .= "  Тел:    $phone\n";
if ($comment) $body .= "\nКомментарий:\n$comment\n";

$body .= "\n----------------------------------------\n";
$body .= "IP: $ip\n";
$body .= "Дата: " . date('Y-m-d H:i:s') . " MSK\n";

// --- Send mail ---
$headers  = "From: $MAIL_FROM\r\n";
$headers .= "Cc: $MAIL_CC\r\n";
$headers .= "Reply-To: $rawEmail\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "X-Mailer: SpecTech-Calc/2.0\r\n";

$sent = @mail($MAIL_TO, "=?UTF-8?B?" . base64_encode($subject) . "?=", $body, $headers);

// --- Log (append, not world-readable) ---
$logFile = __DIR__ . '/.calc_log';
$logLine = date('Y-m-d H:i:s') . " | $ip | $tid | $product | $name | $rawEmail | " . ($sent ? 'OK' : 'FAIL') . "\n";
@file_put_contents($logFile, $logLine, FILE_APPEND | LOCK_EX);

echo json_encode(['ok' => $sent, 'tid' => $tid]);
