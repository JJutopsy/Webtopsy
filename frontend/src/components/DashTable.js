import React, { useEffect, useState } from "react";
import { Doughnut, Bar } from "react-chartjs-2";
import { Chart, ArcElement, registerables } from "chart.js";
import { CategoryScale } from "chart.js";
import Table from 'react-bootstrap/Table'; // Bootstrap Table을 import 합니다.

import {
  Container,
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

const DashTable = ({ db_path }) => {
  const [pieChartData, setPieChartData] = useState({
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
    total: 0
  });
  // Data settings for charts

  const fetchData = async () => {
    const response = await fetch('/extension_distribution', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ db_path: db_path }),
    });

    const data = await response.json();
    // 데이터를 count 기준으로 내림차순 정렬합니다.
    const sortedData = data.sort((a, b) => b.count - a.count);

    // 상위 5개와 그 외를 구분합니다.
    const topFive = sortedData.slice(0, 5);
    const others = sortedData.slice(5);

    // 상위 5개의 labels와 dataCounts를 구합니다.
    const labels = topFive.map(item => item.name);
    const dataCounts = topFive.map(item => item.count);

    // 나머지는 "기타"로 묶어서 count를 합산합니다.
    const othersCount = others.reduce((sum, item) => sum + item.count, 0);
    if (othersCount > 0) {
      labels.push("기타");
      dataCounts.push(othersCount);
    }

    const total = dataCounts.reduce((sum, count) => sum + count, 0);

    setPieChartData({
      labels: labels,
      datasets: [
        {
          data: dataCounts,
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
      total: total,
    });

    const response1 = await fetch('/frequent_entities', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ db_path: db_path }),
    });
    const response2 = await fetch('/after_hours_documents', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ db_path: db_path }),
    });
    const data2 = await response2.json();
    setAfterHoursDocumentList(data2);
    const response3 = await fetch('/recent_comments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ db_path: db_path }),
    });
    const data3 = await response3.json();
    setRecentBookmarkList(data3);
    const response4 = await fetch('/recent_comments/email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ db_path: db_path }),
    });
    const data4 = await response4.json();
    setEmail(data4);
  }


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
  const [recentBookmarkList, setRecentBookmarkList] = useState([{
    id: 0,
    post_id: 0,
    username: "-",
    context: "-",
    create_at: "-",
    type: "-"
  }]);
  const [email, setEmail] = useState([{}]);
  const [afterHoursDocumentList, setAfterHoursDocumentList] = useState([
    {
      name: "-",
      owner: "-",
      time: "-",
    }
  ]);


   

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "20px",
        height: "900px",
        paddingLeft: "30px",
        paddingRight: "30px"
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
            주요 확장자 분표 ({pieChartData.total.toLocaleString()})
            <hr></hr>
          </Typography>
          <Doughnut data={pieChartData} options={doughnutOptions} />
        </div>
      </Paper>
      <Paper elevation={3}>
        <div
          style={{
            width: "100%",
            flexGrow: 1,
            marginBottom: "20px",
          }}
        >
          <Typography variant="h5" padding={"30px"}>
            최근 생성 코멘트
            <hr></hr>
          </Typography>

          <Container>
            <Table striped bordered hover>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Post ID</th>
                  <th>Username</th>
                  <th>Context</th>
                  <th>Create At</th>
                  <th>Line</th>
                </tr>
              </thead>
              <tbody>
                {recentBookmarkList.length > 0 && recentBookmarkList.map(item => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.post_id}</td>
                    <td>{item.username}</td>
                    <td>{item.context}</td>
                    <td>{item.created_at}</td>
                    <td>{item.type}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Container>
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
          <Table striped bordered hover>
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Onwer</th>
                  <th>Last Modified</th>
                </tr>
              </thead>
              <tbody>
                {afterHoursDocumentList.length >0 && email.map(item => (
                  <tr key={item.id}>
                    <td>{item.name}</td>
                    <td>{item.owner}</td>
                    <td>{item.time}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Container>
        </div>
      </Paper>
      <Paper elevation={3}>
        <div
          style={{
            width: "100%",
            flexGrow: 1,
            marginBottom: "20px",
          }}
        >
          <Typography variant="h5" padding={"30px"}>
            최근 이메일 리뷰 ({email.length})
            <hr></hr>
          </Typography>

          <Container>
            <Table striped bordered hover>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Post ID</th>
                  <th>Username</th>
                  <th>Context</th>
                  <th>Create At</th>
                  <th>Line</th>
                </tr>
              </thead>
              <tbody>
                {email.length >0 && email.map(item => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.post_id}</td>
                    <td>{item.username}</td>
                    <td>{item.context}</td>
                    <td>{item.created_at}</td>
                    <td>{item.type}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Container>
        </div>
      </Paper>
    </div>
  );
};

export default DashTable;
