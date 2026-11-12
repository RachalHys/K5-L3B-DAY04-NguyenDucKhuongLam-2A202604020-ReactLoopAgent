"""Demo trace và lỗi trước/sau từ kết quả eval đã lưu; không gọi API."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_case(filename, case_id):
    report = json.loads((ROOT / filename).read_text(encoding='utf-8'))
    return next(case for case in report['cases'] if case['id'] == case_id)


def main():
    print('STATUS INVESTIGATION AGENT — DEMO')
    print('Phát lại kết quả snapshot đã lưu; không gọi model hoặc live API.\n')

    case = read_case('eval_after.json', 'H6')
    print('1. TRACE NHIỀU BƯỚC — H6')
    print('Câu hỏi:', case['question'])
    print('Model:', case['model'])
    for event in case['result']['trace']:
        if event['event'] == 'model':
            print(f"\nBước {event['step']}: model → {event['finish']}")
        elif event['event'] == 'tool':
            print('  Tool:', event['name'], json.dumps(event['arguments'], ensure_ascii=False))
            result = event['result']
            evidence = {key: result[key] for key in
                        ('provider', 'captured_at', 'overall', 'status', 'components', 'url', 'source', 'error')
                        if key in result}
            if result.get('updates'):
                update = result['updates'][0]
                evidence['update_preview'] = update['body'][:220]
                evidence['truncated'] = update.get('truncated', False)
            print('  Bằng chứng:', json.dumps(evidence, ensure_ascii=False))
        else:
            print('  Kiểm tra:', json.dumps(event, ensure_ascii=False))
    print('\nCâu trả lời:', case['result']['answer'])
    print('Điểm:', case['grade']['score'], '/100')

    print('\n2. LỖI LỰA CHỌN TOOL — H4')
    before = read_case('eval_before.json', 'H4')
    after = read_case('eval_after.json', 'H4')
    print('Câu hỏi:', before['question'])
    for label, item in (('Trước cải tiến', before), ('Sau cải tiến', after)):
        calls = [event for event in item['result']['trace'] if event['event'] == 'tool']
        print(f"\n{label}: {item['grade']['score']}/100; "
              f"{len(item['result']['usage'])} lượt gọi model; {len(calls)} lượt gọi tool.")
        for call in calls:
            print('  ', call['name'], json.dumps(call['arguments'], ensure_ascii=False))
        print('Câu trả lời:', item['result']['answer'])
    print('\nH4 trước cải tiến gọi status tools dù câu hỏi yêu cầu không kiểm tra; '
          'sau cải tiến trả lời trực tiếp. Chi tiết đầy đủ nằm trong các file eval và NOTES.md.')


if __name__ == '__main__':
    main()
