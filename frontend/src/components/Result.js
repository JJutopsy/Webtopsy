import React, { useState } from 'react';
import { Typography, Box } from '@mui/material';
import { Badge, Tab, Tabs } from 'react-bootstrap';
import CodeWithComments from './CodeWithComments';


const Result = ({ rows, db_path }) => {
    const [selectedText, setSelectedText] = useState(null);
    const [selectedRow, setSelectedRow] = useState(null);
    const [activeTab, setActiveTab] = useState('default'); // 기본적으로 활성화되어 있는 탭
    const handleSpecialFunction = () => {
        setActiveTab('t1'); // 특정 기능이 작동하면 t1 탭으로 변경
        
      };
    const handleClick = (row) => {
        setSelectedText(row);
        setSelectedRow(row);
    }

    return (
        <>

            <Box display="flex" flexDirection={selectedText ? 'row' : 'column'} >
                <Box flex={selectedText ? 0.5 : 1}>
                    <Tabs
                        defaultActiveKey="plain"
                        id="justify-tab-example"
                        className="mb-3"
                        justify
                        activeKey={activeTab} 
                        style={{
                            position: "sticky",
                            top: 0,
                            
                            paddingRight:25
                        }}>
                        <Tab eventKey='default' title={<span>검색 결과 <Badge variant="secondary">{rows.length}</Badge></span>} >
                            <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                                {rows.map((row, index) => (
                                    <article key={index} onClick={() => handleClick(row)}>
                                        <header>
                                            <Typography variant="h6" style={selectedRow === row ? { fontWeight: 'bold' } : {}}><Badge>{row.owner[1]}</Badge>{row.file_path.replace(row.owner[0], "")}</Typography>
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
                        </Tab>
                        <Tab eventKey='t1' title='해시값 일치' disabled>

                        </Tab>
                        <Tab eventKey='t2' title='미디어 파일 일치' disabled>

                        </Tab>
                        <Tab eventKey='t3' title='유사 문서' disabled>

                        </Tab>
                    </Tabs>
                </Box>
                {selectedText &&
                    <Box flex={0.5} style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                        <CodeWithComments code={selectedText} db_path={db_path} />
                    </Box>
                }
            </Box>

        </>
    );
};

export default Result;
