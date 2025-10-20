"""Constants and configuration defaults for Arbitrium Framework.

This module centralizes constant values and default configurations
that are used across the application.
"""

# Provider-specific retry delay settings for rate limits and errors
PROVIDER_RETRY_DELAYS = {
    # OpenAI tends to have shorter rate limit windows
    "openai": {"initial": 15, "max": 60},
    # Anthropic has strict rate limits but reduced for better performance
    "anthropic": {
        "initial": 30,
        "max": 300,
    },
    # Google/Gemini generally recovers quickly
    "google": {"initial": 10, "max": 45},
    # Cohere similar to OpenAI
    "cohere": {"initial": 15, "max": 60},
    # Azure OpenAI follows similar patterns to OpenAI
    "azure": {"initial": 15, "max": 60},
    # Mistral API
    "mistral": {"initial": 15, "max": 60},
    # Together AI
    "together": {"initial": 10, "max": 40},
    # Vertex AI (Google Cloud)
    "vertex_ai": {"initial": 15, "max": 60},
    # XAI (Grok)
    "xai": {"initial": 15, "max": 60},
    # Conservative default for unknown providers
    "default": {"initial": 30, "max": 90},
}

# Error type patterns for classification (used by both base.py and exceptions.py)
ERROR_PATTERNS = {
    # Rate limit related patterns
    "rate_limit": [
        "rate limit",
        "ratelimit",
        "too many requests",
        "429",
        "tps",
        "tokens per minute",
        "input tokens per minute",
        "requests per minute",
        "rpm",
        "quota",
        "exceeded",
        "limit reached",
        "capacity",
        "throttled",
        "limit error",
        "error code: 429",
        "code: 429",
        "error code: 160",
        "code: 160",
        "error code: 6",
        "code: 6",
        "error code: 1015",
        "code: 1015",
        "anthropicexception",
        "ratelimiterror",
        "rate_limit_error",
    ],
    # Timeout related patterns
    "timeout": ["timeout", "timed out", "time-out"],
    # Connection/network related patterns
    "connection": [
        "connection error",
        "network error",
        "connection reset",
        "unreachable",
    ],
    # Overloaded server patterns (especially for Anthropic)
    "overloaded": [
        "overloaded",
        "overloaded_error",
        "server overloaded",
        "server busy",
        "529",
        "server is currently overloaded",
    ],
    # Other retryable patterns (service issues)
    "service": [
        "retry",
        "service unavailable",
        "unavailable",
        "try again",
        "server error",
        "temporary",
    ],
}

# Timeout and concurrency defaults
DEFAULT_MODEL_TIMEOUT = 300  # 5 minutes in seconds (reduced from 20 min)
DEFAULT_THREAD_POOL_WORKERS = 5
DEFAULT_INPUT_TIMEOUT = 120  # seconds

# Subprocess timeout defaults
DEFAULT_SUBPROCESS_TIMEOUT = 240  # 4 minutes

# Cache and memory limits
DEFAULT_LOG_CACHE_SIZE = 1000
DEFAULT_MAX_INSIGHTS = 100  # Maximum insights in knowledge bank

# Token estimation defaults
DEFAULT_CHARS_PER_TOKEN = 4
DEFAULT_CONTEXT_SAFETY_MARGIN = 0.1  # 10% safety margin
DEFAULT_PRESERVE_START_CHARS = 1000
DEFAULT_PRESERVE_END_CHARS = 1000

# Health check prompt
HEALTH_CHECK_PROMPT = "Say 'OK'"

# Response validation
PLACEHOLDER_RESPONSES = ["###", "...", "n/a", "none", "null"]

