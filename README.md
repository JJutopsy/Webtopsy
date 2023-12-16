# Webtopsy

> AI 라이브러리 설치

Mecab 설치 https://uwgdqo.tistory.com/363

학습 데이터 다운로드(NER) https://drive.google.com/file/d/1vsbDry3b0h4O1QYrjDSKGVSXYQBrk_hs/view?usp=sharing

> 초기 설정

1. .env 파일 생성
2. .env 에서 HOME 경로 변경
3. .env 에서 NER 경로 변경
4. frontend/components/PostList.js에 파싱DB 경로 변경
5. frontend/package.json, backend/app.py > IP 부분 본인 IP로 변경

> example
```
HOME=C:\Users\dswhd\Webtocpy
REACT_APP_HOME=C:/Users/dswhd/Webtocpy
NER=C:\Users\dswhd\NER

```
> 라이브러리 설치
```
pip install -r requirements.txt
```
서버 실행
```
cd backend/
python app.py
```

프론트 실행 
```
cd frontend/
npm i react --legacy-peer-deps
npm start
```

