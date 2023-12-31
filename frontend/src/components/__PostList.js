import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  Typography,
  Box,
  Stack,
  MenuItem,
  Tooltip,
  AppBar,
  Toolbar,
  Paper,
} from "@mui/material";
import Form from "react-bootstrap/Form";
import {
  Badge,
  Button,
  Col,
  Container,
  Dropdown,
  DropdownButton,
  InputGroup,
  Nav,
  NavDropdown,
  NavItem,
  Row,
  Tab,
  Table,
  Tabs,
} from "react-bootstrap";

import "bootstrap/dist/css/bootstrap.css";
import Cookies from "js-cookie";
import Comment from "./Comment";
import SearchIcon from "@mui/icons-material/Search";
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import CodeBlock from "./CodeBlock";
import CommentsList from "./CommentsList";
import Flag from "../pages/Flag";
import DashTable from "./DashTable";
import CodeWithComments from "./CodeWithComments";
import { useRecoilState } from "recoil";
import { LoginName } from "../atom/LoginName";
import "./PostList.css";
function PostList() {



  // URL에서 쿼리 스트링 추출
  const queryString = window.location.search;
  const [User, setUser] = useRecoilState(LoginName);
  // 쿼리 스트링 파싱
  const urlParams = new URLSearchParams(queryString);

  // 'path' 파라미터 값 복호화
  const db_path = decodeURIComponent(urlParams.get('path'));

  const [rows, setRows] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [inputValue, setInputValue] = useState("");
  const [selectedText, setSelectedText] = useState("");
  const [visitedIds, setVisitedIds] = useState({}); // 방문한 Card의 id를 저장하는 상태
  const [selectedId, setSelectedId] = useState(null);
  const [commentCount, setCommentCount] = useState(0);
  const [tags, setTags] = useState([]);
  const [selectedTag, setSelectedTag] = useState(null);
  const [showAll, setShowAll] = useState(false); // 태그 전체 보기 여부를 관리하는 state
  const files = [
    {
      fileName: "파일11.txt",
      filePath: "/경로/파일1.txt",
      author: "작성자1",
      lastModified: "2021-09-01",
      lastAccessed: "2021-09-02",
      created: "2021-08-31",
      md5Hash: "1234567890",
      sha256Hash: "0987654321",
      fileExtension: "txt",
    },
    // 다른 파일들도 추가할 수 있습니다.
  ];
  const handleShowAll = () => {
    setShowAll(true);
  };
  const handleHide = () => {
    setShowAll(false);
  };
  const handleCommentCount = (count) => {
    setCommentCount(count);
  };
  const handleInputValueChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSearch = () => {
    setKeyword(inputValue);

  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSearch();
    }
  };
  const handleBadgeClick = (e, rowId) => {
    e.stopPropagation(); // Card의 onClick 이벤트가 실행되지 않도록 함
    Cookies.remove(`visited_${rowId}`); // 쿠키 삭제
    setSelectedId(null); // 선택된 id 초기화
    setVisitedIds((prev) => ({ ...prev, [rowId]: false })); // 방문한 Card의 id 상태 갱신
  };
  useEffect(() => {
    const fetchData = async () => {
      if (keyword == "") return;
      const data = {
        parsingDBpath: db_path,
        keyword: keyword,
      };

      try {
        const response = await fetch("/keyword", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          throw new Error("Network response was not ok " + response.statusText);
        }

        const result = await response.json();
        const formattedResult = result.map((item, index) => {
          const keywordCount =
            (item.plain_text.match(new RegExp(keyword, "g")) || []).length +
            (item.file_path.match(new RegExp(keyword, "g")) || []).length;
          return {
            id: index + 1,
            fileType: item.file_path.split(".").pop(),
            keywordCount,
            file_path: item.file_path,
            fileName: item.file_path.split("\\").pop(),
            ...item,
          };
        });
        if (keyword != "") setRows(formattedResult);

        const allTags = new Set();
        formattedResult.forEach((item) => {
          if (item.tag) {
            item.tag.split(",").forEach((tag) => allTags.add(tag.trim()));
          }
        });
        setTags(Array.from(allTags));
      } catch (error) {
        console.error(error);
      }
    };


    fetchData();
  }, []);

  return (
    <>
      <div class="topbar">
        {/* <Typography
          variant="h6"
          component="div"
          sx={{ fontWeight: "bold" }}
        >
          키워드 <mark>{keyword}</mark> 검색 결과 ({rows.length})
        </Typography> */}
        <Box
          sx={{
            display: "flex",
            width: "100%",
            justifyContent: "center",
            padding: "20px",
          }}
        >
          <Stack direction={"column"} spacing={1} width={"100%"}>
            <Stack direction="row" spacing={1} width={"100%"}>
              <InputGroup className="mb-3" style={{ height: '40px' }}>
                <DropdownButton
                  as={InputGroup.Prepend}
                  variant="secondary"
                  title={<AddCircleOutlineIcon />}
                  id="input-group-dropdown-1"
                >
                  <Dropdown.Item href="#">사람 이름</Dropdown.Item>
                  <Dropdown.Divider />
                  <Dropdown.Item href="#">기관 이름</Dropdown.Item>
                </DropdownButton>
                <Form.Control
                  type="text"
                  placeholder="Keyword Search "
                  value={inputValue}
                  onChange={handleInputValueChange}
                  onKeyPress={handleKeyPress}
                />
                <Button onClick={handleSearch}>
                  <SearchIcon /> 검색
                </Button>

              </InputGroup>
              <Button style={{ height: '40px' }}>
                <CalendarMonthIcon />
              </Button>
              <Button style={{ height: '40px', width: '120px' }} variant="danger">
                쿼리 초기화
              </Button>
            </Stack>
            {!keyword || rows.length == 0 ? (
              <div
                style={{
                  overflowY: "auto",
                  flex: 1,
                  scrollbarWidth: "none",
                  msOverflowStyle: "none",
                }}
              >
                
                <span style={{display:"flex",alignItems:"center"}}>
                  <span class="status"></span><span>온라인</span>
                </span>

              </div>
            ) : (
              <Box>
                {tags
                  .slice(0, showAll ? tags.length : 10)
                  .map((tag, index) => (
                    <Badge
                      key={index}
                      bg={selectedTag === tag ? "primary" : "secondary"}
                      onClick={() =>
                        setSelectedTag((prev) =>
                          prev === tag ? null : tag
                        )
                      }
                      style={{ cursor: "pointer", marginRight: "5px" }}
                    >
                      {tag}
                    </Badge>
                  ))}
                {showAll ? (
                  <Badge onClick={handleHide} bg="danger" pill>
                    접기..
                  </Badge>
                ) : (
                  tags.length > 10 && (
                    <Badge onClick={handleShowAll} bg="primary" pill>
                      더보기..
                    </Badge>
                  )
                )}
              </Box>
            )}
          </Stack>
        </Box>
        <hr />
      </div>
      <Box
        sx={{
          display: "flex",
          width: "100%"
        }}
      >

        {/* <Box sx={{ flexGrow: 1, backgroundColor: "white" }} width={"15%"}>

          <br />
          <Container component="main">
            <center>
              <Typography
                variant="h6"
                component="div"
                sx={{ fontWeight: "bold" }}
              >
                북마크
              </Typography>
            </center>
            <hr></hr>
            <Box>

            </Box>
          </Container>
        </Box> */}

        <Box width={selectedId ? "85%" : "70%"} sx={{ flexGrow: 1, paddingRight: "20px" }}>

          <div style={{ display: "flex" }}>
            <div
              style={{
                width: selectedText ? "40%" : "100%",
              }}
            >

              <div
                style={{

                  display: "flex",
                  flexDirection: "column",
                  overflow: "auto",
                  paddingLeft: "20px",
                  paddingTop: "20px",
                }}
              >

                <div
                  style={{
                    overflowY: "auto",
                    flex: 1,
                    scrollbarWidth: "none",
                    msOverflowStyle: "none",
                  }}
                >

                  {rows
                    .filter(
                      (row) =>
                        !selectedTag ||
                        (row.tag && row.tag.includes(selectedTag))
                    )
                    .map((row) => {
                      let tags = [];
                      if (row.tag) {
                        tags = row.tag.split(",");
                      }
                      const keywordIndex = row.plain_text.indexOf(keyword);
                      const start = Math.max(
                        0,
                        keywordIndex - (selectedText ? 10 : 20)
                      );
                      const end = Math.min(
                        row.plain_text.length,
                        keywordIndex + keyword.length + (selectedText ? 30 : 80)
                      );
                      const textSlice = row.plain_text.slice(start, end);
                      const highlightedText = textSlice.replace(
                        new RegExp(keyword, "gi"),
                        (match) => `<mark>${match}</mark>`
                      );

                      return (
                        <Card
                          key={row.id}
                          sx={{
                            minWidth: 275,
                            marginBottom: 2,
                            boxShadow: 3,
                            backgroundColor:
                              row.id === selectedId ? "#eeeeee" : "default",
                          }}
                          onClick={() => {
                            // 이미 선택된 셀이 다시 클릭되었는지 판단
                            if (row.id === selectedId) {
                              // 이미 선택된 셀이면 선택 해제
                              setSelectedText("");
                              setSelectedId(null);
                            } else {
                              // 새로운 셀이 선택되었으면 정보 업데이트
                              setSelectedText(row.plain_text);
                              setSelectedId(row.id); // 선택된 셀의 id 저장
                              Cookies.set(
                                `visited_${row.id}`,
                                new Date().toISOString(),
                                { expires: 7 }
                              );
                            }
                          }}
                        >
                          <CardContent>
                            <Stack
                              direction={"row"}
                              spacing={1}
                              justifyContent="space-between"
                            >
                              <Typography
                                variant="h10"
                                component="div"
                                sx={
                                  selectedText
                                    ? {
                                      fontWeight: "bold",
                                      overflow: "hidden",
                                      textOverflow: "ellipsis",
                                      whiteSpace: "nowrap",
                                      maxWidth: 260,
                                    }
                                    : { fontWeight: "bold" }
                                }
                              >
                                {row.fileName}
                              </Typography>
                              <Stack direction={"row"} spacing={1}>
                                <Typography variant="body2">
                                  <Badge bg="danger">
                                    키워드 Hit : {row.keywordCount}
                                  </Badge>
                                </Typography>
                                <Typography variant="body2">
                                  {row.tag &&
                                    row.tag.split(",").map((tag, index) => (
                                      <Badge
                                        key={index}
                                        bg="secondary"
                                        style={{ marginRight: "5px" }}
                                      >
                                        {tag.trim()}
                                      </Badge>
                                    ))}
                                </Typography>
                                <Typography variant="body2">
                                  {Cookies.get(`visited_${row.id}`) &&
                                    !visitedIds[row.id] && (
                                      <Tooltip
                                        title={
                                          <>
                                            {`읽은 시간: ${new Date(
                                              Cookies.get(`visited_${row.id}`)
                                            ).toLocaleString()}`}
                                            <br />
                                            {`읽은 사람 (3): @서종찬, @김기동, @우현우`}
                                          </>
                                        }
                                        arrow
                                      >
                                        <Badge
                                          bg="success"
                                          onClick={(e) =>
                                            handleBadgeClick(e, row.id)
                                          }
                                          style={{ cursor: "pointer" }}
                                        >
                                          Visited
                                        </Badge>
                                      </Tooltip>
                                    )}
                                </Typography>
                              </Stack>
                            </Stack>
                            <Stack
                              direction={"row"}
                              justifyContent="space-between"
                            >
                              <Typography variant="body2">
                                <pre>{row.file_path}</pre>
                              </Typography>
                            </Stack>
                            <Typography
                              variant="h6"
                              dangerouslySetInnerHTML={{
                                __html: highlightedText,
                              }}
                            ></Typography>
                          </CardContent>
                        </Card>
                      );
                    })}
                </div>
              </div>
            </div>
            {selectedText && (
              <div
                style={{
                  height: "100vh",
                  width: "60%",
                  display: "flex",
                  flexDirection: "column",
                  overflow: "auto",
                  paddingLeft: "20px",
                }}
              ><Paper>
                  <Tabs
                    defaultActiveKey="plain"
                    id="justify-tab-example"
                    className="mb-3"
                    justify
                    style={{
                      position: "sticky",
                      top: 0,
                      backgroundColor: "#E9EDF5",
                    }}
                  >
                    <Tab eventKey="plain" title="본문">
                      <CodeWithComments code={selectedText}></CodeWithComments>
                    </Tab>

                    <Tab eventKey="fileinfo" title="메타 데이터 정보">

                      <Table striped bordered hover>
                        <thead>
                          <tr>
                            <th>메타데이터</th>
                            <th>값</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <th>파일 명</th>
                            <th></th>
                          </tr>
                          <tr>
                            <th>파일 출처</th>
                            <th>
                              {/* <Badge bg="primary">고수봉 대리.zip</Badge>
                              ~\카카오톡 받은 파일\골절이란.hwp */}
                            </th>
                          </tr>
                          <tr>
                            <th>파일 경로</th>
                            <th>
                              <pre>
                                {/* C:\Users\SeoJongChan\Documents\카카오톡 받은
                                파일\골절이란.hwp */}
                              </pre>
                            </th>
                          </tr>
                          <tr>
                            <th>
                              <pre>생성 시간</pre>
                            </th>
                            <th>2021-10-23 08:12:56</th>
                          </tr>
                          <tr>
                            <th>
                              <pre>수정 시간</pre>
                            </th>
                            <th>2021-10-23 08:12:56</th>
                          </tr>
                          <tr>
                            <th>
                              <pre>마지막 접근 시간</pre>
                            </th>
                            <th>2021-10-24 15:22:06</th>
                          </tr>
                          <tr>
                            <th>해시값<br></br>(sha-256)</th>
                            <th>
                              5af2943af85e379b01a77217a15dbbfa71a12fce2ba626f5e136357d57f33213
                            </th>
                          </tr>
                        </tbody>
                      </Table>
                    </Tab>
                  </Tabs>
                </Paper>
              </div>
            )}
          </div>
        </Box>
        {!selectedId &&
          <Box sx={{ flexGrow: 1, backgroundColor: "white" }} width={"15%"}>
            <br />
            <Container component="main">
              <center>
                <Typography
                  variant="h6"
                  component="div"
                  sx={{ fontWeight: "bold" }}
                >
                  {selectedId ? "코멘트" : "최근 코멘트"}
                </Typography>
              </center>
              <hr></hr>
              <Box>
                {selectedId ? (
                  <Comment
                    selectedId={selectedId}
                    onCommentCount={handleCommentCount}
                    db_path={db_path}
                  ></Comment>
                ) : (
                  <CommentsList db_path={db_path}></CommentsList>
                )}
              </Box>
            </Container>
          </Box>
        }

      </Box>
    </>
  );
}
export default PostList;
