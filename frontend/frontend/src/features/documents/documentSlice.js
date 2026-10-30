import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  documentId: null,
  fileName: "",
  ingested: false,
};

const documentSlice = createSlice({
  name: "document",
  initialState,
  reducers: {
    setDocument(state, action) {
      state.documentId = action.payload.documentId;
      state.fileName = action.payload.fileName;
    },
    setIngested(state) {
      state.ingested = true;
    },
  },
});

export const { setDocument, setIngested } = documentSlice.actions;
export default documentSlice.reducer;