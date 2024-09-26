document.addEventListener("DOMContentLoaded", function() {
    // DOM 요소 가져오기
    const loginToggle = document.getElementById('loginToggle');
    const signupToggle = document.getElementById('signupToggle');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loggedInStatus = document.getElementById('loggedInStatus');
    const welcomeMessage = document.getElementById('welcomeMessage');
    const authButtons = document.getElementById('authButtons');
    const logoutButton = document.getElementById('logoutButton');
    const voiceSearchButton = document.getElementById('voiceSearchButton');
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');

    // 로그인 상태를 확인하는 함수
    function checkLoginStatus() {
        const token = localStorage.getItem('access_token');
        const username = localStorage.getItem('username'); // username 저장된 값 불러오기
        if (token && username) {
            // 로그인 상태 유지 - 리뷰 기능 사용 가능
            loginForm.style.display = 'none';
            signupForm.style.display = 'none';
            authButtons.style.display = 'none';
            loggedInStatus.style.display = 'block';
            welcomeMessage.textContent = `${username}님, 리뷰를 남길 수 있습니다.`; // username과 함께 메시지 표시
        } else {
            // 로그인되지 않은 상태 - 리뷰 기능 사용 불가, 검색 가능
            loginForm.style.display = 'none';
            signupForm.style.display = 'none';
            authButtons.style.display = 'block';
            loggedInStatus.style.display = 'none';
            welcomeMessage.textContent = "비회원 상태입니다. 리뷰는 남길 수 없습니다.";
        }
    }

    // 페이지 로드 시 로그인 상태 확인
    checkLoginStatus();

    // 로그인과 회원가입 폼 토글
    // 변경: if 조건문 제거. 요소가 없는 경우 에러 방지를 위해 추가되었던 것으로 보임
    loginToggle.addEventListener('click', () => {
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
    });

    signupToggle.addEventListener('click', () => {
        signupForm.style.display = 'block';
        loginForm.style.display = 'none';
    });

    // 로그아웃 처리
    // 변경: if 조건문 제거
    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('access_token');
        // 변경: checkLoginStatus 함수 호출 추가
        checkLoginStatus();
        // 변경: 직접적인 스타일 변경 대신 checkLoginStatus 함수에 의존
        alert('로그아웃되었습니다. 리뷰 기능을 사용할 수 없습니다.');
    });


    // 회원가입 처리
    // 변경: 함수 선언을 이벤트 리스너로 변경
    signupForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const username = document.getElementById('signupUsername').value;
        const password = document.getElementById('signupPassword').value;
        
        fetch('/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);  // 회원가입 성공 메시지
                signupForm.style.display = 'none';
                loginForm.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('회원가입 중 오류가 발생했습니다.');
        });
    });

    // 로그인 처리
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        fetch('/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.access_token) {
                alert('로그인 성공!');
                localStorage.setItem('access_token', data.access_token);  // JWT 토큰 저장
                localStorage.setItem('username', username);  // username 저장
                
                checkLoginStatus();
                welcomeMessage.textContent = `${username}님, 환영합니다! 리뷰를 남길 수 있습니다.`;
            } else {
                alert('로그인 실패. 아이디 또는 비밀번호를 확인하세요.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('로그인 중 오류가 발생했습니다.');
        });
    });

    // 검색 요청을 처리하는 함수
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();  // 기본 폼 동작 막기
        const searchInputValue = searchInput.value;


        // 변경: searchInput 대신 searchInputValue 사용
        if (!searchInputValue) {
            alert("검색어와 지역을 입력하세요!");
            return;
        }

        const formData = new URLSearchParams();
        // 변경: searchInput 대신 searchInputValue 사용
        formData.append('search_input', searchInputValue);

        fetch('http://127.0.0.1:8000/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok. Status: ' + response.status);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            }

            return response.text();
        })
        .then(data => {
            if (typeof data === 'string') {
                document.body.innerHTML = data;
            } else {
                console.log('JSON 응답:', data);
                // 변경: JSON 데이터 처리에 대한 주석 추가
                // JSON 데이터를 사용하여 결과를 표시하는 로직을 여기에 추가
            }
        })
        .catch(error => {
            console.error('Error during fetch:', error);
            alert('Error: ' + error.message);
        });
    });

    // 음성 인식 기능
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'ko-KR';

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            searchInput.value = transcript;
            alert(`음성 인식 결과: ${transcript}`);
        };

        recognition.onend = function() {
            console.log('음성 인식이 종료되었습니다.');
        };

        voiceSearchButton.addEventListener('click', () => {
            recognition.start();
            console.log('음성 인식이 시작되었습니다.');
        });
    } else {
        voiceSearchButton.style.display = 'none';
        console.log('음성 인식이 지원되지 않는 브라우저입니다.');
    }
});

// 추천 문장 카드 자동 검색 기능 (전역 함수)
function autoSearch(searchTerm) {
    document.getElementById('searchInput').value = searchTerm;
    document.getElementById('searchForm').dispatchEvent(new Event('submit'));
}