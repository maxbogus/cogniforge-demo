#!/bin/bash
# Скрипт копирования демо-данных из diplomMagistrate в cogniforge

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DATA="/home/maxbogus/Repositories/diplomMagistrate/data"
DEST_ROOT="$PROJECT_ROOT/data"

echo "=============================================="
echo "Копирование демо-данных в cogniforge"
echo "=============================================="
echo ""

# Создание директорий
echo "[1/4] Создание директорий..."
mkdir -p "$DEST_ROOT/inbound/wikipedia"
mkdir -p "$DEST_ROOT/inbound/terms"
mkdir -p "$DEST_ROOT/indices"
echo "   ✓ Создано: data/inbound/wikipedia"
echo "   ✓ Создано: data/inbound/terms"
echo "   ✓ Создано: data/indices"

# Копирование wikipedia JSON файлов
echo ""
echo "[2/4] Копирование wikipedia_cache/*.json..."
WIKI_COUNT=$(find "$SRC_DATA/wikipedia_cache" -name "*.json" 2>/dev/null | wc -l)
WIKI_SIZE=$(du -sh "$SRC_DATA/wikipedia_cache" 2>/dev/null | cut -f1)
echo "   Найдено файлов: $WIKI_COUNT (размер: $WIKI_SIZE)"

if [ "$WIKI_COUNT" -gt 0 ]; then
    cp -v "$SRC_DATA/wikipedia_cache"/*.json "$DEST_ROOT/inbound/wikipedia/"
    echo "   ✓ Скопировано в data/inbound/wikipedia/"
else
    echo "   ✗ Файлы не найдены!"
fi

# Копирование terms.csv
echo ""
echo "[3/4] Копирование terms.csv..."
if [ -f "$SRC_DATA/terms.csv" ]; then
    cp -v "$SRC_DATA/terms.csv" "$DEST_ROOT/inbound/terms/terms.csv"
    TERMS_SIZE=$(du -sh "$SRC_DATA/terms.csv" | cut -f1)
    echo "   ✓ Скопировано (размер: $TERMS_SIZE)"
else
    echo "   ✗ Файл terms.csv не найден!"
fi

# Копирование FAISS индексов
echo ""
echo "[4/4] Копирование FAISS файлов..."
INDEX_COUNT=$(find "$SRC_DATA/model_cache" -name "*.index" -o -name "*.meta.pkl" 2>/dev/null | wc -l)
INDEX_SIZE=$(du -sh "$SRC_DATA/model_cache" 2>/dev/null | cut -f1)
echo "   Найдено файлов: $INDEX_COUNT (размер: $INDEX_SIZE)"

if [ "$INDEX_COUNT" -gt 0 ]; then
    cp -v "$SRC_DATA/model_cache"/*.index "$DEST_ROOT/indices/"
    cp -v "$SRC_DATA/model_cache"/*.meta.pkl "$DEST_ROOT/indices/"
    echo "   ✓ Скопировано в data/indices/"
else
    echo "   ✗ Файлы не найдены!"
fi

# Статистика
echo ""
echo "=============================================="
echo "СТАТИСТИКА"
echo "=============================================="
echo ""
echo "Wikipedia cache:"
echo "   Файлов: $(find "$DEST_ROOT/inbound/wikipedia" -name "*.json" 2>/dev/null | wc -l)"
echo "   Размер: $(du -sh "$DEST_ROOT/inbound/wikipedia" 2>/dev/null | cut -f1)"
echo ""
echo "Terms:"
echo "   Файлов: $(find "$DEST_ROOT/inbound/terms" -name "*.csv" 2>/dev/null | wc -l)"
echo "   Размер: $(du -sh "$DEST_ROOT/inbound/terms" 2>/dev/null | cut -f1)"
echo ""
echo "Indices (FAISS):"
echo "   Файлов: $(find "$DEST_ROOT/indices" -type f 2>/dev/null | wc -l)"
echo "   Размер: $(du -sh "$DEST_ROOT/indices" 2>/dev/null | cut -f1)"
echo ""
echo "=============================================="
echo "Готово!"
echo "=============================================="
