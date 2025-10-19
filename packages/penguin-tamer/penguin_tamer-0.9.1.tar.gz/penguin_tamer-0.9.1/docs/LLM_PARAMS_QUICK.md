# ⚡ LLM Parameters Quick Reference

## 📋 Все параметры

| Параметр | Тип | Диапазон | По умолчанию | Описание |
|----------|-----|----------|--------------|----------|
| `temperature` | float | 0.0-2.0 | 0.8 | Креативность (выше = креативнее) |
| `max_tokens` | int/null | 1-∞ | null | Макс. длина ответа |
| `top_p` | float | 0.0-1.0 | 0.95 | Nucleus sampling |
| `frequency_penalty` | float | -2.0-2.0 | 0.0 | Штраф за повторы |
| `presence_penalty` | float | -2.0-2.0 | 0.0 | Штраф за упоминание |
| `stop` | list/null | - | null | Стоп-последовательности |
| `seed` | int/null | - | null | Детерминизм |

## 🎯 Готовые конфигурации

#### Точные технические команды
```yaml
temperature: 0.2
max_tokens: 500
frequency_penalty: 0.1
presence_penalty: 0.0
```

### Обычное использование
```yaml
temperature: 0.7
max_tokens: null
frequency_penalty: 0.0
```

#### Креативный brainstorming
```yaml
temperature: 1.2
max_tokens: null
frequency_penalty: 0.5
presence_penalty: 0.6
```

### Короткие ответы
```yaml
temperature: 0.5
max_tokens: 300
stop: ["\n\n\n"]
```

#### Воспроизводимые тесты
```yaml
temperature: 0.7
max_tokens: 1000
seed: 42
```

## 🔧 Редактирование

```bash
# Открыть конфиг
nano ~/.config/penguin-tamer/penguin-tamer/config.yaml

# Или через меню
pt --settings
```

## 🐛 Отладка

```bash
# Показать все параметры запроса
export PT_DEBUG=1
pt "ваш запрос"
```

## 💡 Советы

- 🎚️ Меняйте **либо** `temperature` **либо** `top_p`
- 📏 `max_tokens`: 100 токенов ≈ 75 слов
- 🔁 `frequency_penalty`: 0.3-0.5 для уменьшения повторов
- 🌱 `seed`: 42 для воспроизводимости

📚 Подробная документация: [LLM_PARAMETERS_GUIDE.md](LLM_PARAMETERS_GUIDE.md)
