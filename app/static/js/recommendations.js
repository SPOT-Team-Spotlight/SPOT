document.addEventListener("DOMContentLoaded", function() {
    const recommendations = [
        "파스타와 와인을 함께 즐길 수 있는 분위기 좋은 레스토랑을 추천해주세요. 특히 가족들과 함께 갈 만한 조용한 곳이면 좋겠어요.",
        "햄버거가 유명하고, 아이들을 위한 놀이 공간이 마련된 패밀리 레스토랑을 찾아주세요. 가능하다면 야외 좌석도 있는 곳으로 부탁드립니다.",
        "순대국을 판매하는 가게 중에서도 정통 순대국 맛을 유지하면서 청결하고 넓은 주차장이 있는 식당을 추천해 주세요.",
        "일식 요리를 제대로 맛볼 수 있는 가게를 찾고 싶어요. 특히 사시미와 스시를 제공하고, 정통 일식 다다미 방이 있는 가게를 추천해 주세요.",
        "김밥, 떡볶이, 튀김 등 다양한 분식 메뉴를 모두 맛볼 수 있는 가성비 좋은 분식집을 추천해 주세요."
    ];
    
    function getRandomRecommendations(count) {
        const shuffled = recommendations.sort(() => 0.5 - Math.random());
        return shuffled.slice(0, count);
    }

    function renderRecommendationSlides() {
        const swiperWrapper = document.getElementById('swiperWrapper');
        const randomRecommendations = getRandomRecommendations(8);
    
        swiperWrapper.innerHTML = randomRecommendations.map(rec => `
            <div class="swiper-slide" role="button" tabindex="0" aria-label="추천 문장">${rec}</div>
        `).join('');

        console.log("슬라이드 렌더링 완료:", swiperWrapper.innerHTML);
    }

    // Render slides before Swiper initialization
    renderRecommendationSlides();
    
    document.addEventListener("DOMContentLoaded", function() {
        const swiper = new Swiper('.swiper-container', {
            loop: true,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            slidesPerView: 1,
            spaceBetween: 20,
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
        });
    });
    
});
