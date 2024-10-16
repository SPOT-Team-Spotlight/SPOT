document.addEventListener("DOMContentLoaded", function() {
    const recommendations = [
        "파스타와 와인을 함께 즐길 수 있는 분위기 좋은 레스토랑을 추천해주세요. 특히 가족들과 함께 갈 만한 조용한 곳이면 좋겠어요.",
        "햄버거가 유명하고, 아이들을 위한 놀이 공간이 마련된 패밀리 레스토랑을 찾아주세요. 가능하다면 야외 좌석도 있는 곳으로 부탁드립니다.",
        "순대국을 판매하는 가게 중에서도 정통 순대국 맛을 유지하면서 청결하고 넓은 주차장이 있는 식당을 추천해 주세요.",
        "일식 요리를 제대로 맛볼 수 있는 가게를 찾고 싶어요. 특히 사시미와 스시를 제공하고, 정통 일식 다다미 방이 있는 가게를 추천해 주세요.",
        "김밥, 떡볶이, 튀김 등 다양한 분식 메뉴를 모두 맛볼 수 있는 가성비 좋은 분식집을 추천해 주세요.",
        "신선한 해산물을 즐길 수 있는 분위기 좋은 해산물 전문 식당을 추천해주세요. 특히 데이트하기에 적합한 조용한 곳이면 좋겠어요.",

"채식주의자를 위한 다양한 메뉴가 있는 건강한 레스토랑을 찾아주세요. 특히 가족 단위로 방문하기 좋은 넓은 공간이 있는 곳을 원합니다.",

"전통적인 한식을 현대적으로 재해석한 맛집을 추천해주세요. 특히 친구들과 함께 편안하게 식사할 수 있는 분위기가 중요해요.",

"베이커리와 카페를 동시에 즐길 수 있는 곳을 찾아주세요. 특히 신선한 빵과 다양한 커피 메뉴가 있는 아늑한 공간이면 좋겠습니다."
,
"스테이크가 맛있는 고급 레스토랑을 추천해주세요. 특히 특별한 기념일에 방문하기 좋은 로맨틱한 분위기의 곳을 원합니다."
,
"아이들을 위한 놀이 공간이 마련된 패밀리 레스토랑을 찾아주세요. 가능하다면 메뉴가 다양하고 저렴한 가격대인 곳이면 좋겠습니다."
,
"퓨전 요리를 맛볼 수 있는 독특한 레스토랑을 추천해주세요. 특히 인스타그램에 올리기 좋은 비주얼이 뛰어난 곳을 찾고 있어요."
,
"편안한 분위기에서 다양한 맥주를 즐길 수 있는 펍을 찾아주세요. 특히 라이브 음악이 있는 곳이면 더욱 좋겠습니다."
,
"저녁 노을을 감상할 수 있는 루프탑 레스토랑을 추천해주세요. 특히 다양한 와인 리스트가 있는 곳을 원합니다."
,
"정갈한 일본 정식과 신선한 사시미를 제공하는 일식당을 찾아주세요. 특히 조용하고 깔끔한 내부가 있는 곳이면 좋겠어요."
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
