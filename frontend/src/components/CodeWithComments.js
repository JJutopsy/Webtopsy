import React, { useState } from 'react';
import { Modal, Button, Dropdown } from 'react-bootstrap';
import './CodeWithComments.css';
import { BsThreeDots } from 'react-icons/bs';
const CodeWithComments = ({ code }) => {
    const [show, setShow] = useState(false);
    const [selectedLine, setSelectedLine] = useState(null);
    const [highlightedLine, setHighlightedLine] = useState(null);
    const [dropdownLine, setDropdownLine] = useState(null);

    const handleClose = () => setShow(false);
    const handleShow = (lineNumber) => {
        setSelectedLine(lineNumber);
        setHighlightedLine(lineNumber);
        setDropdownLine(lineNumber);
    };

    const lines = code.split('\n');

    return (
        <div>
            <div style={{ fontFamily: 'monospace' }}>
                {lines.map((line, index) => (
                    <div key={index} style={highlightedLine === index + 1 ? { backgroundColor: 'yellow' } : {}}>
                        <code style={{ display: 'flex', alignItems: 'center' }}>
                            {dropdownLine === index + 1 ? (
                                <Dropdown>
                                    <Dropdown.Toggle variant="primary" id="dropdown-basic" style={{ border: 'none', marginRight: '5px' ,padding: '2px 10px' }}>
                                        <BsThreeDots size={15}/>
                                    </Dropdown.Toggle>
                                    <Dropdown.Menu>
                                        <Dropdown.Item href="#/action-1">태그 설정</Dropdown.Item>
                                        <Dropdown.Item onClick={() => {setShow(true)}}>코멘트 작성</Dropdown.Item>
                                        <Dropdown.Item href="#/action-3"></Dropdown.Item>
                                    </Dropdown.Menu>
                                </Dropdown>
                            ) : (<div className='block'></div>)}
                            <span className="line" onClick={() => handleShow(index + 1)}>
                                {index + 1}
                            </span>
                            <span style={{maxWidth:'80%'}}>{line}</span>
                        </code>
                    </div>
                ))}
            </div>

            <Modal show={show} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Comment on line {selectedLine}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <textarea
                        style={{ width: '100%', height: '200px' }}
                        placeholder="Write your comment here..."
                    />
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        Close
                    </Button>
                    <Button variant="primary" onClick={handleClose}>
                        Save Changes
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
};

export default CodeWithComments;

