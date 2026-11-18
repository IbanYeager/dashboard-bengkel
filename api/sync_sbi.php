<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');

set_time_limit(180);

$pythonBin = 'python';
$candidates = [
    'C:\\Users\\HP\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe',
    'C:\\Python310\\python.exe',
    'C:\\Python311\\python.exe',
    'C:\\Python312\\python.exe'
];
foreach ($candidates as $cand) {
    if (file_exists($cand)) {
        $pythonBin = escapeshellarg($cand);
        break;
    }
}

$scriptPath = realpath(__DIR__ . '/../scripts/sync_sbi_data.py');
if (!$scriptPath || !file_exists($scriptPath)) {
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Script sync SBI tidak ditemukan']);
    exit;
}

$cmd = $pythonBin . " " . escapeshellarg($scriptPath) . " --force 2>&1";
exec($cmd, $output, $returnCode);

if ($returnCode === 0) {
    $dataPath = realpath(__DIR__ . '/../data/sbi_data.json');
    $meta = [];
    if ($dataPath && file_exists($dataPath)) {
        $json = json_decode(file_get_contents($dataPath), true);
        $meta = $json['meta'] ?? [];
    }
    echo json_encode([
        'status' => 'success',
        'message' => 'Sinkronisasi data SBI dari Google Spreadsheet berhasil!',
        'meta' => $meta,
        'log' => implode("\n", array_slice($output, -10))
    ]);
} else {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => 'Gagal menyinkronkan data SBI.',
        'log' => implode("\n", $output)
    ]);
}
