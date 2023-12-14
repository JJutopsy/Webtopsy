import React, { useEffect, useState } from 'react';
import { Modal, Button, Dropdown, Tabs, Tab, Table, Badge, OverlayTrigger, Tooltip, ListGroup, Form, Spinner } from 'react-bootstrap';
import Toast from 'react-bootstrap/Toast';
import ToastContainer from 'react-bootstrap/ToastContainer';

import './CodeWithComments.css';
import { BsThreeDots } from 'react-icons/bs';
import { useRecoilState } from 'recoil';
import { LoginName } from '../atom/LoginName';
import { Box, Stack } from '@mui/material';
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
    const [thread, setThread] = useState({});

    const handleClose = () => setShow(false);
    const fetchComments = async () => {
        try {
            const response = await fetch(`/comment/email/${code.id}`, {
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
        handleFind();
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
    const downloadBase64File = (base64Data, filename) => {
        const byteCharacters = atob(base64Data);
        const byteArrays = [];

        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
            const slice = byteCharacters.slice(offset, offset + 512);
            const byteNumbers = new Array(slice.length);
            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }

        const blob = new Blob(byteArrays);
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    }
    const handleFind = () => {
        setIsLoading(true);
        setThread({});
        const data = {
            parsingDBpath: db_path,
            email_subject: code.subject
        }
        fetch('/emlthread', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }).then(response => response.json()).then(data => {
            setThread(data);
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
        fetch('/comment/email', {
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
                <Tab eventKey='info' title="파일 정보">
                    <Table striped bordered hover style={{ width: "50wv" }}>
                        <thead>
                            <tr>
                                <th>메타데이터</th>
                                <th>값</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th>파일 경로</th>
                                <th>
                                    {code.file_path}

                                </th>
                            </tr>
                        </tbody>
                    </Table>
                </Tab>
                <Tab eventKey="metadata" title="이메일 스레딩" onClick={() => setActiveTab("metadata")}>
                    <Box width={'100%'}>
                        <Stack direction={'column'} spacing={1}>
                            {thread.related_emails && thread.related_emails.map((email, i) => (
                                <Box>
                                    <Stack direction={'row'} justifyContent={code.sender === email.sender ? 'flex-end' : 'flex-start'}>
                                        <Toast key={1} maxWidth='300px'>
                                            <Toast.Header closeButton={false}>
                                                <img
                                                    src="holder.js/20x20?text=%20"
                                                    className="rounded me-2"
                                                    alt=""
                                                />
                                                <strong className="me-auto">{email.sender}</strong>
                                                <small>{email.date}</small>
                                            </Toast.Header>
                                            <Toast.Body><strong>{email.subject}</strong><hr />{email.body}<hr>
                                            </hr>{email.att_file_name &&
                                                <a onClick={() => downloadBase64File(email.att_file_data, email.att_file_name)} href='#'>
                                                    <strong>첨부파일</strong> : {email.att_file_name}
                                                </a>
                                                }
                                            </Toast.Body>
                                        </Toast>
                                    </Stack>
                                </Box>
                            ))}

                        </Stack>
                    </Box>
                </Tab>
            </Tabs>


            <Modal show={show} onHide={handleClose} dialogClassName="my-modal" aria-labelledby="example-custom-modal-styling-title">
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

