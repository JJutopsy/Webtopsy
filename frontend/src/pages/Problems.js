import React, { useState, useEffect } from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Header from '../components/Header';
import StickyFooter from '../components/StickyFooter';
import Table from 'react-bootstrap/Table';
import { createTheme, ThemeProvider } from '@mui/material';
import problemList from '../res/data.json'
import { Link } from 'react-router-dom';
export default function Problem() {
    const [dataList, setDataList] = useState([]);
    useEffect(() => {
        setDataList(problemList.problem_list);
    }, [])
    console.log(problemList);
    const theme = createTheme({
        typography: {
            fontFamily: "'Galmuri9', sans-serif;",
        }

    });
    return (
        <>

            <Container component="main" sx={{ mt: 5 }} maxWidth="lg">
                <ThemeProvider theme={theme}>
                    <Typography variant='h3' id="problem">Problem Set</Typography>
                    <Typography variant='h5'>다양한 문제를 풀어 보아요.</Typography>
                </ThemeProvider>
                <CssBaseline><br></br></CssBaseline>
                <Table striped bordered hover size="sm" >
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Name</th>
                            <th><center>Author</center></th>
                            <th>Solved</th>
                        </tr>
                    </thead>
                    <tbody>
                        {
                            dataList ? dataList.map((item, index) => {
                                return (
                                    <tr className='problemTable'>
                                        <td>{item.no}</td>
                                        <td >
                                            <Link to={`/problem/${item.no}`}>{item.title}</Link>
                                        </td>
                                        <td className='author'>
                                            <center><Link to={`/users/${item.author}`}>{item.author}</Link></center>
                                        </td>
                                        <td>{item.solved}</td>
                                    </tr>

                                )
                            }) : ''
                        }
                    </tbody>
                </Table>
            </Container>
            <StickyFooter />
        </>
    );
}