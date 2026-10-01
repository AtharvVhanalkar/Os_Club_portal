import { Route, Routes } from 'react-router-dom'
import Header from './components/Header.jsx'
import Footer from './components/Footer.jsx'
import RequireOrganizer from './components/RequireOrganizer.jsx'
import Home from './pages/Home.jsx'
import SessionDetail from './pages/SessionDetail.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import NotFound from './pages/NotFound.jsx'
import Contributors from './pages/Contributors.jsx'
import Dashboard from './pages/organizer/Dashboard.jsx'
import SessionEditor from './pages/organizer/SessionEditor.jsx'
import ManageSession from './pages/organizer/ManageSession.jsx'

export default function App() {
  return (
    <div className="app">
      <Header />
      <main className="main" id="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/sessions/:id" element={<SessionDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/contributors" element={<Contributors />} />
          <Route element={<RequireOrganizer />}>
            <Route path="/organize" element={<Dashboard />} />
            <Route path="/organize/new" element={<SessionEditor />} />
            <Route path="/organize/:id" element={<ManageSession />} />
            <Route path="/organize/:id/edit" element={<SessionEditor />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
