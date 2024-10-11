const recommendations = [
    "어머니 생신이라서 많은 사람들이 한번에 들어갈 수 있는 고급스럽고 살짝 어른스러운 맛집 추천해줘",
    "남친이랑 1주년 기념으로 데이트하기 좋은 분위기 좋은 맛집 찾아줘",
    "신입사원이 들어와서 술을 파는 곳 중에 첫 회식하기 좋은 고급스러운 중식당 찾아줘",
    "친구들이랑 갈건데 1인당 3만원 이하로 먹을 수 있을만한 가성비 좋은 맛집 찾아줘",
    "노키즈존이라서 어른들과 아이들이 모두 갈 수 있을만한 분위기 좋은 카페 찾아줘 ",
    "분위기 좋은 카페 추천해줘",
    "짜장면 맛집 추천해줘",
    "마라탕 맛집 추천해줘",
    "고깃집 추천해줘",
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