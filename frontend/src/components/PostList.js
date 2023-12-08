import React, { useEffect, useState } from "react";
import {
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
  Card,
  Nav,
  NavDropdown,
  NavItem,
  Row,
  Tab,
  Table,
  Tabs,
  ListGroup,
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
import Result from "./Result";

function PostList() {



  // URL에서 쿼리 스트링 추출
  const queryString = window.location.search;
  const [User, setUser] = useRecoilState(LoginName);
  // 쿼리 스트링 파싱
  const urlParams = new URLSearchParams(queryString);

  // 'path' 파라미터 값 복호화
  const db_path = decodeURIComponent(urlParams.get('path'));
  const [activeTab, setActiveTab] = useState('first');
  const [rows, setRows] = useState([]);
  const [keyword, setKeyword] = useState('');
  const [tagDict, setTagDict] = useState({});
  // 태그를 관리하는 상태
  const [selectedTag, setSelectedTag] = useState(null);

  // 태그를 클릭했을 때의 이벤트 핸들러
  const handleTagClick = (tag) => {
    setSelectedTag(tag);
  };

  // 선택된 태그가 있으면 해당 태그를 포함한 항목만 필터링
  const filteredRows = selectedTag ? rows.filter(row => row.tags.some(tagObj => tagObj.tag === selectedTag)) : rows;
  const sortedTags = Object.entries(tagDict).sort((a, b) => b[1].count - a[1].count);

  const handleSearch = async () => {
    const json =
    {
      parsingDBpath: db_path,
      keyword: keyword,
    };

    const response = await fetch('http://localhost:5000/keyword', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(json)
    });
    const data = await response.json();
    // 랜덤한 색상을 생성하는 함수
    const getRandomColor = () => {
      const letters = '0123456789ABCDEF';
      let color = '#';
      for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
      }
      return color;
    };

    let tagDict = {}
    // 태그를 쉼표로 잘라서 리스트로 만드는 작업
    const processedData = data.map(item => {
      const tags = item.tag.split(',').map(tag => {
        // 태그가 처음 나오는 경우
        if (!tagDict[tag]) {
          tagDict[tag] = {
            color: getRandomColor(),
            count: 1
          };
        } else {
          // 태그가 이미 나온 경우
          tagDict[tag].count += 1;
        }

        return {
          tag,
          color: tagDict[tag].color,
          count: tagDict[tag].count
        };
      });

      return {
        ...item,
        tags
      };
    });

    console.log(tagDict);
    setTagDict(tagDict);
    console.log(processedData);

    setRows(processedData);
  };

  return (
    <>
      <div className="topbar" style={{
        padding: 10
      }}>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
          }}
        >

          <Stack direction={"column"} width={"100%"}>
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
                  value={keyword}
                  onChange={e => setKeyword(e.target.value)}
                />
                <Button onClick={handleSearch}>
                  <SearchIcon /> 검색
                </Button>

              </InputGroup>
              <Button style={{ height: '40px' }}>
                <CalendarMonthIcon />
              </Button>
              <Button style={{ height: '40px', width: '130px' }} variant="danger">
                쿼리 초기화
              </Button>
            </Stack>

          </Stack>
        </div>
      </div>
      <Container fluid>
        <div style={{ display: 'flex' }}>
          <Col md={3}>
            <div className="tagList">
              <Card>
                <Card.Header>
                  <Nav variant="tabs" defaultActiveKey="first" onSelect={setActiveTab}>
                    <Nav.Item>
                      <Nav.Link eventKey="first">태그 보기</Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                      <Nav.Link eventKey="second">코멘트 보기</Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                      <Nav.Link eventKey="third">북마크</Nav.Link>
                    </Nav.Item>
                  </Nav>
                </Card.Header>
                <Card.Body style={{ height: '80vh' }}>
                  {activeTab === 'first' ? (
                    <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                      {sortedTags.map(([tag, { color, count }], index) => (
                        <div className={`Note-category-item ${selectedTag === tag ? 'selected' : ''}`}
                          key={index} onClick={() => handleTagClick(tag)}>
                          <span className="Note-category-item">
                            <span className="status" style={{ backgroundColor: color }}></span>
                            <span className="Note-category-lebel">{tag}</span>
                          </span>
                          <span>{count}</span>
                        </div>
                      ))}
                    </div>
                  ) : activeTab === 'second' ? (
                    <div>
                      <ListGroup as="ol">
                        <ListGroup.Item
                          action
                          as="li"
                          className="d-flex justify-content-between align-items-start"
                        >
                          <div className="ms-2 me-auto">
                            <div className="fw-bold">File Name 1</div>
                            제일 마지막 메세지
                          </div>
                          <Badge bg="primary" pill>
                            14
                          </Badge>
                        </ListGroup.Item>
                        <ListGroup.Item
                          action
                          as="li"
                          className="d-flex justify-content-between align-items-start"
                        >
                          <div className="ms-2 me-auto">
                            <div className="fw-bold">File Name 2</div>
                            제일 마지막 메세지
                          </div>
                          <Badge bg="primary" pill>
                            14
                          </Badge>
                        </ListGroup.Item>
                      </ListGroup>
                    </div>
                  ) : (
                    <div>
                      <ListGroup as="ol">
                        <ListGroup.Item
                          action
                          as="li"
                          className="d-flex justify-content-between align-items-start"
                        >
                          <div className="ms-2 me-auto">
                            <div className="fw-bold">BookMark Name 1</div>
                            북마크 생성자
                          </div>
                          <Badge bg="primary" pill>
                            5
                          </Badge>
                        </ListGroup.Item>
                        <ListGroup.Item
                          action
                          as="li"
                          className="d-flex justify-content-between align-items-start"
                        >
                          <div className="ms-2 me-auto">
                            <div className="fw-bold">BookMark Name 2</div>
                            북마크 생성자
                          </div>
                          <Badge bg="primary" pill>
                            5
                          </Badge>
                        </ListGroup.Item>
                      </ListGroup>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </div>
          </Col>
          <Col md={9}>
            <div className="searchResult">
              <Result rows={filteredRows} />
            </div>
          </Col>
        </div>
      </Container >

    </>
  );
}
export default PostList;
