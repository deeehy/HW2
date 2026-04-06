const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const previewArea = document.getElementById('previewArea');
const imagePreview = document.getElementById('imagePreview');
const analyzeBtn = document.getElementById('analyzeBtn');
const resetBtn = document.getElementById('resetBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const resultOverlay = document.getElementById('resultOverlay');
const ageResult = document.getElementById('ageResult');
const errorMsg = document.getElementById('errorMsg');

let currentFile = null;

// UI State Management -> 초기 상태(업로드)로 돌아가기
function showUploadState() {
    dropzone.classList.remove('hidden');
    previewArea.classList.add('hidden');
    analyzeBtn.classList.add('hidden');
    resetBtn.classList.add('hidden');
    resultOverlay.classList.add('hidden');
    errorMsg.classList.add('hidden');
    currentFile = null;
    fileInput.value = '';
}

// UI State Management -> 미리보기 상태
function showPreviewState(file, dataUrl) {
    currentFile = file;
    imagePreview.src = dataUrl;
    dropzone.classList.add('hidden');
    previewArea.classList.remove('hidden');
    analyzeBtn.classList.remove('hidden');
    resetBtn.classList.remove('hidden');
    errorMsg.classList.add('hidden');
    resultOverlay.classList.add('hidden');
    
    // 버튼 텍스트 초기화
    resetBtn.textContent = "다른 사진 선택";
}

// 에러 메시지 렌더링
function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.classList.remove('hidden');
}

// 브라우즈 버튼 클릭 시 숨겨진 input 활성화
browseBtn.addEventListener('click', (e) => {
    e.preventDefault();
    fileInput.click();
});

// 파일 다이얼로그에서 파일 선택 시 
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

// Drag & Drop 로직
dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});

// 파일 무결성 검증 및 썸네일 생성
function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showError("안타깝지만 이미지 파일(jpg, png 등)만 분석할 수 있습니다.");
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => showPreviewState(file, e.target.result);
    // 파일을 base64 포맷으로 읽어서 브라우저에 바로 렌더링하도록 함
    reader.readAsDataURL(file);
}

// 초기화 버튼 이벤트
resetBtn.addEventListener('click', showUploadState);

// 대망의 API Prediction 통신 과정
analyzeBtn.addEventListener('click', async () => {
    // 예외 처리 방어
    if (!currentFile) return;

    // 분석을 시작하면 로딩 상태 진입
    analyzeBtn.classList.add('hidden');
    resetBtn.classList.add('hidden');
    loadingOverlay.classList.remove('hidden');
    errorMsg.classList.add('hidden');

    // 파일을 FastAPI가 읽을 수 있는 Multi-part FormData로 패키징
    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        // 서버에 비동기 Request 전송
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        
        // HTTP 400, 500 등 에러 코드 시 예외를 던짐
        if (!response.ok) throw new Error(result.detail || "서버에서 예측에 실패했습니다.");

        // 성공! 결과 업데이트
        ageResult.textContent = result.predicted_age_range;
        if (result.predicted_gender) {
            document.getElementById('genderResult').textContent = result.predicted_gender.toUpperCase();
        }
        
        // 로딩 끄고 결과 뱃지 켜기 (애니메이션 발동)
        loadingOverlay.classList.add('hidden');
        resultOverlay.classList.remove('hidden');
        
        // 다시 시도 허용
        resetBtn.classList.remove('hidden'); 
        resetBtn.textContent = "다시 해보기";
        
    } catch (err) {
        // 에러 발생 시 UI 롤백 및 에러 표시
        loadingOverlay.classList.add('hidden');
        analyzeBtn.classList.remove('hidden');
        resetBtn.classList.remove('hidden');
        showError("네트워크 오류: " + err.message);
    }
});
