<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
if (!$input || !isset($input['message'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing message']);
    exit;
}

// Rate limiting (simple file-based)
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$rateFile = sys_get_temp_dir() . '/chat_rate_' . md5($ip);
$now = time();
if (file_exists($rateFile)) {
    $data = json_decode(file_get_contents($rateFile), true);
    if ($data && $data['count'] >= 20 && ($now - $data['start']) < 3600) {
        http_response_code(429);
        echo json_encode(['error' => 'Too many requests. Try again later.']);
        exit;
    }
    if (($now - $data['start']) >= 3600) {
        $data = ['start' => $now, 'count' => 1];
    } else {
        $data['count']++;
    }
} else {
    $data = ['start' => $now, 'count' => 1];
}
file_put_contents($rateFile, json_encode($data));

$apiKey = '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';

$systemPrompt = "Ты — ИИ-ассистент компании Integraleus. Integraleus создаёт интеллектуальных ИИ-агентов для промышленности и бизнеса.

Основные услуги:
- Промышленная автоматизация (SCADA, OPC UA, мониторинг оборудования)
- Бизнес-аналитика и автоматизация отчётов
- Чат-боты и ассистенты для техподдержки, HR, продаж
- Мониторинг серверов и инфраструктуры 24/7
- Работа с документами (ТЗ, договоры, регламенты)
- Кастомная разработка ИИ-решений

Технологии: Claude, GPT, Python, Docker, OPC UA, MQTT, PostgreSQL, Grafana, OpenClaw.

Контакты:
- Email: mail@integraleus.ru
- Telegram: @Integraleus

Правила:
- Отвечай кратко и по делу (2-4 предложения)
- Будь дружелюбным и профессиональным
- Отвечай на русском языке
- Если вопрос не по теме — вежливо перенаправь к услугам компании
- Не выдумывай цены — говори что стоимость зависит от задачи и предложи связаться
- Если спрашивают сроки — от 1 до 4 недель в зависимости от сложности";

$messages = [
    ['role' => 'system', 'content' => $systemPrompt]
];

// Support conversation history
if (isset($input['history']) && is_array($input['history'])) {
    foreach (array_slice($input['history'], -10) as $msg) {
        if (isset($msg['role']) && isset($msg['content'])) {
            $messages[] = [
                'role' => $msg['role'] === 'user' ? 'user' : 'assistant',
                'content' => substr($msg['content'], 0, 500)
            ];
        }
    }
}

$messages[] = ['role' => 'user', 'content' => substr($input['message'], 0, 500)];

$payload = json_encode([
    'model' => 'gpt-4o-mini',
    'messages' => $messages,
    'max_tokens' => 300,
    'temperature' => 0.7
]);

$ch = curl_init('https://api.openai.com/v1/chat/completions');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $payload,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'Authorization: Bearer ' . $apiKey
    ],
    CURLOPT_TIMEOUT => 30,
    CURLOPT_CONNECTTIMEOUT => 10
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    http_response_code(502);
    echo json_encode(['error' => 'API connection failed']);
    exit;
}

if ($httpCode !== 200) {
    http_response_code(502);
    echo json_encode(['error' => 'API error', 'status' => $httpCode]);
    exit;
}

$data = json_decode($response, true);
$reply = $data['choices'][0]['message']['content'] ?? 'Извините, не удалось получить ответ. Напишите нам на mail@integraleus.ru';

echo json_encode(['reply' => $reply]);
