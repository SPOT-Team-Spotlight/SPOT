document.addEventListener("DOMContentLoaded", function() {
    // 주소를 위도와 경도로 변환하는 함수
    function getCoordinatesByAddress(address, callback) {
        fetch(`http://127.0.0.1:8000/geocode?address=${encodeURIComponent(address)}`)
            .then(response => response.json())
            .then(data => {
                if (data.addresses && data.addresses.length > 0) {
                    const latitude = parseFloat(data.addresses[0].y);
                    const longitude = parseFloat(data.addresses[0].x);
                    callback(latitude, longitude); // 콜백을 사용해 위도와 경도 전달
                } else {
                    console.error("주소를 찾을 수 없습니다.");
                    callback(NaN, NaN);
                }
            })
            .catch(error => {
                console.error("지오코딩 요청 중 오류 발생:", error);
                callback(NaN, NaN);
            });
    }
    // 슬라이더 관련 DOM 요소
    const sliderWrapper = document.getElementById('sliderWrapper');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    let currentIndex = 0;

    // 슬라이더 아이템 개수
    const totalItems = document.querySelectorAll('.slider-item').length;

    // 슬라이드 이동 함수
    function moveSlider(index) {
        const slideWidth = sliderWrapper.querySelector('.slider-item').clientWidth;
        sliderWrapper.style.transform = `translateX(${-index * slideWidth}px)`;
        renderMap(index);
    }

    // 이전 버튼 클릭
    prevBtn.addEventListener('click', function() {
        if (currentIndex > 0) {
            currentIndex--;
            moveSlider(currentIndex);
        }
    });

    // 다음 버튼 클릭
    nextBtn.addEventListener('click', function() {
        if (currentIndex < totalItems - 1) {
            currentIndex++;
            moveSlider(currentIndex);
        }
    });

    // 지도 렌더링 함수
    function renderMap(index) {

        console.log(`인덱스 ${index}에 대한 지도를 렌더링 시도 중`);

        const mapDivId = `map-${index}`;
        const mapElement = document.getElementById(mapDivId);
        const sliderItems = document.querySelectorAll('.slider-item');

        if (index >= 0 && index < sliderItems.length) {
            const sliderItem = sliderItems[index];
            
            if (!mapElement) {
                console.error(`ID가 ${mapDivId}인 지도 요소를 찾을 수 없음`);
                return;
            }
        
            if (mapElement.dataset.rendered !== "true") {
                // 지도 이미 렌더링되었는지 확인 (중복 렌더링 방지)
                mapElement.dataset.rendered = "true";
                mapElement.style.width = '100%';
                mapElement.style.height = '300px';

                const address = sliderItem.dataset.address;
                console.log(`슬라이더 아이템 주소: ${address}`);

                if (!address) {
                    console.error("주소 정보가 없습니다.");
                    return;
                }
                // 지오코딩을 통해 주소로부터 위도와 경도를 가져와 지도 렌더링
                getCoordinatesByAddress(address, (latitude, longitude) => {
                    if (!isNaN(latitude) && !isNaN(longitude)) {
                        console.log(`위도: ${latitude}, 경도: ${longitude}`);
                    
                        // 지도 API를 사용해 지도 생성
                        const mapOptions = {
                            center: new naver.maps.LatLng(latitude, longitude),
                            zoom: 14
                        };
                        const map = new naver.maps.Map(mapElement, mapOptions);

                        // 마커 추가
                        const marker = new naver.maps.Marker({
                            position: new naver.maps.LatLng(latitude, longitude),
                            map: map
                        });
                    } else {
                        console.error("올바른 좌표를 얻지 못했습니다. 기본 위치를 사용합니다.");
                        latitude = 37.4979; // 강남역의 위도
                        longitude = 127.0276; // 강남역의 경도
                    }
                });
            }
        } else {
            console.error(`잘못된 인덱스: ${index}`);
        }
    }

    function initMap() {
        if (typeof naver !== 'undefined' && naver.maps) {
            console.log("네이버 지도 API가 로드됨");
            console.log("초기 지도 렌더링 중, 인덱스:", currentIndex);
            renderMap(currentIndex);
        } else {
            console.error("네이버 지도 API가 로드되지 않음");
            // API가 로드되지 않았을 때의 처리를 여기에 추가할 수 있습니다.
            // 예: 사용자에게 오류 메시지를 표시하거나, 일정 시간 후 다시 시도하는 등
        }
    }

    // 네이버 지도 API 로드 확인 및 초기화
    function checkNaverMapsAPI() {
        if (typeof naver !== 'undefined' && naver.maps) {
            initMap();
        } else {
            setTimeout(checkNaverMapsAPI, 100);  // 100ms 후에 다시 확인
        }
    }

    // API 로드 확인 시작
    checkNaverMapsAPI();
});
