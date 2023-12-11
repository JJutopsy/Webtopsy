import React, { useEffect, useState } from 'react';
import { Modal, Button, Dropdown, Tabs, Tab, Table, Badge, OverlayTrigger, Tooltip, ListGroup, Form, Spinner } from 'react-bootstrap';
import './CodeWithComments.css';
import { BsThreeDots } from 'react-icons/bs';
import { useRecoilState } from 'recoil';
import { LoginName } from '../atom/LoginName';
import { Stack } from '@mui/material';
const CodeWithEmails = ({ code, db_path, setResultSimilarity }) => {
    const [activeTab, setActiveTab] = useState('plain');
    const [User, setUser] = useRecoilState(LoginName);
    const [show, setShow] = useState(false);
    const [selectedLine, setSelectedLine] = useState(null);
    const [message, setMessage] = useState("");
    const [highlightedLine, setHighlightedLine] = useState(null);
    const [highlightedLines, setHighlightedLines] = useState([]);
    const [dropdownLine, setDropdownLine] = useState(null);
    const [comment, setComment] = useState("");
    const [comments, setComments] = useState([]);
    const [fetchedLines, setFetchedLines] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleClose = () => setShow(false);
    const fetchComments = async () => {
        try {
            const response = await fetch(`http://localhost:5000/comment/email/${code.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ db_path: db_path }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setComments(data);
            setFetchedLines(data.map(comment => parseInt(comment.type)));
        } catch (error) {
            console.error('Fetching comments failed: ', error);
        }
    };

    useEffect(() => {
        fetchComments();
    }, [code.id, db_path, activeTab]);
    const isLineHighlighted = (lineNumber) => {
        return comments.some(comment => comment.type === lineNumber);
    }

    const getCommentsForLine = (lineNumber) => {
        return comments.filter(comment => comment.type === lineNumber);
    }
    const handleShow = (lineNumber) => {
        if (selectedLine === lineNumber) {
            setSelectedLine(null);
            setHighlightedLine(null);
            setDropdownLine(null);
            setHighlightedLines([]);
        } else {
            setSelectedLine(lineNumber);
            setHighlightedLine(lineNumber);
            setDropdownLine(lineNumber);
            setHighlightedLines([lineNumber]);
        }
    };

    const handleCommentChange = (e) => {
        setComment(e.target.value);
    };
    const handleLineClick = (lineNumber) => {
        setActiveTab('plain');
        // 스크롤을 해당 라인으로 이동시킵니다.
        // scroll.scrollTo(lineNumber * lineHeight); // lineHeight는 라인의 높이를 나타내는 값입니다.
    };
    const handleFind = () => {
        setIsLoading(true);
        setResultSimilarity({});
        const data = {
            parsingDBpath: db_path,
            key_document_id: code.id
        }
        fetch('http://localhost:5000/similarity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }).then(response => response.json()).then(data => {
            setResultSimilarity(data);
            setIsLoading(false);
        }).catch((error) => {
            console.log('Error', error);
            setIsLoading(false);
        })
    }
    const submitComment = () => {
        const newComment = {
            post_id: code.id,
            username: User || "Anonymous",
            context: comment,
            type: selectedLine,
            db_path: db_path
        };
        console.log(newComment);
        fetch('http://localhost:5000/comment/email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newComment),
        }).then(response => response.json()).then(data => {
            console.log('Success:', data);
        }).catch((error) => {
            console.error('Error:', error);
        });
        setComment("");
        fetchComments();
    }
    const lines = code.body.split('\n');

    return (
        <div>
            <Tabs
                defaultActiveKey="plain"
                onSelect={(k) => setActiveTab(k)}
                id="justify-tab-example"
                className="mb-3"
                justify
                style={{
                    position: "sticky",
                    top: 0,
                    backgroundColor: "#E9EDF5",
                }}
            >
                <Tab eventKey="plain" title={<span>본문 <Badge variant="secondary">{comments.length}</Badge></span>} onClick={() => setActiveTab("plain")}>
                    <div style={{ fontFamily: 'monospace' }}>
                        {lines.map((line, index) => {
                            const lineNumber = index + 1;
                            const commentsForLine = comments.filter(comment => parseInt(comment.type) === lineNumber); //해당 라인에 대한 모든 코멘트를 찾습니다.
                            const renderTooltip = (props) => (
                                <Tooltip id={`line-${lineNumber}-tooltip`} {...props} bsPrefix="tooltip-custom">
                                    {commentsForLine.map((comment, i) => (
                                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', }}>
                                            <span>{`${comment.username}: ${comment.context}`}</span>
                                            <span style={{ marginLeft: 'auto' }}>{`${comment.created_at}`}</span>
                                        </div>
                                    ))}
                                </Tooltip>
                            );
                            return (
                                <div style={fetchedLines.includes(lineNumber) || highlightedLines.includes(lineNumber) ? { backgroundColor: '#FFF78A' } : {}}>
                                    <code style={{ display: 'flex', alignItems: 'center' }}>
                                        {dropdownLine === index + 1 ? (
                                            <Dropdown>
                                                <Dropdown.Toggle variant="primary" id="dropdown-basic" style={{ border: 'none', marginRight: '5px', padding: '2px 10px' }}>
                                                    <BsThreeDots size={15} />
                                                </Dropdown.Toggle>
                                                <Dropdown.Menu>
                                                    <Dropdown.Item onClick={() => { setShow(true) }}>코멘트 작성</Dropdown.Item>
                                                </Dropdown.Menu>
                                            </Dropdown>
                                        ) : (<div className='block'></div>)}
                                        {commentsForLine.length > 0 ? (
                                            <OverlayTrigger
                                                key={index}
                                                placement="bottom"
                                                overlay={renderTooltip}
                                            >
                                                <span className="line" onClick={() => handleShow(index + 1)}>
                                                    {index + 1}
                                                </span>
                                            </OverlayTrigger>
                                        ) : (
                                            <span className="line" onClick={() => handleShow(index + 1)}>
                                                {index + 1}
                                            </span>
                                        )}
                                        <span style={{ maxWidth: '80%' }}>{line}</span>
                                    </code>
                                </div>
                            );
                        })}

                    </div>
                </Tab>
                <Tab eventKey="metadata" title="이메일 스레딩" onClick={() => setActiveTab("metadata")}>
                   
                </Tab>
            </Tabs>


            <Modal show={show} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Comment on line {selectedLine}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <h5>Previous comments:</h5>
                    <ListGroup>
                        {comments.filter(comment => parseInt(comment.type) === selectedLine).map((comment, i) => (
                            <ListGroup.Item key={i}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <div>{`${comment.username}: ${comment.context}`}</div>
                                    <div>{comment.created_at}</div>
                                </div>
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                    <Form.Control
                        as="textarea"
                        style={{ marginTop: '10px' }}
                        placeholder="Write your comment here..."
                        onChange={handleCommentChange}
                        value={comment}
                    />
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        닫기
                    </Button>
                    <Button variant="primary" onClick={submitComment}>
                        코멘트 작성
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
};

export default CodeWithEmails;

