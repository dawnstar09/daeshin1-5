# Supabase 설정 가이드

이 프로젝트는 야자 관리 데이터를 Supabase에 저장하여 Koyeb 배포 시에도 데이터가 유지되도록 합니다.

## 1. Supabase 프로젝트 생성

1. [Supabase](https://supabase.com)에 접속하여 계정 생성
2. 새 프로젝트 생성
3. 프로젝트 이름과 데이터베이스 비밀번호 설정
4. 지역 선택 (한국에서 사용 시 `ap-northeast-1` 추천)

## 2. 데이터베이스 테이블 생성

Supabase 대시보드에서 SQL 편집기를 열고 다음 SQL을 실행:

```sql
-- 야자 학생 테이블 생성
CREATE TABLE yaja_students (
    id BIGSERIAL PRIMARY KEY,
    date TEXT NOT NULL,
    period INTEGER NOT NULL,
    student_name TEXT NOT NULL,
    student_code TEXT NOT NULL,
    student_number TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성 (성능 향상)
CREATE INDEX idx_yaja_students_date ON yaja_students(date);
CREATE INDEX idx_yaja_students_period ON yaja_students(period);
CREATE INDEX idx_yaja_students_student_code ON yaja_students(student_code);
```

## 3. 환경 변수 설정

### Koyeb 배포 시

Koyeb 대시보드에서 환경 변수를 설정:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
FLASK_SECRET_KEY=your-secret-key-here
```

### 로컬 개발 시

프로젝트 루트에 `.env` 파일 생성:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
FLASK_SECRET_KEY=dev-secret-key-change-in-production
```

## 4. API 키 확인

Supabase 대시보드 → Settings → API에서 다음 정보 확인:

- **Project URL**: `SUPABASE_URL`에 사용
- **anon public**: `SUPABASE_KEY`에 사용

## 5. 데이터베이스 정책 설정

Supabase 대시보드 → Authentication → Policies에서 테이블 접근 권한 설정:

```sql
-- 모든 사용자가 읽기/쓰기 가능하도록 설정 (테스트용)
CREATE POLICY "Enable all access" ON yaja_students FOR ALL USING (true) WITH CHECK (true);

-- 또는 더 안전한 정책 (프로덕션용)
CREATE POLICY "Enable read access for all users" ON yaja_students FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON yaja_students FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON yaja_students FOR UPDATE USING (true);
CREATE POLICY "Enable delete for all users" ON yaja_students FOR DELETE USING (true);
```

## 6. 테스트

1. Flask 앱 실행: `python flask_app.py`
2. 야자 관리 페이지에서 학생 추가 테스트
3. 야자 통계 페이지에서 데이터 확인

## 7. 문제 해결

### 연결 실패 시
- 환경 변수가 올바르게 설정되었는지 확인
- Supabase 프로젝트가 활성 상태인지 확인
- 네트워크 방화벽 설정 확인

### 데이터 저장 실패 시
- 데이터베이스 정책 설정 확인
- 테이블 구조가 올바른지 확인
- Supabase 로그에서 오류 메시지 확인

## 8. 백업 및 마이그레이션

### 기존 SQLite 데이터를 Supabase로 마이그레이션

```python
import sqlite3
from database import db_manager

# SQLite에서 데이터 읽기
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM yaja_students')
rows = cursor.fetchall()
conn.close()

# Supabase로 데이터 이전
for row in rows:
    db_manager.add_yaja_student(
        date=row[1],
        periods=[row[2]],
        student_name=row[3],
        student_code=row[4],
        student_number=row[5],
        reason=row[6]
    )
```

## 9. 모니터링

Supabase 대시보드에서 다음 항목들을 모니터링:

- 데이터베이스 사용량
- API 호출 수
- 에러 로그
- 성능 메트릭

## 10. 비용 관리

Supabase 무료 티어 제한:
- 데이터베이스: 500MB
- API 호출: 50,000/월
- 인증: 50,000/월

프로젝트 규모에 따라 유료 플랜 고려 필요
