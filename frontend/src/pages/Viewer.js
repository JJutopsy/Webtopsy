import React, { useState } from "react";
import CssBaseline from "@mui/material/CssBaseline";
import Container from "@mui/material/Container";
import { Box, Typography } from "@mui/material";

import PostList from "../components/PostList";
import CommentsList from "../components/CommentsList";

export default function Viewer() {
  const [keyword, setKeyword] = useState(""); // 키워드를 저장할 state
  const [inputValue, setInputValue] = useState(""); // 임시로 Textarea의 값을 저장할 state

  const handleInputValueChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSearch = () => {
    setKeyword(inputValue);
    console.log(keyword);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Textarea에서 엔터를 쳤을 때 아래로 내려가는 것을 막음
      handleSearch();
    }
  };

  return (
    <>
      <Box sx={{ display: "flex", backgroundColor: "#E9EDF5" }}>
        <Box sx={{ flexGrow: 1 }} width={"100%"}>
          {/* <SearchResult /> */}
          <Container component="main" maxWidth="false">
            <PostList />
          </Container>
        </Box>
      </Box>
    </>
  );
}
