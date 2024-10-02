document.addEventListener("DOMContentLoaded", function() {
    const voiceSearchButton = document.getElementById('voiceSearchButton');
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    const spinner = document.getElementById('spinner');
    const spinnerMessage = document.getElementById('spinnerMessage');

    const messages = [
        "맛집 검색 중...",
        "갈매기에게 감자튀김을 뺏기지 않으려고 애쓰는 중...",
        "마라탕이나 마라샹궈냐... 고민하는 중...",
        "맛집 찾는 프로그램 개발하다가 리뷰 보고 배고파지는 중...",
        "J처럼 식도락 여행 계획 세우다가, 그냥 P로 살까 생각하는 중...",
        "야식 메뉴 고르다가 식당 문 닫을까봐 걱정하는 중...",
        "골목에서 나는 맛있는 냄새 따라가는 중...",
        "음식 사진 어떻게 찍어야 인스타 셀럽 될 지 고민하는 중...",
        "연말 식당 고르다가 리뷰보고 망설이는 중...",
        "떡볶이와 마라탕 사이에서 고민하는 중..."
    ];

    // 랜덤 메시지 선택 함수
    function getRandomMessage() {
        return messages[Math.floor(Math.random() * messages.length)];
    }

    // 메시지 업데이트 함수
    function updateSpinnerMessage() {
        spinnerMessage.textContent = getRandomMessage();
    }

    // 검색 폼 제출 이벤트 처리
    searchForm.addEventListener('submit', function(event) {
        // 스피너 표시
        spinner.style.display = 'flex';
        updateSpinnerMessage();

        // 2초마다 메시지 업데이트
        const messageInterval = setInterval(updateSpinnerMessage, 2000);

        // 페이지 이동 시 인터벌 정리
        window.addEventListener('unload', function() {
            clearInterval(messageInterval);
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
            searchForm.submit();
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

    // 페이지 로드 시 추천 카드 렌더링
    renderRecommendationCards();

    // 자동 검색 함수 수정
    window.autoSearch = function(searchTerm) {
        searchInput.value = searchTerm;
        spinner.style.display = 'flex';
        updateSpinnerMessage();
        const messageInterval = setInterval(updateSpinnerMessage, 2000);
        searchForm.submit();

        // 페이지 이동 시 인터벌 정리
        window.addEventListener('unload', function() {
            clearInterval(messageInterval);
        });
    };
});
