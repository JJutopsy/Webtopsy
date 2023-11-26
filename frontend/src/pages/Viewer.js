import React, { useState } from "react";
import CssBaseline from "@mui/material/CssBaseline";
import Container from "@mui/material/Container";
import { Box, Typography } from "@mui/material";

import PostList from "../components/PostList";
import CommentsList from "../components/CommentsList";

export default function Viewer() {
  return (
    <>
      <Box sx={{ display: "flex", backgroundColor: "#E9EDF5" }}>
            <PostList />
      </Box>
    </>
  );
}
