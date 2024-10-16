document.addEventListener("DOMContentLoaded", function() {
    // 주소를 위도와 경도로 변환하는 함수
    function getCoordinatesByAddress(address, callback) {
        const apiBaseUrl = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') 
                            ? 'http://127.0.0.1:8000' 
                            : `http://${window.location.hostname}:8000`;

        fetch(`${apiBaseUrl}/geocode?address=${encodeURIComponent(address)}`)
            .then(response => response.json())
            .then(data => {
                if (data.addresses && data.addresses.length > 0) {
                    const latitude = parseFloat(data.addresses[0].y);
                    const longitude = parseFloat(data.addresses[0].x);
                    callback(latitude, longitude);
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

    // 사용자의 현재 위치를 실시간으로 추적하는 함수
    function trackUserLocation(updateCallback) {
        if (navigator.geolocation) {
            return navigator.geolocation.watchPosition(
                (position) => {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    updateCallback(latitude, longitude);
                },
                (error) => {
                    console.error("사용자의 위치를 추적하는 데 실패했습니다.", error);
                },
                {
                    enableHighAccuracy: true,
                    maximumAge: 0,
                    timeout: 5000
                }
            );
        } else {
            console.error("Geolocation은 이 브라우저에서 지원되지 않습니다.");
            return null;
        }
    }

    // 슬라이더 관련 DOM 요소
    const sliderWrapper = document.getElementById('sliderWrapper');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    let currentIndex = 0;

    // 슬라이더 아이템 개수
    const totalItems = document.querySelectorAll('.slider-item').length;


    // 사용자 위치 저장 변수
    let userLatitude = NaN;
    let userLongitude = NaN;

    // 각 맵에 대한 정보를 저장할 객체
    const mapInfo = {};

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

            if (!mapInfo[index]) {
                const address = sliderItem.dataset.address;
                const name = sliderItem.querySelector("h2").innerText;

                console.log(`슬라이더 아이템 주소: ${address}`);

                if (!address) {
                    console.error("주소 정보가 없습니다.");
                    return;
                }

                showSpinner();

                getCoordinatesByAddress(address, (latitude, longitude) => {
                    if (!isNaN(latitude) && !isNaN(longitude)) {
                        console.log(`위도: ${latitude}, 경도: ${longitude}`);

                        const mapOptions = {
                            center: new naver.maps.LatLng(latitude, longitude),
                            zoom: 15
                        };
                        const map = new naver.maps.Map(mapElement, mapOptions);

                        const storeMarker = new naver.maps.Marker({
                            position: new naver.maps.LatLng(latitude, longitude),
                            map: map,
                            title: name
                        });

                        mapInfo[index] = { map, storeMarker, latitude, longitude };
                        //이거 지도클릭시 네이버 지도 링크로 가는건데 현재 검색된 식당의 고유ID가 없어서 그 주변 위치기반으로 이동됨.
                        naver.maps.Event.addListener(map, 'click', function() {
                            const naverMapUrl = `https://map.naver.com/v5/?c=${longitude},${latitude},15,0,0,0,dh`;
                            window.open(naverMapUrl, '_blank');
                        });

                        // // 지도 클릭 시 전체 화면으로 확대
                        // naver.maps.Event.addListener(map, 'click', function() {
                        //     openFullscreenMap(index);
                        // });

                        // updateUserLocationOnMap(index);

                        // 지도 리사이즈 처리
                        window.addEventListener('resize', () => handleMapResize(map, latitude, longitude));

                        // 가게 정보 표시 업데이트
                        updateStoreInfo(mapElement, name, address);

                        // 지도 범위 설정
                        updateMapBounds(index);
                    } else {
                        console.error("올바른 좌표를 얻지 못했습니다. 기본 위치를 사용합니다.");
                    }

                    hideSpinner();
                });
            } else {
                // 이미 렌더링된 지도의 경우, 사용자 위치만 업데이트
                updateUserLocationOnMap(index);
            }
        } else {
            console.error(`잘못된 인덱스: ${index}`);
        }
    }

    // 전체 화면 지도 열기
    function openFullscreenMap(index) {
        const fullscreenContainer = document.createElement('div');
        fullscreenContainer.style.position = 'fixed';
        fullscreenContainer.style.top = '0';
        fullscreenContainer.style.left = '0';
        fullscreenContainer.style.width = '100%';
        fullscreenContainer.style.height = '100%';
        fullscreenContainer.style.backgroundColor = 'white';
        fullscreenContainer.style.zIndex = '1000';

        const mapDiv = document.createElement('div');
        mapDiv.style.width = '100%';
        mapDiv.style.height = '100%';
        fullscreenContainer.appendChild(mapDiv);

        const closeButton = document.createElement('button');
        closeButton.textContent = '닫기';
        closeButton.style.position = 'absolute';
        closeButton.style.top = '10px';
        closeButton.style.right = '10px';
        closeButton.style.zIndex = '1001';
        fullscreenContainer.appendChild(closeButton);

        document.body.appendChild(fullscreenContainer);

        const { map, storeMarker, latitude, longitude } = mapInfo[index];
        const fullscreenMap = new naver.maps.Map(mapDiv, {
            center: map.getCenter(),
            zoom: map.getZoom()
        });

        new naver.maps.Marker({
            position: storeMarker.getPosition(),
            map: fullscreenMap,
            title: storeMarker.getTitle()
        });

        updateUserLocationOnMap(index, fullscreenMap);

        closeButton.addEventListener('click', () => {
            document.body.removeChild(fullscreenContainer);
        });
    }

    // 지도 리사이즈 처리를 담당하는 함수
    function handleMapResize(map, latitude, longitude) {
        naver.maps.Event.trigger(map, 'resize');
        map.setCenter(new naver.maps.LatLng(latitude, longitude));
    }

    // 스피너 표시 함수
    function showSpinner() {
        const spinner = document.getElementById('spinner');
        if (spinner) spinner.style.display = 'flex';
    }

    // 스피너 숨기기 함수
    function hideSpinner() {
        const spinner = document.getElementById('spinner');
        if (spinner) spinner.style.display = 'none';
    }

    // 사용자 위치 업데이트 함수
    function updateUserLocationOnMap(index, mapInstance = null) {
        const map = mapInstance || mapInfo[index].map;
        if (!map) return;

        if (!isNaN(userLatitude) && !isNaN(userLongitude)) {
            const userPosition = new naver.maps.LatLng(userLatitude, userLongitude);
            
            if (!mapInfo[index].userMarker) {
                mapInfo[index].userMarker = new naver.maps.Marker({
                    position: userPosition,
                    map: map,
                    icon: {
                        content: '<div style="width: 20px; height: 20px; background-color: blue; border-radius: 50%; border: 2px solid white;"></div>',
                        anchor: new naver.maps.Point(10, 10)
                    },
                    title: "내 위치"
                });
            } else {
                mapInfo[index].userMarker.setPosition(userPosition);
            }

            updateMapBounds(index, mapInstance);
        }
    }

    // 지도 범위 업데이트 함수
    function updateMapBounds(index, mapInstance = null) {
        const { map, storeMarker } = mapInfo[index];
        const targetMap = mapInstance || map;
        if (!targetMap || !storeMarker) return;

        const bounds = new naver.maps.LatLngBounds();
        bounds.extend(storeMarker.getPosition());
        
        if (!isNaN(userLatitude) && !isNaN(userLongitude)) {
            bounds.extend(new naver.maps.LatLng(userLatitude, userLongitude));
        }

        targetMap.fitBounds(bounds, { top: 50, right: 50, bottom: 50, left: 50 });
    }

    // 가게 정보 표시 업데이트 함수
    function updateStoreInfo(mapElement, name, address) {
        const mapContainer = mapElement.parentElement;
        let storeInfoElement = mapContainer.querySelector('.store-info');

        if(!storeInfoElement) {
            storeInfoElement = document.createElement('div');
            storeInfoElement.classList.add('store-info');
            mapElement.parentNode.insertBefore(storeInfoElement, mapElement.nextSibling);
        }

        storeInfoElement.innerHTML = `<strong>${name}</strong><br>${address}`;
    }

    // 실시간으로 사용자의 위치를 추적하고 업데이트
    const watchId = trackUserLocation((latitude, longitude) => {
        userLatitude = latitude;
        userLongitude = longitude;
        console.log(`사용자 위치 업데이트: 위도 ${userLatitude}, 경도 ${userLongitude}`);

        // 모든 렌더링된 지도에 사용자 위치 업데이트
        Object.keys(mapInfo).forEach(index => {
            updateUserLocationOnMap(parseInt(index));
        });
    });

    // 페이지 언로드 시 위치 추적 중지
    window.addEventListener('beforeunload', () => {
        if (watchId !== null) {
            navigator.geolocation.clearWatch(watchId);
        }
    });

    // 네이버 지도 API 로드 확인 및 초기화
    function initMap() {
        if (typeof naver !== 'undefined' && naver.maps) {
            console.log("네이버 지도 API가 로드됨");
            console.log("초기 지도 렌더링 중, 인덱스:", currentIndex);
            renderMap(currentIndex);
        } else {
            console.error("네이버 지도 API가 로드되지 않음");
        }
    }

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