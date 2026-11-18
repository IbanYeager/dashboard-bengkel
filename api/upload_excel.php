<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Max upload size 100MB
ini_set('upload_max_filesize', '100M');
ini_set('post_max_size', '100M');
ini_set('max_execution_time', 300);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['status' => 'error', 'message' => 'Metode request tidak diizinkan. Gunakan POST.']);
    exit;
}

if (!isset($_FILES['excel_file']) || $_FILES['excel_file']['error'] !== UPLOAD_ERR_OK) {
    echo json_encode([
        'status' => 'error', 
        'message' => 'Gagal mengunggah berkas. Pastikan ukuran file tidak melebihi batas (maks 100MB).'
    ]);
    exit;
}

$file = $_FILES['excel_file'];
$fileName = $file['name'];
$ext = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));

if ($ext !== 'xlsx') {
    echo json_encode([
        'status' => 'error', 
        'message' => 'Format file tidak didukung. Harap unggah file Excel berekstensi .xlsx.'
    ]);
    exit;
}

$targetExcel = realpath(__DIR__ . '/..') . '/DASH KIARACONDONG 24-26.xlsx';
$backupExcel = realpath(__DIR__ . '/..') . '/DASH KIARACONDONG 24-26.backup.xlsx';

// Create backup of current master excel if exists
if (file_exists($targetExcel)) {
    copy($targetExcel, $backupExcel);
}

// Move uploaded file
if (!move_uploaded_file($file['tmp_name'], $targetExcel)) {
    echo json_encode([
        'status' => 'error',
        'message' => 'Gagal menyimpan file Excel ke server.'
    ]);
    exit;
}

// Execute python ETL sync
$scriptPath = realpath(__DIR__ . '/../scripts/etl_sync.py');
if (!$scriptPath || !file_exists($scriptPath)) {
    echo json_encode([
        'status' => 'error',
        'message' => 'File Excel tersimpan, namun script etl_sync.py tidak ditemukan.'
    ]);
    exit;
}

$cmd = "python " . escapeshellarg($scriptPath) . " 2>&1";
exec($cmd, $output, $returnCode);

if ($returnCode === 0) {
    echo json_encode([
        'status' => 'success',
        'message' => 'File Excel berhasil diunggah dan seluruh data dashboard telah diperbarui!',
        'log' => implode("\n", array_slice($output, -10))
    ]);
} else {
    echo json_encode([
        'status' => 'warning',
        'message' => 'File tersimpan, namun proses sinkronisasi ETL menghasilkan peringatan.',
        'log' => implode("\n", $output)
    ]);
}
