import * as React from "react";
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Header from "../components/Header";
import StickyFooter from "../components/StickyFooter";
import Table from "react-bootstrap/Table";
import { createTheme, ThemeProvider } from "@mui/material";
import { useState, useEffect } from "react";

const Document = () => {
  const theme = createTheme({
    typography: {
      fontFamily: "'Galmuri9', sans-serif;",
    },
  });
  return (
    <>
      <Container component="main" sx={{ mt: 5 }} maxWidth="lg">
        <ThemeProvider theme={theme}>
          <Typography variant="h3" id="rank">
            Document
          </Typography>
        </ThemeProvider>
        <CssBaseline>
          <br></br>
        </CssBaseline>
        <Typography variant="h5">툴 사용법 소개</Typography>
      </Container>
      <StickyFooter />
    </>
  );
};

export default Document;
