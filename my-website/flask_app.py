import os
import sqlite3
import pandas as pd
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from database import db_manager
from config import Config

_root_dir = os.path.dirname(os.path.abspath(__file__))
_static_folder = os.path.join(_root_dir, 'src')

app = Flask(__name__, static_folder=_static_folder, static_url_path='')
app.config.from_object(Config)

# DB 초기화 함수 (SQLite용 - 기존 호환성 유지)
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        password TEXT NOT NULL
    )''')
    
    # 야자 관리 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS yaja_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        period INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        student_code TEXT NOT NULL,
        student_number TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 학특사 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS hagteugsa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        max_members INTEGER NOT NULL,
        creator_name TEXT NOT NULL,
        creator_code TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 학특사 참여자 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS hagteugsa_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hagteugsa_id INTEGER NOT NULL,
        member_name TEXT NOT NULL,
        member_code TEXT NOT NULL,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hagteugsa_id) REFERENCES hagteugsa (id) ON DELETE CASCADE
    )''')
    
    # 수행평가 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS suhang (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        title TEXT NOT NULL,
        deadline TEXT NOT NULL,
        description TEXT NOT NULL,
        creator_name TEXT NOT NULL,
        creator_code TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

init_db()

# 회원가입 API
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    user_id = data.get('id')
    name = data.get('name')
    pw = data.get('password')
    if not user_id or not name or not pw:
        return {'success': False, 'msg': '모든 항목을 입력하세요.'}, 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE id=?', (user_id,))
    if c.fetchone():
        conn.close()
        return {'success': False, 'msg': '이미 존재하는 아이디입니다.'}, 409
    pw_hash = generate_password_hash(pw)
    c.execute('INSERT INTO users (id, name, password) VALUES (?, ?, ?)', (user_id, name, pw_hash))
    conn.commit()
    conn.close()
    return {'success': True}

# 로그인 API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('id')
    pw = data.get('password')
    if not user_id or not pw:
        return {'success': False, 'msg': '모든 항목을 입력하세요.'}, 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password, name FROM users WHERE id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    if not row or not check_password_hash(row[0], pw):
        return {'success': False, 'msg': '아이디 또는 비밀번호가 올바르지 않습니다.'}, 401
    return {'success': True, 'name': row[1]}

