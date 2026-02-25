// Firebase 설정 파일
// 보안을 위해 환경 변수나 별도 설정 파일 사용 권장

// 방법 1: 환경 변수 사용 (프로덕션 권장)
const firebaseConfig = {
    apiKey: window.FIREBASE_CONFIG?.apiKey || "AIzaSyB1KuFpZXadilPAP8gX2JX5Ltyn_H9TLgE",
    authDomain: window.FIREBASE_CONFIG?.authDomain || "studio-1147259802-cf97a.firebaseapp.com",
    databaseURL: window.FIREBASE_CONFIG?.databaseURL || "https://studio-1147259802-cf97a-default-rtdb.firebaseio.com",
    projectId: window.FIREBASE_CONFIG?.projectId || "studio-1147259802-cf97a",
    storageBucket: window.FIREBASE_CONFIG?.storageBucket || "studio-1147259802-cf97a.firebasestorage.app",
    messagingSenderId: window.FIREBASE_CONFIG?.messagingSenderId || "460329655700",
    appId: window.FIREBASE_CONFIG?.appId || "1:460329655700:web:0b7744b022640314d50381"
};

// Firebase 초기화
if (typeof firebase !== 'undefined') {
    firebase.initializeApp(firebaseConfig);
} else {
    console.error('Firebase SDK가 로드되지 않았습니다.');
}

// Realtime Database 참조
const database = firebase.database();

// 야자 데이터베이스 참조
const yajaRef = database.ref('yaja_students');

// Firebase 연결 상태 모니터링
const connectedRef = database.ref('.info/connected');
connectedRef.on('value', (snap) => {
    if (snap.val() === true) {
        console.log('🔗 Firebase에 연결되었습니다.');
    } else {
        console.log('❌ Firebase 연결이 끊어졌습니다.');
    }
});
