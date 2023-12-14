import { Box, Typography } from '@mui/material';
import React, { useState } from 'react';
import { Badge, Tab, Tabs } from 'react-bootstrap';
import { FaArrowRight } from 'react-icons/fa';
import CodeWithEmails from './CodeWithEmails';

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
                                                <span>{row.date}　</span>
                                                <span>[ {row.sender}</span>
                                                <FaArrowRight className="mx-2" />
                                                <span style={{
                                                    maxWidth: '30ch',
                                                    whiteSpace: 'nowrap',
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                }}>{row.receiver} ]</span>

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
                    <CodeWithEmails code={selectedText} db_path={db_path} />
                </Box>
            )}
        </Box>
    );
};

export default EmailResult;