# 야자 학생 추가 API (Supabase 우선, 실패 시 SQLite)
@app.route('/api/yaja/add', methods=['POST'])
def add_yaja_student():
    try:
        data = request.json
        date = data.get('date')
        periods = data.get('periods')  # 배열
        student_name = data.get('student_name')
        student_code = data.get('student_code')
        student_number = data.get('student_number')
        reason = data.get('reason')
        
        if not all([date, periods, student_name, student_code, student_number, reason]):
            return {'success': False, 'msg': '모든 필드를 입력하세요.'}, 400
        
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.add_yaja_student(date, periods, student_name, student_code, student_number, reason)
            if result['success']:
                return result
        
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # 각 차시별로 데이터 삽입
        for period in periods:
            c.execute('''INSERT INTO yaja_students 
                         (date, period, student_name, student_code, student_number, reason)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (date, period, student_name, student_code, student_number, reason))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    except Exception as e:
        return {'success': False, 'msg': str(e)}, 500

# 야자 학생 목록 조회 API (Supabase 우선, 실패 시 SQLite)
@app.route('/api/yaja/list/<date>')
def get_yaja_students(date):
    try:
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.get_yaja_students(date)
            if result['success']:
                return result
        
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('''SELECT id, period, student_name, student_code, student_number, reason
                     FROM yaja_students WHERE date = ? ORDER BY period, student_name''', (date,))
        
        rows = c.fetchall()
        conn.close()
        
        # 차시별로 정리
        students = {1: [], 2: [], 3: []}
        for row in rows:
            student_data = {
                'id': row[0],
                'name': row[2],
                'code': row[3],
                'studentNumber': row[4],
                'reason': row[5]
            }
            students[row[1]].append(student_data)
        
        return {'success': True, 'data': students}
    except Exception as e:
        return {'success': False, 'msg': str(e)}, 500

# 야자 학생 삭제 API (Supabase 우선, 실패 시 SQLite)
@app.route('/api/yaja/delete/<int:student_id>', methods=['DELETE'])
def delete_yaja_student(student_id):
    try:
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.delete_yaja_student(student_id)
            if result['success']:
                return result
        
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('DELETE FROM yaja_students WHERE id = ?', (student_id,))
        
        if c.rowcount == 0:
            conn.close()
            return {'success': False, 'msg': '해당 학생을 찾을 수 없습니다.'}, 404
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    except Exception as e:
        return {'success': False, 'msg': str(e)}, 500

# 야자 통계 API (새로 추가)
@app.route('/api/yaja/statistics')
def get_yaja_statistics():
    try:
        # 쿼리 파라미터에서 날짜 범위 가져오기
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.get_yaja_statistics(start_date, end_date)
            if result['success']:
                return result
        
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        query = '''SELECT date, period, reason, student_name 
                   FROM yaja_students'''
        params = []
        if start_date:
            query += ' WHERE date >= ?'
            params.append(start_date)
            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)
        elif end_date:
            query += ' WHERE date <= ?'
            params.append(end_date)
        query += ' ORDER BY date, period'
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        # 날짜+학생명 단위로 집계
        stats = {
            'total_absences': 0,  # 전체 불참(날짜+학생명) 카운트
            'daily_stats': {},    # 날짜별 불참 학생 수
            'weekly_stats': {},
            'reason_stats': {},
            'student_stats': {},  # 학생별 불참(날짜 단위) 카운트
            'period_stats': {1: 0, 2: 0, 3: 0},
            'student_details': {}
        }
        # (date, student_name) -> {'periods': set, 'reasons': [사유목록]}
        day_student_map = {}
        for row in rows:
            date = row[0]
            period = row[1]
            reason = row[2]
            student_name = row[3]
            key = (date, student_name)
            if key not in day_student_map:
                day_student_map[key] = {'periods': set(), 'reasons': []}
            day_student_map[key]['periods'].add(period)
            day_student_map[key]['reasons'].append(reason)
            # 차시별 통계(전체)
            stats['period_stats'][period] += 1
        # 날짜별 학생 집합, 학생별 날짜 집합, 사유 집계
        daily_unique_students = {}
        for (date, student_name), info in day_student_map.items():
            # 날짜별 유니크 학생
            if date not in daily_unique_students:
                daily_unique_students[date] = set()
            daily_unique_students[date].add(student_name)
            # 학생별 날짜 카운트
            if student_name not in stats['student_stats']:
                stats['student_stats'][student_name] = 0
            stats['student_stats'][student_name] += 1
            # 학생별 상세 통계
            if student_name not in stats['student_details']:
                stats['student_details'][student_name] = {
                    'total': 0,
                    'periods': {1: 0, 2: 0, 3: 0},
                    'reasons': {}
                }
            stats['student_details'][student_name]['total'] += 1
            for p in info['periods']:
                stats['student_details'][student_name]['periods'][p] += 1
            # 대표 사유(가장 많이 나온 사유)
            from collections import Counter
            reason_counter = Counter(info['reasons'])
            top_reason = reason_counter.most_common(1)[0][0] if reason_counter else '-'
            if top_reason not in stats['student_details'][student_name]['reasons']:
                stats['student_details'][student_name]['reasons'][top_reason] = 0
            stats['student_details'][student_name]['reasons'][top_reason] += 1
            # 전체 사유 통계
            for r in set(info['reasons']):
                if r not in stats['reason_stats']:
                    stats['reason_stats'][r] = 0
                stats['reason_stats'][r] += 1
        # 일별 통계(불참 학생 수)
        for date, students in daily_unique_students.items():
            stats['daily_stats'][date] = len(students)
        # 전체 불참(날짜+학생명) 카운트
        stats['total_absences'] = sum(len(students) for students in daily_unique_students.values())
        # 일평균 불참: 날짜별 유니크 학생 수의 합 / 날짜 수
        stats['daily_unique_students'] = {d: list(s) for d, s in daily_unique_students.items()}
        stats['unique_absence_sum'] = sum(len(s) for s in daily_unique_students.values())
        stats['unique_absence_avg'] = round(stats['unique_absence_sum'] / len(daily_unique_students), 2) if daily_unique_students else 0
        return {'success': True, 'data': stats}
    except Exception as e:
        return {'success': False, 'msg': str(e)}, 500

# 학특사 관련 API들

# 학특사 생성 API
@app.route('/api/hagteugsa/create', methods=['POST'])
def create_hagteugsa():
    try:
        data = request.json
        title = data.get('title')
        description = data.get('description')
        max_members = data.get('max_members')
        creator_name = data.get('creator_name')
        creator_code = data.get('creator_code')
        if not all([title, description, max_members, creator_name, creator_code]):
            return {'success': False, 'msg': '모든 필드를 입력하세요.'}, 400
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.create_hagteugsa(title, description, max_members, creator_name, creator_code)
            if result['success']:
                return result
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''INSERT INTO hagteugsa (title, description, max_members, creator_name, creator_code)
                     VALUES (?, ?, ?, ?, ?)''',
                  (title, description, max_members, creator_name, creator_code))
        hagteugsa_id = c.lastrowid
        c.execute('''INSERT INTO hagteugsa_members (hagteugsa_id, member_name, member_code)
                     VALUES (?, ?, ?)''',
                  (hagteugsa_id, creator_name, creator_code))
        conn.commit()
        conn.close()
        return {'success': True, 'id': hagteugsa_id}
    except Exception as e:
        return {'success': False, 'msg': str(e)}, 500

