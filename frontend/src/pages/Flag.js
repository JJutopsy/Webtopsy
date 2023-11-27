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
} from "@mui/material";
import Header from "../components/Header";
import StickyFooter from "../components/StickyFooter";

Chart.register(ArcElement);
Chart.register(CategoryScale);
Chart.register(...registerables);

const theme = createTheme();

const Flag = () => {
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
      label: "자주 언급된 단체",
      data: {
        labels: ["T1", "GenG", "KT", "LCK", "WBG"],
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
            data: [100, 80, 70, 65, 52],
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
      documentName: "example1.pdf",
      creationTime: "2023-06-11 14:34:56",
      note: "경쟁사 GenG 언급",
    },
    {
      documentName: "example2.pdf",
      creationTime: "2023-06-13 12:21:43",
      note: "거래내역 불일치",
    },
    {
      documentName: "example3.docx",
      creationTime: "2023-06-16 10:11:46",
      note: "본인 소관 외 문서",
    },
    // ... rest of the data
  ];

  const afterHoursDocumentList = [
    {
      documentName: "example4.docx",
      author: "문현준",
      creationTime: "2023-06-01 19:30:33",
    },
    {
      documentName: "example5.pdf",
      author: "문현준",
      creationTime: "2023-06-02 22:00:45",
    },
    {
      documentName: "example6.hwp",
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
    <ThemeProvider theme={theme}>
      <Container component="main" sx={{ mt: 5 }} maxWidth="lg">
        <Header />
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "20px",
            height: "600px",
            backgroundColor: "#E9EDF5",
          }}
        >
          {/* Recent Bookmark List */}
          <div
            style={{
              gridArea: "1 / 2 / 2 / 3",
              width: "100%",
              flexGrow: 1,
              marginBottom: "20px",
            }}
          >
            <h2>최근 생성 북마크 목록</h2>
            <TableContainer>
              <Table sx={{ minWidth: 650 }}>
                <TableHead>
                  <TableRow>
                    <TableCell
                      style={{
                        width: "33%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
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
                        }}
                      >
                        {item.documentName}
                      </TableCell>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                      >
                        {item.creationTime}
                      </TableCell>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                      >
                        {item.note}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </div>

          {/* Doughnut Chart */}
          <Paper elevation={3}>
            <div
              style={{
                gridArea: "1 / 1 / 2 / 2",
                width: "100%",
                height: "200px",
              }}
            >
              <h2>주요 확장자 분포</h2>
              <Doughnut data={pieChartData} options={doughnutOptions} />
            </div>
          </Paper>
          {/* Bar Chart */}
          <div
            style={{
              width: "400px",
              height: "200px",
              marginBottom: "20px",
            }}
          >
            <h2>주요 키워드</h2>
            
            <Tabs value={currentBarChart} onChange={handleTabChange} centered style={{width:"300px"}}>
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

          {/* After Hours Document List */}
          <div
            style={{
              width: "100%",
              flexGrow: 1,
              marginBottom: "20px",
            }}
          >
            <h2>업무시간 외 생성 문서 목록</h2>
            <TableContainer>
              <Table sx={{ minWidth: 650 }}>
                <TableHead>
                  <TableRow>
                    <TableCell
                      style={{
                        width: "33%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
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
                        }}
                      >
                        {item.documentName}
                      </TableCell>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                      >
                        {item.author}
                      </TableCell>
                      <TableCell
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                      >
                        {item.creationTime}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </div>
        </div>
      </Container>
      <StickyFooter />
    </ThemeProvider>
  );
};

export default Flag;
