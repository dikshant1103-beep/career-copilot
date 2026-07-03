import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Upload from "./pages/Upload";
import Search from "./pages/Search";
import JobDetail from "./pages/JobDetail";
import Tracker from "./pages/Tracker";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Upload />} />
        <Route path="/search" element={<Search />} />
        <Route path="/job/:id" element={<JobDetail />} />
        <Route path="/tracker" element={<Tracker />} />
      </Route>
    </Routes>
  );
}
