import React, { useState } from 'react';
import { FaHeart } from "react-icons/fa";
import Textarea from "@mui/joy/Textarea";
import { Button, Container, Stack } from "@mui/material";

function Footer() {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFocus = () => {
    setIsExpanded(true);
  }

  const handleBlur = () => {
    setIsExpanded(false);
  }

  return (
    <footer>
      <Container fixed style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Stack direction="column" spacing={2}>
          <Textarea
            minRows={1}
            style={{ width: '600px' }}
            placeholder="Keyword Search "
            onFocus={handleFocus}
            onBlur={handleBlur}
          />
          {isExpanded && 
            <Button variant="contained" color="primary">
              추가 버튼
            </Button>
          }
        </Stack>

      </Container>
      <p>Project JJtopsy</p>
    </footer>
  );
}

export default Footer;