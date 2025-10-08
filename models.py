from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from keybert import KeyBERT
from peft import PeftModel, PeftConfig
import torch
import os
import structlog

logger = structlog.get_logger()

def load_models():
    """
    Загружает все модели: Saiga, embeddings, zero-shot, KeyBERT.
    Fallback на CPU без квантизации, если CUDA/IPEX недоступны.
    """
    try:
        model_name = "IlyaGusev/saiga2_7b_lora"  # Или saiga3 если доступна

        # Env для multi-backend (фикс для CPU)
        os.environ["BNB_COMPUTE_BACKEND"] = "CPU"  # Или "IPEX" если IPEX установлен

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        if torch.cuda.is_available():
            # GPU: 4-bit quantization
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            logger.info("Saiga загружена с 4-bit quantization на GPU.")
        else:
            # CPU: Пытаемся с квантизацией via IPEX/multi-backend; fallback без
            try:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float32,  # CPU-friendly
                    bnb_4bit_use_double_quant=False,
                    bnb_4bit_quant_type="nf4"
                )
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    quantization_config=quantization_config,
                    device_map="cpu",
                    low_cpu_mem_usage=True,
                    torch_dtype=torch.float32
                )
                logger.info("Saiga загружена с 4-bit quantization на CPU (IPEX).")
            except Exception as cpu_quant_err:
                logger.warning(f"Квантизация на CPU failed: {cpu_quant_err}. Fallback без quant (высокий RAM).")
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    device_map="cpu"
                )

        # LoRA adapter
        config = PeftConfig.from_pretrained(model_name)
        model = PeftModel.from_pretrained(model, model_name)
        logger.info("LoRA adapter применён.")

        # Zero-shot
        zero_shot = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
        logger.info("Zero-shot classifier загружен.")

        # KeyBERT
        kw_model = KeyBERT(model='paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("KeyBERT загружен.")

        return tokenizer, model, zero_shot, kw_model
    except Exception as e:
        logger.error(f"Ошибка при загрузке моделей: {e}")
        raise