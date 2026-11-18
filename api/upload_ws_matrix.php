<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

ini_set('upload_max_filesize', '50M');
ini_set('post_max_size', '50M');
ini_set('max_execution_time', 300);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['status' => 'error', 'message' => 'Metode request tidak diizinkan. Gunakan POST.']);
    exit;
}

if (!isset($_FILES['ws_excel_file']) || $_FILES['ws_excel_file']['error'] !== UPLOAD_ERR_OK) {
    echo json_encode([
        'status' => 'error',
        'message' => 'Gagal mengunggah berkas Excel WS Matrix. Pastikan file valid dan ukuran di bawah 50MB.'
    ]);
    exit;
}

$file = $_FILES['ws_excel_file'];
$fileName = $file['name'];
$ext = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));

if (!in_array($ext, ['xlsx', 'xls'])) {
    echo json_encode([
        'status' => 'error',
        'message' => 'Format file tidak didukung. Harap unggah berkas Excel berekstensi .xlsx atau .xls.'
    ]);
    exit;
}

$baseDir = realpath(__DIR__ . '/..');
$targetExcel = $baseDir . '/KPI Dashboard Kabeng GR-ags.xlsx';
$backupExcel = $baseDir . '/KPI Dashboard Kabeng GR-ags.backup.xlsx';

// Create backup if exists
if (file_exists($targetExcel)) {
    @copy($targetExcel, $backupExcel);
}

// Move uploaded file
if (!move_uploaded_file($file['tmp_name'], $targetExcel)) {
    echo json_encode([
        'status' => 'error',
        'message' => 'Gagal menyimpan file Excel WS Matrix ke server.'
    ]);
    exit;
}

// Execute python extraction script
$scriptPath = $baseDir . '/scripts/extract_ws_table.py';
if (file_exists($scriptPath)) {
    $cmd = "python " . escapeshellarg($scriptPath) . " 2>&1";
    exec($cmd, $output, $returnCode);
    
    echo json_encode([
        'status' => 'success',
        'message' => 'Berkas Excel KPI Kabeng berhasil disimpan dan diekstrak secara permanen ke server!',
        'file_name' => $fileName,
        'log' => implode("\n", array_slice($output, -5))
    ]);
} else {
    echo json_encode([
        'status' => 'success',
        'message' => 'Berkas Excel berhasil disimpan di server.',
        'file_name' => $fileName
    ]);
}
