document.addEventListener("DOMContentLoaded", function() {
    // DOM 요소 가져오기
    const voiceSearchButton = document.getElementById('voiceSearchButton');
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');


    // 검색 요청을 처리하는 함수
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();  // 기본 폼 동작 막기
        const searchInputValue = searchInput.value;


        // 변경: searchInput 대신 searchInputValue 사용
        if (!searchInputValue) {
            alert("검색어와 지역을 입력하세요!");
            return;
        }

        const formData = new URLSearchParams();
        // 변경: searchInput 대신 searchInputValue 사용
        formData.append('search_input', searchInputValue);

        fetch('http://127.0.0.1:8000/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok. Status: ' + response.status);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            }

            return response.text();
        })
        .then(data => {
            if (typeof data === 'string') {
                document.body.innerHTML = data;
            } else {
                console.log('JSON 응답:', data);
                // 변경: JSON 데이터 처리에 대한 주석 추가
                // JSON 데이터를 사용하여 결과를 표시하는 로직을 여기에 추가
            }
        })
        .catch(error => {
            console.error('Error during fetch:', error);
            alert('Error: ' + error.message);
        });
    });

    // 음성 인식 기능
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'ko-KR';

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            searchInput.value = transcript;
            alert(`음성 인식 결과: ${transcript}`);
        };

        recognition.onend = function() {
            console.log('음성 인식이 종료되었습니다.');
        };

        voiceSearchButton.addEventListener('click', () => {
            recognition.start();
            console.log('음성 인식이 시작되었습니다.');
        });
    } else {
        voiceSearchButton.style.display = 'none';
        console.log('음성 인식이 지원되지 않는 브라우저입니다.');
    }
});

// 추천 문장 카드 자동 검색 기능 (전역 함수)
function autoSearch(searchTerm) {
    document.getElementById('searchInput').value = searchTerm;
    document.getElementById('searchForm').dispatchEvent(new Event('submit'));
}