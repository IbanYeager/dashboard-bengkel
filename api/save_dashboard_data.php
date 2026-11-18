<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['status' => 'error', 'message' => 'Metode request tidak diizinkan. Gunakan POST.']);
    exit;
}

$input = file_get_contents('php://input');
if (!$input) {
    echo json_encode(['status' => 'error', 'message' => 'Payload JSON kosong.']);
    exit;
}

$decoded = json_decode($input, true);
if (!$decoded) {
    echo json_encode(['status' => 'error', 'message' => 'Payload bukan format JSON yang valid.']);
    exit;
}

$dataPath = realpath(__DIR__ . '/..') . '/data/dashboard_data.json';
$backupPath = realpath(__DIR__ . '/..') . '/data/dashboard_data.backup.json';

if (file_exists($dataPath)) {
    @copy($dataPath, $backupPath);
}

if (file_put_contents($dataPath, json_encode($decoded, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE))) {
    echo json_encode([
        'status' => 'success',
        'message' => 'Berkas data/dashboard_data.json berhasil disimpan dan disinkronkan di server lokal.'
    ]);
} else {
    echo json_encode([
        'status' => 'error',
        'message' => 'Gagal menulis ke berkas data/dashboard_data.json. Periksa izin akses folder.'
    ]);
}
