import * as React from "react";
import { useState, useCallback, useRef } from "react";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import { SurveyCreatorWidget } from "../components/SurveyCreator/SurveyCreator";
import Box from "@mui/material/Box";
import Tab from "@mui/material/Tab";
import TabContext from "@mui/lab/TabContext";
import TabList from "@mui/lab/TabList";
import TabPanel from "@mui/lab/TabPanel";
import { Model } from "survey-core";
import { Survey } from "survey-react-ui";
import { json } from "../components/json";
import Textarea from "@mui/joy/Textarea";

import { usePdf } from "@mikecousins/react-pdf";

function Pathway() {
  const [value, setValue] = React.useState("1");
  const [page, setPage] = useState(1);
  const canvasRef = useRef(null);

  const { pdfDocument, pdfPage } = usePdf({
    file: "http://localhost:3000/1.pdf",
    page,
    canvasRef,
  });
  const [answer, setAnswer] = React.useState({});
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  const survey = new Model(json);
  survey.focusFirstQuestionAutomatic = false;

  const alertResults = useCallback((sender) => {
    const results = JSON.stringify(sender.data);
    console.log("result data : " + JSON.stringify(sender.data, null, 3));
    alert(results);
    survey2.data = results;
  }, []);

  survey.onComplete.add(alertResults);
  //survey.mode = "display";

  const survey2 = new Model(json);
  survey2.onComplete.add((sender, options) => {
    console.log("result data : " + JSON.stringify(sender.data, null, 3));
  });
  survey2.data = {
    VisitCount: 5,
    BasicInfo: {
      height: 170,
      weight: 60,
      HbA1c: 100,
    },
    lastdate: "2023-10-25T17:00",
  };
  survey2.mode = "display";

  return (
    <>
      {" "}
      <header>
        <h1>Pathway</h1>
      </header>
      <Stack spacing={2} direction="row" justifyContent="flex-end">
        <Button variant="outlined" style={{ textTransform: "none" }}>
          Read Data Management
        </Button>
        <Button variant="outlined" style={{ textTransform: "none" }}>
          Write Data Management
        </Button>
        <Button variant="outlined" style={{ textTransform: "none" }}>
          Create Pathway
        </Button>
        <Button
          variant="outlined"
          style={{ textTransform: "none" }}
          color="error"
        >
          Delete
        </Button>
        <Button
          variant="outlined"
          style={{ textTransform: "none" }}
          color="success"
        >
          Export
        </Button>
      </Stack>
      <br></br>
      {/* <SurveyCreatorWidget></SurveyCreatorWidget> */}
      <Box sx={{ width: "100%", typography: "body1" }}>
        <TabContext value={value}>
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <TabList onChange={handleChange} aria-label="lab API tabs example">
              <Tab
                label="Upload JSON"
                style={{ textTransform: "none" }}
                value="1"
              />
              <Tab
                label="Preview Write Data From"
                style={{ textTransform: "none" }}
                value="2"
              />
              <Tab
                label="Show Example Write Data"
                style={{ textTransform: "none" }}
                value="3"
              />
            </TabList>
          </Box>
          <TabPanel value="1">
            <Textarea minRows={20} placeholder={JSON.stringify(json)} />
            <br></br>
            <Button
              variant="contained"
              style={{ textTransform: "none" }}
              color="success"
            >
              Upload
            </Button>
            <div>
              {!pdfDocument && <span>Loading...</span>}
              <canvas ref={canvasRef} />
              {Boolean(pdfDocument && pdfDocument.numPages) && (
                <nav>
                  <ul className="pager">
                    <li className="previous">
                      <button
                        disabled={page === 1}
                        onClick={() => setPage(page - 1)}
                      >
                        Previous
                      </button>
                    </li>
                    <li className="next">
                      <button
                        disabled={page === pdfDocument.numPages}
                        onClick={() => setPage(page + 1)}
                      >
                        Next
                      </button>
                    </li>
                  </ul>
                </nav>
              )}
            </div>
          </TabPanel>
          <TabPanel value="2">
            <Survey model={survey} />
          </TabPanel>
          <TabPanel value="3">
            <Survey model={survey2}></Survey>
          </TabPanel>
        </TabContext>
      </Box>
    </>
  );
}

export default Pathway;
