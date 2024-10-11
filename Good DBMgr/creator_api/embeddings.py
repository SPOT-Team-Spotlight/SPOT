from .datas.constants import EMBEDDING_MODEL_TYPES, EMBEDDING_MODEL_VERSIONS
from langchain_openai import OpenAIEmbeddings 
import json
from .api_key import get_key
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib

class EmbeddingModule():
    def __init__(self, model_name, version, max_workers=10) -> None:
        self.model_name = model_name
        self.version = version
        self.instance = None
        self.get_embedding_instance() # 초기화 시 한 번만 인스턴스 생성
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.embedding_cache = {}
        

    def get_embedding_instance(self):
        """
        외부 호출 x
        """
        if (self.model_name in EMBEDDING_MODEL_TYPES) and (self.version in EMBEDDING_MODEL_VERSIONS[self.model_name]):
            if self.model_name == "OpenAI":
                self.instance = OpenAIEmbeddings(openai_api_key=get_key("OPENAI_API_KEY"), model=self.version)
    
    def get_text_embedding_sync(self, text): 
        """
        동기 임베딩 생성 함수
        """
        if self.instance is None:
            self.get_embedding_instance()

        if isinstance(text, dict):
            text = json.dumps(text, ensure_ascii=False)
        elif not isinstance(text, str):
            text = str(text)

        embedded_result = self.instance.embed_query(text)
        return np.array(embedded_result, dtype=np.float32)
    
    async def get_text_embedding_async(self, text):
        """
        비동기 임베딩 생성 함수
        """
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        if text_hash in self.embedding_cache:
            return self.embedding_cache[text_hash]
        else:
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(self.executor, self.get_text_embedding_sync, text)
            self.embedding_cache[text_hash] = embedding
            return embedding

    async def get_text_embeddings_async(self, texts):
        """
        여러 텍스트의 임베딩을 비동기적으로 생성하는 함수
        """
        tasks = [self.get_text_embedding_async(text) for text in texts]
        return await asyncio.gather(*tasks)

    def get_text_embeddings_batch(self, texts):
        """
        배치 임베딩을 생성하는 동기 함수
        """
        if self.instance is None:
            self.get_embedding_instance()

        # 텍스트 전처리
        processed_texts = []
        for text in texts:
            if isinstance(text, dict):
                processed_texts.append(json.dumps(text, ensure_ascii=False))
            elif not isinstance(text, str):
                processed_texts.append(str(text))
            else:
                processed_texts.append(text)
        
        # 배치 임베딩 생성
        embedded_results = self.instance.embed_documents(processed_texts)
        
        # 결과를 numpy 배열로 변환
        embeddings = [np.array(embed, dtype=np.float32) for embed in embedded_results]
        
        return embeddings