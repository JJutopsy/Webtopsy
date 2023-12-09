import React, { useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Box, Button, FormControl, Grid, InputLabel, OutlinedInput, TextField, Typography } from '@mui/material';
import CodeWithComments from './CodeWithComments';

const EmailList = () => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    // 'path' 파라미터 값 복호화
    const db_path = decodeURIComponent(urlParams.get('path'));
    const [search, setSearch] = useState('');
    const [rows, setRows] = useState([]);
    const [selectedCell, setSelectedCell] = useState(null);
    const fetchData = async () => {
        try {
            const json =
            {
                parsingDBpath: db_path,
                keyword: search,
            };

            const response = await fetch('http://localhost:5000/keyword/email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(json)
            });
            const data = await response.json();
            const dataWithId = data.map((item, index) => ({ ...item, id: index }));
            setRows(dataWithId);
        } catch (error) {
            console.error('Failed to fetch data:', error);
        }
    };

    return (
        <div>
            <Box sx={{ display: 'flex', justifyContent: 'center', m: 1, p: 1 }}>
                <FormControl variant="outlined">
                    <InputLabel htmlFor="search-input">Search</InputLabel>
                    <OutlinedInput
                        id="search-input"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        label="Search"
                    />
                </FormControl>
                <Button variant="contained" color="primary" onClick={fetchData} sx={{ mx: 2 }}>
                    Search
                </Button>
            </Box>

            <Grid container>

                    <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                        <DataGrid
                            rows={rows}
                            columns={[
                                { field: 'id', headerName: 'ID', width: 90 },
                                { field: 'subject', headerName: 'Subject', width: 200 },
                                { field: 'sender', headerName: 'Sender', width: 200 },
                                { field: 'receiver', headerName: 'Receiver', width: 200 },
                                { field: 'date', headerName: 'Date', width: 200 },
                            ]}
                            pageSize={5}
                            onCellClick={(cellParams) => {
                                if (selectedCell && selectedCell.id === cellParams.id) {
                                    setSelectedCell(null);
                                } else {
                                    setSelectedCell(cellParams.row);
                                }
                            }}
                        />
                    </div>
                <Grid item xs={5}>
                    <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                        <Button variant='primary'>이메일 스레딩</Button>
                        {selectedCell && (
                            <CodeWithComments code={selectedCell.body} />

                        )}
                    </div>

                </Grid>
            </Grid>
        </div>
    );
};

export default EmailList;
