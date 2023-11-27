import React, { useState, useEffect } from "react";
import CommentForm from "./CommentForm";
import { Box, Stack, Typography } from "@mui/material";
import { Badge, Card, ListGroup } from "react-bootstrap";

export default function Comment({ selectedId, onCommentCount, db_path }) {
  const typeColors = {
    관심: "primary",
    중요: "danger",
    "확인 바람": "warning",
    "": "",
  };
  const [comments, setComments] = useState([]);
  const [selected, setSelected] = useState({ name: "", color: "" });

  const handleAddComment = (newComment) => {
    const updatedComments = [...comments, newComment];
    setComments(updatedComments);
    onCommentCount(updatedComments.length); // 댓글 개수 전달
  };

  useEffect(() => {
    if (selectedId !== null) {
      const data = {
        db_path: db_path,
      };
      fetch(`http://localhost:5000/comments/${selectedId}`, {
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
          setComments(data);
          onCommentCount(data.length);
        })
        .catch((error) => console.error(error));
    }
  }, [selectedId]);

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
                      <b>@{comment.username} </b>
                    </Typography>
                    <Typography>{comment.created_at}</Typography>
                  </Stack>
                </Card.Header>
                <Card.Body>{comment.context}</Card.Body>
              </Card>
            </ListGroup.Item>
          </Box>
        ))}
      </Box>
      <div style={{ position: "sticky", bottom: 0 }}>
        <CommentForm
          selectedId={selectedId}
          onAddComment={handleAddComment}
          db_path={db_path}
        />
      </div>
    </div>
  );
}
