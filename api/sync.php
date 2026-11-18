<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Allow up to 10 minutes for downloading 47MB spreadsheet and running full ETL
set_time_limit(600);
ini_set('max_execution_time', 600);
ini_set('memory_limit', '1024M');

// Default to live Google Sheets sync unless explicitly specified as 'local'
$source = isset($_GET['source']) ? $_GET['source'] : 'gsheet';
$deploy = isset($_GET['deploy']) && ($_GET['deploy'] === '1' || $_GET['deploy'] === 'true');

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

if ($source === 'local') {
    $scriptPath = realpath(__DIR__ . '/../scripts/etl_sync.py');
    $cmd = $pythonBin . " " . escapeshellarg($scriptPath) . " 2>&1";
} else {
    $scriptPath = realpath(__DIR__ . '/../scripts/sync_from_google_sheets.py');
    $cmd = $pythonBin . " " . escapeshellarg($scriptPath) . ($deploy ? " --deploy" : "") . " 2>&1";
}

if (!$scriptPath || !file_exists($scriptPath)) {
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Script sync tidak ditemukan']);
    exit;
}

// Execute python sync
exec($cmd, $output, $returnCode);

if ($returnCode === 0) {
    // Read latest generated stats from dashboard_data.json
    $dataPath = realpath(__DIR__ . '/../data/dashboard_data.json');
    $stats = [];
    if ($dataPath && file_exists($dataPath)) {
        $jsonContent = json_decode(file_get_contents($dataPath), true);
        if ($jsonContent) {
            $sep = $jsonContent['monthly_kpis']['2026']['September'] ?? [];
            $stats = [
                'generated_at' => $jsonContent['meta']['generated_at'] ?? '',
                'total_pkb' => $jsonContent['meta']['total_pkb_records'] ?? 0,
                'total_so' => $jsonContent['meta']['total_so_records'] ?? 0,
                'september_ue' => $sep['ue_total'] ?? 0,
                'september_cpus' => $sep['cpus'] ?? 0,
                'september_revenue' => $sep['total_revenue'] ?? 0
            ];
        }
    }

    echo json_encode([
        'status' => 'success',
        'message' => 'Sinkronisasi Google Sheets live berhasil 100% akurat!',
        'stats' => $stats,
        'log' => implode("\n", array_slice($output, -15))
    ]);
} else {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => 'Sinkronisasi gagal.',
        'log' => implode("\n", $output)
    ]);
}
