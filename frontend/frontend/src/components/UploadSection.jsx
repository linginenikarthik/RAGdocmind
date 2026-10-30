import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import api from "../api/client";
import {
  setDocument,
  setIngested,
} from "../features/documents/documentSlice";

function UploadSection() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const dispatch = useDispatch();

  const documentId = useSelector(
    (state) => state.document.documentId
  );

  const uploadFile = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await api.post("/documents/upload", formData);
    console.log("Upload response:", res.data);

    dispatch(
      setDocument({
        documentId: res.data.id,
        fileName: file.name,
      })
    );

    setStatus("PDF uploaded successfully");
  };

  const ingestDocument = async () => {
    const res = await api.post(
      `/documents/${documentId}/ingest`
    );

    dispatch(setIngested(true));

    setStatus(
      `${res.data.chunks_created} chunks indexed`
    );
  };

  return (
    <div className="card">
      <h2>Upload PDF</h2>

      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={uploadFile}>
        Upload
      </button>

      {documentId && (
        <button onClick={ingestDocument}>
          Create Embeddings
        </button>
      )}

      <p>{status}</p>
    </div>
  );
}

export default UploadSection;