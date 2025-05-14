import React, { useState } from "react";
import { Upload, Button, Radio, Input, Typography, Row, Col, Divider } from "antd";
import { UploadOutlined, ArrowRightOutlined } from "@ant-design/icons";

const { Title, Text } = Typography;

const langMap = ["English", "German", "Spanish", "French", "Chinese"];

const App = () => {
  const [file, setFile] = useState(null);
  const [fileExt, setFileExt] = useState(null);
  const [content, setContent] = useState("");
  const [translated, setTranslated] = useState("");
  const [reversed, setReversed] = useState("");
  const [summary, setSummary] = useState("");
  const [selectedLang, setSelectedLang] = useState("English");

  const handleFileUpload = ({ file }) => {
    const reader = new FileReader();
    const ext = file.name.split(".").pop();
    setFileExt(ext);

    reader.onload = (e) => {
      if (ext === "pdf") {
        setContent(<iframe src={e.target.result} width="100%" height="400px" title="PDF Viewer" />);
      } else if (ext === "txt") {
        setContent(e.target.result);
      } else {
        setContent(<p>Viewer not supported for this file type.</p>);
      }
    };

    if (file.type === "application/pdf") {
      reader.readAsDataURL(file);
    } else {
      reader.readAsText(file);
    }

    setFile(file);
  };

  const simulateTranslation = (text) => text + " [Translated]";
  const simulateReverseTranslation = (text) => text + " [Reversed]";
  const simulateSummary = (text) => (typeof text === 'string' ? text.substring(0, 100) : "Preview") + "... [Summary]";

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>📄 PDF/Word/Excel/Text Language Translator</Title>

      <Upload beforeUpload={() => false} onChange={handleFileUpload} accept=".pdf,.doc,.docx,.xlsx,.txt">
        <Button icon={<UploadOutlined />}>Upload PDF/Word/Excel/Text</Button>
      </Upload>

      {file && (
        <div style={{ marginTop: 24 }}>
          <Row justify="space-between" align="middle" gutter={16} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Text strong>Selected File:</Text> {file.name}
            </Col>
            <Col span={12}>
              <Text strong>Target Language: </Text>
              <Radio.Group
                options={langMap.map((lang) => ({ label: lang, value: lang }))}
                value={selectedLang}
                onChange={(e) => setSelectedLang(e.target.value)}
                optionType="button"
                buttonStyle="solid"
              />
            </Col>
          </Row>

          <Row gutter={[12, 12]} align="top" justify="center" wrap>
            <Col span={7}>
              <Title level={4}>📄 Original</Title>
              <div style={{ border: "1px solid #ddd", padding: 10, minHeight: 200 }}>{content}</div>
            </Col>

            <Col span={1} style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Button icon={<ArrowRightOutlined />} onClick={() => setTranslated(simulateTranslation("" + content))} />
            </Col>

            <Col span={7}>
              <Title level={4}>🌐 Translated</Title>
              <div style={{ border: "1px solid #ddd", padding: 10, minHeight: 200 }}>{translated}</div>
            </Col>

            <Col span={1} style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Button icon={<ArrowRightOutlined />} onClick={() => setReversed(simulateReverseTranslation(translated))} />
            </Col>

            <Col span={7}>
              <Title level={4}>🔁 Reverse Translated</Title>
              <div style={{ border: "1px solid #ddd", padding: 10, minHeight: 200 }}>{reversed}</div>
            </Col>

            <Col span={24}>
              <Divider />
              <Title level={4}>📝 Summary</Title>
              <Button onClick={() => setSummary(simulateSummary("" + content))}>Show Summary</Button>
              {summary && <div style={{ marginTop: 10, border: "1px solid #ddd", padding: 10 }}>{summary}</div>}
            </Col>

            <Col span={24}>
              <Divider />
              <Title level={4}>💬 Ask a Question</Title>
              <Input.Search
                placeholder="Ask a question about the file..."
                enterButton="Ask"
                onSearch={(val) => alert("LLM response to: " + val)}
              />
            </Col>
          </Row>
        </div>
      )}
    </div>
  );
};

export default App;