# Score extraction patterns for evaluation parsing
# ВАЖНО: Паттерны применяются по порядку. Самые строгие и надежные должны идти первыми.
SCORE_EXTRACTION_PATTERNS = [
    # =================================================================================
    # УРОВЕНЬ 1: ЖЕЛЕЗОБЕТОННАЯ НАДЕЖНОСТЬ  # noqa: RUF003
    # Эти паттерны ищут четкие, однозначные форматы. Они сработают в 90% случаев.
    # Порядок важен - более специфичные паттерны должны идти первыми!
    # =================================================================================
    # 1. Оценка в скобках с явным "Score:" после упоминания модели: "LLM1 provided... (Score: 8.3)"  # noqa: RUF003
    # ЭТОТ ПАТТЕРН ИДЁТ ПЕРВЫМ, чтобы избежать ложных срабатываний на "Score -" в тексте
    # Лимит 800 символов для поиска (некоторые модели пишут длинные описания перед оценкой)
    r"({model_name})[^\n(]{{0,800}}?\((?:Score|Rating)\s*:\s*(\d+(?:\.\d+)?)",
    # 2. Оценка в скобках после упоминания модели: "Ответ от LLM1 был хорош (8/10)."
    # Лимит 800 символов, чтобы не захватить далекие скобки, но покрыть длинные описания
    r"({model_name})[^\n(]{{0,800}}?\((\d+(?:\.\d+)?)(?:/10)?\)",
    # 3. Формат когда оценки на одной строке: "LLM1: 7.8LLM2: 8.2" (число сразу перед моделью)
    # (?<=\d) - positive lookbehind проверяет, что перед моделью есть цифра (конец предыдущей оценки)
    # Это ловит случаи без пробелов между оценками
    r"(?<=\d)({model_name})\s*[:\-]\s*(\d+(?:\.\d+)?)(?!\d)",
    # 4. Самый частый формат с word boundary: "LLM1: 9.5" (может быть в середине строки)  # noqa: RUF003
    # Word boundary перед моделью гарантирует, что мы не захватим "MLLM1" или подобное
    # Negative lookahead (?!\d) после числа гарантирует, что мы не захватим "9" из "95"
    r"\b({model_name})\s*[:\-]\s*(\d+(?:\.\d+)?)(?!\d)",
    # 5. Формат в начале строки (более строгий): "LLM1: 9.5/10" или "LLM1: 9"
    # Также ловит варианты с пробелами и дефисом "LLM1 - 9.5"  # noqa: RUF003
    r"^\s*({model_name})\s*[:\-]\s*(\d+(?:\.\d+)?)(?!\d)",
    # 6. Формат с круглыми скобками, который часто выдают модели: "((LLM1)): 9/10"  # noqa: RUF003
    r"\(+({model_name})\)+\s*[:\-]?\s*(\d+(?:\.\d+)?)(?!\d)",
    # 7. Формат где Score/Rating идет СРАЗУ после модели: "LLM1Score: 8.0", "LLM1:Score: 8.0", "LLM1 Score: 8.0"  # noqa: RUF003
    # Ловит случаи с двоеточием или без него после имени модели  # noqa: RUF003
    # ВАЖНО: Только двоеточие ":", НЕ дефис, чтобы избежать ложных срабатываний на "Score - текст"  # noqa: RUF003
    r"\b({model_name})\s*:?\s*(?:Score|Rating)\s*:\s*(\d+(?:\.\d+)?)(?!\d)",
    # 8. Формат с явным указанием слова "Score" или "Rating" ДО числа.  # noqa: RUF003
    # Ловит: "Score for LLM1: 9", "LLM1 Rating: 8.5"
    # ВАЖНО: Только двоеточие ":", НЕ дефис  # noqa: RUF003
    r"({model_name})\s*:?\s*(?:Score|Rating)\s*(?:is|for)?\s*:\s*(\d+(?:\.\d+)?)(?!\d)",
    # =================================================================================
    # УРОВЕНЬ 2: ВЫСОКАЯ НАДЕЖНОСТЬ  # noqa: RUF003
    # Эти паттерны ищут чуть менее строгие, но все еще очень вероятные форматы.
    # =================================================================================
    # 5. Оценка внутри жирного текста Markdown: "**LLM1: 9/10**"
    r"\*\*({model_name})\s*[:\-]\s*(\d+(?:\.\d+)?)(?:/10)?\*\*",
    # 6. Оценка в заголовке Markdown: "## Оценка для LLM1 **Score: 8.5/10**"
    r"##?\s*({model_name})\s*(?:Evaluation|Analysis|Review).*?\*\*Score:\s*(\d+(?:\.\d+)?)(?:/10)?\*\*",
    # =================================================================================
    # УРОВЕНЬ 3: "ОТЧАЯННЫЕ МЕРЫ"  # noqa: RUF003
    # Эти паттерны ищут оценку в "мусоре", когда ничего другое не сработало.
    # Они более гибкие, но достаточно безопасные, чтобы не захватить случайные цифры.
    # =================================================================================
    # 7. Общий паттерн, который ищет двоеточие/дефис после названия модели.
    # `.{0,30}?` ограничивает поиск 30 символами, чтобы не "убежать" далеко.
    # Ловит: "Моя оценка для **LLM1** - это, пожалуй: **9**"
    r"({model_name}).{{0,30}}?[:\-]\s*(\d+(?:\.\d+)?)\b",
    # 8. Финальный, самый общий паттерн. Ищет слово "Score" рядом с названием модели.  # noqa: RUF003
    # Ловит: "Что касается LLM1, я бы дал ему score 8 из 10"
    r"({model_name}).{{0,30}}?(?:Score|Rating).{{0,30}}?(\d+(?:\.\d+)?)\b",
]
