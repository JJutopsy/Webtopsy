import React, { useState } from "react";
import CssBaseline from "@mui/material/CssBaseline";
import Container from "@mui/material/Container";
import { AppBar, Box, Button, Stack, Toolbar, Typography } from "@mui/material";
import { Tab, Tabs } from 'react-bootstrap';
import PostList from "../components/PostList";
import CommentsList from "../components/CommentsList";
import './Viewer.css'
import IconButton from '@material-ui/core/IconButton';
import SettingsIcon from '@material-ui/icons/Settings';
import NotificationsIcon from '@material-ui/icons/Notifications';
import HelpIcon from '@material-ui/icons/Help';
import Dashboard from "./Dashboard";
import DashTable from "../components/DashTable";
import EmailList from "../components/EmailList";
import { useRecoilState } from "recoil";
import { LoginName } from "../atom/LoginName";
import { Link } from 'react-router-dom';

export default function Viewer() {
  const [User, setUser] = useRecoilState(LoginName);
  const [key, setKey] = useState('first');
  const dataString = localStorage.getItem('caseInfo');
  const caseInfo = JSON.parse(dataString);
  return (
    <>
      <div style={{ position: "sticky", top: 0, zIndex: 1 }}>
        <AppBar position="sticky" style={{ height: '50px', backgroundColor: '#0d6efd', boxShadow: 'none' }}>
          <Toolbar style={{ minHeight: '50px', display: 'flex', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex' }}>
              <Stack direction={'row'} spacing={1}>
                <Typography variant="h6" component="div" sx={{ flexGrow: 1, lineHeight: '50px', fontWeight: "bold" }}>
                  <Link to="/case" style={{ color: 'inherit', textDecoration: 'none' }}>Webtopsy</Link>
                </Typography>

                <Typography variant="h6" component="div" sx={{ flexGrow: 1, lineHeight: '50px' }}>
                  |
                </Typography>
                <Typography variant="h6" component="div" sx={{ flexGrow: 1, lineHeight: '50px', fontWeight: "bold" }}>
                  {caseInfo.casename}
                </Typography>
              </Stack>
            </div>
            <div>
              <Stack direction={'row'} spacing={1}>
                <Button color="inherit">TimeZone : KST (UTC+9)</Button>
                <IconButton color="inherit">
                  <SettingsIcon />
                </IconButton>
                <IconButton color="inherit">
                  <NotificationsIcon />
                </IconButton>
                <IconButton color="inherit">
                  <HelpIcon />
                </IconButton>
                <Button color="inherit">{User}</Button>
              </Stack>
            </div>
          </Toolbar>
        </AppBar>
        <Tabs
          id="controlled-tab-example"
          activeKey={key}
          onSelect={(k) => setKey(k)}
          style={{
            position: "sticky",
            top: 50,
            backgroundColor: "white",
            zIndex: 10
          }}
        >
          <Tab eventKey="first" title="Dashbaord" >
            <Box>
              <br></br>
              <DashTable db_path={caseInfo.parsingDBpath} />
            </Box>
          </Tab>
          <Tab eventKey="second" title="Search & Review">
            <PostList />
          </Tab>
          <Tab eventKey="third" title="Email Investigation">
            <EmailList />
          </Tab>
        </Tabs>
      </div>
    </>
  );
}
