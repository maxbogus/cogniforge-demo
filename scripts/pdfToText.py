#!/bin/bash

# Скрипт для конвертации PDF в текст
# Требует установки: poppler-utils (pdftotext)

set -e

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "Использование: $0 <input.pdf> [output.txt]"
    echo "Пример: $0 document.pdf output.txt"
    exit 1
fi

INPUT_PDF="$1"

if [ $# -ge 2 ]; then
    OUTPUT_FILE="$2"
else
    # Автоматическое имя файла
    OUTPUT_FILE="${INPUT_PDF%.pdf}.txt"
fi

# Проверка существования файла
if [ ! -f "$INPUT_PDF" ]; then
    echo "Ошибка: Файл $INPUT_PDF не найден"
    exit 1
fi

# Проверка наличия pdftotext
if ! command -v pdftotext &> /dev/null; then
    echo "Ошибка: pdftotext не найден. Установите:"
    echo "  Ubuntu/Debian: sudo apt-get install poppler-utils"
    echo "  macOS: brew install poppler"
    echo "  CentOS/RHEL: sudo yum install poppler-utils"
    exit 1
fi

echo "Конвертация $INPUT_PDF в $OUTPUT_FILE..."

# Конвертация с параметрами:
# -layout: сохраняет макет
# -nopgbrk: не добавляет разрывы страниц
# -enc UTF-8: кодировка UTF-8
pdftotext -layout -nopgbrk -enc UTF-8 "$INPUT_PDF" "$OUTPUT_FILE"

# Удаление лишних пробелов и пустых строк
sed -i 's/[[:space:]]\+/ /g' "$OUTPUT_FILE"
sed -i '/^[[:space:]]*$/d' "$OUTPUT_FILE"

echo "Готово! Файл сохранен: $OUTPUT_FILE"
echo "Размер файла: $(wc -l < "$OUTPUT_FILE") строк, $(wc -c < "$OUTPUT_FILE") байт"
