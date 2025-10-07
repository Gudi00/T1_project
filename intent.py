from langchain.memory import ConversationSummaryMemory
import structlog

logger = structlog.get_logger()

def detect_intent(query, history, zero_shot, kw_model, threshold=0.7):
    """
    Hybrid intent: Экстракт топ-3-5 ключевых слов с KeyBERT, затем zero-shot классификация.
    Учёт истории из memory.
    Labels: ["приветствие", "рекомендация", "вызов администратора"]
    """
    try:
        # Экстракт ключевых слов (ngram 1-3)
        keywords = kw_model.extract_keywords(query, keyphrase_ngram_range=(1, 3), stop_words=None, top_n=5)
        keywords_str = ", ".join([kw[0] for kw in keywords])
        logger.info(f"Ключевые слова: {keywords_str}")

        # Подготовка истории
        if history:
            summarized_history = history.buffer  # Или summarize если >5 turns
        else:
            summarized_history = ""

        # Enhanced query для zero-shot
        enhanced_query = f"{summarized_history}\nПользователь: {query}\nКлючевые слова: {keywords_str}"

        # Zero-shot
        labels = ["приветствие", "рекомендация", "вызов администратора"]
        hypothesis_template = "Это предложение относится к категории {}."  # RU template
        result = zero_shot(enhanced_query, candidate_labels=labels, hypothesis_template=hypothesis_template)

        intent = result['labels'][0] if result['scores'][0] >= threshold else "рекомендация"
        logger.info(f"Определён intent: {intent} (score: {result['scores'][0]})")

        return intent, keywords_str
    except Exception as e:
        logger.error(f"Ошибка в detect_intent: {e}")
        return "рекомендация", ""