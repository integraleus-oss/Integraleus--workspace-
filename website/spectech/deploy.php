<?php
/**
 * deploy.php — secure file deployment endpoint
 * Protection: error suppression, key validation, file type whitelist, path sanitization
 */
error_reporting(0);
ini_set('display_errors', 0);

// --- Auth ---
$KEY = 'spt2026deploy';

if (!isset($_GET['key']) || $_GET['key'] !== $KEY) {
    http_response_code(403);
    echo 'no';
    exit;
}

// --- Only POST ---
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo 'no';
    exit;
}

// --- File parameter ---
$file = $_GET['file'] ?? 'index.html';

// Sanitize: no null bytes, no .., no absolute paths, no backslashes
$file = str_replace(["\0", "\\"], '', $file);
if (strpos($file, '..') !== false || $file[0] === '/') {
    http_response_code(400);
    echo 'no';
    exit;
}

// Whitelist extensions
$ext = strtolower(pathinfo($file, PATHINFO_EXTENSION));
$allowed = ['html', 'css', 'js', 'txt', 'json', 'svg', 'png', 'jpg', 'jpeg', 'gif', 'ico', 'webp', 'woff', 'woff2'];
if (!in_array($ext, $allowed)) {
    http_response_code(403);
    echo 'no';
    exit;
}

// --- Read body ---
$data = file_get_contents('php://input');
if (!$data || strlen($data) < 10) {
    http_response_code(400);
    echo 'no';
    exit;
}

// Prevent PHP code injection in any file
if (preg_match('/<\?php|<\?=/i', $data)) {
    http_response_code(403);
    echo 'no';
    exit;
}

// --- Write file ---
$target = __DIR__ . '/' . $file;
$dir = dirname($target);
if (!is_dir($dir)) {
    mkdir($dir, 0755, true);
}

$bytes = file_put_contents($target, $data);
if ($bytes === false) {
    http_response_code(500);
    echo 'error';
    exit;
}

// Log deployment
$logFile = __DIR__ . '/.deploy_log';
$logLine = date('Y-m-d H:i:s') . ' | ' . ($_SERVER['REMOTE_ADDR'] ?? '?') . ' | ' . $file . ' | ' . $bytes . " bytes\n";
@file_put_contents($logFile, $logLine, FILE_APPEND | LOCK_EX);

echo 'OK:' . $bytes . ':' . $file;
