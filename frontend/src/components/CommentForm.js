import { Stack } from "@mui/material";
import React, { useState } from "react";
import {
  Form,
  Button,
  InputGroup,
  Card,
  DropdownButton,
  Dropdown,
  ButtonGroup,
} from "react-bootstrap";
import { LoginName } from "../atom/LoginName";
import { useRecoilState } from "recoil";
import { Badge } from "react-bootstrap";
export default function CommentForm({ selectedId, onAddComment, db_path }) {
  const [user, setUser] = useRecoilState(LoginName);
  const [content, setContent] = useState("");
  const [selected, setSelected] = useState({ name: "", color: "" });
  const names = ["서종찬", "우현우", "권순형", "이종민", "손석훈"];
  const getRandomName = () => {
    return names[Math.floor(Math.random() * names.length)];
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // 입력된 코멘트 데이터를 생성
    const newComment = {
      post_id: selectedId,
      username: user || getRandomName(),
      context: content,
      type: selected.name,
      db_path: db_path,
    };

    // 서버로 코멘트 데이터 전송
    fetch("http://localhost:5000/comment", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(newComment),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok " + response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        console.log(data);
        // 부모 컴포넌트에게 새 댓글 알림
        onAddComment(newComment);
        // 입력 필드 초기화
        setUser("");
        setContent("");
        setSelected({ name: "", color: "" });
      })
      .catch((error) => console.error(error));
  };
  return (
    <Form onSubmit={handleSubmit}>
      <Card>
        {/* <Card.Header>
          코멘트{" "}
          <span>
            {" "}
            {selected && (
              <Badge
                bg={selected.color}
                text={selected.color == "warning" ? "dark" : ""}
              >
                {selected.name}
              </Badge>
            )}
          </span>
        </Card.Header> */}
        <Card.Body>
          <Card.Text>
            {" "}
            <Form.Group controlId="content">
              <Form.Control
                as="textarea"
                rows={2}
                placeholder="코멘트 내용을 입력하세요."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                style={{
                  border: "none",
                  resize: "none",
                  outline: "none",
                }}
              />
            </Form.Group>{" "}
          </Card.Text>
        </Card.Body>

        <Card.Footer className="text-muted">
          <Stack direction={"row"} spacing={1} justifyContent={"right"}>
            <Dropdown as={ButtonGroup}>
              <Button variant="success" type="submit">
                작성
              </Button>
              <Dropdown.Toggle
                split
                variant="success"
                id="dropdown-split-basic"
              />
              <Dropdown.Menu>
                <Dropdown.Item
                  onClick={() =>
                    setSelected({ name: "관심", color: "primary" })
                  }
                >
                  관심
                </Dropdown.Item>
                <Dropdown.Item
                  onClick={() => setSelected({ name: "중요", color: "danger" })}
                >
                  중요
                </Dropdown.Item>
                <Dropdown.Item
                  onClick={() =>
                    setSelected({ name: "확인 바람", color: "warning" })
                  }
                >
                  확인 바람
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </Stack>
        </Card.Footer>
      </Card>
    </Form>
  );
}
