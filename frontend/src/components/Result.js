import { Typography } from '@mui/material';
import React from 'react';
import { Badge } from 'react-bootstrap';

const Result = ({ rows }) => {
    const ownerPath = "C:\\Users\\dswhd\\OneDrive\\문서\\디포 자료\\행복의류 증거데이터 v0811\\구매팀_강수민(대리)";
    const owner = "강수민"
    return (
        <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
            {rows.map((row, index) => (

                    <article key={index}>
                        <header>
                            <Typography variant="h6"><Badge>{owner}</Badge>{row.file_path.replace(ownerPath, "")}</Typography>
                        </header>
                        <section>

                            {/* <Typography variant="h6">{row.plain_text}</Typography> */}
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
    );
};

export default Result;