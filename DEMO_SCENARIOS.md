# CogniForge: Демонстрационные сценарии для курса AI-Vibecoding

## ✅ Реализовано

### Доступные URLs
| Сервис | URL | Описание |
|--------|-----|----------|
| **Frontend** | http://localhost:3000 | Dashboard CogniForge |
| **Demo Page** | http://localhost:3000/demo | Интерактивные демо сценарии |
| **API Docs** | http://localhost:3000/api/docs | Swagger UI |
| **Health** | http://localhost:3000/health | System health |

### Реализованные компоненты

#### Демо-компоненты (`frontend/src/components/demo/`)
- **ScenarioCard** - интерактивная карточка сценария с кнопками управления
- **PipelineVisualizer** - анимированная визуализация RAG pipeline
- **MetricsDisplay** - отображение VCVI метрик (TTP, P2D, MCC, NSM)
- **DemoSearchPanel** - панель семантического поиска с результатами

---

## 📋 Сценарии демонстрации

### Сценарий 1: RAG Pipeline
**Цель:** Показать полный цикл работы RAG-системы

**Steps:**
1. Загрузка документа (PDF, DOCX, TXT)
2. Извлечение текста
3. Chunking (512 tokens per chunk)
4. Embeddings (all-MiniLM-L6-v2, 384 dim)
5. FAISS Index
6. Семантический поиск

**API команды:**
```bash
# Загрузить документ
curl -X POST http://localhost:3000/api/documents/upload \
  -F "file=@data/inbound/sample.pdf"

# Поиск по документу
curl -X POST http://localhost:3000/api/documents/search \
  -H "Content-Type: application/json" \
  -d '{"query": "что было в договоре про сроки?", "top_k": 5}'
```

---

### Сценарий 2: Due Diligence Analyzer
**Цель:** Анализ M&A документов

**Features:**
- Автоматическая категоризация (Contracts, Reports, Financials, Legal)
- Cross-document similarity analysis
- Structured extraction

```bash
# Поиск по ключевым словам
curl -X POST http://localhost:3000/api/documents/search \
  -d '{"query": "earn-out conditions"}'
```

---

### Сценарий 3: Resume Screening
**Цель:** Сравнение кандидатов с вакансией

```bash
# Поиск резюме
curl -X POST http://localhost:3000/api/documents/search \
  -d '{"query": "Python developer, 5 years experience, ML"}'
```

---

### Сценарий 4: System Monitoring
**Цель:** Показать observability

**Endpoints:**
```bash
# Health check
curl http://localhost:3000/health

# System info
curl http://localhost:3000/api/system/info

# Version
curl http://localhost:3000/api/version
```

---

## 📊 VCVI Метрики CogniForge

| Метрика | Значение | Комментарий |
|---------|----------|-------------|
| **TTP** | ~2 мин | Время исправления через AI |
| **P2D** | ~10 мин | Время от пуша до деплоя |
| **MCC** | <5% | Ручной код: только фиксы |
| **AC** | 1 | Основной агент + Clinerules |
| **NSM** | <100ms | RAG search latency |

---

## 🎓 Ключевые выводы для студентов

1. **RAG != просто embeddings** — chunking strategy, hybrid search
2. **Observability с первого дня** — health checks, metrics
3. **Docker Compose упрощает деплой** — single-port architecture
4. **VCVI считается просто** — метрики важнее слов

---

## 🔒 Безопасность

### ❌ Скрыто:
- API keys и secrets
- Database connection strings
- Реальные суммы сделок M&A

### ✅ Открыто:
- Архитектура системы
- API endpoints (Swagger)
- VCVI метрики
- Код без секретов

---

*Для демонстрации: http://localhost:3000/demo*
