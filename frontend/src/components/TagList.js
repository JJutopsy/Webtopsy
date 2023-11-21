import React, { useState } from "react";
import { Badge } from "react-bootstrap";

function TagList({ tags }) {
  const [showAll, setShowAll] = useState(false);

  const handleShowAll = () => {
    setShowAll(true);
  };

  const handleHide = () => {
    setShowAll(false);
  };

  return (
    <div>
      {tags.slice(0, showAll ? tags.length : 10).map((tag, index) => (
        <Badge key={index} variant="secondary">
          {tag}
        </Badge>
      ))}
      {showAll ? (
        <Badge onClick={handleHide} variant="secondary">
          접기..
        </Badge>
      ) : (
        tags.length > 10 && (
          <Badge onClick={handleShowAll} variant="secondary">
            더보기..
          </Badge>
        )
      )}
    </div>
  );
}
export default TagList;
