import json
import os

def analyze_notion_data():
    files = ['notion_data_1.json', 'notion_data_2.json']
    all_pages = []
    
    for f in files:
        if os.path.exists(f):
            with open(f, 'r') as file:
                data = json.load(file)
                all_pages.extend(data.get('results', []))
    
    stats = {
        'total': len(all_pages),
        'channels': {},
        'outcomes': {},
        'steps': {
            'document': 0,
            'coding_test': 0,
            'interview_1': 0,
            'interview_2': 0,
            'final_pass': 0
        }
    }
    
    for page in all_pages:
        props = page.get('properties', {})
        
        # 지원 경로
        channels = props.get('지원 경로', {}).get('multi_select', [])
        for c in channels:
            name = c.get('name')
            stats['channels'][name] = stats['channels'].get(name, 0) + 1
        if not channels:
            stats['channels']['미기입'] = stats['channels'].get('미기입', 0) + 1
            
        # 합불 여부 및 단계 분석
        outcomes = props.get('합불 여부', {}).get('multi_select', [])
        outcome_names = [o.get('name') for o in outcomes]
        
        for name in outcome_names:
            stats['outcomes'][name] = stats['outcomes'].get(name, 0) + 1
            
        # 단계별 도달 및 탈락 분석
        # 서류 도달 (모든 지원)
        stats['steps']['document'] += 1
        
        # 1차 면접 도달 여부 확인 (1차 면접 날짜가 있거나 면접 관련 결과가 있는 경우)
        has_iv1_date = props.get('1차 면접', {}).get('date') is not None
        if has_iv1_date or any('면접' in n for n in outcome_names) or any('라이브코딩' in n for n in outcome_names):
            stats['steps']['interview_1'] += 1
            
        # 2차 면접 도달
        has_iv2_date = props.get('2차 면접', {}).get('date') is not None
        if has_iv2_date or '2차 면접 불합' in outcome_names or '합격' in outcome_names:
            stats['steps']['interview_2'] += 1
            
        # 최종 합격
        if '합격' in outcome_names:
            stats['steps']['final_pass'] += 1
            
        # 코딩테스트 탈락
        if '코딩테스트 불합격' in outcome_names:
            stats['steps']['coding_test'] += 1

    print(json.dumps(stats, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    analyze_notion_data()
