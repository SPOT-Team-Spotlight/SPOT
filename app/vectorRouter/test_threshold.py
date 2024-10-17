import unittest
import numpy as np
from threshold import filter_results  # 같은 폴더 내에 있으므로 경로를 단순하게 작성 가능

class TestThresholdFilter(unittest.TestCase):

    def test_filter_results(self):
        # 테스트할 데이터 준비
        distances = np.array([0.5, 1.2, 0.3, 1.5, 0.8])  # 거리 배열
        indices = np.array([0, 1, 2, 3, 4])  # 인덱스 배열
        threshold = 1.0  # 쓰레스홀드 값

        # filter_results 함수를 사용해 필터링
        filtered_distances, filtered_indices = filter_results(distances, indices, threshold)

        # 테스트 1: 모든 필터링된 거리 값들이 threshold 이하인지 확인
        self.assertTrue(np.all(filtered_distances < threshold), "Filtered distances contain values greater than threshold.")

        # 테스트 2: 필터링된 결과의 개수 확인 (1.0 이상의 값들은 필터링되었기 때문에 3개가 남아야 함)
        self.assertEqual(len(filtered_distances), 3, "Filtered results have incorrect number of elements.")

        # 테스트 3: 필터링된 인덱스들이 올바른지 확인
        # 필터링 후 남아야 할 인덱스는 0.5, 0.3, 0.8의 인덱스들이므로 [0, 2, 4]가 되어야 함
        self.assertListEqual(filtered_indices.tolist(), [0, 2, 4], "Filtered indices do not match expected values.")

if __name__ == "__main__":
    unittest.main()