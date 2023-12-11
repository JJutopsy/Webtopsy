import React, { useCallback } from "react"; // useCallback을 추가로 import합니다.
import Card from "react-bootstrap/Card";
import Button from "react-bootstrap/Button";
import { useSetRecoilState, useRecoilValue } from 'recoil';
import { buttonState } from "../atom/ButtonState";
import { useNavigate } from 'react-router-dom';

export default function CaseCard({ caseItem }) {
  const setButtonState = useSetRecoilState(buttonState);
  const buttonStateValue = useRecoilValue(buttonState);
  const navigate = useNavigate();

  // handleOpen 함수를 정의합니다.
  const handleOpen = useCallback(() => {
    const data = JSON.stringify(caseItem);
    localStorage.setItem('caseInfo', data);
    navigate("/case/example");
  }, [caseItem, navigate]); // caseItem과 navigate를 의존성 배열에 추가합니다.

  // useEffect를 제거하고 Button 컴포넌트의 onClick 이벤트에서 handleOpen 함수를 호출합니다.
  return (
    <Card style={{ width: "18rem" }}>
      <Card.Header>#{caseItem.id}</Card.Header>
      <Card.Body>
        <Card.Title>{caseItem.casename}</Card.Title>
        <Card.Text>{caseItem.caseinfo}</Card.Text>
        <Card.Text>{caseItem.parsingDBpath}</Card.Text>
        <Button
          variant="primary"
          onClick={() => {
            setButtonState(true);
            handleOpen(); // Button 클릭 시 handleOpen 함수를 호출합니다.
          }}
        >
          접속
        </Button>
      </Card.Body>
    </Card>
  );
}
