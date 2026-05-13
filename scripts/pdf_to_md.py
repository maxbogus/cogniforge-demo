#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to LLM-Optimized Markdown Converter
Создает структурированный, легко парсимый Markdown для LLM-анализа
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import pdfplumber

class LLMOptimizedMarkdownConverter:
    def __init__(self):
        # Паттерны для полного удаления (системные сообщения и артефакты)
        self.remove_patterns = [
            r'^📌 Thought for \d+ seconds [✅✓]$',
            r'^={5,}\s*Page \d+\s*={5,}$',
            r'^📄 Page \d+$',
            r'^Страница \d+$',
            r'^\*\s*Страница\s+\d+\s*\*$',
            r'^📌 Анализ \w+$',
            r'^📌 Создание \w+$',
            r'^📌 Разработка \w+$',
            r'^📌 Мы \w+$',
            r'^📌 Теперь \w+$',
            r'^📌 Документ \w+$',
            r'^📌 Готово!$',
            r'^📋 ФИНАЛЬНЫЙ ОТЧЕТ$',
            r'^={20,}$',
            r'^-{20,}$',
            r'^📊 \w+$',
            r'^✅ \w+$',
            r'^⚠️ \w+$',
            r'^❌ \w+$',
            r'^💡 \w+$',
            r'^🔧 \w+$',
            r'^📖 \w+$',
            r'^🔄 \w+$',
            r'^\s*\[file content (begin|end)\]$',
            r'^\s*PDF\s+\d+\.\d+KB\s*$',
            r'^#+\s*(?:PDF|deepseek_markdown)',
        ]
        
        # Паттерны для нормализации заголовков
        self.section_patterns = [
            (r'^(\d+\.\d+\.?\s+)(.+)', '###'),      # 1.1. Подраздел
            (r'^(\d+\.\s+)(.+)', '##'),             # 1. Раздел
            (r'^([IVXLCDM]+\.\s+)(.+)', '##'),      # I. Раздел
            (r'^([а-яА-Я]\.\s+)(.+)', '##'),        # A. Раздел
        ]
        
        # Признаки начала приложений
        self.appendice_patterns = [
            r'^Приложение [A-ZА-Я]',
            r'^Appendix [A-Z]',
            r'^ПРИЛОЖЕНИЕ',
            r'^Приложения и источники данных',
        ]
        
        # Структура документа
        self.document_structure = {
            "main": [],
            "appendix_a": [],
            "appendix_b": [],
            "appendix_c": [],
            "metadata": {}
        }

    def clean_text(self, text: str) -> str:
        """Очищает текст от артефактов и нормализует пробелы"""
        if not text:
            return ""
        
        # Удаляем невидимые символы и управляющие коды
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Заменяем проблемные символы
        replacements = {
            '�': '',
            '\uf0b7': '•',
            '\uf0a7': '§',
            '\uf0b0': '°',
            '\xad': '',  # мягкий перенос
        }
        
        for bad, good in replacements.items():
            text = text.replace(bad, good)
        
        # Нормализуем пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Исправляем пунктуацию
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        text = re.sub(r'([([{<])\s+', r'\1', text)
        text = re.sub(r'\s+([)\]}>])', r'\1', text)
        
        return text.strip()

    def is_system_artifact(self, line: str) -> bool:
        """Проверяет, является ли строка системным артефактом"""
        line = line.strip()
        
        # Проверяем по паттернам удаления
        for pattern in self.remove_patterns:
            if re.match(pattern, line, flags=re.IGNORECASE):
                return True
        
        # Проверяем короткие строки с эмодзи
        if len(line) < 5 and any(char in line for char in '📌📊✅⚠️❌💡🔧📖🔄📋'):
            return True
        
        return False

    def detect_section_type(self, line: str) -> Tuple[str, str]:
        """Определяет тип секции и нормализует заголовок"""
        line = line.strip()
        
        # Проверяем приложения
        for pattern in self.appendice_patterns:
            if re.match(pattern, line, flags=re.IGNORECASE):
                return "appendix", line
        
        # Проверяем нумерованные заголовки
        for pattern, level in self.section_patterns:
            match = re.match(pattern, line)
            if match:
                return "section", f"{level} {line}"
        
        # Заголовки без нумерации
        if len(line) < 100 and not line.endswith('.'):
            # Проверяем по заглавным буквам и длине
            words = line.split()
            if (len(words) <= 8 and 
                any(w[0].isupper() for w in words if w) and
                not line.startswith('- ') and
                not line.startswith('* ') and
                not line.startswith('• ')):
                return "section", f"## {line}"
        
        return "content", line

    def extract_and_clean_json(self, lines: List[str], start_idx: int) -> Tuple[Optional[str], int]:
        """Извлекает и чистит JSON блок"""
        json_lines = []
        brace_count = 0
        i = start_idx
        in_json = False
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Начало JSON
            if line.startswith('{') and not in_json:
                in_json = True
            
            if in_json:
                # Считаем скобки
                brace_count += line.count('{')
                brace_count -= line.count('}')
                
                json_lines.append(line)
                
                # Конец JSON блока
                if brace_count == 0 and line.endswith('}'):
                    try:
                        json_text = ' '.join(json_lines)
                        # Пытаемся распарсить
                        parsed = json.loads(json_text)
                        # Форматируем красиво
                        clean_json = json.dumps(parsed, ensure_ascii=False, indent=2)
                        return clean_json, i
                    except json.JSONDecodeError:
                        # Пробуем почистить
                        json_text = self.repair_json(' '.join(json_lines))
                        try:
                            parsed = json.loads(json_text)
                            clean_json = json.dumps(parsed, ensure_ascii=False, indent=2)
                            return clean_json, i
                        except:
                            return None, start_idx
            
            i += 1
        
        return None, start_idx

    def repair_json(self, json_text: str) -> str:
        """Пытается почистить сломанный JSON"""
        # Удаляем лишние пробелы в ключах
        json_text = re.sub(r'"\s+:\s+', '": ', json_text)
        # Исправляем незакрытые кавычки
        json_text = re.sub(r':\s*([^"\s{}\[\],]+)([,}])', r': "\1"\2', json_text)
        # Удаляем лишние запятые
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        return json_text

    def format_table_markdown(self, lines: List[str]) -> List[str]:
        """Форматирует таблицу в Markdown"""
        if not lines:
            return []
        
        # Находим все строки с табличной структурой
        table_lines = []
        for line in lines:
            if '|' in line and line.count('|') >= 2:
                table_lines.append(line)
        
        if len(table_lines) < 2:
            return lines  # Недостаточно строк для таблицы
        
        # Определяем количество колонок
        col_count = max(line.count('|') for line in table_lines)
        
        # Создаем отформатированную таблицу
        formatted = []
        for i, line in enumerate(table_lines):
            cols = line.split('|')
            # Нормализуем количество колонок
            while len(cols) < col_count + 1:
                cols.append('')
            
            # Очищаем ячейки
            cols = [c.strip() for c in cols[:col_count + 1]]
            
            # Формируем строку
            formatted_line = '| ' + ' | '.join(cols[1:-1]) + ' |'
            formatted.append(formatted_line)
            
            # Добавляем разделитель после заголовка
            if i == 0 and len(table_lines) > 1:
                separator = '|' + '|'.join([' --- '] * (col_count - 1)) + '|'
                formatted.append(separator)
        
        formatted.append('')  # Пустая строка после таблицы
        return formatted

    def organize_content(self, lines: List[str]) -> Dict[str, List[str]]:
        """Организует контент по разделам"""
        structure = {
            "main": [],
            "appendix_a": [],
            "appendix_b": [],
            "appendix_c": [],
            "other_appendix": []
        }
        
        current_section = "main"
        current_appendix = None
        buffer = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if self.is_system_artifact(line):
                i += 1
                continue
            
            # Определяем тип контента
            section_type, normalized_line = self.detect_section_type(line)
            
            # Обработка приложений
            if section_type == "appendix":
                # Сохраняем буфер предыдущего раздела
                if buffer and current_appendix:
                    structure[current_appendix].extend(buffer)
                elif buffer:
                    structure[current_section].extend(buffer)
                
                buffer = []
                
                # Определяем какое приложение
                if 'Приложение A' in line or 'Приложение А' in line or 'appendix_a' in line.lower():
                    current_appendix = "appendix_a"
                    current_section = "appendix"
                elif 'Приложение B' in line or 'Приложение Б' in line or 'appendix_b' in line.lower():
                    current_appendix = "appendix_b"
                    current_section = "appendix"
                elif 'Приложение C' in line or 'Приложение В' in line or 'appendix_c' in line.lower():
                    current_appendix = "appendix_c"
                    current_section = "appendix"
                else:
                    current_appendix = "other_appendix"
                    current_section = "appendix"
                
                structure[current_appendix].append(normalized_line)
            
            # Обработка JSON
            elif line.strip().startswith('{'):
                json_text, new_idx = self.extract_and_clean_json(lines, i)
                if json_text:
                    buffer.append('```json')
                    buffer.append(json_text)
                    buffer.append('```')
                    buffer.append('')
                    i = new_idx
                else:
                    buffer.append(normalized_line)
            
            # Обработка таблиц
            elif '|' in line and line.count('|') >= 2:
                # Собираем строки таблицы
                table_lines = [line]
                j = i + 1
                while j < len(lines) and '|' in lines[j] and lines[j].count('|') >= 2:
                    table_lines.append(lines[j])
                    j += 1
                
                formatted_table = self.format_table_markdown(table_lines)
                buffer.extend(formatted_table)
                i = j - 1
            
            # Обычный контент
            else:
                buffer.append(normalized_line)
            
            i += 1
        
        # Сохраняем последний буфер
        if buffer and current_appendix:
            structure[current_appendix].extend(buffer)
        elif buffer:
            structure[current_section].extend(buffer)
        
        return structure

    def extract_from_pdf(self, pdf_path: str) -> List[str]:
        """Извлекает текст из PDF"""
        all_lines = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                print(f"📖 Чтение PDF: {len(pdf.pages)} страниц")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"   Страница {page_num}...", end='\r')
                    
                    text = page.extract_text()
                    if text:
                        # Очищаем и разбиваем на строки
                        lines = [self.clean_text(l) for l in text.split('\n') if self.clean_text(l)]
                        all_lines.extend(lines)
                
                print(f"\n✅ Извлечено {len(all_lines)} строк")
                
        except Exception as e:
            print(f"\n❌ Ошибка чтения PDF: {e}")
            raise
        
        return all_lines

    def create_metadata(self, pdf_path: Path, structure: Dict) -> Dict[str, Any]:
        """Создает метаданные документа"""
        return {
            "document_type": "TCO Calculator and Strategy",
            "source_file": pdf_path.name,
            "converter": "LLMOptimizedMarkdownConverter",
            "version": "2.0",
            "encoding": "UTF-8",
            "language": "ru",
            "sections": {
                "main": len(structure["main"]),
                "appendix_a": len(structure["appendix_a"]),
                "appendix_b": len(structure["appendix_b"]),
                "appendix_c": len(structure["appendix_c"]),
                "other_appendix": len(structure["other_appendix"])
            },
            "total_lines": sum(len(v) for v in structure.values())
        }

    def write_structured_document(self, structure: Dict, metadata: Dict, output_path: Path):
        """Записывает структурированный документ"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Заголовок документа
            f.write(f"# {metadata['document_type']}\n\n")
            
            # Метаданные в JSON
            f.write("## 📋 МЕТАДАННЫЕ ДОКУМЕНТА\n\n")
            f.write("```json\n")
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            f.write("\n```\n\n")
            
            # Основной документ
            f.write("---\n\n")
            f.write("# РАЗДЕЛ 1: ОСНОВНОЙ ДОКУМЕНТ\n\n")
            if structure["main"]:
                f.write("\n".join(structure["main"]))
                f.write("\n\n")
            
            # Приложения
            f.write("---\n\n")
            
            if structure["appendix_a"]:
                f.write("# РАЗДЕЛ 2: МАТЕМАТИЧЕСКИЕ МОДЕЛИ (Приложение A)\n\n")
                f.write("\n".join(structure["appendix_a"]))
                f.write("\n\n")
            
            if structure["appendix_b"]:
                f.write("# РАЗДЕЛ 3: SKILLS MATRIX (Приложение B)\n\n")
                f.write("\n".join(structure["appendix_b"]))
                f.write("\n\n")
            
            if structure["appendix_c"]:
                f.write("# РАЗДЕЛ 4: КАЛЬКУЛЯТОРЫ (Приложение C)\n\n")
                f.write("\n".join(structure["appendix_c"]))
                f.write("\n\n")
            
            if structure["other_appendix"]:
                f.write("# РАЗДЕЛ 5: ДОПОЛНИТЕЛЬНЫЕ ПРИЛОЖЕНИЯ\n\n")
                f.write("\n".join(structure["other_appendix"]))
                f.write("\n\n")
            
            # Статистика
            f.write("---\n\n")
            f.write("# СТАТИСТИКА ОБРАБОТКИ\n\n")
            f.write("## Объем документа\n")
            f.write(f"- Всего строк: {metadata['total_lines']}\n")
            f.write(f"- Основной документ: {len(structure['main'])} строк\n")
            f.write(f"- Приложение A: {len(structure['appendix_a'])} строк\n")
            f.write(f"- Приложение B: {len(structure['appendix_b'])} строк\n")
            f.write(f"- Приложение C: {len(structure['appendix_c'])} строк\n\n")
            
            f.write("## Форматы контента\n")
            
            # Считаем таблицы
            all_content = []
            for section in structure.values():
                all_content.extend(section)
            
            tables = sum(1 for line in all_content if '|' in line and '---' in line)
            json_blocks = sum(1 for line in all_content if line.strip() == '```json')
            code_blocks = sum(1 for line in all_content if line.strip().startswith('```'))
            
            f.write(f"- Таблицы Markdown: {tables}\n")
            f.write(f"- JSON блоки: {json_blocks}\n")
            f.write(f"- Блоки кода: {code_blocks}\n\n")
            
            f.write("> Документ оптимизирован для LLM-анализа\n")
            f.write("> Структура: Основной текст → Приложения → JSON/Таблицы\n")

    def convert_pdf_to_structured_md(self, pdf_path: str, output_path: str = None) -> Tuple[str, Dict]:
        """Основной метод конвертации"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"Файл не найден: {pdf_path}")
        
        if output_path is None:
            output_path = pdf_path.with_suffix('.structured.md')
        
        print("=" * 60)
        print(f"🔄 Конвертация PDF в структурированный Markdown")
        print(f"📄 Входной файл: {pdf_path.name}")
        print("=" * 60)
        
        # Извлекаем текст
        extracted_lines = self.extract_from_pdf(str(pdf_path))
        
        # Организуем по разделам
        structure = self.organize_content(extracted_lines)
        
        # Создаем метаданные
        metadata = self.create_metadata(pdf_path, structure)
        
        # Записываем структурированный документ
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.write_structured_document(structure, metadata, output_path)
        
        print(f"\n✅ Структурированный документ сохранен: {output_path}")
        print(f"📊 Статистика:")
        print(f"   - Основной документ: {len(structure['main'])} строк")
        print(f"   - Приложение A: {len(structure['appendix_a'])} строк")
        print(f"   - Приложение B: {len(structure['appendix_b'])} строк")
        print(f"   - Приложение C: {len(structure['appendix_c'])} строк")
        print(f"   - Всего строк: {metadata['total_lines']}")
        print("=" * 60)
        
        return str(output_path), metadata

