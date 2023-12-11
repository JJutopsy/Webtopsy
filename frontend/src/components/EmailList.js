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
import DatePicker from "react-datepicker";

import "react-datepicker/dist/react-datepicker.css";
import EmailResult from "./EmailResult";

function EmailList() {

  const dataString = localStorage.getItem('caseInfo');
  const caseInfo = JSON.parse(dataString);
  const db_path = caseInfo.parsingDBpath;
  const [activeTab, setActiveTab] = useState('first');
  const [rows, setRows] = useState([]);
  const [keyword, setKeyword] = useState('');
  const [tagDict, setTagDict] = useState({});
  const [selectedTag, setSelectedTag] = useState(null);

  const [nameDict, setNameDict] = useState({});
  const [selectedName, setSelectedName] = useState(null);

  const handleTagClick = (tag) => {
    setSelectedTag(tag);
  };
  const handleNameClick = (name) => {
    setSelectedName(name);
  }

  // 선택된 태그가 있으면 해당 태그를 포함한 항목만 필터링
  const filteredRows = selectedName
    ? rows.filter(row => row.names.some(nameObj => nameObj.name === selectedName))
    : selectedTag
      ? rows.filter(row => row.tags.some(tagObj => tagObj.tag === selectedTag))
      : rows;

  const sortedTags = Object.entries(tagDict).sort((a, b) => b[1].count - a[1].count);
  const sortedNames = Object.entries(nameDict).sort((a, b) => b[1].count - a[1].count);

  const handleSearch = async () => {
    const json =
    {
      parsingDBpath: db_path,
      keyword: keyword,
    };

    const response = await fetch('http://localhost:5000/keyword/email', {
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
    let nameDict = {}
    // 태그를 쉼표로 잘라서 리스트로 만드는 작업
    const processedData = data.map(item => {
        const tags = item.tag ? item.tag.split(',').filter(e => e.trim().length > 1).map(tag => {
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
        }) : [];
      
        // NNP 속성에서 사람 이름을 추출하는 과정
        const names = item.NNP ? item.NNP.split(',').filter(e => {
          const name = e.replace("_인명", "").trim();
          // 이름이 한국어 2글자 이상 3글자 이하인지 확인
          return e.includes("_인명") && /^[\uAC00-\uD7A3]*$/.test(name) && name.length >= 2 && name.length <= 3
        }).map(name => {
          name = name.replace("_인명", "").trim();
          // 이름이 처음 나오는 경우
          if (!nameDict[name]) {
            nameDict[name] = {
              color: getRandomColor(),
              count: 1
            };
          } else {
            // 이름이 이미 나온 경우
            nameDict[name].count += 1;
          }
          return {
            name,
            color: nameDict[name].color,
            count: nameDict[name].count
          };
        }) : [];
      
        return {
          ...item,
          tags,
          names,
        };
      });
      


    setTagDict(tagDict);
    setNameDict(nameDict);
    console.log(nameDict);
    setSelectedTag("");
    setSelectedName("");
    setRows(processedData);
  };
  useEffect(() => {
    handleSearch();
  }, []);
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
          <Col md={2}>
            <div className="tagList">
              <Card>
                <Card.Header>
                  <Nav variant="tabs" defaultActiveKey="first" onSelect={setActiveTab}>
                    <Nav.Item>
                      <Nav.Link eventKey="first">태그 보기</Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                      <Nav.Link eventKey="second">인명 보기</Nav.Link>
                    </Nav.Item>
                  </Nav>
                </Card.Header>
                <Card.Body style={{ height: '80vh' }}>
                  {activeTab === 'first' ? (
                    <div style={{ maxHeight: '75vh', overflowY: 'scroll' }}>
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
                  ) : (
                    <div style={{ maxHeight: '75vh', overflowY: 'scroll' }}>
                      {sortedNames.map(([name, { color, count }], index) => (
                        <div className={`Note-category-item ${sortedNames === name ? 'selected' : ''}`}
                          key={index} onClick={() => handleNameClick(name)}>
                          <span className="Note-category-item">
                            <span className="status" style={{ backgroundColor: color }}></span>
                            <span className="Note-category-lebel">{name}</span>
                          </span>
                          <span>{count}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </Card.Body>
              </Card>
            </div>
          </Col>
          <Col md={10}>
            <div className="searchResult">
              {/* <Result rows={filteredRows} db_path={db_path} /> */}
              <EmailResult rows={filteredRows} db_path={db_path}/>
            </div>
          </Col>
        </div>
      </Container >

    </>
  );
}
export default EmailList;
