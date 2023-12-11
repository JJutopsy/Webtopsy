import React, { useEffect, useState } from 'react';
import { Typography, Box } from '@mui/material';
import { Badge, Tab, Tabs } from 'react-bootstrap';
import CodeWithComments from './CodeWithComments';


const Result = ({ rows, db_path }) => {
    const [selectedText, setSelectedText] = useState(null);
    const [selectedRow, setSelectedRow] = useState(null);
    const [resultSimilarity, setResultSimilarity] = useState({});
    const [hashSim, setHashSim] = useState([]);
    const [mediaSim, setMediaSim] = useState([]);
    const [totalSim, setTotalSim] = useState([]);
    const handleClick = (row) => {
        setSelectedText(row);
        setSelectedRow(row);
    }
    const handleResult = async (result) => {
        const { identical_documents, similar_information_docs, similar_media } = result;
      
        const fetchDocument = async (id) => {
          const req = { db_path: db_path }
          const response = await fetch(`http://localhost:5000/keyword/${id}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            }, body: JSON.stringify(req)
          });
          let data = await response.json();
      
          const getRandomColor = () => {
            const letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
              color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
          };
      
          let tagDict = {};
          let nameDict = {};
      
          // Process single data item
          const tags = data.tag.split(',').filter(e => e.trim().length > 1).map(tag => {
            if (!tagDict[tag]) {
              tagDict[tag] = {
                color: getRandomColor(),
                count: 1
              };
            } else {
              tagDict[tag].count += 1;
            }
            return {
              tag,
              color: tagDict[tag].color,
              count: tagDict[tag].count
            };
          });
          
          const names = data.NNP.split(',').filter(e => {
            const name = e.replace("_인명", "").trim();
            return e.includes("_인명") && /^[\uAC00-\uD7A3]*$/.test(name) && name.length >= 2 && name.length <= 3
          }).map(name => {
            name = name.replace("_인명", "").trim();
            if (!nameDict[name]) {
              nameDict[name] = {
                color: getRandomColor(),
                count: 1
              };
            } else {
              nameDict[name].count += 1;
            }
            return {
              name,
              color: nameDict[name].color,
              count: nameDict[name].count
            };
          });
      
          const owner = data.owner.split(',').map(e => e.trim());
      
          data = {
            ...data,
            tags,
            names,
            owner
          };
      
          return data;
        };
      
        if (identical_documents) {
          const hashSim = await Promise.all(identical_documents.map((doc) => fetchDocument(doc.id)));
          setHashSim(hashSim);
        }
      
        if (similar_media) {
          const mediaSim = await Promise.all(similar_media.map((doc) => fetchDocument(doc.id)));
          setMediaSim(mediaSim);
        }
      
        if (similar_information_docs) {
          const totalSim = await Promise.all(similar_information_docs.map((doc) => fetchDocument(doc.id)));
          setTotalSim(totalSim);
        }
      };
      
    useEffect(() => {
        handleResult(resultSimilarity);
    }, [resultSimilarity])
    return (
        <>

            <Box display="flex" flexDirection={selectedText ? 'row' : 'column'} >
                <Box flex={selectedText ? 0.5 : 1}>
                    <Tabs
                        defaultActiveKey="default"
                        id="justify-tab-example"
                        className="mb-3"
                        justify
                        style={{
                            position: "sticky",
                            top: 0,

                            paddingRight: 25
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
                        <Tab eventKey='t1' title={ hashSim && hashSim.length !== 0
                            ? <span>해시값 일치 <Badge variant='secondary'>
                                {hashSim.length}</Badge></span> : "해시값 일치"} disabled={hashSim && hashSim.length === 0}>
                            <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                                {hashSim.map((row, index) => (
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
                        <Tab eventKey='t2' title={mediaSim && mediaSim.length !== 0
                            ? <span>미디어 일치 <Badge variant='secondary'>
                                {mediaSim.length}</Badge></span> : "미디어 일치"} disabled={mediaSim && mediaSim.length === 0}>
                            <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                                {mediaSim.map((row, index) => (
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
                        <Tab eventKey='t3' title={totalSim && totalSim.length !== 0
                            ? <span>유사 문서 <Badge variant='secondary'>
                                {totalSim.length}</Badge></span> : "유사 문서"} disabled={totalSim && totalSim.length === 0}>
                                <div style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                                {totalSim.map((row, index) => (
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
                    </Tabs>
                </Box>
                {selectedText &&
                    <Box flex={0.5} style={{ maxHeight: '80vh', overflowY: 'scroll' }}>
                        <CodeWithComments code={selectedText} db_path={db_path} setResultSimilarity={setResultSimilarity} />
                    </Box>
                }
            </Box>

        </>
    );
};

export default Result;
