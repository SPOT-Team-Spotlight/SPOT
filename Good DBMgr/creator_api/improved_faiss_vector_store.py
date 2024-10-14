import os
import pickle
import numpy as np
import faiss
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ImprovedFaissVectorStore:
    def __init__(self, index_dir="vdb_data", shard_size=1000000, num_shards=10):
        """
        개선된 Faiss 벡터 저장소 초기화
        :param index_dir: 인덱스 파일을 저장할 디렉토리
        :param shard_size: 각 샤드의 최대 크기
        :param num_shards: 최대 샤드 수
        """
        self.index_dir = index_dir
        self.shard_size = shard_size
        self.num_shards = num_shards
        self.shards = []
        self.metadata = []
        self.dim = None
        self.executor = ThreadPoolExecutor(max_workers=4)  # 비동기 작업을 위한 스레드 풀

        os.makedirs(self.index_dir, exist_ok=True)
        self.load_shards()

    def load_shards(self):
        """기존 샤드 로드 또는 새 샤드 생성"""
        for i in range(self.num_shards):
            shard_file = os.path.join(self.index_dir, f"shard_{i}.index")
            metadata_file = os.path.join(self.index_dir, f"metadata_{i}.pkl")
            
            if os.path.exists(shard_file) and os.path.exists(metadata_file):
                # 기존 샤드와 메타데이터 로드
                shard = faiss.read_index(shard_file, faiss.IO_FLAG_MMAP)
                with open(metadata_file, 'rb') as f:
                    shard_metadata = pickle.load(f)
                
                self.shards.append(shard)
                self.metadata.append(shard_metadata)
                
                if self.dim is None:
                    self.dim = shard.d
            else:
                # 새 샤드 생성 (필요한 경우)
                if self.dim is None:
                    # 첫 번째 샤드인 경우, 아직 차원을 모르므로 생성 연기
                    self.shards.append(None)
                    self.metadata.append([])
                else:
                    new_shard = faiss.IndexFlatL2(self.dim)
                    self.shards.append(new_shard)
                    self.metadata.append([])

    async def add_to_index(self, vector_dict, metadata):
        """
        벡터와 메타데이터를 인덱스에 추가
        :param vector_dict: 추가할 벡터 딕셔너리
        :param metadata: 연관된 메타데이터
        """
        combined_vectors = np.vstack([v.flatten() for v in vector_dict.values()])

        if self.dim is None:
            self.dim = combined_vectors.shape[1]
            # 첫 번째 샤드 초기화
            self.shards[0] = faiss.IndexFlatL2(self.dim)

        # 여유 공간이 있는 샤드 찾기
        shard_index = next((i for i, shard in enumerate(self.shards) 
                            if shard is None or shard.ntotal < self.shard_size), None)

        if shard_index is None:
            # 모든 샤드가 가득 찼다면, 가능한 경우 새 샤드 생성
            if len(self.shards) < self.num_shards:
                self.shards.append(faiss.IndexFlatL2(self.dim))
                self.metadata.append([])
                shard_index = len(self.shards) - 1
            else:
                raise ValueError("모든 샤드가 가득 찼습니다. num_shards나 shard_size를 늘리세요.")

        # 선택된 샤드에 추가
        shard = self.shards[shard_index]
        shard.add(combined_vectors)
        self.metadata[shard_index].append(metadata)

        # 업데이트된 샤드와 메타데이터를 비동기적으로 저장
        await self.save_shard(shard_index)

    async def save_shard(self, shard_index):
        """특정 샤드와 그 메타데이터를 비동기적으로 저장"""
        shard_file = os.path.join(self.index_dir, f"shard_{shard_index}.index")
        metadata_file = os.path.join(self.index_dir, f"metadata_{shard_index}.pkl")

        # ThreadPoolExecutor를 사용하여 I/O 작업 수행
        await asyncio.get_event_loop().run_in_executor(
            self.executor,
            lambda: faiss.write_index(self.shards[shard_index], shard_file)
        )

        await asyncio.get_event_loop().run_in_executor(
            self.executor,
            lambda: pickle.dump(self.metadata[shard_index], open(metadata_file, 'wb'))
        )

    async def search(self, query_vector, k=5):
        """
        주어진 쿼리 벡터와 가장 유사한 k개의 벡터 검색
        :param query_vector: 검색할 쿼리 벡터
        :param k: 반환할 결과의 개수
        :return: (거리, 인덱스) 튜플
        """
        if self.dim is None:
            raise ValueError("인덱스가 비어 있습니다")

        query_vector = query_vector.reshape(1, -1)
        if query_vector.shape[1] != self.dim:
            raise ValueError(f"쿼리 벡터의 차원({query_vector.shape[1]})이 "
                             f"인덱스의 차원({self.dim})과 일치하지 않습니다")

        # 모든 샤드에서 검색 수행
        results = await asyncio.gather(*[
            self.search_shard(shard, query_vector, k)
            for shard in self.shards if shard is not None
        ])

        # 결과 병합 및 정렬
        all_distances = np.concatenate([r[0] for r in results])
        all_indices = np.concatenate([r[1] for r in results])
        
        # 정렬하여 상위 k개 결과 선택
        sorted_indices = np.argsort(all_distances)[:k]
        top_distances = all_distances[sorted_indices]
        top_indices = all_indices[sorted_indices]

        return top_distances, top_indices

    async def search_shard(self, shard, query_vector, k):
        """
        개별 샤드에서 비동기적으로 검색 수행
        """
        return await asyncio.get_event_loop().run_in_executor(
            self.executor,
            lambda: shard.search(query_vector, k)
        )

    def get_metadata(self, indices):
        """
        주어진 인덱스에 해당하는 메타데이터 반환
        """
        metadata = []
        for idx in indices:
            shard_idx = idx // self.shard_size
            local_idx = idx % self.shard_size
            metadata.append(self.metadata[shard_idx][local_idx])
        return metadata