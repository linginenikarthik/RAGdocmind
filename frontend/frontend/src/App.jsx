import { useState } from "react";
import Navbar from "./components/Navbar";
import UploadSection from "./components/UploadSection";
import ChatSection from "./components/ChatSection";
import { useSelector } from "react-redux";
import "./App.css";

function App() {
  // const [documentId, setDocumentId] = useState(null);
    const documentId = useSelector(
    (state) => state.document.documentId
  );
  console.log("App documentId:", documentId);

  return (
    <div className="app">
      <Navbar />

      <div className="container">
        {/* <UploadSection
          documentId={documentId}
          setDocumentId={setDocumentId}
        /> */}
        <UploadSection/>

        {documentId && <ChatSection documentId={documentId} />}
      </div>
    </div>
  );
}

export default App;