<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');

$dataPath = __DIR__ . '/../data/dashboard_data.json';

if (!file_exists($dataPath)) {
    http_response_code(404);
    echo json_encode([
        'status' => 'error',
        'message' => 'Data dashboard belum tersedia. Silakan jalankan proses sinkronisasi ETL terlebih dahulu.'
    ]);
    exit;
}

// Read and return JSON
$jsonContent = file_get_contents($dataPath);
echo $jsonContent;
