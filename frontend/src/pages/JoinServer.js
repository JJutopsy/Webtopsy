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
import Badge from 'react-bootstrap/Badge';
export default function JoinServer() {
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
            Join Server
          </Typography>
          <Typography variant="h5">
            현재 열려 있는 케이스를 확인 할 수 있습니다.
          </Typography>
        </ThemeProvider>
        <CssBaseline>
          <br></br>
        </CssBaseline>
        <Table striped bordered hover size="lg">
          <thead>
            <tr>
              <th>#</th>
              <th>Status</th>
              <th>Case Name</th>
              <th>Case Description</th>
              <th>Host Address</th>
              <th>User</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td><Badge bg="success">Open</Badge></td>
              <td>성심당 사건</td>
              <td>튀김소보로가 바삭하지 않아 판사를 고소함</td>
              <td>192.168.1.4</td>
              <td>1/8</td>
            </tr>
          </tbody>
        </Table>
      </Container>
      <StickyFooter />
    </>
  );
}
