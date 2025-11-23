// src/App.jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ProcessingPage from "./pages/ProcessingPage";
import ReviewPage from "./pages/ReviewPage";
import Home from "./pages/Home";
import ChatPage from "./pages/ChatPage";
import ParticleBackground from "./components/ParticleBackground";
function App() {
  return (
    <>
    <ParticleBackground />
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/Upload" element={<UploadPage />} />
        <Route path="/processing/:jobId" element={<ProcessingPage />} />
        <Route path="/review/:jobId" element={<ReviewPage />} />
        <Route path="/chat/:jobId" element={<ChatPage />} />
      </Routes>
    </BrowserRouter>
  </>
  );
}

export default App;