# 학특사 목록 조회 API
@app.route('/api/hagteugsa/list')
def get_hagteugsa_list():
    try:
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.get_hagteugsa_list()
            if result['success']:
                return result
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''SELECT h.id, h.title, h.description, h.max_members, h.creator_name,
                            COUNT(hm.id) as current_members
                     FROM hagteugsa h
                     LEFT JOIN hagteugsa_members hm ON h.id = hm.hagteugsa_id
                     GROUP BY h.id
                     ORDER BY h.created_at DESC''')
        rows = c.fetchall()
        hagteugsa_list = []
        for row in rows:
            c.execute('''SELECT member_name FROM hagteugsa_members 
                         WHERE hagteugsa_id = ? ORDER BY joined_at''', (row[0],))
            members = [member[0] for member in c.fetchall()]
            hagteugsa_list.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'max_members': row[3],
                'creator_name': row[4],
                'current_members': row[5],
                'members': members
            })
        conn.close()
        return {'success': True, 'data': hagteugsa_list}
    except Exception as e:
        return {'success': False, 'msg': str(e)}, 500

# 학특사 참여 API
@app.route('/api/hagteugsa/join', methods=['POST'])
def join_hagteugsa():
    try:
        data = request.json
        hagteugsa_id = data.get('hagteugsa_id')
        member_name = data.get('member_name')
        member_code = data.get('member_code')
        if not all([hagteugsa_id, member_name, member_code]):
            return {'success': False, 'msg': '모든 필드를 입력하세요.'}, 400
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.join_hagteugsa(hagteugsa_id, member_name, member_code)
            if result['success']:
                return result
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT max_members FROM hagteugsa WHERE id = ?', (hagteugsa_id,))
        hagteugsa = c.fetchone()
        if not hagteugsa:
            conn.close()
            return {'success': False, 'msg': '존재하지 않는 학특사입니다.'}, 404
        c.execute('SELECT COUNT(*) FROM hagteugsa_members WHERE hagteugsa_id = ?', (hagteugsa_id,))
        current_count = c.fetchone()[0]
        if current_count >= hagteugsa[0]:
            conn.close()
            return {'success': False, 'msg': '모집이 마감되었습니다!'}, 400
        c.execute('SELECT id FROM hagteugsa_members WHERE hagteugsa_id = ? AND member_name = ?', 
                  (hagteugsa_id, member_name))
        if c.fetchone():
            conn.close()
            return {'success': False, 'msg': '이미 참여하셨습니다!'}, 400
        c.execute('''INSERT INTO hagteugsa_members (hagteugsa_id, member_name, member_code)
                     VALUES (?, ?, ?)''',
                  (hagteugsa_id, member_name, member_code))
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'msg': str(e)}, 500

# 학특사 삭제 API
@app.route('/api/hagteugsa/delete/<int:hagteugsa_id>', methods=['DELETE'])
def delete_hagteugsa(hagteugsa_id):
    try:
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.delete_hagteugsa(hagteugsa_id)
            if result['success']:
                return result
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('DELETE FROM hagteugsa_members WHERE hagteugsa_id = ?', (hagteugsa_id,))
        c.execute('DELETE FROM hagteugsa WHERE id = ?', (hagteugsa_id,))
        if c.rowcount == 0:
            conn.close()
            return {'success': False, 'msg': '해당 학특사를 찾을 수 없습니다.'}, 404
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'msg': str(e)}, 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

# CSV 파일을 사용하는 fallback 함수
def fallback_csv_meal_data():
    try:
        # CSV 파일 경로
        csv_path = os.path.join(_static_folder, 'food_calender.csv')
        
        if not os.path.exists(csv_path):
            return {'success': False, 'error': 'CSV 파일을 찾을 수 없습니다.'}
        
        # CSV 파일 읽기
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # 현재 날짜를 기준으로 이번 주 월~금 계산
        today = datetime.now()
        # 이번 주 월요일 찾기 (weekday(): 월요일=0, 일요일=6)
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=4)  # 금요일까지
        
        # 날짜 형식 변환 및 필터링
        df['급식일자'] = pd.to_datetime(df['급식일자'], format='%Y%m%d')
        week_data = df[(df['급식일자'] >= week_start) & (df['급식일자'] <= week_end)]
        
        # 중식만 필터링 (식사코드 2)
        lunch_data = week_data[week_data['식사코드'] == 2].copy()
        
        # 요일별 데이터 정리
        weekdays = ['월', '화', '수', '목', '금']
        meal_list = []
        
        for i, day in enumerate(weekdays):
            day_date = week_start + timedelta(days=i)
            day_data = lunch_data[lunch_data['급식일자'].dt.date == day_date.date()]
            
            if not day_data.empty:
                row = day_data.iloc[0]
                # 메뉴 처리 (HTML 태그 제거 및 알레르기 정보 제거)
                menu_raw = str(row['요리명'])
                menu_items = []
                for item in menu_raw.replace('<br/>', '\n').split('\n'):
                    if item.strip():
                        # 괄호 안의 숫자(알레르기 정보) 제거
                        import re
                        clean_item = re.sub(r'\s*\([0-9.,\s]+\)', '', item.strip())
                        if clean_item:
                            menu_items.append(clean_item)
                
                # 칼로리 정보 처리
                calories_raw = str(row['칼로리정보']) if pd.notna(row['칼로리정보']) else ''
                if calories_raw and calories_raw != 'nan':
                    calories = calories_raw
                else:
                    calories = '칼로리 정보 없음'
                
                meal_list.append({
                    'day': day,
                    'date': day_date.strftime('%m/%d'),
                    'menu': menu_items,
                    'calories': calories,
                    'isToday': day_date.date() == today.date()
                })
            else:
                # 데이터가 없는 경우
                meal_list.append({
                    'day': day,
                    'date': day_date.strftime('%m/%d'),
                    'menu': ['급식 정보가 없습니다.'],
                    'calories': '',
                    'isToday': day_date.date() == today.date()
                })
        
        return {'success': True, 'data': meal_list}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

# 급식 데이터 처리 함수 (NEIS API 사용)
def process_meal_data():
    try:
        import requests
        from urllib.parse import quote
        
        # 나이스 API 설정 (대전대신고등학교)
        # API 키를 여기에 입력하세요 - https://open.neis.go.kr/portal/myPage/actKeyPage.do 에서 발급
        api_key = "99fa174825f445738a1daa51aa2ccefb"  # 실제 API 키로 교체 필요
        
        # API 키가 설정되지 않은 경우에만 CSV 파일 사용
        if api_key == "YOUR_API_KEY_HERE" or not api_key:
            return fallback_csv_meal_data()
            
        base_url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
        
        # 현재 날짜 기준으로 이번 주 데이터 
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        # 요일별 데이터 정리
        weekdays = ['월', '화', '수', '목', '금']
        meal_list = []
        
        for i, day in enumerate(weekdays):
            day_date = week_start + timedelta(days=i)
            
            # API 파라미터
            params = {
                'Key': api_key,
                'Type': 'json',
                'pIndex': 1,
                'pSize': 100,
                'ATPT_OFCDC_SC_CODE': 'G10',  # 대전광역시교육청
                'SD_SCHUL_CODE': '7430048',    # 대전대신고등학교
                'MLSV_YMD': day_date.strftime('%Y%m%d'),
                'MMEAL_SC_CODE': '2'  # 중식
            }
            
            try:
                response = requests.get(base_url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'mealServiceDietInfo' in data and len(data['mealServiceDietInfo']) > 1:
                        meal_info = data['mealServiceDietInfo'][1]['row'][0]
                        
                        # 메뉴 처리 (알레르기 정보 제거)
                        menu_raw = meal_info.get('DDISH_NM', '')
                        menu_items = []
                        
                        for item in menu_raw.replace('<br/>', '\n').split('\n'):
                            if item.strip():
                                import re
                                # 괄호 안의 숫자(알레르기 정보) 제거
                                clean_item = re.sub(r'\s*\([0-9.,\s]+\)', '', item.strip())
                                if clean_item:
                                    menu_items.append(clean_item)
                        
                        # 칼로리 정보
                        calories = meal_info.get('CAL_INFO', '칼로리 정보 없음')
                        
                        meal_list.append({
                            'day': day,
                            'date': day_date.strftime('%m/%d'),
                            'menu': menu_items,
                            'calories': calories,
                            'isToday': day_date.date() == today.date()
                        })
                    else:
                        # API에서 데이터를 찾을 수 없는 경우
                        meal_list.append({
                            'day': day,
                            'date': day_date.strftime('%m/%d'),
                            'menu': ['급식 정보가 없습니다.'],
                            'calories': '',
                            'isToday': day_date.date() == today.date()
                        })
                else:
                    # API 요청 실패
                    meal_list.append({
                        'day': day,
                        'date': day_date.strftime('%m/%d'),
                        'menu': ['급식 정보를 가져올 수 없습니다.'],
                        'calories': '',
                        'isToday': day_date.date() == today.date()
                    })
            except requests.RequestException:
                # 네트워크 오류
                meal_list.append({
                    'day': day,
                    'date': day_date.strftime('%m/%d'),
                    'menu': ['네트워크 오류로 급식 정보를 가져올 수 없습니다.'],
                    'calories': '',
                    'isToday': day_date.date() == today.date()
                })
        
        return {'success': True, 'data': meal_list}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

# 급식 데이터 API 엔드포인트
@app.route('/api/meal')
def get_meal_data():
    result = process_meal_data()
    return jsonify(result)

# 학특사 목록 조회 API (Supabase 우선, 실패 시 SQLite)
@app.route('/api/hagteugsa/list', methods=['GET'])
def get_suhang_list():
    try:
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.get_suhang_list()
            if result['success']:
                return jsonify(result)
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''SELECT id, subject, title, deadline, description, creator_name, creator_code, created_at 
                     FROM suhang ORDER BY deadline ASC''')
        suhang_list = []
        for row in c.fetchall():
            suhang_list.append({
                'id': row[0],
                'subject': row[1],
                'title': row[2],
                'deadline': row[3],
                'description': row[4],
                'creator_name': row[5],
                'creator_code': row[6],
                'created_at': row[7]
            })
        conn.close()
        return jsonify({
            'success': True,
            'data': suhang_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'msg': str(e)
        })

