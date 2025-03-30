# RAG System

## Для старта

### Устанавливаем модель
Скачиваем ollama с официального сайта
```bash 
  ollama pull ollama pull 3.1:8b
```
```bash 
  ollama serve
```
### Устанавливаем проект
```bash 
  git clone https://github.com/IvanMalkS/rag
```
```bash
  pipx install poetry
```
```bash
  poetry install
```
### Запускаем проект
```bash
  poetry run main.py
```

## Примеры .env

```env
OLLAMA_BASE_URL=http://localhost:11000
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TIMEOUT=60
OLLAMA_TEMPERATURE=0.3
OLLAMA_TOP_P=0.9
OLLAMA_REPEAT_PENALTY=1.1
FASTAPI_PORT=8000
```