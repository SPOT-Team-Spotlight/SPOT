import numpy as np

def filter_results(distances, indices, threshold):
    """
    검색 결과를 쓰레스홀드 값으로 필터링합니다.
    :param distances: 검색된 거리 배열
    :param indices: 검색된 인덱스 배열
    :param threshold: 필터링을 위한 쓰레스홀드 값
    :return: 필터링된 거리와 인덱스 배열
    """
    filtered_distances = []
    filtered_indices = []

    for distance, index in zip(distances, indices):
        if distance < threshold:
            filtered_distances.append(distance)
            filtered_indices.append(index)

    return np.array(filtered_distances), np.array(filtered_indices)
