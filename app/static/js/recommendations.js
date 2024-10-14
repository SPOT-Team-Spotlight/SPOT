const recommendations = [
    "파스타와 와인을 함께 즐길 수 있는 분위기 좋은 레스토랑을 추천해주세요. 특히 가족들과 함께 갈 만한 조용한 곳이면 좋겠어요.",
    "햄버거가 유명하고, 아이들을 위한 놀이 공간이 마련된 패밀리 레스토랑을 찾아주세요. 가능하다면 야외 좌석도 있는 곳으로 부탁드립니다.",
    "순대국을 판매하는 가게 중에서도 정통 순대국 맛을 유지하면서 청결하고 넓은 주차장이 있는 식당을 추천해 주세요.",
    "일식 요리를 제대로 맛볼 수 있는 가게를 찾고 싶어요. 특히 사시미와 스시를 제공하고, 정통 일식 다다미 방이 있는 가게를 추천해 주세요.",
    "김밥, 떡볶이, 튀김 등 다양한 분식 메뉴를 모두 맛볼 수 있는 가성비 좋은 분식집을 추천해 주세요. 가능한 서울 중심부에 위치해 있고 야간에도 영업하는 곳이었으면 좋겠습니다. ",
    "맛있는 파스타",
    "일식 점심",
    "돈가스",
    "김밥 저렴한 곳",
    "파스타 맛집 추천해줘",
    "썸남과 갈만한 모던한 분위기의 맛집 추천해줘",
    "강남 직장인 회식 장소로 좋은 단체석이 있는 술집 찾아줘",
    "남친이랑 1주년 기념으로 데이트하기 좋은 분위기 좋은 맛집 찾아줘",
    "친구들이랑 갈건데 1인당 3만원 이하로 먹을 수 있을만한 가성비 좋은 맛집 찾아줘",
    "야경이 예쁘고 뷰가 좋은 고급스러운 레스토랑 추천해줘"
];

function getRandomRecommendations(count) {
    const shuffled = recommendations.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

function renderRecommendationCards() {
    const cardContainer = document.getElementById('cardContainer');
    const randomRecommendations = getRandomRecommendations(4);
    
    cardContainer.innerHTML = randomRecommendations.map(rec => `
        <div class="card" onclick="autoSearch('${rec}')">
            <div class="icon"></div>
            ${rec}
        </div>
    `).join('');
}