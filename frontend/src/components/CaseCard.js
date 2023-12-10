import React, { useEffect } from "react";
import Card from "react-bootstrap/Card";
import Button from "react-bootstrap/Button";
import { useSetRecoilState, useRecoilValue } from 'recoil';
import { buttonState } from "../atom/ButtonState";
import { useNavigate } from 'react-router-dom';  // useNavigate를 import합니다.

export default function CaseCard({ caseItem }) {
  const setButtonState = useSetRecoilState(buttonState);
  const buttonStateValue = useRecoilValue(buttonState);
  const navigate = useNavigate();  // useNavigate 훅을 사용합니다.

  useEffect(() => {
    if (buttonStateValue) {
      const data = JSON.stringify(caseItem);
      localStorage.setItem('caseInfo', data);
      navigate("/case/example?path=" + encodeURIComponent(caseItem.parsingDBpath));  // 페이지를 이동합니다.
    }
  }, [buttonStateValue, navigate]);  // navigate를 의존성 배열에 추가합니다.

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
          }}
        >
          접속
        </Button>
      </Card.Body>
    </Card>
  );
}
