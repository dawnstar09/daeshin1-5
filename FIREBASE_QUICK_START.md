# 🔥 Firebase 야자 통계 빠른 시작 가이드

## 🎯 핵심 변경사항

### ✅ 완료된 작업
1. **Firebase Realtime Database 연동** - 실시간 데이터 동기화
2. **주별/월별 통계 추가** - 학생별 주당/월당 평균 불참 횟수
3. **사유별 상세 통계** - 각 학생의 사유별 불참 횟수 표시
4. **실시간 업데이트** - 데이터 변경 시 자동 갱신

## 🚀 빠른 설정 (5분)

### 1단계: Firebase 프로젝트 생성
```
1. https://console.firebase.google.com/ 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름: daeshin-yaja (원하는 이름)
4. Realtime Database 활성화
```

### 2단계: Firebase 설정 복사
```
1. Firebase Console → 프로젝트 설정 (⚙️)
2. "내 앱" → 웹 앱 추가
3. SDK 설정 코드 복사
```

### 3단계: 설정 파일 수정
`my-website/src/scripts/firebase-config.js` 열기:

```javascript
const firebaseConfig = {
    apiKey: "여기에_복사한_API_키",
    authDomain: "프로젝트ID.firebaseapp.com",
    databaseURL: "https://프로젝트ID-default-rtdb.firebaseio.com",
    projectId: "프로젝트ID",
    storageBucket: "프로젝트ID.appspot.com",
    messagingSenderId: "메시징_센더_ID",
    appId: "앱_ID"
};
```

### 4단계: 보안 규칙 설정
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

### 5단계: 완료!
`src/pages/yaja_statistics.html` 페이지를 열어서 테스트

## 📊 새로운 통계 기능

### 요약 카드에 추가된 항목
- **주평균 불참**: 주당 평균 몇 명이 빠지는지
- **월평균 불참**: 월당 평균 몇 명이 빠지는지

### 학생별 테이블에 추가된 정보
- **주별 평균**: 해당 학생이 주당 평균 몇 번 빠지는지
- **월별 평균**: 해당 학생이 월당 평균 몇 번 빠지는지
- **사유별 상세**: 모든 사유와 각 사유별 횟수 표시

## 🔄 실시간 업데이트 작동 방식

1. **페이지 로드 시**: Firebase에 자동 연결
2. **데이터 변경 감지**: Firebase에서 데이터가 추가/수정/삭제되면 자동 감지
3. **자동 갱신**: 페이지 새로고침 없이 통계 자동 업데이트
4. **연결 상태 표시**: 콘솔에 연결 상태 로그 출력

## 📝 테스트 방법

### 방법 1: Firebase Console에서 직접 추가
```
1. Firebase Console → Realtime Database
2. yaja_students 노드 클릭
3. "+" 버튼으로 데이터 추가:
   - date: "2024-12-03"
   - period: 1
   - student_name: "테스트"
   - student_code: "99999"
   - student_number: "99"
   - reason: "테스트"
   - created_at: "2024-12-03T10:00:00Z"
4. 통계 페이지에서 자동 업데이트 확인
```

### 방법 2: 마이그레이션 스크립트 사용
```bash
# firebase-admin 설치
pip install firebase-admin

# 서비스 계정 키 다운로드
# Firebase Console → 프로젝트 설정 → 서비스 계정 → 새 비공개 키 생성

# 마이그레이션 실행
python firebase_migration.py
```

## 🎨 화면 구성

### 상단 요약 (6개 카드)
```
┌─────────────┬─────────────┬─────────────┐
│ 총 불참 횟수│ 일평균 불참 │ 불참 학생 수│
├─────────────┼─────────────┼─────────────┤
│ 가장 많은   │ 주평균 불참 │ 월평균 불참 │
│   사유      │   (NEW!)    │   (NEW!)    │
└─────────────┴─────────────┴─────────────┘
```

### 차트 (3개)
1. 📊 일별 불참 현황 (라인 차트)
2. 📈 차시별 불참 현황 (막대 차트)
3. 🏷️ 사유별 불참 현황 (도넛 차트)

### 상세 테이블
```
학생명 | 총불참 | 주평균 | 월평균 | 주요사유 | 사유별상세 | 1차시 | 2차시 | 3차시
────────────────────────────────────────────────────────────────────────
홍길동 |   5    |  2.5   |  5.0   |  병원   | 병원(3)... |   2   |   2   |   1
```

## 🔧 문제 해결

### "Firebase에 연결되지 않았습니다"
```
✅ firebase-config.js 설정 확인
✅ Firebase Console에서 databaseURL 확인
✅ 인터넷 연결 확인
```

### 데이터가 안 보임
```
✅ Firebase Console에 데이터가 있는지 확인
✅ 보안 규칙에서 .read = true 확인
✅ 브라우저 콘솔(F12) 에러 메시지 확인
```

### 실시간 업데이트 안됨
```
✅ 콘솔에 "🔄 Firebase 데이터 업데이트 감지" 메시지 확인
✅ 페이지 새로고침 후 재시도
✅ Firebase 연결 상태 확인
```

## 📁 파일 구조

```
my-website/
├── src/
│   ├── pages/
│   │   └── yaja_statistics.html  ← 메인 통계 페이지 (수정됨)
│   └── scripts/
│       └── firebase-config.js    ← Firebase 설정 (새로 생성)
├── firebase_migration.py         ← 마이그레이션 스크립트 (새로 생성)
└── FIREBASE_YAJA_SETUP.md        ← 상세 가이드 (새로 생성)
```

## 💡 다음 단계 제안

1. **알림 기능**: 특정 학생이 일정 횟수 이상 불참 시 알림
2. **필터링**: 사유별, 차시별 필터링
3. **데이터 내보내기**: CSV/Excel 다운로드
4. **인증 추가**: Firebase Authentication으로 접근 제어

## 🆘 도움이 필요하면

1. 브라우저 개발자 도구 (F12) 열기
2. Console 탭에서 에러 메시지 확인
3. Firebase Console → Realtime Database → 데이터 확인
4. 보안 규칙 확인

---

**중요**: Firebase 무료 플랜은 동시 연결 100개, 다운로드 10GB/월까지 무료입니다.
학교 사용 규모로는 충분합니다! 🎉
