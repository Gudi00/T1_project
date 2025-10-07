from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryMemory, ConversationBufferMemory
from transformers import pipeline  # для создания пайплайна генерации текста
from langchain_community.llms import HuggingFacePipeline
import torch
import structlog

logger = structlog.get_logger()

def create_chain(model, tokenizer, retriever, dynamic_data):
    """
    Создаёт LangChain цепочку с custom prompt, memory, RAG.
    """
    try:
        # LLM pipeline
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200, temperature=0.7, do_sample=True)
        llm = HuggingFacePipeline(pipeline=pipe)

        # Memory: ConversationSummaryMemory с fallback на Buffer
        memory = ConversationSummaryMemory(llm=llm, max_token_limit=1500, memory_key="chat_history", return_messages=True)
        # Fallback на Buffer если <5 turns (реализуйте проверку в app)

        # Custom RU prompt
        prompt_template = """
        Ты — русскоязычный ассистент поддержки. Ответь естественно на основе контекста.
        Контекст: {context}
        Динамические данные: {dynamic}
        История: {chat_history}
        Вопрос: {question}
        Ответ:
        """
        PROMPT = PromptTemplate(input_variables=["context", "dynamic", "chat_history", "question"], template=prompt_template)

        # Chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": PROMPT}
        )
        # Добавляем dynamic_data в input
        def run_chain(query, history):
            return chain({"question": query, "dynamic": dynamic_data, "chat_history": history})

        logger.info("Chain создана.")
        return run_chain, memory
    except Exception as e:
        logger.error(f"Ошибка в create_chain: {e}")
        raise