document.addEventListener("DOMContentLoaded", function() {
    // DOM 요소 가져오기
    const voiceSearchButton = document.getElementById('voiceSearchButton');
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    const loadingScreen = document.getElementById('loadingScreen');
    const resultsContainer = document.getElementById('results');

    // 검색 요청을 처리하는 함수
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();  // 기본 폼 동작 막기
        const searchInputValue = searchInput.value;

        if (!searchInputValue) {
            alert("검색어를 입력하세요!");
            return;
        }

        // 로딩 화면 표시
        loadingScreen.style.display = 'flex';
        resultsContainer.innerHTML = '';

        const formData = new URLSearchParams();
        formData.append('search_input', searchInputValue);

        fetch('/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            // 로딩 화면 숨기기
            loadingScreen.style.display = 'none';
            // 결과 페이지 내용으로 현재 페이지 업데이트
            document.body.innerHTML = html;
            // 스크립트 재실행을 위해 페이지에 스크립트 태그 추가
            const script = document.createElement('script');
            script.src = '/static/script.js';
            document.body.appendChild(script);
        })
        .catch(error => {
            console.error('Error during fetch:', error);
            loadingScreen.style.display = 'none';
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

    
    // 슬라이더 기능
    const slider = document.getElementById('results-slider');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const slideIndicator = document.getElementById('slide-indicator');
    
    if (slider && prevBtn && nextBtn) {
        const slides = slider.children;
        let currentSlide = 0;

        // 슬라이드 표시기 생성
        for (let i = 0; i < slides.length; i++) {
            const dot = document.createElement('div');
            dot.classList.add('indicator-dot');
            dot.addEventListener('click', () => goToSlide(i));
            slideIndicator.appendChild(dot);
        }

        function updateSlider() {
            slider.style.transform = `translateX(-${currentSlide * 100}%)`;
            
            // 표시기 업데이트
            const dots = slideIndicator.children;
            for (let i = 0; i < dots.length; i++) {
                dots[i].classList.toggle('active', i === currentSlide);
            }

            // 버튼 상태 업데이트
            prevBtn.style.display = currentSlide === 0 ? 'none' : 'block';
            nextBtn.style.display = currentSlide === slides.length - 1 ? 'none' : 'block';
        }

        function goToSlide(n) {
            currentSlide = n;
            updateSlider();
        }

        function nextSlide() {
            if (currentSlide < slides.length - 1) {
                currentSlide++;
                updateSlider();
            }
        }

        function prevSlide() {
            if (currentSlide > 0) {
                currentSlide--;
                updateSlider();
            }
        }

        nextBtn.addEventListener('click', nextSlide);
        prevBtn.addEventListener('click', prevSlide);

        // 키보드 네비게이션 추가
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight') nextSlide();
            if (e.key === 'ArrowLeft') prevSlide();
        });

        // 초기 상태 설정
        updateSlider();
    }
});

// 추천 문장 카드 자동 검색 기능 (전역 함수)
function autoSearch(searchTerm) {
    document.getElementById('searchInput').value = searchTerm;
    document.getElementById('searchForm').dispatchEvent(new Event('submit'));
}