import React, { useState } from "react";
import { Doughnut, Bar } from "react-chartjs-2";
import { Chart, ArcElement, registerables } from "chart.js";
import { CategoryScale } from "chart.js";
import {
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  ThemeProvider,
  createTheme,
  Button,
  Tabs,
  Tab,
  Box,
  Paper,
  Typography,
} from "@mui/material";
import Header from "../components/Header";
import StickyFooter from "../components/StickyFooter";

Chart.register(ArcElement);
Chart.register(CategoryScale);
Chart.register(...registerables);

const theme = createTheme();

const DashTable = () => {
  // Data settings for charts
  const pieChartData = {
    labels: ["pdf", "docx", "eml", "hwp", "기타"],
    datasets: [
      {
        data: [140, 135, 69, 74, 55],
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4CAF50",
          "#FF5733",
        ],
        hoverBackgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4CAF50",
          "#FF5733",
        ],
      },
    ],
  };

  const barChartOptions = [
    {
      label: "자주 언급된 인물",
      data: {
        labels: ["최우제", "문현준", "이상혁", "이민형", "류민석"],
        datasets: [
          {
            backgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4CAF50",
              "#FF5733",
            ],
            borderColor: "#fff",
            borderWidth: 1,
            hoverBackgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4CAF50",
              "#FF5733",
            ],
            hoverBorderColor: "#fff",
            data: [60, 50, 40, 35, 32],
          },
        ],
      },
    },
    {
      label: "자주 언급된 장소",
      data: {
        labels: ["서울", "가산", "광화문", "부산", "고척"],
        datasets: [
          {
            backgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4CAF50",
              "#FF5733",
            ],
            borderColor: "#fff",
            borderWidth: 1,
            hoverBackgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4CAF50",
              "#FF5733",
            ],
            hoverBorderColor: "#fff",
            data: [110, 54, 40, 37, 22],
          },
        ],
      },
    },
    {
      label: "자주 등장한 태그",
      data: {
        labels: ["발주", "보고", "정산", "수주", "우승"],
        datasets: [
          {
            backgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4CAF50",
              "#FF5733",
            ],
            borderColor: "#fff",
            borderWidth: 1,
            hoverBackgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4CAF50",
              "#FF5733",
            ],
            hoverBorderColor: "#fff",
            data: [167, 146, 140, 97, 52],
          },
        ],
      },
    },
  ];

  // Chart options
  const chartOptions = {
    maintainAspectRatio: false,
    responsive: true,
    width: 50,
    height: 50,
    plugins: {
      legend: {
        display: false,
      },
    },
  };

  const doughnutOptions = {
    maintainAspectRatio: false,
    responsive: true,
    width: 50,
    height: 50,
    plugins: {
      legend: {
        position: "bottom",
      },
    },
  };

  // List data
  const recentBookmarkList = [
    {
      markName: "GenG전자 관련",
      documentName: "GenG 전자 재무제표 비교표.pdf",
      creationTime: "2023-06-11 14:34:56",
      note: "경쟁사 GenG 언급",
    },
    {
      markName: "불일치 내역 관련",
      documentName: "행복 물산 거래 수주 내역.xls",
      creationTime: "2023-06-13 12:21:43",
      note: "실제 거래내역 불일치",
    },
    {
      markName: "GenG전자 관련",
      documentName: "인사팀 발령 회의 배치도.docx",
      creationTime: "2023-06-16 10:11:46",
      note: "본인 소관 외 문서",
    },
    // ... rest of the data
  ];

  const afterHoursDocumentList = [
    {
      documentName: "문현준대리_휴가 계획표.docx",
      author: "문현준",
      creationTime: "2023-06-01 19:30:33",
    },
    {
      documentName: "외주 견적 계약서.pdf",
      author: "문현준",
      creationTime: "2023-06-02 22:00:45",
    },
    {
      documentName: "10주년 행사 식순 및 참가자 명단.hwp",
      author: "이상혁",
      creationTime: "2023-07-08 21:30:12",
    },
    // ... rest of the data
  ];

  const [currentBarChart, setCurrentBarChart] = useState(0);

  const handleTabChange = (event, newValue) => {
    setCurrentBarChart(newValue);
  };

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "20px",
        height: "900px",
        backgroundColor: "#E9EDF5",
      }}
    >
      {/* Recent Bookmark List */}

      {/* Doughnut Chart */}
      <Paper elevation={3}>
        <div
          style={{
            gridArea: "1 / 1 / 2 / 2",
            height: "320px",
          }}
        >
          <Typography variant="h5" padding={"30px"}>
            주요 확장자 분표
            <hr></hr>
          </Typography>
          <Doughnut data={pieChartData} options={doughnutOptions} />
        </div>
      </Paper>
      <Paper elevation={3}>
        <div
          style={{
            gridArea: "1 / 2 / 2 / 3",
            width: "100%",
            flexGrow: 1,
            marginBottom: "20px",
          }}
        >
          <Typography variant="h5" padding={"30px"}>
            최근 생성 북마크
            <hr></hr>
          </Typography>

          <Container>
            <TableContainer>
              <Table sx={{ minWidth: 650 }}>
                <TableHead>
                  <TableRow style={{ backgroundColor: "#f2f2f2" }}>
                    {" "}
                    {/* 테이블 헤더 색상 변경 */}
                    <TableCell
                      style={{
                        width: "33%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        padding: "10px",
                        border: "1px solid #ddd",
                        textAlign: "center",
                        fontWeight: "bold",
                      }}
                    >
                      북마크 명
                    </TableCell>
                    <TableCell
                      style={{
                        width: "33%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        padding: "10px",
                        border: "1px solid #ddd",
                        textAlign: "center",
                        fontWeight: "bold",
                      }}
                    >
                      문서명
                    </TableCell>
                    <TableCell
                      style={{
                        width: "33%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        padding: "10px",
                        border: "1px solid #ddd",
                        textAlign: "center",
                        fontWeight: "bold",
                      }}
                    >
                      생성일시
                    </TableCell>
                    <TableCell
                      style={{
                        width: "33%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        padding: "10px",
                        border: "1px solid #ddd",
                        textAlign: "center",
                        fontWeight: "bold",
                      }}
                    >
                      비고
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentBookmarkList.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          padding: "10px",
                          border: "1px solid #ddd",
                          textAlign: "center",
                        }}
                      >
                        {item.markName}
                      </TableCell>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          padding: "10px",
                          border: "1px solid #ddd",
                          textAlign: "center",
                        }}
                      >
                        {item.documentName}
                      </TableCell>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          padding: "10px",
                          border: "1px solid #ddd",
                          textAlign: "center",
                        }}
                      >
                        {item.creationTime}
                      </TableCell>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          padding: "10px",
                          border: "1px solid #ddd",
                          textAlign: "center",
                        }}
                      >
                        {item.note}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Container>
        </div>
      </Paper>
      {/* Bar Chart */}
      <Paper elevation={3}>
        <div
          style={{
            gridArea: "2 / 1 / 3 / 2",
            width: "100%",
            height: "200px",
            marginBottom: "20px",
          }}
        >
          <Typography variant="h5" padding={"30px"}>
            주요 키워드
            <hr></hr>
          </Typography>
          <Tabs value={currentBarChart} onChange={handleTabChange} centered>
            {barChartOptions.map((chart, index) => (
              <Tab key={index} label={chart.label} />
            ))}
          </Tabs>
          <Box sx={{ p: 3 }}>
            <Bar
              data={barChartOptions[currentBarChart].data}
              options={chartOptions}
            />
          </Box>
        </div>
      </Paper>

      {/* After Hours Document List */}
      <Paper elevation={3}>
        <div
          style={{
            gridArea: "2 / 2 / 3 / 3",
            width: "100%",
            flexGrow: 1,
            marginBottom: "20px",
          }}
        >
          <Typography variant="h5" padding={"30px"}>
            업무 시간 외 시간에 사용한 문서
            <hr></hr>
          </Typography>
          <Container>
            <TableContainer>
              <Table sx={{ minWidth: 650 }}>
                <TableHead>
                  <TableRow style={{ backgroundColor: "#f2f2f2" }}>
                    {" "}
                    {/* 테이블 헤더 색상 변경 */}
                    <TableCell
                      style={{
                        width: "33%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        padding: "10px",
                        border: "1px solid #ddd",
                        textAlign: "center",
                        fontWeight: "bold",
                      }}
                    >
                      문서명
                    </TableCell>
                    <TableCell
                      style={{
                        width: "33%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        padding: "10px",
                        border: "1px solid #ddd",
                        textAlign: "center",
                        fontWeight: "bold",
                      }}
                    >
                      작성자
                    </TableCell>
                    <TableCell
                      style={{
                        width: "33%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        padding: "10px",
                        border: "1px solid #ddd",
                        textAlign: "center",
                        fontWeight: "bold",
                      }}
                    >
                      생성 시간
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {afterHoursDocumentList.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          padding: "10px",
                          border: "1px solid #ddd",
                          textAlign: "center",
                        }}
                      >
                        {item.documentName}
                      </TableCell>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          padding: "10px",
                          border: "1px solid #ddd",
                          textAlign: "center",
                        }}
                      >
                        {item.author}
                      </TableCell>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          padding: "10px",
                          border: "1px solid #ddd",
                          textAlign: "center",
                        }}
                      >
                        {item.creationTime}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Container>
        </div>
      </Paper>
    </div>
  );
};

export default DashTable;
