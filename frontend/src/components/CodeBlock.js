import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { solarizedlight } from "react-syntax-highlighter/dist/esm/styles/prism";

const CodeBlock = ({ value }) => {
  const stringValue = String(value);

  const lines = stringValue.split("\n");
  return (
    <SyntaxHighlighter language="jsx" style={solarizedlight}>
      {lines.map((line, i) => {
        if (i === 2) {
          // 강조하려는 라인 번호를 조정하세요.
          return (
            <span style={{ backgroundColor: "lightyellow" }}>
              {" "}
              {/* 강조할 색상을 변경하세요. */}
              {line}
              <div style={{ fontSize: "0.8em", color: "red" }}>
                {" "}
                {/* 댓글 스타일을 조정하세요. */}이 부분은 중요합니다!
              </div>
            </span>
          );
        } else {
          return <span>{line}</span>;
        }
      })}
    </SyntaxHighlighter>
  );
};

export default CodeBlock;
