import React, { useState, useEffect } from "react";
import CommentForm from "./CommentForm";
import { Box, Stack, Typography } from "@mui/material";
import { Badge, Card, ListGroup } from "react-bootstrap";

// 코멘트 데이터 예시

export default function CommentsList({ db_path }) {
  const typeColors = {
    관심: "primary",
    중요: "danger",
    "확인 바람": "warning",
    "": "",
  };

  const [comments, setComments] = useState([]);

  useEffect(() => {
    const fetchComments = () => {
      const data = {
        db_path: db_path,
      };
      fetch("http://localhost:5000/recent_comments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(
              "Network response was not ok " + response.statusText
            );
          }
          return response.json();
        })
        .then((data) => {
          console.log(data); // 콘솔에 응답 출력
          setComments(data); // 상태 업데이트
        })
        .catch((error) => console.error(error));
    };
    // 폴링 시작
    const intervalId = setInterval(fetchComments, 100); // 5초마다 새로운 댓글 확인

    // 컴포넌트가 언마운트될 때 폴링 중지
    return () => clearInterval(intervalId);
  }, [db_path]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <Box
        sx={{
          overflowY: "auto",
          flex: 1,
          scrollbarWidth: "none",
          msOverflowStyle: "none",
        }}
      >
        {comments.map((comment) => (
          <Box my={2} key={comment.id}>
            <ListGroup.Item className="border-left">
              <Card>
                <Card.Header>
                  <Stack direction={"row"} justifyContent="space-between">
                    <Typography>
                      <b>@{comment.username} </b>
                      
                    </Typography>
                    <Typography>{comment.created_at}</Typography>
                    
                  </Stack>
                </Card.Header>
                <Card.Body>
                  {comment.context} <a href="#">#{comment.post_id}</a>
                  <br></br>
                  <div>
                  <span>
                        {comment.type && (
                          <Badge
                            bg={typeColors[comment.type]}
                            text={
                              typeColors[comment.type] == "warning"
                                ? "dark"
                                : ""
                            }
                          >
                            {comment.type}
                          </Badge>
                        )}
                        </span>
                      </div>
                </Card.Body>
              </Card>
            </ListGroup.Item>
          </Box>
        ))}
      </Box>
    </div>
  );
}
