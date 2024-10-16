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
    

