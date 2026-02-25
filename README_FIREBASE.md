# 🔥 Firebase 야자 통계 시스템

## 🎯 주요 기능

### ✨ 새로운 기능
- ✅ **실시간 데이터 동기화** - Firebase Realtime Database 연동
- ✅ **주별/월별 통계** - 학생별 주당/월당 평균 불참 횟수
- ✅ **사유별 상세 분석** - 각 학생의 사유별 불참 통계
- ✅ **자동 업데이트** - 데이터 변경 시 페이지 자동 갱신
- ✅ **향상된 UI** - 더 많은 정보를 한눈에

## 🚀 5분 안에 시작하기

### 1. Firebase 프로젝트 만들기
```
1. https://console.firebase.google.com 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름 입력
4. Realtime Database 활성화
```

### 2. 웹 앱 설정 복사
```
1. 프로젝트 설정 (⚙️) → 일반
2. "내 앱" 섹션에서 웹 앱 (</>) 추가
3. SDK 설정 코드 복사
```

### 3. 설정 파일 수정
`my-website/src/scripts/firebase-config.js` 파일을 열어서:

```javascript
const firebaseConfig = {
    apiKey: "여기에_붙여넣기",
    authDomain: "여기에_붙여넣기",
    databaseURL: "여기에_붙여넣기",
    projectId: "여기에_붙여넣기",
    storageBucket: "여기에_붙여넣기",
    messagingSenderId: "여기에_붙여넣기",
    appId: "여기에_붙여넣기"
};
```

### 4. 보안 규칙 설정
Firebase Console → Realtime Database → 규칙:

```json
{
  "rules": {
    "yaja_students": {
      ".read": true,
      ".write": true
    }
  }
}
```

### 5. 테스트!
```
1. my-website/src/pages/firebase_test.html 열기
2. "샘플 데이터 추가" 버튼 클릭
3. "통계 페이지 열기" 버튼 클릭
4. 실시간으로 통계 확인!
```

## 📊 새로 추가된 통계

### 전체 통계 카드
- 📊 총 불참 횟수
- 📈 일평균 불참
- 👥 불참 학생 수
- 🎯 가장 많은 사유
- **📅 주평균 불참** ← NEW!
- **📆 월평균 불참** ← NEW!

### 학생별 상세 정보
- 학생명
- 총 불참 횟수
- **주별 평균** ← NEW!
- **월별 평균** ← NEW!
- 주요 사유
- **사유별 상세** ← NEW!
- 1/2/3차시별 불참

## 📁 파일 구조

```
my-website/
├── src/
│   ├── pages/
│   │   ├── yaja_statistics.html    ← 메인 통계 페이지 (업데이트됨)
│   │   └── firebase_test.html      ← 테스트 페이지 (새로 생성)
│   └── scripts/
│       └── firebase-config.js      ← Firebase 설정 (새로 생성)
├── firebase_migration.py           ← 데이터 마이그레이션 도구
└── requirements.txt                ← Python 패키지 (firebase-admin 추가)
```

## 🔧 데이터 마이그레이션 (선택사항)

기존 SQLite/Supabase 데이터를 Firebase로 옮기려면:

### 설치
```bash
pip install firebase-admin
```

### 서비스 계정 키 다운로드
```
1. Firebase Console → 프로젝트 설정 → 서비스 계정
2. "새 비공개 키 생성" 클릭
3. JSON 파일 다운로드
```

### 마이그레이션 실행
```bash
python firebase_migration.py
```

## 💻 사용 예시

### 기본 사용
```javascript
// 페이지 로드 시 자동으로:
// 1. Firebase 연결
// 2. 실시간 리스너 설정
// 3. 데이터 로드 및 통계 계산
// 4. 차트 표시
```

### 실시간 업데이트
```javascript
// Firebase에서 데이터 변경되면:
yajaRef.on('value', (snapshot) => {
    // 자동으로 통계 재계산
    loadStatistics();
});
```

### 주별/월별 통계
```javascript
// ISO 8601 주차 기준
const weekKey = getWeekKey('2024-12-03');
// -> "2024-12-02" (그 주 월요일)

// 월별 집계
const monthKey = date.substring(0, 7);
// -> "2024-12"
```

## 📈 통계 계산 방법

### 주별 평균
```
학생별 주당 평균 = 해당 기간의 총 불참 / 주 수

예시:
- 2주 동안 6번 불참 = 3.0 (주당 평균)
- 3주 동안 5번 불참 = 1.67 (주당 평균)
```

### 월별 평균
```
학생별 월당 평균 = 해당 기간의 총 불참 / 월 수

예시:
- 2개월 동안 24번 불참 = 12.0 (월당 평균)
- 1개월 동안 8번 불참 = 8.0 (월당 평균)
```

## 🎨 UI 개선 사항

### Before (기존)
```
[학생명] [주요사유] [사유전체] [총횟수] [1차시] [2차시] [3차시]
```

### After (개선)
```
[학생명] [총불참] [주평균] [월평균] [주요사유] [사유별상세] [1차시] [2차시] [3차시]
```

## 🔍 문제 해결

### Q: Firebase 연결이 안돼요
A: 
1. firebase-config.js의 설정 확인
2. Firebase Console에서 Realtime Database 활성화 확인
3. 브라우저 콘솔(F12)에서 에러 메시지 확인

### Q: 데이터가 안 보여요
A:
1. Firebase Console → Realtime Database에 데이터 있는지 확인
2. 보안 규칙에서 .read가 true인지 확인
3. firebase_test.html에서 샘플 데이터 추가해보기

### Q: 실시간 업데이트가 안돼요
A:
1. 페이지 새로고침
2. 콘솔에 "🔄 Firebase 데이터 업데이트 감지" 메시지 확인
3. Firebase Console에서 직접 데이터 추가/수정해보기

## 📚 추가 문서

- **FIREBASE_QUICK_START.md** - 빠른 시작 가이드 (5분)
- **FIREBASE_YAJA_SETUP.md** - 상세 설정 가이드
- **CHANGES.md** - 변경 사항 전체 목록

## 🌟 주요 장점

### 1. 실시간 동기화
- 여러 브라우저에서 동시에 열어도 자동 동기화
- 데이터 추가/수정 즉시 반영

### 2. 무료 사용
- Firebase 무료 플랜으로 충분
- 동시 연결 100개까지 무료
- 다운로드 10GB/월 무료

### 3. 확장 가능
- 서버 없이 실시간 데이터베이스
- 모바일 앱 연동 가능
- 인증 시스템 추가 가능

### 4. 안정성
- Google 인프라 사용
- 자동 백업
- 99.95% 가동률

## 🎯 다음 단계

1. **알림 시스템** - 특정 학생 임계값 알림
2. **데이터 내보내기** - CSV/Excel 다운로드
3. **모바일 앱** - React Native/Flutter
4. **권한 관리** - Firebase Authentication
5. **예측 분석** - 트렌드 분석 및 예측

## 📞 지원

문제가 있으면:
1. 브라우저 개발자 도구(F12) 확인
2. Firebase Console 로그 확인
3. GitHub Issues에 문의

## 📝 라이선스

이 프로젝트는 교육 목적으로 사용됩니다.

---

**만든 날짜**: 2024-12-03  
**버전**: 2.0.0  
**상태**: ✅ 프로덕션 준비 완료

🎉 즐거운 코딩 되세요!
