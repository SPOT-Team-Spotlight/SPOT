document.addEventListener("DOMContentLoaded", function() {
    const recommendations = [
        "분위기 좋은 디저트 카페 찾아줘",
        "강남역에서 단체로 갈만한 술집",
        "순대국을 판매하는 가게 중에서도 정통 순대국 맛을 유지하면서 깨끗한 곳 찾아줘",
        "친구들과 청첩장 모임하기 좋은 레스토랑 찾아줘",
        "1인당 3만원 이하로 먹을 수 있는 가성비 좋은 맛집 찾아줘",
        "전통적인 한식을 현대적으로 재해석한 맛집을 추천해주세요.",
        "마라탕 맛집 추천해줘",
        "퓨전 요리를 맛볼 수 있는 독특한 레스토랑을 추천해주세요.",
        "초밥이 먹고 싶은데 유명하고 맛있는 식당 찾아줘",
        "다양한 맥주를 즐길 수 있는 펍을 찾아주세요."

    ];

    const spinner = document.getElementById('spinner');
    const spinnerMessage = document.getElementById('spinnerMessage');
    console.log('spinner:', spinner);
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
    let messageInterval;
    
    function getRandomRecommendations(count) {
        const shuffled = recommendations.sort(() => 0.5 - Math.random());
        return shuffled.slice(0, count);
    }

    function renderRecommendationSlides() {
        const swiperWrapper = document.getElementById('swiperWrapper');
        const randomRecommendations = getRandomRecommendations(); 

        swiperWrapper.innerHTML = randomRecommendations.map(rec => `
            <div class="swiper-slide recommendation-card" role="button" tabindex="0" aria-label="추천 문장">
                <div class="item-text">${rec}</div>
            </div>
        `).join('');

        console.log("슬라이드 렌더링 완료:", swiperWrapper.innerHTML);
        
        const slides = document.querySelectorAll('.swiper-slide');
        slides.forEach(slide => {
            slide.addEventListener('click', function() {
                const searchText = slide.textContent.trim();  // 슬라이드 텍스트를 가져옴
                window.autoSearch(searchText);  // autoSearch 호출
            });
        });
    }

     // 로딩 메시지 업데이트 함수
     function updateSpinnerMessage() {
        if (spinnerMessage) {
            spinnerMessage.textContent = messages[Math.floor(Math.random() * messages.length)];
        }
    }

    // 추천 카드에 클릭 이벤트 리스너를 추가하는 함수
    function addClickListenersToCards() {
        const swiperWrapper = document.getElementById('swiperWrapper');
        const searchInput = document.getElementById('searchInput');
        const searchForm = document.getElementById('searchForm');
        const spinner = document.getElementById('spinner');
    
        // swiperWrapper에 한 번만 이벤트 리스너 추가
        swiperWrapper.addEventListener('click', (event) => {
            // 클릭된 요소가 recommendation-card인지 확인
            const card = event.target.closest('.recommendation-card');
            if (card) {
                const cardText = card.querySelector('.item-text').textContent.trim();
                searchInput.value = cardText;

                // 로딩 화면 표시
                if (spinner) {
                    spinner.style.display = 'flex';
                    updateSpinnerMessage(); // 첫 로딩 메시지 설정
                    messageInterval = setInterval(updateSpinnerMessage, 2000);
                }
    
                // 폼 유효성 검사 후 제출
                if (searchForm.reportValidity()) {
                    searchForm.submit();
                }

                // 페이지 이동 시 인터벌 정리
                window.addEventListener('unload', function() {
                    clearInterval(messageInterval);
                });
            }
        });
    }

    // 슬라이드를 렌더링한 후 초기화 작업 수행
    renderRecommendationSlides();

    // 추천 카드에 이벤트 리스너 추가 (이벤트 위임 방식, 한 번만 호출)
    addClickListenersToCards();

    // Swiper 초기화
    const swiper = new Swiper('.swiper-container', {
        loop: true,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        slidesPerView: 2,
        slidesPerGroup: 2,
        spaceBetween: 20,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
    });

    
});
