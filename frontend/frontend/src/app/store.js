import { configureStore } from "@reduxjs/toolkit";
import documentReducer from "../features/documents/documentSlice";
import chatReducer from "../features/chat/chatSlice";

export const store = configureStore({
  reducer: {
    document: documentReducer,
    chat: chatReducer,
  },
});