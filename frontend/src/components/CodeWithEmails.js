import React from 'react';
import { Tab, Tabs } from 'react-bootstrap';

const CodeWithEmails = ({code, db_path}) => {
    const lines = code && code.body.split('\n');
    const [activeTab, setActiveTab] = useState('plain');
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
            <Tab eventKey='plain' title={본문}>
                                
            </Tab>
            </Tabs>
        </div>
    );
};

export default CodeWithEmails;