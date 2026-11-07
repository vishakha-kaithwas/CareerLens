import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { WorkflowProvider } from './context/WorkflowContext';
import { Layout } from './components/Layout';
import { LandingPage } from './pages/LandingPage';
import { AnalyzePage } from './pages/AnalyzePage';
import { DashboardPage } from './pages/DashboardPage';
import { RoadmapPage } from './pages/RoadmapPage';
import { ImprovementPage } from './pages/ImprovementPage';
import { OverviewPage } from './pages/OverviewPage';

export const App: React.FC = () => {
  return (
    <WorkflowProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<LandingPage />} />
            <Route path="analyze" element={<AnalyzePage />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="roadmap" element={<RoadmapPage />} />
            <Route path="improvement" element={<ImprovementPage />} />
            <Route path="overview" element={<OverviewPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </WorkflowProvider>
  );
};

export default App;
