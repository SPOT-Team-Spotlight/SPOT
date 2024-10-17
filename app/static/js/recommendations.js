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
    
    function getRandomRecommendations(count) {
        const shuffled = recommendations.sort(() => 0.5 - Math.random());
        return shuffled.slice(0, count);
    }

    function renderRecommendationSlides() {
        const swiperWrapper = document.getElementById('swiperWrapper');
        const randomRecommendations = getRandomRecommendations();
    
        swiperWrapper.innerHTML = randomRecommendations.map(rec => `
            <div class="swiper-slide" role="button" tabindex="0" aria-label="추천 문장">
            <div class="item-text">${rec}</div></div>
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

    // Render slides before Swiper initialization
    renderRecommendationSlides();
            const swiper = new Swiper('.swiper-container', {
            
            loop: true,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            slidesPerView: 2,
            spaceBetween: 20,
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
           
        });
    });
    

