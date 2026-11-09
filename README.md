# vat-skills

부가세챙김이(비공식 도우미)의 규칙 파일 저장소예요. 신고·납부 대행이나 세무대리·세무상담이 아니에요.

## 들어 있는 파일
| 파일 | 내용 |
|---|---|
| `vat-rules.md` | 부가세챙김이 업무 규칙 |
| `vat-start.md` | 부가세챙김이 시작하기 |
| `vat-table.md` | 부가세챙김이 기준표 (확인일이 적힌 숫자 표) |
| `MANIFEST.txt` | 위 세 파일이 맞는 판인지 확인하는 목록 |
| `VERSION` | 이 저장소의 판 번호 (예: 6.4) |
| `SHA256SUMS` | 모든 파일이 맞는지 `sha256sum -c`로 확인하는 목록 |
| `tests/` | 판·목록·새 판 확인·법령 연결 묻기 시험 |
| `tools/make_manifest.py` | `MANIFEST.txt`·`SHA256SUMS`를 다시 만드는 도구 |

## 새 판 받기 (하루 한 번)
도우미는 하루 한 번 이 저장소의 최신 정식 릴리즈를 확인해요. 새 판이 있으면 임시 폴더에 받아 `sha256sum -c SHA256SUMS`와 시험을 모두 통과할 때만 `~/vat-skills` 폴더를 바꾸고, 하나라도 실패하면 쓰던 판을 그대로 써요. 이전 판은 `~/vat-skills.prev`에 남겨요. 판이 같거나 낮으면 바꾸지 않아요.

## 시험
```bash
sha256sum -c SHA256SUMS
python3 -m unittest discover -s tests
```

© 엘비즈파트너스
