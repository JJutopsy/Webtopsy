# Webtopsy

> 초기 설정

1. .env 에서 HOME 경로 변경
2. .env 에서 NER 경로 변경
3. frontend/components/PostList.js에 파싱DB 경로 변경

```
pip install -r requirements.txt
```

```
cd frontend/
npm i react --legacy-peer-deps
npm start
```

> 에러가 날 시

1. `backend/server/__init__.py `이동
2. `from .newcase import newcase_bp` 등 에러나는 모듈 제외
