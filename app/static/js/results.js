document.addEventListener("DOMContentLoaded", function() {
    // 주소를 위도와 경도로 변환하는 함수
    function getCoordinatesByAddress(address, callback) {
        // 현재 호스트 주소를 감지하여 로컬 또는 IP 기반으로 설정
        const apiBaseUrl = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') 
                            ? 'http://127.0.0.1:8000' 
                            : `http://${window.location.hostname}:8000`;

        fetch(`${apiBaseUrl}/geocode?address=${encodeURIComponent(address)}`)
            .then(response => response.json())
            .then(data => {
                if (data.addresses && data.addresses.length > 0) {
                    const latitude = parseFloat(data.addresses[0].y);
                    const longitude = parseFloat(data.addresses[0].x);
                    callback(latitude, longitude); // 콜백을 사용해 위도와 경도 전달
                } else {
                    console.error("주소를 찾을 수 없습니다.");
                    data.address
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
        const sliderItem = sliderItems[index];

        if (index >= 0 && index < sliderItems.length) {
            
            if (!mapElement || !sliderItem) {
                console.error(`ID가 ${mapDivId}인 지도 요소를 찾을 수 없음`);
                return;
            }
        
            if (mapElement.dataset.rendered !== "true") {
                // 지도 이미 렌더링되었는지 확인 (중복 렌더링 방지)
                mapElement.dataset.rendered = "true";

                const address = sliderItem.dataset.address;
                const name = sliderItem.querySelector("h2").innerText;

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
                            zoom: 15
                        };
                        const map = new naver.maps.Map(mapElement, mapOptions);

                        // 마커 추가
                        const marker = new naver.maps.Marker({
                            position: new naver.maps.LatLng(latitude, longitude),
                            map: map
                        });

                         // 지도 리사이즈 처리 (모바일에서 제대로 보이도록)
                         window.addEventListener('resize', () => handleMapResize(map, latitude, longitude));

                        // 가게 이름과 주소 표시 업데이트
                        const mapContainer = mapElement.parentElement;
                        let storeInfoElement = mapContainer.querySelector('.store-info');

                        if(!storeInfoElement) {
                            // 중복 방지를 위해 기존에 추가된 요소가 있는지 확인 후, 없을 때만 추가
                            const mapInfoElement = document.createElement('div');
                            mapInfoElement.classList.add('store-info');
                            mapInfoElement.innerHTML = `<strong>${name}</strong><br>${address}`;
                            mapElement.parentNode.insertBefore(mapInfoElement, mapElement.nextSibling);
                        }
                    } else {
                        console.error("올바른 좌표를 얻지 못했습니다. 기본 위치를 사용합니다.");
                    }
                });
            }
        } else {
            console.error(`잘못된 인덱스: ${index}`);
        }
    }

    // 지도 리사이즈 처리를 담당하는 함수
    function handleMapResize(map, latitude, longitude) {
        naver.maps.Event.trigger(map, 'resize');
        map.setCenter(new naver.maps.LatLng(latitude, longitude));
    }

    function initMap() {
        if (typeof naver !== 'undefined' && naver.maps) {
            console.log("네이버 지도 API가 로드됨");
            console.log("초기 지도 렌더링 중, 인덱스:", currentIndex);
            renderMap(currentIndex);
        } else {
            console.error("네이버 지도 API가 로드되지 않음");
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
