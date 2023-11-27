import React, { useRef } from "react";

const FileUploadComponent = () => {
  const onChange = (event) => {
    const value = event.target.value;

    // this will return C:\fakepath\somefile.ext
    // console.log(value);

    const files = event.target.files;

    //this will return an ARRAY of File object
    console.log(files);
  };

  return (
    <div>
      <input type="file" onChange={onChange} />
    </div>
  );
};

export default FileUploadComponent;
