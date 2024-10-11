import pickle
import os

# meta Data의 파일 이름 초기화
meta_name = 'spot_metadata'
meta_file_name = meta_name + '.pkl'

# pkl 파일 불러오기
try:
    with open(meta_file_name, 'rb') as f:
        pkl = pickle.load(f)
    print("메타 데이터가 성공적으로 로드되었습니다.")
except FileNotFoundError:
    print("메타 데이터이 존재하지 않습니다.")
except pickle.UnpicklingError:
    print("메타 데이터를 열 수 없거나 손상되었습니다.")

def print_meta(file_name='pkl_output'):
    """
    메타 데이터를 txt로 출력해주는 함수
    이미 존재할 경우 덮어씌워집니다
    """
    full_name = file_name + '.txt'

    # pkl 파일 읽기
    with open(meta_file_name, 'rb') as f:
        data = pickle.load(f)

    # txt 파일로 저장하기
    with open(full_name, 'w') as f:
        for i, d in enumerate(data):
            word = str(i) + " : " + str(d) + "\n"
            f.write(word)
        else:
            print(f"메타데이터를 {full_name}로 저장했습니다")

def append_meta(dst_file=meta_file_name, src_file=None, after_write_option='d'):
    """
    meta 데이터를 합치는 함수
    dst_file : 대상 메타 데이터의 파일명
    src_file : 덧붙힐 메타 데이터의 파일명
    after_write_option : 덧붙힌 뒤에 할 행동, 기본 d -> 덧붙힌 뒤 삭제
    """
    src_file = str(src_file) + '.pkl'

    # 두 메타데이터 파일 불러오기
    try:
        with open(meta_file_name, 'rb') as f:
            metadata1 = pickle.load(f)
        print(f"A 데이터 {meta_file_name}를 로드했습니다.")
    except FileNotFoundError:
        print(f"A 데이터 {meta_file_name}이(가) 존재하지 않습니다.")
        raise  
    except pickle.UnpicklingError:
        print(f"A 데이터 {meta_file_name}를 열 수 없거나 손상되었습니다.")
        raise  

    try:
        with open(src_file, 'rb') as f:
            metadata2 = pickle.load(f)
        print(f"B 데이터 {src_file}를 로드했습니다.")
    except FileNotFoundError:
        print(f"B 데이터 {src_file}이(가) 존재하지 않습니다.")
        raise  
    except pickle.UnpicklingError:
        print(f"B 데이터 {src_file}를 열 수 없거나 손상되었습니다.")
        raise  

    # 메타데이터 병합
    merged_metadata = metadata1 + metadata2  # 리스트 형태라면

    # 병합된 메타데이터 저장
    with open(dst_file, 'wb') as f:
        pickle.dump(merged_metadata, f)
        print(f"{src_file}를 {meta_file_name}에 덧붙히는데 성공했습니다.")

     # 파일 삭제
    if(after_write_option == 'd'):
        if os.path.exists(src_file):
            os.remove(src_file)
            print(f"{src_file} 파일이 삭제되었습니다.")
        else:
            print(f"{src_file} 파일이 존재하지 않습니다.")

if __name__ == "__main__":
    # append_meta(src_file="bbb", after_write_option='c')
    print_meta()