from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from keybert import KeyBERT
from peft import PeftModel, PeftConfig
import torch
import structlog

logger = structlog.get_logger()

def load_models():
    """
    Загружает все модели: Saiga, embeddings, zero-shot, KeyBERT.
    """
    try:
        # Saiga в 4-bit quantization
        model_name = "IlyaGusev/saiga_llama3_8b"  # Или saiga3 если доступна
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        # Если LoRA, примените Peft
        config = PeftConfig.from_pretrained(model_name)
        model = PeftModel.from_pretrained(model, model_name)
        logger.info("Saiga модель загружена с 4-bit quantization.")

        # Zero-shot classifier
        zero_shot = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
        logger.info("Zero-shot classifier загружен.")

        # KeyBERT
        kw_model = KeyBERT(model='paraphrase-multilingual-MiniLM-L12-v2')  # Multilingual для RU
        logger.info("KeyBERT загружен.")

        return tokenizer, model, zero_shot, kw_model
    except Exception as e:
        logger.error(f"Ошибка при загрузке моделей: {e}")
        raise