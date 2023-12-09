import React, { useState } from 'react';
import { Typography, Box } from '@mui/material';
import { Badge } from 'react-bootstrap';
import CodeWithComments from './CodeWithComments';
import { useRecoilState } from 'recoil';
import { LoginName } from '../atom/LoginName';

const Result = ({ rows ,db_path}) => {
    const [User, setUser] = useRecoilState(LoginName);
    const [selectedText, setSelectedText] = useState(null);
    const [selectedRow, setSelectedRow] = useState(null);
    const ownerPath = "C:\\Users\\dswhd\\OneDrive\\문서\\카카오톡 받은 파일";
    const owner = "서종찬"

    const handleClick = (row) => {
        setSelectedText(row);
        setSelectedRow(row);
    }

    return (
        <Box display="flex" flexDirection={selectedText ? 'row' : 'column'} >
            <Box flex={selectedText ? 0.5 : 1}>
                <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                {rows.map((row, index) => (
                    <article key={index} onClick={() => handleClick(row)}>
                        <header>
                            <Typography variant="h6" style={selectedRow === row ? { fontWeight: 'bold' } : {}}><Badge>{owner}</Badge>{row.file_path.replace(ownerPath, "")}</Typography>
                        </header>
                        <section>
                            <div style={{ display: 'flex' }}>
                                {row.tags.map((tagObj, tagIndex) => (
                                    <div className="tagCard" key={tagIndex}>
                                        <span className="status" style={{ backgroundColor: tagObj.color }}></span>
                                        <span>{tagObj.tag}</span>
                                    </div>
                                ))}
                            </div>
                            <span>{row.m_time}</span>
                        </section>
                        <hr></hr>
                    </article>
                ))}
                </div>
            </Box>
            {selectedText && 
                <Box flex={0.5} style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                    <CodeWithComments code={selectedText} db_path={db_path}/>
                </Box>
            }
        </Box>
    );
};

export default Result;
