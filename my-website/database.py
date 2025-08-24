try:
    from supabase import create_client, Client
except ImportError:
    try:
        from supabase_py import create_client, Client
    except ImportError:
        print("Warning: Supabase module not found. Using SQLite fallback.")
        create_client = None
        Client = None

from config import Config
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        if create_client is None:
            logger.warning("Supabase module not available. Using SQLite fallback.")
            self.supabase = None
            return
            
        try:
            self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            logger.info("Supabase 연결 성공")
        except Exception as e:
            logger.error(f"Supabase 연결 실패: {e}")
            self.supabase = None
    
    def is_connected(self):
        return self.supabase is not None
    
    def create_tables(self):
        """필요한 테이블들을 생성합니다."""
        if not self.is_connected():
            logger.error("Supabase에 연결되지 않았습니다.")
            return False
        
        try:
            # 야자 학생 테이블 생성
            self.supabase.table('yaja_students').select('*').limit(1).execute()
            logger.info("yaja_students 테이블 확인됨")
            
            # 학특사 테이블 생성
            self.supabase.table('hagteugsa').select('*').limit(1).execute()
            logger.info("hagteugsa 테이블 확인됨")
            
            # 수행평가 테이블 생성
            self.supabase.table('suhang').select('*').limit(1).execute()
            logger.info("suhang 테이블 확인됨")
            
            return True
        except Exception as e:
            logger.error(f"테이블 생성 실패: {e}")
            return False
    
    # 야자 관리 함수들
    def add_yaja_student(self, date, periods, student_name, student_code, student_number, reason):
        """야자 학생을 추가합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            # 각 차시별로 데이터 삽입
            for period in periods:
                data = {
                    'date': date,
                    'period': period,
                    'student_name': student_name,
                    'student_code': student_code,
                    'student_number': student_number,
                    'reason': reason
                }
                self.supabase.table('yaja_students').insert(data).execute()
            
            return {'success': True}
        except Exception as e:
            logger.error(f"야자 학생 추가 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    def get_yaja_students(self, date):
        """특정 날짜의 야자 학생 목록을 조회합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            response = self.supabase.table('yaja_students')\
                .select('*')\
                .eq('date', date)\
                .order('period')\
                .order('student_name')\
                .execute()
            
            # 차시별로 정리
            students = {1: [], 2: [], 3: []}
            for row in response.data:
                student_data = {
                    'id': row['id'],
                    'name': row['student_name'],
                    'code': row['student_code'],
                    'studentNumber': row['student_number'],
                    'reason': row['reason']
                }
                students[row['period']].append(student_data)
            
            return {'success': True, 'data': students}
        except Exception as e:
            logger.error(f"야자 학생 조회 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    def delete_yaja_student(self, student_id):
        """야자 학생을 삭제합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            response = self.supabase.table('yaja_students')\
                .delete()\
                .eq('id', student_id)\
                .execute()
            
            if not response.data:
                return {'success': False, 'msg': '해당 학생을 찾을 수 없습니다.'}
            
            return {'success': True}
        except Exception as e:
            logger.error(f"야자 학생 삭제 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    def get_yaja_statistics(self, start_date=None, end_date=None):
        """야자 통계를 조회합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            query = self.supabase.table('yaja_students').select('*')
            
            if start_date:
                query = query.gte('date', start_date)
            if end_date:
                query = query.lte('date', end_date)
            
            response = query.execute()
            
            # 통계 데이터 처리
            stats = {
                'total_absences': len(response.data),
                'daily_stats': {},
                'weekly_stats': {},
                'reason_stats': {},
                'student_stats': {},
                'period_stats': {1: 0, 2: 0, 3: 0}
            }
            
            for row in response.data:
                date = row['date']
                period = row['period']
                reason = row['reason']
                student_name = row['student_name']
                
                # 일별 통계
                if date not in stats['daily_stats']:
                    stats['daily_stats'][date] = 0
                stats['daily_stats'][date] += 1
                
                # 차시별 통계
                stats['period_stats'][period] += 1
                
                # 사유별 통계
                if reason not in stats['reason_stats']:
                    stats['reason_stats'][reason] = 0
                stats['reason_stats'][reason] += 1
                
                # 학생별 통계
                if student_name not in stats['student_stats']:
                    stats['student_stats'][student_name] = 0
                stats['student_stats'][student_name] += 1
            
            return {'success': True, 'data': stats}
        except Exception as e:
            logger.error(f"야자 통계 조회 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    # 학급특색사업 함수들
    def create_hagteugsa(self, title, description, max_members, creator_name, creator_code):
        """학급특색사업을 생성합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            # 학특사 생성
            response = self.supabase.table('hagteugsa').insert({
                'title': title,
                'description': description,
                'max_members': max_members,
                'creator_name': creator_name,
                'creator_code': creator_code
            }).execute()
            
            if not response.data:
                return {'success': False, 'msg': '학특사 생성 실패'}
            
            hagteugsa_id = response.data[0]['id']
            
            # 생성자를 첫 번째 멤버로 추가
            self.supabase.table('hagteugsa_members').insert({
                'hagteugsa_id': hagteugsa_id,
                'member_name': creator_name,
                'member_code': creator_code
            }).execute()
            
            return {'success': True, 'id': hagteugsa_id}
        except Exception as e:
            logger.error(f"학특사 생성 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    def get_hagteugsa_list(self):
        """학급특색사업 목록을 조회합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            # 학특사 목록과 각각의 멤버 수 조회
            response = self.supabase.table('hagteugsa')\
                .select('*, hagteugsa_members!inner(member_name)')\
                .order('created_at', desc=True)\
                .execute()
            
            hagteugsa_list = []
            for row in response.data:
                # 각 학특사의 멤버 목록 조회
                members_response = self.supabase.table('hagteugsa_members')\
                    .select('member_name')\
                    .eq('hagteugsa_id', row['id'])\
                    .order('joined_at')\
                    .execute()
                
                members = [member['member_name'] for member in members_response.data]
                
                hagteugsa_list.append({
                    'id': row['id'],
                    'title': row['title'],
                    'description': row['description'],
                    'max_members': row['max_members'],
                    'creator_name': row['creator_name'],
                    'current_members': len(members),
                    'members': members
                })
            
            return {'success': True, 'data': hagteugsa_list}
        except Exception as e:
            logger.error(f"학특사 목록 조회 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    def join_hagteugsa(self, hagteugsa_id, member_name, member_code):
        """학급특색사업에 참여합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            # 학특사 정보 조회
            hagteugsa_response = self.supabase.table('hagteugsa')\
                .select('max_members')\
                .eq('id', hagteugsa_id)\
                .execute()
            
            if not hagteugsa_response.data:
                return {'success': False, 'msg': '존재하지 않는 학특사입니다.'}
            
            # 현재 참여자 수 확인
            members_response = self.supabase.table('hagteugsa_members')\
                .select('*', count='exact')\
                .eq('hagteugsa_id', hagteugsa_id)
            
            current_count = len(members_response.execute().data)
            
            if current_count >= hagteugsa_response.data[0]['max_members']:
                return {'success': False, 'msg': '모집이 마감되었습니다!'}
            
            # 이미 참여했는지 확인
            existing_response = self.supabase.table('hagteugsa_members')\
                .select('id')\
                .eq('hagteugsa_id', hagteugsa_id)\
                .eq('member_name', member_name)\
                .execute()
            
            if existing_response.data:
                return {'success': False, 'msg': '이미 참여하셨습니다!'}
            
            # 참여자 추가
            self.supabase.table('hagteugsa_members').insert({
                'hagteugsa_id': hagteugsa_id,
                'member_name': member_name,
                'member_code': member_code
            }).execute()
            
            return {'success': True}
        except Exception as e:
            logger.error(f"학특사 참여 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    def delete_hagteugsa(self, hagteugsa_id):
        """학급특색사업을 삭제합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            # 멤버 먼저 삭제
            self.supabase.table('hagteugsa_members')\
                .delete()\
                .eq('hagteugsa_id', hagteugsa_id)\
                .execute()
            
            # 학특사 삭제
            response = self.supabase.table('hagteugsa')\
                .delete()\
                .eq('id', hagteugsa_id)\
                .execute()
            
            if not response.data:
                return {'success': False, 'msg': '해당 학특사를 찾을 수 없습니다.'}
            
            return {'success': True}
        except Exception as e:
            logger.error(f"학특사 삭제 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    # 수행평가 함수들
    def add_suhang(self, subject, title, deadline, description, creator_name, creator_code):
        """수행평가를 추가합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            response = self.supabase.table('suhang').insert({
                'subject': subject,
                'title': title,
                'deadline': deadline,
                'description': description,
                'creator_name': creator_name,
                'creator_code': creator_code
            }).execute()
            
            if not response.data:
                return {'success': False, 'msg': '수행평가 추가 실패'}
            
            return {'success': True, 'msg': '수행평가가 성공적으로 추가되었습니다.'}
        except Exception as e:
            logger.error(f"수행평가 추가 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    def get_suhang_list(self):
        """수행평가 목록을 조회합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            response = self.supabase.table('suhang')\
                .select('*')\
                .order('deadline', asc=True)\
                .execute()
            
            suhang_list = []
            for row in response.data:
                suhang_list.append({
                    'id': row['id'],
                    'subject': row['subject'],
                    'title': row['title'],
                    'deadline': row['deadline'],
                    'description': row['description'],
                    'creator_name': row['creator_name'],
                    'creator_code': row['creator_code'],
                    'created_at': row['created_at']
                })
            
            return {'success': True, 'data': suhang_list}
        except Exception as e:
            logger.error(f"수행평가 목록 조회 실패: {e}")
            return {'success': False, 'msg': str(e)}
    
    def delete_suhang(self, suhang_id):
        """수행평가를 삭제합니다."""
        if not self.is_connected():
            return {'success': False, 'msg': '데이터베이스 연결 실패'}
        
        try:
            response = self.supabase.table('suhang')\
                .delete()\
                .eq('id', suhang_id)\
                .execute()
            
            if not response.data:
                return {'success': False, 'msg': '해당 수행평가를 찾을 수 없습니다.'}
            
            return {'success': True, 'msg': '수행평가가 성공적으로 삭제되었습니다.'}
        except Exception as e:
            logger.error(f"수행평가 삭제 실패: {e}")
            return {'success': False, 'msg': str(e)}

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()