def main():
    if len(sys.argv) < 2:
        print("LLM-Optimized PDF to Markdown Converter")
        print("=" * 40)
        print("Использование: python pdf_to_md.py <pdf_file> [output.md]")
        print("\nПримеры:")
        print("  python pdf_to_md.py TCO_calculator.pdf")
        print("  python pdf_to_md.py TCO_calculator.pdf structured_output.md")
        print("\nОсобенности:")
        print("  • Удаляет системные артефакты LLM")
        print("  • Структурирует по разделам и приложениям")
        print("  • Чистит и форматирует JSON")
        print("  • Оптимизирует таблицы для Markdown")
        print("  • Добавляет метаданные для легкого парсинга")
        return 1
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(pdf_file):
        print(f"❌ Файл не найден: {pdf_file}")
        return 1
    
    converter = LLMOptimizedMarkdownConverter()
    
    try:
        output_path, metadata = converter.convert_pdf_to_structured_md(pdf_file, output_file)
        
        print("\n🎯 РЕКОМЕНДАЦИИ ДЛЯ LLM-АНАЛИЗА:")
        print("=" * 40)
        print("1. Документ разделен на четкие секции:")
        print("   • РАЗДЕЛ 1: Основной документ")
        print("   • РАЗДЕЛ 2: Математические модели")
        print("   • РАЗДЕЛ 3: Skills Matrix")
        print("   • РАЗДЕЛ 4: Калькуляторы")
        print("\n2. JSON блоки помещены в ```json для легкого парсинга")
        print("\n3. Таблицы отформатированы в Markdown")
        print("\n4. Все системные сообщения удалены")
        print("\n✅ Документ готов для анализа в DeepSeek и других LLM")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Ошибка конвертации: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
