import { Box, Typography } from '@mui/material';
import React, { useState } from 'react';
import { Badge, Tab, Tabs } from 'react-bootstrap';
import { FaArrowRight } from 'react-icons/fa';

const EmailResult = ({ rows, db_path }) => {
    const [selectedRow, setSelectedRow] = useState(null);
    const [selectedText, setSelectedText] = useState(null);

    const handleClick = (row) => {
        setSelectedText(row);
        setSelectedRow(row);
    };

    return (
        <Box display="flex">
            <Box flex={1} style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                <Tabs
                    defaultActiveKey="default"
                    id="justify-tab-example"
                    className="mb-3"
                    justify
                    style={{
                        position: "sticky",
                        top: 0,
                        paddingRight: 25
                    }}
                >
                    <Tab eventKey='default' title={<span>검색 결과 <Badge variant="secondary">{rows.length}</Badge></span>}>
                        <div>
                            <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                                {rows && rows.map((row, index) => (
                                    <article key={index} onClick={() => handleClick(row)}>
                                        <header>
                                            <Typography variant="h6" style={selectedRow === row ? { fontWeight: 'bold' } : {}}>{row.subject}</Typography>
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
                                            <div className="d-flex align-items-center">
                                                <span>{row.sender}</span>
                                                <FaArrowRight className="mx-2" />
                                                <span>{row.receiver}</span>
                                            </div>
                                        </section>
                                        <hr></hr>
                                    </article>
                                ))}
                            </div>
                        </div>
                    </Tab>
                </Tabs>
            </Box>
            {selectedText && (
                <Box flex={1} style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                   
                </Box>
            )}
        </Box>
    );
};

export default EmailResult;