# 수행평가 추가 API
@app.route('/api/suhang/add', methods=['POST'])
def add_suhang():
    try:
        data = request.json
        subject = data.get('subject')
        title = data.get('title')
        deadline = data.get('deadline')
        description = data.get('description')
        creator_name = data.get('creator_name')
        creator_code = data.get('creator_code')
        if not all([subject, title, deadline, description, creator_name, creator_code]):
            return jsonify({
                'success': False,
                'msg': '모든 필드를 입력해주세요.'
            })
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.add_suhang(subject, title, deadline, description, creator_name, creator_code)
            if result['success']:
                return jsonify(result)
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''INSERT INTO suhang (subject, title, deadline, description, creator_name, creator_code)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (subject, title, deadline, description, creator_name, creator_code))
        conn.commit()
        conn.close()
        return jsonify({
            'success': True,
            'msg': '수행평가가 성공적으로 추가되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'msg': str(e)
        })

# 수행평가 삭제 API
@app.route('/api/suhang/delete/<int:suhang_id>', methods=['DELETE'])
def delete_suhang(suhang_id):
    try:
        # Supabase에 먼저 시도
        if db_manager.is_connected():
            result = db_manager.delete_suhang(suhang_id)
            if result['success']:
                return jsonify(result)
        # Supabase 실패 시 SQLite 사용
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        # 수행평가 존재 확인
        c.execute('SELECT creator_name, creator_code FROM suhang WHERE id = ?', (suhang_id,))
        suhang = c.fetchone()
        if not suhang:
            conn.close()
            return jsonify({
                'success': False,
                'msg': '해당 수행평가를 찾을 수 없습니다.'
            })
        # 수행평가 삭제
        c.execute('DELETE FROM suhang WHERE id = ?', (suhang_id,))
        conn.commit()
        conn.close()
        return jsonify({
            'success': True,
            'msg': '수행평가가 성공적으로 삭제되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'msg': str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)