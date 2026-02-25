# Firebase 야자 통계 연동 가이드

## 📋 개요
이 가이드는 야자 통계 페이지를 Firebase Realtime Database에 연결하고 실시간 업데이트 기능을 설정하는 방법을 설명합니다.

## 🔥 Firebase 프로젝트 설정

### 1. Firebase 프로젝트 생성
1. [Firebase Console](https://console.firebase.google.com/)에 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름 입력 (예: daeshin-yaja)
4. Google Analytics 설정 (선택사항)
5. 프로젝트 생성 완료

### 2. Realtime Database 활성화
1. Firebase Console에서 왼쪽 메뉴 → "Realtime Database" 클릭
2. "데이터베이스 만들기" 클릭
3. 위치 선택 (asia-southeast1 권장)
4. 보안 규칙 선택:
   - **개발 중**: "테스트 모드에서 시작" 선택
   - **프로덕션**: "잠금 모드에서 시작" 선택 후 규칙 수정

### 3. 웹 앱 추가
1. Firebase Console → 프로젝트 설정 (⚙️ 아이콘)
2. "일반" 탭 → "내 앱" 섹션
3. 웹 앱 추가 (</> 아이콘)
4. 앱 닉네임 입력 (예: yaja-statistics)
5. Firebase SDK 설정 코드 복사

## 🔧 프로젝트 설정

### 1. Firebase 설정 업데이트
`src/scripts/firebase-config.js` 파일을 열어 Firebase Console에서 받은 설정으로 업데이트:

```javascript
const firebaseConfig = {
    apiKey: "실제_API_키",
    authDomain: "프로젝트ID.firebaseapp.com",
    databaseURL: "https://프로젝트ID-default-rtdb.firebaseio.com",
    projectId: "프로젝트ID",
    storageBucket: "프로젝트ID.appspot.com",
    messagingSenderId: "메시징_센더_ID",
    appId: "앱_ID"
};
```

### 2. 데이터베이스 구조
Firebase Realtime Database의 데이터 구조:

```json
{
  "yaja_students": {
    "uniqueId1": {
      "date": "2024-03-15",
      "period": 1,
      "student_name": "홍길동",
      "student_code": "10101",
      "student_number": "1",
      "reason": "병원",
      "created_at": "2024-03-15T09:00:00Z"
    },
    "uniqueId2": {
      "date": "2024-03-15",
      "period": 2,
      "student_name": "김철수",
      "student_code": "10102",
      "student_number": "2",
      "reason": "학원",
      "created_at": "2024-03-15T10:00:00Z"
    }
  }
}
```

### 3. 보안 규칙 설정
Firebase Console → Realtime Database → "규칙" 탭:

**개발 환경 (모든 접근 허용):**
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

**프로덕션 환경 (읽기만 허용, 쓰기는 인증 필요):**
```json
{
  "rules": {
    "yaja_students": {
      ".read": true,
      ".write": "auth != null"
    }
  }
}
```

## 📊 새로운 통계 기능

### 1. 주별 통계
- 각 학생이 주당 평균 몇 번 빠졌는지 계산
- ISO 8601 주차 기준으로 집계

### 2. 월별 통계
- 각 학생이 월당 평균 몇 번 빠졌는지 계산
- YYYY-MM 형식으로 집계

### 3. 사유별 상세 통계
- 각 학생의 사유별 불참 횟수 표시
- 가장 많이 사용한 사유 강조 표시

### 4. 실시간 업데이트
- Firebase의 `onValue` 리스너로 데이터 변경 감지
- 데이터 추가/수정/삭제 시 자동으로 통계 갱신

## 🚀 사용 방법

### 1. 기존 데이터 마이그레이션 (선택사항)
기존 Supabase 또는 SQLite 데이터를 Firebase로 이전하려면:

```python
# migration_to_firebase.py
import firebase_admin
from firebase_admin import credentials, db
import sqlite3

# Firebase 초기화
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://프로젝트ID-default-rtdb.firebaseio.com'
})

# SQLite에서 데이터 읽기
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM yaja_students')
rows = cursor.fetchall()

# Firebase에 데이터 쓰기
ref = db.reference('yaja_students')
for row in rows:
    ref.push({
        'date': row[1],
        'period': row[2],
        'student_name': row[3],
        'student_code': row[4],
        'student_number': row[5],
        'reason': row[6],
        'created_at': row[7]
    })

conn.close()
print('마이그레이션 완료!')
```

### 2. 페이지 접속
1. `src/pages/yaja_statistics.html` 페이지 열기
2. 날짜 범위 선택 (이번 주, 지난 주, 지난 달 등)
3. "통계 조회" 버튼 클릭

### 3. 실시간 업데이트 확인
- Firebase Console에서 데이터 추가/수정
- 페이지에서 자동으로 통계가 업데이트되는지 확인

## 📈 표시되는 통계 정보

### 요약 카드
1. **총 불참 횟수**: 전체 기간 동안의 총 불참 횟수
2. **일평균 불참**: 하루 평균 불참 학생 수
3. **불참 학생 수**: 중복 제외 학생 수
4. **가장 많은 사유**: 가장 많이 사용된 불참 사유
5. **주평균 불참**: 주당 평균 불참 횟수 (NEW!)
6. **월평균 불참**: 월당 평균 불참 횟수 (NEW!)

### 차트
1. **일별 불참 현황**: 날짜별 불참 학생 수 라인 차트
2. **차시별 불참 현황**: 1/2/3차시별 막대 차트
3. **사유별 불참 현황**: 사유별 비율 도넛 차트

### 학생별 상세 테이블
각 학생별로:
- 총 불참 횟수
- 주별 평균 불참 (NEW!)
- 월별 평균 불참 (NEW!)
- 주요 사유 (가장 많이 사용한 사유)
- 사유별 상세 (모든 사유와 횟수) (NEW!)
- 차시별 불참 횟수 (1/2/3차시)

## 🔍 트러블슈팅

### Firebase 연결 실패
**증상**: 콘솔에 "Firebase에 연결되지 않았습니다" 메시지
**해결**:
1. `firebase-config.js`의 설정 확인
2. Firebase Console에서 databaseURL 확인
3. 네트워크 연결 확인

### 데이터가 로드되지 않음
**증상**: "데이터를 불러오는 중..." 메시지가 계속 표시
**해결**:
1. Firebase Console → Realtime Database에 데이터가 있는지 확인
2. 보안 규칙에서 읽기 권한 확인
3. 브라우저 콘솔에서 에러 메시지 확인

### 실시간 업데이트가 작동하지 않음
**증상**: Firebase에서 데이터 변경해도 페이지가 업데이트되지 않음
**해결**:
1. 브라우저 콘솔에서 "🔄 Firebase 데이터 업데이트 감지" 메시지 확인
2. 페이지 새로고침 후 재시도
3. Firebase 연결 상태 확인

## 💡 추가 기능 제안

### 1. 알림 시스템
특정 학생이 일정 횟수 이상 불참하면 알림:
```javascript
function checkAbsenceThreshold(studentDetails) {
    Object.entries(studentDetails).forEach(([name, details]) => {
        if (details.total >= 5) {
            console.warn(`⚠️ ${name} 학생이 ${details.total}회 불참했습니다.`);
        }
    });
}
```

### 2. 데이터 내보내기
통계를 CSV 파일로 내보내기:
```javascript
function exportToCSV() {
    const csv = Object.entries(currentStats.student_details)
        .map(([name, details]) => 
            `${name},${details.total},${getTopReason(details.reasons)}`
        )
        .join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'yaja_statistics.csv';
    a.click();
}
```

### 3. 필터링 기능
특정 사유나 차시만 필터링하여 통계 보기

## 📝 참고 자료
- [Firebase Realtime Database 문서](https://firebase.google.com/docs/database)
- [Firebase 보안 규칙](https://firebase.google.com/docs/database/security)
- [Chart.js 문서](https://www.chartjs.org/docs/latest/)

## 🆘 지원
문제가 발생하면 Firebase Console의 로그를 확인하거나 브라우저 개발자 도구의 콘솔 메시지를 참고하세요.
