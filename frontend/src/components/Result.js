import { Typography } from '@mui/material';
import React from 'react';

const Result = ({ rows }) => {
    const colorList = ['red', 'blue', 'green', 'yellow', 'purple'];

    return (
        <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
            {rows.map((row, index) => (
                <article key={index}>
                    <header>
                        <Typography variant="h6">{row.file_path}</Typography>
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