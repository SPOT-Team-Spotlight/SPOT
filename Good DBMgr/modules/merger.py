import faiss
import numpy as np
import pickle
import os

class Merger:
    @staticmethod
    def merge_vdbs(vdb1_index_path, vdb1_meta_path, vdb2_index_path, vdb2_meta_path, output_dir):
        # 첫번째 벡터DB 인덱스 가져오기
        index1 = faiss.read_index(vdb1_index_path)
        
        # 두번째 벡터DB 인덱스 가져오기
        index2 = faiss.read_index(vdb2_index_path)
        
        # 두 인덱스의 차원 비교
        if index1.d != index2.d:
            raise ValueError("차원이 서로 달라서 병합할 수 없습니다.")
        
        # 인덱스 머지하기
        merged_index = faiss.IndexFlatL2(index1.d)
        merged_index.add(index1.reconstruct_n(0, index1.ntotal))
        merged_index.add(index2.reconstruct_n(0, index2.ntotal))
        
        # 메타 데이터 들고오기
        with open(vdb1_meta_path, 'rb') as f:
            meta1 = pickle.load(f)
        with open(vdb2_meta_path, 'rb') as f:
            meta2 = pickle.load(f)
        
        # 메타 데이터 병합하기 (data_id 조정)
        max_data_id = max(item['data_id'] for item in meta1) if meta1 else -1
        print(max_data_id)
        for item in meta2:
            item['data_id'] += max_data_id + 1

        # 메타 데이터 병합하기
        merged_meta = meta1 + meta2
        
        # 출력 디렉토리가 없다면 새로 만들기
        os.makedirs(output_dir, exist_ok=True)
        
        # 병합된 인덱스 저장하기
        output_index_path = os.path.join(output_dir, 'merged_index.bin')
        faiss.write_index(merged_index, output_index_path)
        
        # 병합된 메타데이터 저장하기
        output_meta_path = os.path.join(output_dir, 'merged_metadata.pkl')
        with open(output_meta_path, 'wb') as f:
            pickle.dump(merged_meta, f)
        
        return output_index_path, output_meta_path
    
    @staticmethod
    def verify_merge(merged_index_path, merged_meta_path):
        """
        병합된 데이터 검증
        """
        # 검증할 데이터의 인덱스 들고오기
        merged_index = faiss.read_index(merged_index_path)
        
        # 검증할 데이터의 메타데이터 들고오기
        with open(merged_meta_path, 'rb') as f:
            merged_meta = pickle.load(f)
        
        # 인덱스와 메타데이터의 차원이 일치하는지 알아보기
        if merged_index.ntotal != len(merged_meta):
            raise ValueError("검증실패 : 차원이 일치하지 않습니다")
 
        return True