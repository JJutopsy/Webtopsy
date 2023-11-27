import { Route, Routes } from "react-router-dom";
import Document from "./pages/Document";
import Home from "./pages/Home";
import { createTheme, ThemeProvider } from "@mui/material/styles";

import "bootstrap/dist/css/bootstrap.min.css";
import Flag from "./pages/Flag";
import Hof from "./pages/Cases";
import "./App.css";
import ProblemView from "./pages/ProblemView";
import Header from "./components/Header";
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import { RecoilRoot } from "recoil";
import JoinServer from "./pages/JoinServer";
import StickyFooter from "./components/StickyFooter";
import Cases from "./pages/Cases";
import Viewer from "./pages/Viewer";
const theme = createTheme({
  typography: {
    fontFamily: "Noto Sans KR, sans-serif",
  },
});
const App = () => {
  return (
    <>
      <RecoilRoot>
        <ThemeProvider theme={theme}>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              minHeight: "100vh",
            }}
          >
            <CssBaseline />
            <Header style={{ position: "relative" }}></Header>

            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/document" element={<Document />}></Route>
              <Route path="/qstart" element={<JoinServer />} />
              <Route path="/case" element={<Cases />} />
              <Route path="/case/example" element={<Viewer />} />
              <Route path="/hof" element={<Hof />} />
              <Route path="/flag" element={<Flag />} />
            </Routes>
          </Box>
        </ThemeProvider>
      </RecoilRoot>
    </>
  );
};

export default App;
