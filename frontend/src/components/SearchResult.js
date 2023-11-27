import React, { useState, useEffect } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { Button, Form } from "react-bootstrap";
import Chip from "@mui/material/Chip";
import Container from "@mui/material/Container";
import SendIcon from "@mui/icons-material/Send";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { solarizedlight } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Box, Stack } from "@mui/material";
import Textarea from "@mui/joy/Textarea";

export default function SearchResult() {
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
  const [rows, setRows] = useState([]);
  const [selectedText, setSelectedText] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const handleColumnWidthChange = (params) => {
    const { field, width } = params;
    // 열의 너비 변경 사항 처리 로직 작성
    // 예: 열의 너비를 저장하거나 다른 동작 수행
    console.log(`Column "${field}" width changed to ${width}px`);
  };
  useEffect(() => {
    const fetchData = async () => {
      const data = {
        parsingDBpath:
          "C:\\Users\\SeoJongChan\\Webtopsy\\cases\\케이스\\parsing.sqlite",
        keyword: keyword,
      };

      try {
        const response = await fetch("http://localhost:5000/keyword", {
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
            id: index + 1, // id를 정수로 저장
            fileType: item.file_path.split(".").pop(), // 확장자 분류
            keywordCount, // 키워드 카운트 저장
            file_path: item.file_path,
            fileName: item.file_path.split("\\").pop(),
            ...item,
          };
        });
        setRows(formattedResult);
      } catch (error) {
        console.error(error);
      }
    };

    console.log(rows);
    fetchData();
  }, [keyword]);

  const columns = [
    {
      field: "id",
      headerName: "ID",
      width: 70,
      type: "number",
      sortComparator: (v1, v2) => v1 - v2,
    },
    {
      field: "fileType",
      headerName: "Type",
      width: 80,
      renderCell: (params) => {
        const colorMap = {
          doc: "primary",
          docx: "secondary",
          pptx: "success",
          xlsx: "error",
          pdf: "warning",
          hwp: "info",
          eml: "default",
          pst: "primary",
          ost: "secondary",
          ppt: "success",
          xls: "error",
          csv: "warning",
          txt: "info",
          zip: "default",
          "7z": "primary",
        };
        return <Chip label={params.value} color={colorMap[params.value]} />;
      },
    },
    { field: "keywordCount", headerName: "Hit", width: 70 }, // 새로운 칼럼 추가
    { field: "file_path", headerName: "Path", flex: 1 },
    { field: "fileName", headerName: "Name", flex: 1 },
    { field: "m_time", headerName: "Modified Time", flex: 1 },
    { field: "a_time", headerName: "Access Time", flex: 1 },
    { field: "c_time", headerName: "Create TIme", flex: 1 },
  ];

  return (
    <>
      <div style={{ display: "flex" }}>
        <div
          style={{
            height: "550px",
            width: selectedText ? "50%" : "100%",
          }}
        >
          <DataGrid
            rows={rows}
            columns={columns}
            rowHeight={40}
            onColumnWidthChange={handleColumnWidthChange}
            onCellClick={(params, event) => {
              // 이미 선택된 셀이 다시 클릭되었는지 판단
              if (params.id === selectedId) {
                // 이미 선택된 셀이면 선택 해제
                setSelectedText("");
                setSelectedId(null);
              } else {
                // 새로운 셀이 선택되었으면 정보 업데이트
                const selectedRow = params.row;
                setSelectedText(selectedRow ? selectedRow.plain_text : "");
                setSelectedId(params.id); // 선택된 셀의 id 저장
              }
            }}
          />
          <Box component="footer">
            <Container
              fixed
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                paddingTop: 15,
                bottom: 30,
              }}
            >
              <Stack direction="row" spacing={1} width={"100%"}>
                <Form.Control
                  type="text"
                  placeholder="Keyword Search "
                  value={inputValue}
                  onChange={handleInputValueChange}
                  onKeyPress={handleKeyPress}
                />
                <Button onClick={handleSearch}>
                  <SendIcon />
                </Button>
              </Stack>
            </Container>
          </Box>
        </div>
        {selectedText && (
          <div
            style={{
              height: "550px",
              width: "50%",
              display: "flex",
              flexDirection: "column",
              overflow: "auto",
              padding: "5px",
            }}
          >
            <div style={{ flexBasis: "90%", overflow: "auto" }}>
              <SyntaxHighlighter
                language="text" // 텍스트 언어를 사용
                style={solarizedlight} // solarizedlight 스타일을 사용
                showLineNumbers // 라인 번호를 표시
                wrapLongLines // 긴 줄을 감싸기
              >
                {selectedText}
              </SyntaxHighlighter>
            </div>
            <hr></hr>
            <Box style={{ flexBasis: "10%", overflow: "auto" }}>
              <Stack direction="row" spacing={1}></Stack>
            </Box>
          </div>
        )}
      </div>
    </>
  );
}
