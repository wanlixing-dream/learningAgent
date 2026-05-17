import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Brain, Activity, Home } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import DomainDetail from './pages/DomainDetail';
import TracesPage from './pages/TracesPage';

function NavLink({ to, icon: Icon, label }: { to: string; icon: any; label: string }) {
  const loc = useLocation();
  const active = loc.pathname === to || (to !== '/' && loc.pathname.startsWith(to));
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors
        ${active ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}
    >
      <Icon size={18} />
      {label}
    </Link>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <aside className="w-60 bg-white border-r border-gray-200 flex flex-col">
          <div className="px-5 py-5 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <Brain size={24} className="text-indigo-600" />
              <span className="text-lg font-bold text-gray-900">LearningAgent</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">AI 学习助手 Dashboard</p>
          </div>
          <nav className="flex-1 px-3 py-4 space-y-1">
            <NavLink to="/" icon={Home} label="总览" />
            <NavLink to="/traces" icon={Activity} label="执行追踪" />
          </nav>
          <div className="px-5 py-4 border-t border-gray-100 text-xs text-gray-400">
            v0.7.0 · MCP Ready
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/domain/:name" element={<DomainDetail />} />
            <Route path="/traces" element={<TracesPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
