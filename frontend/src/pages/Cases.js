import CssBaseline from "@mui/material/CssBaseline";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Card from "react-bootstrap/Card";
import Button from "react-bootstrap/Button";
import React, { useState, useEffect } from "react";
import Form from "react-bootstrap/Form";
import Modal from "react-bootstrap/Modal";
import { Box, createTheme, Grid, ThemeProvider } from "@mui/material";
import InputGroup from "react-bootstrap/InputGroup";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import DirectoryBrowser from "../components/DirectoryBrowser";
import StickyFooter from "../components/StickyFooter";
import "./modal.css";
import axios from "axios";
import Tab from "@mui/material/Tab";
import TabContext from "@mui/lab/TabContext";
import TabList from "@mui/lab/TabList";
import TabPanel from "@mui/lab/TabPanel";
import { useRecoilState } from 'recoil';
import { buttonState } from "../atom/ButtonState";
import CaseCard from '../components/CaseCard';  // CaseCard 컴포넌트를 import합니다.


export default function Cases() {
  const [state, setState] = useRecoilState(buttonState); // Recoil 상태와 setState 가져오기

  const [show, setShow] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [name, setName] = useState("");
  const [info, setInfo] = useState("");
  const [open, setOpen] = useState(false);
  const [cases, setCases] = useState([]);

  const [value, setValue] = React.useState("1");
  const [isCommentAllowed, setIsCommentAllowed] = useState(true); // 코멘트 달기 권한을 저장할 state

  const handleCommentPermissionChange = (event) => {
    setIsCommentAllowed(event.target.checked);
  };
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  const handleSelectedItemsChange = (items) => {
    setSelectedItems(items);
  };
  const handleNameChange = (e) => {
    setName(e.target.value);
  };
  const handleInfoChange = (e) => {
    setInfo(e.target.value);
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(false);
  };

  const sendCaseRequest = () => {
    if (name === "" || selectedItems.length === 0) {
      setOpen(true);
    } else {
      const currentItems = selectedItems.map(item => item.current);
      const owners = selectedItems.map(item=>item.owner);
      const data = {
        casename: name,
        caseinfo: info,
        filesWithOwners : selectedItems,
        total: selectedItems.length,
        nnp: true,
        tag: true,
      };

      console.log(data);
      fetch("http://localhost:5000/newcase", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
        .then((response) => response.json())
        .then((data) => console.log(data))
        .catch((error) => {
          console.error("Error:", error);
        });
      fetchCases().then((data) => setCases(data));
      setShow(false);
    }
  };

  const handleClose = () => {
    setShow(false);
  };

  const handleShow = () => setShow(true);

  const theme = createTheme({
    typography: {
      fontFamily: "'Galmuri9', sans-serif;",
    },
  });

  async function fetchCases() {
    const response = await axios.get("http://localhost:5000/case");

    return response.data.cases;
  }

  useEffect(() => {
    fetchCases().then((data) => setCases(data));
  }, []);

  return (
    <>
      <Container component="main" sx={{ mt: 5, zIndex: 0 }} maxWidth="lg">
        <ThemeProvider theme={theme}>
          <Typography variant="h3" id="rank">
            Cases
          </Typography>
        </ThemeProvider>
        <Typography variant="h5">생성한 케이스를 관리하는 페이지</Typography>
        <CssBaseline>
          <br></br>
        </CssBaseline>
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(18rem, 2fr))",
            gap: 9,
            p: 2,
          }}
        >
          <Card style={{ width: "18rem" }}>
            <Card.Header>New Case</Card.Header>
            <Card.Body>
              <Card.Title>케이스 생성</Card.Title>
              <Card.Text>
                여기를 클릭하여 케이스를 생성할 수 있습니다.
              </Card.Text>
              <Button variant="primary" onClick={handleShow}>
                케이스 생성
              </Button>
            </Card.Body>
          </Card>

          {cases.map((caseItem, index) => (
            <CaseCard caseItem={caseItem} />
          ))}
        </Box>

        <Modal
          show={show}
          onHide={() => setShow(false)}
          dialogClassName="my-modal"
          aria-labelledby="example-custom-modal-styling-title"
          backdrop="static"
          keyboard={false}
        >
          <Modal.Header closeButton>
            <Modal.Title id="example-custom-modal-styling-title">
              케이스 생성
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Box sx={{ width: "100%", typography: "body1", height: "500px" }}>
              <TabContext value={value}>
                <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
                  <TabList
                    onChange={handleChange}
                    aria-label="lab API tabs example"
                  >
                    <Tab label="케이스 정보 입력" value="1" />
                    <Tab label="수집 증거물 업로드" value="2" />
                    <Tab label="케이스 생성 옵션" value="3" />
                  </TabList>
                </Box>
                <TabPanel value="1">
                  <Form>
                    <Container>
                      <InputGroup className="mb-3">
                        <InputGroup.Text id="basic-addon1">
                          이름
                        </InputGroup.Text>
                        <Form.Control
                          placeholder="케이스 이름 입력"
                          aria-label="Username"
                          aria-describedby="basic-addon1"
                          required
                          value={name}
                          onChange={handleNameChange}
                        />
                      </InputGroup>

                      <Form.Group controlId="content">
                        <Form.Control
                          as="textarea"
                          rows={5}
                          placeholder="케이스 설명을 입력하세요."
                          value={info}
                          onChange={handleInfoChange}
                          style={{ backgroundColor: "#E9ECF0" }}
                        />
                      </Form.Group>
                    </Container>
                  </Form>
                </TabPanel>
                <TabPanel value="2">
                  <Form.Group
                    className="mb-3"
                    controlId="exampleForm.ControlInput1"
                  >
                    <DirectoryBrowser
                      onSelectedItemsChange={handleSelectedItemsChange}
                    />
                  </Form.Group>
                </TabPanel>
                <TabPanel value="3">
                  <h4>전처리 옵션</h4>
                  <div style={{ display: "flex" }}>
                    <div style={{ paddingRight: 30 }}>
                      <Form.Check
                        type="checkbox"
                        label="태그 추출"
                        checked={isCommentAllowed}
                        onChange={handleCommentPermissionChange}
                      />
                      <p>
                        *문서와 이메일 내부의 주요 키워드를 태그로 추출합니다.
                      </p>
                    </div>
                    <div style={{ paddingRight: 30 }}>
                      <Form.Check
                        type="checkbox"
                        label="개체명 추출"
                        checked={isCommentAllowed}
                        onChange={handleCommentPermissionChange}
                      />
                      <p>
                        *문서와 이메일 내부의 인명, 단체, 장소, 시간 표현, 양,
                        금전적 가치 등을 추출합니다.
                      </p>
                    </div>
                  </div>
                  <hr></hr>
                  <h4>초기 유저 권한</h4>
                  <div style={{ display: "flex" }}>
                    <div style={{ paddingRight: 30 }}>
                      <Form.Check
                        type="checkbox"
                        label="코멘트 작성 허용"
                        checked={isCommentAllowed}
                        onChange={handleCommentPermissionChange}
                      />
                      <p>
                        *케이스에 접근한 유저의 코멘트 작성 기본 권한을
                        '허용'으로 설정합니다.
                      </p>
                    </div>
                    <div style={{ paddingRight: 30 }}>
                      <Form.Check
                        type="checkbox"
                        label="파일 업로드/다운로드 허용"
                        checked={isCommentAllowed}
                        onChange={handleCommentPermissionChange}
                      />
                      <p>
                        케이스 내부의 파일에 대하여 업로드/다운로드를
                        허용합니다.
                      </p>
                    </div>
                  </div>
                </TabPanel>
              </TabContext>
            </Box>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleClose}>
              닫기
            </Button>
            {value === "3" && (
              <Button variant="primary" onClick={sendCaseRequest}>
                생성
              </Button>
            )}
          </Modal.Footer>
        </Modal>
        <Snackbar
          open={open}
          autoHideDuration={1500}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: "top", horizontal: "right" }}
        >
          <Alert
            onClose={handleCloseSnackbar}
            severity="warning"
            sx={{ width: "100%" }}
          >
            모든 필드를 채워주세요!
          </Alert>
        </Snackbar>
      </Container>
      <StickyFooter />
    </>
  );
}
