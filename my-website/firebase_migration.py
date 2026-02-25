"""
Firebase 데이터 마이그레이션 및 동기화 스크립트
기존 Supabase/SQLite 데이터를 Firebase Realtime Database로 이전
"""

import os
import sqlite3
import json
from datetime import datetime

try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_AVAILABLE = True
except ImportError:
    print("경고: firebase-admin이 설치되지 않았습니다.")
    print("설치하려면: pip install firebase-admin")
    FIREBASE_AVAILABLE = False


class FirebaseMigration:
    def __init__(self, service_account_path, database_url):
        """
        Firebase 마이그레이션 초기화
        
        Args:
            service_account_path: Firebase 서비스 계정 키 JSON 파일 경로
            database_url: Firebase Realtime Database URL
        """
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin 패키지가 필요합니다.")
        
        try:
            # Firebase 초기화
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            print("✅ Firebase 연결 성공")
        except Exception as e:
            print(f"❌ Firebase 초기화 실패: {e}")
            raise
    
    def migrate_from_sqlite(self, db_path='users.db'):
        """
        SQLite에서 Firebase로 야자 데이터 마이그레이션
        
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        try:
            # SQLite 연결
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 야자 학생 데이터 조회
            cursor.execute('''
                SELECT id, date, period, student_name, student_code, 
                       student_number, reason, created_at 
                FROM yaja_students 
                ORDER BY created_at
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                print("⚠️ 마이그레이션할 데이터가 없습니다.")
                return
            
            # Firebase에 데이터 쓰기
            ref = db.reference('yaja_students')
            
            print(f"📊 {len(rows)}개의 레코드를 마이그레이션합니다...")
            
            migrated_count = 0
            for row in rows:
                data = {
                    'date': row[1],
                    'period': row[2],
                    'student_name': row[3],
                    'student_code': row[4],
                    'student_number': row[5],
                    'reason': row[6],
                    'created_at': row[7] if row[7] else datetime.now().isoformat()
                }
                
                # Firebase에 푸시
                ref.push(data)
                migrated_count += 1
                
                if migrated_count % 10 == 0:
                    print(f"진행 중... {migrated_count}/{len(rows)}")
            
            print(f"✅ 마이그레이션 완료! {migrated_count}개의 레코드를 이전했습니다.")
            
        except sqlite3.Error as e:
            print(f"❌ SQLite 오류: {e}")
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {e}")
    
    def migrate_from_supabase(self, supabase_url, supabase_key):
        """
        Supabase에서 Firebase로 야자 데이터 마이그레이션
        
        Args:
            supabase_url: Supabase 프로젝트 URL
            supabase_key: Supabase Anon Key
        """
        try:
            from supabase import create_client
        except ImportError:
            print("❌ supabase-py가 설치되지 않았습니다.")
            print("설치하려면: pip install supabase")
            return
        
        try:
            # Supabase 연결
            supabase = create_client(supabase_url, supabase_key)
            
            # 야자 데이터 조회
            response = supabase.table('yaja_students').select('*').execute()
            records = response.data
            
            if not records:
                print("⚠️ 마이그레이션할 데이터가 없습니다.")
                return
            
            # Firebase에 데이터 쓰기
            ref = db.reference('yaja_students')
            
            print(f"📊 {len(records)}개의 레코드를 마이그레이션합니다...")
            
            migrated_count = 0
            for record in records:
                data = {
                    'date': record['date'],
                    'period': record['period'],
                    'student_name': record['student_name'],
                    'student_code': record['student_code'],
                    'student_number': record['student_number'],
                    'reason': record['reason'],
                    'created_at': record.get('created_at', datetime.now().isoformat())
                }
                
                ref.push(data)
                migrated_count += 1
                
                if migrated_count % 10 == 0:
                    print(f"진행 중... {migrated_count}/{len(records)}")
            
            print(f"✅ 마이그레이션 완료! {migrated_count}개의 레코드를 이전했습니다.")
            
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {e}")
    
    def add_sample_data(self):
        """테스트용 샘플 데이터 추가"""
        ref = db.reference('yaja_students')
        
        sample_data = [
            {
                'date': '2024-12-02',
                'period': 1,
                'student_name': '홍길동',
                'student_code': '10101',
                'student_number': '1',
                'reason': '병원',
                'created_at': datetime.now().isoformat()
            },
            {
                'date': '2024-12-02',
                'period': 2,
                'student_name': '김철수',
                'student_code': '10102',
                'student_number': '2',
                'reason': '학원',
                'created_at': datetime.now().isoformat()
            },
            {
                'date': '2024-12-03',
                'period': 1,
                'student_name': '홍길동',
                'student_code': '10101',
                'student_number': '1',
                'reason': '병원',
                'created_at': datetime.now().isoformat()
            },
        ]
        
        for data in sample_data:
            ref.push(data)
        
        print(f"✅ {len(sample_data)}개의 샘플 데이터를 추가했습니다.")
    
    def export_to_json(self, output_file='yaja_backup.json'):
        """Firebase 데이터를 JSON 파일로 백업"""
        try:
            ref = db.reference('yaja_students')
            data = ref.get()
            
            if not data:
                print("⚠️ 백업할 데이터가 없습니다.")
                return
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 데이터를 {output_file}에 백업했습니다.")
            
        except Exception as e:
            print(f"❌ 백업 실패: {e}")
    
    def clear_all_data(self, confirm=False):
        """Firebase의 모든 야자 데이터 삭제 (주의!)"""
        if not confirm:
            print("⚠️ 경고: 모든 데이터가 삭제됩니다!")
            print("실행하려면 clear_all_data(confirm=True)를 호출하세요.")
            return
        
        try:
            ref = db.reference('yaja_students')
            ref.delete()
            print("✅ 모든 데이터를 삭제했습니다.")
        except Exception as e:
            print(f"❌ 삭제 실패: {e}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Firebase 야자 데이터 마이그레이션 도구")
    print("=" * 60)
    print()
    
    # Firebase 설정 (환경 변수 또는 직접 입력)
    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT', 
                                     'path/to/serviceAccountKey.json')
    database_url = os.getenv('FIREBASE_DATABASE_URL', 
                             'https://your-project-id-default-rtdb.firebaseio.com')
    
    print("📋 설정:")
    print(f"  - 서비스 계정 키: {service_account_path}")
    print(f"  - 데이터베이스 URL: {database_url}")
    print()
    
    if not FIREBASE_AVAILABLE:
        print("❌ firebase-admin 패키지가 설치되지 않았습니다.")
        print("설치: pip install firebase-admin")
        return
    
    if not os.path.exists(service_account_path):
        print("❌ 서비스 계정 키 파일을 찾을 수 없습니다.")
        print("Firebase Console에서 서비스 계정 키를 다운로드하세요.")
        return
    
    try:
        # 마이그레이션 객체 생성
        migration = FirebaseMigration(service_account_path, database_url)
        
        # 메뉴 표시
        while True:
            print("\n" + "=" * 60)
            print("작업 선택:")
            print("  1. SQLite에서 마이그레이션")
            print("  2. Supabase에서 마이그레이션")
            print("  3. 샘플 데이터 추가")
            print("  4. 데이터 백업 (JSON)")
            print("  5. 종료")
            print("=" * 60)
            
            choice = input("\n선택 (1-5): ").strip()
            
            if choice == '1':
                db_path = input("SQLite DB 경로 [users.db]: ").strip() or 'users.db'
                migration.migrate_from_sqlite(db_path)
            
            elif choice == '2':
                supabase_url = input("Supabase URL: ").strip()
                supabase_key = input("Supabase Key: ").strip()
                if supabase_url and supabase_key:
                    migration.migrate_from_supabase(supabase_url, supabase_key)
                else:
                    print("❌ URL과 Key를 모두 입력해주세요.")
            
            elif choice == '3':
                migration.add_sample_data()
            
            elif choice == '4':
                output_file = input("출력 파일명 [yaja_backup.json]: ").strip() or 'yaja_backup.json'
                migration.export_to_json(output_file)
            
            elif choice == '5':
                print("👋 종료합니다.")
                break
            
            else:
                print("❌ 잘못된 선택입니다.")
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == '__main__':
    main()
