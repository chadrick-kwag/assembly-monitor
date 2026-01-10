import { Routes, Route } from 'react-router-dom';
import AppNavbar from './components/AppNavbar';
import Container from 'react-bootstrap/Container';
import LegislationList from './components/LegislationList';
import LegislationDetail from './components/LegislationDetail';

function App() {
  return (
    <>
      <AppNavbar />
      <Container className="mt-4">
        <Routes>
          <Route path="/" element={<LegislationList />} />
          <Route path="/post/:id" element={<LegislationDetail />} />
        </Routes>
      </Container>
    </>
  );
}

export default App;
