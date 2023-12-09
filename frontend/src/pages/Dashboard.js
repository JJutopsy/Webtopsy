import { Container, Grid, Paper, Typography } from "@mui/material";
import { Stack } from "react-bootstrap";
import { Doughnut } from "react-chartjs-2";
import { BarChart } from '@mui/x-charts/BarChart';

const Dashboard = () => {

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
  const uData = [4000, 3000, 2000,];
  const ppdata = [1000, 2000, 1300];
  const pData = [2400, 1398, 9800,];


  const xLabels = [
    '이종민의 PC',
    '손석훈의 노트북',
    '고수민.zip',
  ];
  return (
    <>
      <br></br>
      <div >
        <Grid container spacing={3}>
          <Grid item xs={2} sm={6} md={4}>
            <Paper style={{ height: '100%', padding: '1rem' }}>
              <Stack>
                <Typography variant="h6" align="center">Case 정보 전체 요약</Typography>
              </Stack>
              <div style={{ height: '300px', width: '500px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Doughnut data={pieChartData} />
              </div>
              
            </Paper>
          </Grid>
          <Grid item xs={2} sm={6} md={4}>
            <Paper style={{ height: '100%', padding: '1rem' }}>
              <Stack>
                <Typography variant="h6" align="center">인풋 데이터 분석</Typography>
              </Stack>
              <BarChart
                width={500}
                height={300}
                series={[
                  {
                    data: pData,
                    label: 'docx',
                    id: 'pvId',

                    yAxisKey: 'leftAxisId',
                  },
                  {
                    data: ppdata,
                    label: 'pdf',
                    id: 'ppId',
                    yAxisKey: 'centerAxisId',
                  },
                  {
                    data: uData,
                    label: 'hwp',
                    id: 'uvId',

                    yAxisKey: 'rightAxisId',
                  },
                ]}
                xAxis={[{ data: xLabels, scaleType: 'band' }]}
                yAxis={[{ id: 'leftAxisId' }, { id: 'centerAxisId' }, { id: 'rightAxisId' }]}
              />
            </Paper>
          </Grid>
          <Grid item xs={2} sm={6} md={4}>
            <Paper style={{ height: '100%', padding: '1rem' }}>Block3</Paper>
          </Grid>
          <Grid item xs={2} sm={6} md={4}>
            <Paper style={{ height: '100%', padding: '1rem' }}>Block4</Paper>
          </Grid>
          <Grid item xs={2} sm={6} md={4}>
            <Paper style={{ height: '100%', padding: '1rem' }}>Block5</Paper>
          </Grid>
          <Grid item xs={2} sm={6} md={4}>
            <Paper style={{ height: '100%', padding: '1rem' }}>Block6</Paper>
          </Grid>
        </Grid>
      </div>


    </>
  );
};

export default Dashboard;
