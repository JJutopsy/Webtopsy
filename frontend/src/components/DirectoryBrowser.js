import React, { useState, useEffect } from "react";
import Button from "@mui/material/Button";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import { Box, Checkbox } from "@mui/material";
import { grey } from "@mui/material/colors";
import { Pagination } from "@mui/material";
import { Form, OverlayTrigger, Tooltip } from "react-bootstrap";
import { Badge } from "react-bootstrap";
import FolderIcon from "@mui/icons-material/Folder";
import DescriptionIcon from "@mui/icons-material/Description";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

const DirectoryBrowser = ({ onSelectedItemsChange }) => {
  const [pathStr, setPath] = useState("C:\\Users");
  const [files, setFiles] = useState([]);
  const [page, setPage] = useState(1);
  const [checkedItems, setCheckedItems] = useState([]);
  const itemsPerPage = 10;

  const fetchFiles = async (newPath) => {
    const response = await fetch("http://localhost:5000/files", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ path: newPath }),
    });
    const data = await response.json();
    if (data.error) {
      alert("Error: " + data.error);
    } else {
      setFiles(data.files);
      console.log(files);
      setPath(newPath);
    }
  };

  useEffect(() => {
    fetchFiles(pathStr);
  }, []);

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      fetchFiles(pathStr);
    }
  };

  const onFileClick = (file) => {
    if (file === "..") {
      const newPath = pathStr.split("\\").slice(0, -1).join("\\");
      fetchFiles(newPath);
    } else if (file.isDirectory) {
      const newPath = `${pathStr}\\${file.name}`;
      fetchFiles(newPath);
    }
  };

  const handleCheckboxChange = (event, file) => {
    const filePath = pathStr + "\\" + file.name;

    let badgeColor = "primary";
    if (filePath.endsWith(".zip")) {
      badgeColor = "warning";
    } else if (filePath.endsWith(".001") || filePath.endsWith(".dd")) {
      badgeColor = "danger";
    }

    if (event.target.checked) {
      setCheckedItems((prevItems) => [
        ...prevItems,
        { current: filePath, previous: null, color: badgeColor },
      ]);
    } else {
      setCheckedItems((prevItems) =>
        prevItems.filter((item) => item.current !== filePath)
      );
    }
  };

  useEffect(() => {
    onSelectedItemsChange(checkedItems);
  }, [checkedItems]);

  return (
    <div style={{ display: "flex" }}>
      <Box width={1 / 2}>
        <Form.Group className="mb-3" controlId="path">
          <Form.Control
            type="text"
            placeholder="Enter directory"
            value={pathStr}
            onChange={(e) => setPath(e.target.value)}
            onKeyDown={handleKeyPress}
          />
        </Form.Group>
        <div style={{ height: "250px", overflow: "auto" }}>
          <List style={{ maxHeight: "90%", overflow: "auto" }}>
            <ListItem button onClick={() => onFileClick("..")}>
              <ArrowBackIcon style={{ marginRight: "0.5rem" }} /> 이전
            </ListItem>
            {files.map((file, index) => (
              <div style={{ display: "flex" }}>
                <Checkbox
                  checked={checkedItems.some(
                    (item) => item.current === pathStr + "\\" + file.name
                  )}
                  onChange={(e) => handleCheckboxChange(e, file)}
                />

                <ListItem
                  key={index}
                  button
                  onClick={() => onFileClick(file)}
                  style={{ display: "flex", alignItems: "center" }}
                >
                  {file.isDirectory ? (
                    <>
                      <FolderIcon
                        style={{ marginRight: "0.5rem", color: "#A7D397" }}
                      />
                      {file.name}
                    </>
                  ) : (
                    <>
                      <DescriptionIcon style={{ marginRight: "0.5rem" }} />
                      {file.name}
                    </>
                  )}
                </ListItem>
              </div>
            ))}
          </List>
        </div>
      </Box>
      <Box paddingLeft={"15px"}>
        <div>
          <h3>선택된 목록</h3>
          <br></br>
          {checkedItems.map((item, index) => (
            <div style={{ display: "block", marginRight: "10px" }}>
              <OverlayTrigger
                key={index}
                placement="top"
                overlay={
                  <Tooltip id={`tooltip-${index}`}>
                    수집 증거물 경로: {item.previous || "없음"}
                  </Tooltip>
                }
              >
                <Badge
                  bg={item.color}
                  text={item.color == "warning" ? "dark" : ""}
                  style={{ marginRight: "10px", cursor: "pointer" }} // cursor를 pointer로 설정하여 클릭 가능함을 표시
                  onClick={() => {
                    // 클릭 이벤트 추가
                    setCheckedItems((prevItems) =>
                      prevItems.filter((_, i) => i !== index)
                    ); // 클릭한 아이템을 제외한 나머지 아이템들로 상태 업데이트
                  }}
                >
                  {item.current}
                </Badge>
              </OverlayTrigger>

              <Badge
                bg="secondary" // Badge 색을 회색으로 변경
                style={{ marginRight: "10px", cursor: "pointer" }} // cursor를 pointer로 설정하여 클릭 가능함을 표시
                onClick={() => {
                  const newName = prompt("새 이름을 입력하세요.");
                  if (newName) {
                    setCheckedItems((prevItems) =>
                      prevItems.map((item, i) =>
                        i === index
                          ? {
                              current: newName,
                              previous: item.current,
                              color: item.color,
                            }
                          : item
                      )
                    );
                  }
                }}
              >
                이름 변경
              </Badge>
            </div>
          ))}
        </div>
      </Box>
    </div>
  );
};

export default DirectoryBrowser;
