# 🔐 보안 설정 가이드

## ⚠️ 중요: 개인정보 보호

Firebase 설정 정보가 GitHub에 노출되지 않도록 보호하는 방법입니다.

## 🛡️ 보안 방법

### 방법 1: Local 설정 파일 사용 (권장)

1. **설정 파일 생성**:
   ```bash
   # firebase-config.local.js 파일을 생성하고 실제 설정 입력
   cp src/scripts/firebase-config.local.js src/scripts/firebase-config.local.js
   ```

2. **실제 설정 입력**:
   ```javascript
   // src/scripts/firebase-config.local.js
   window.FIREBASE_CONFIG = {
       apiKey: "실제_API_키",
       authDomain: "실제_프로젝트.firebaseapp.com",
       databaseURL: "https://실제_프로젝트-rtdb.firebaseio.com",
       projectId: "실제_프로젝트_ID",
       storageBucket: "실제_프로젝트.appspot.com",
       messagingSenderId: "실제_센더_ID",
       appId: "실제_앱_ID"
   };
   ```

3. **Git에서 제외 확인**:
   ```bash
   # .gitignore에 이미 추가되어 있음
   *.local.js
   firebase-config.local.js
   ```

### 방법 2: 환경 변수 사용 (서버 배포 시)

**Koyeb/Vercel 등에서**:
```
FIREBASE_API_KEY=실제_키
FIREBASE_AUTH_DOMAIN=실제_도메인
FIREBASE_DATABASE_URL=실제_URL
FIREBASE_PROJECT_ID=실제_ID
FIREBASE_STORAGE_BUCKET=실제_버킷
FIREBASE_MESSAGING_SENDER_ID=실제_센더
FIREBASE_APP_ID=실제_앱ID
```

**Flask에서 환경 변수 전달**:
```python
# flask_app.py
@app.route('/firebase-config.js')
def firebase_config():
    config = {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID')
    }
    js_code = f"window.FIREBASE_CONFIG = {json.dumps(config)};"
    return Response(js_code, mimetype='application/javascript')
```

### 방법 3: Firebase 보안 규칙로 제한

Firebase Console → Realtime Database → 규칙:

```json
{
  "rules": {
    "yaja_students": {
      ".read": "request.auth != null || request.headers.origin == 'https://yourdomain.com'",
      ".write": "request.auth != null"
    }
  }
}
```

## 🚨 이미 GitHub에 올라간 경우

### 1. 즉시 Firebase 키 재생성
```
1. Firebase Console → 프로젝트 설정
2. 웹 API 키 재생성
3. 새로운 키로 교체
```

### 2. Git 히스토리에서 제거
```bash
# BFG Repo-Cleaner 사용
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch src/scripts/firebase-config.js" \
  --prune-empty --tag-name-filter cat -- --all

# 강제 푸시
git push origin --force --all
```

### 3. 보안 규칙 강화
```json
{
  "rules": {
    "yaja_students": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

## ✅ 체크리스트

- [ ] `firebase-config.local.js` 파일 생성
- [ ] `.gitignore`에 `*.local.js` 추가 확인
- [ ] 실제 Firebase 설정을 local 파일에만 입력
- [ ] GitHub에 푸시하기 전 `git status`로 확인
- [ ] Firebase 보안 규칙 설정
- [ ] (선택) Firebase App Check 활성화

## 🔍 안전 확인 방법

```bash
# 커밋 전 확인
git status

# 다음 파일들이 untracked 상태여야 함:
# - firebase-config.local.js
# - serviceAccountKey.json
# - .env
```

## 📱 Firebase App Check (추가 보안)

Firebase Console → App Check:
1. reCAPTCHA v3 활성화
2. 허용된 도메인 추가
3. 앱에 App Check SDK 추가

```html
<!-- App Check SDK 추가 -->
<script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-check-compat.js"></script>

<script>
// App Check 초기화
const appCheck = firebase.appCheck();
appCheck.activate(
  'RECAPTCHA_SITE_KEY',
  true // 자동 새로고침
);
</script>
```

## 🆘 문제 발생 시

1. **키가 노출된 것 같다면**: 즉시 Firebase Console에서 키 재생성
2. **의심스러운 활동**: Firebase Console → Usage에서 확인
3. **비용 증가**: 일일 사용량 제한 설정

---

**중요**: 보안은 한 번 설정하고 끝이 아닙니다. 정기적으로 점검하세요!
