import React, { useEffect, useState } from 'react';
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
    useEffect(()=>{
        fetchData();
    },[]);

    return (
        <div>
           
        </div>
    );
};

export default EmailList;
