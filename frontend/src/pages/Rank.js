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

export default function Rank() {
  const [data, setData] = useState([]);

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
            Rank
          </Typography>
          <Typography variant="h5">랭킹을 확인할 수 있어요.</Typography>
        </ThemeProvider>
        <CssBaseline>
          <br></br>
        </CssBaseline>
      </Container>
      <StickyFooter />
    </>
  );
}
