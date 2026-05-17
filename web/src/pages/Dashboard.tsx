import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Brain, Database, FileText, ArrowRight, RefreshCw } from 'lucide-react';
import { api } from '../api';
import type { Domain } from '../api';

function StatCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: string | number; color: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-4">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-xs text-gray-500">{label}</p>
      </div>
    </div>
  );
}

function MasteryBar({ value }: { value: number }) {
  const color = value >= 70 ? 'bg-green-500' : value >= 40 ? 'bg-amber-500' : 'bg-red-400';
  return (
    <div className="w-full bg-gray-100 rounded-full h-2">
      <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${value}%` }} />
    </div>
  );
}

export default function Dashboard() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    api.getDomains()
      .then(setDomains)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const totalKnowledge = domains.reduce((s, d) => s + d.knowledge_count, 0);
  const totalMemory = domains.reduce((s, d) => s + d.memory_count, 0);
  const avgMastery = domains.length
    ? Math.round(domains.reduce((s, d) => s + d.avg_mastery, 0) / domains.length)
    : 0;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">学习总览</h1>
          <p className="text-sm text-gray-500 mt-1">所有学习领域一览</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <RefreshCw size={14} />
          刷新
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          ⚠️ API 连接失败: {error}
          <p className="mt-1 text-red-500">请确保后端已启动: <code className="bg-red-100 px-1 rounded">python api/server.py</code></p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard icon={BookOpen} label="学习领域" value={domains.length} color="bg-indigo-500" />
        <StatCard icon={FileText} label="知识笔记" value={totalKnowledge} color="bg-emerald-500" />
        <StatCard icon={Database} label="记忆条目" value={totalMemory} color="bg-violet-500" />
        <StatCard icon={Brain} label="平均掌握度" value={`${avgMastery}%`} color="bg-amber-500" />
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20 text-gray-400">
          <RefreshCw size={20} className="animate-spin mr-2" /> 加载中...
        </div>
      )}

      {/* Empty */}
      {!loading && domains.length === 0 && !error && (
        <div className="text-center py-20">
          <Brain size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">还没有学习领域</p>
          <p className="text-sm text-gray-400 mt-2">使用 CLI 运行 <code className="bg-gray-100 px-2 py-0.5 rounded">/create Python</code> 创建第一个</p>
        </div>
      )}

      {/* Domain Cards */}
      <div className="grid grid-cols-2 gap-4">
        {domains.map((d) => (
          <Link
            key={d.name}
            to={`/domain/${encodeURIComponent(d.name)}`}
            className="group bg-white rounded-xl border border-gray-200 p-5 hover:border-indigo-300 hover:shadow-md transition-all"
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                {d.name}
              </h3>
              <ArrowRight size={16} className="text-gray-300 group-hover:text-indigo-500 transition-colors" />
            </div>

            <MasteryBar value={d.avg_mastery} />
            <p className="text-xs text-gray-500 mt-2 text-right">{d.avg_mastery}% 掌握度</p>

            <div className="flex gap-4 mt-3 text-xs text-gray-500">
              <span>{d.concept_count} 概念</span>
              <span>{d.knowledge_count} 笔记</span>
              <span>{d.memory_count} 记忆</span>
              {d.has_plan && <span className="text-green-600">✓ 有计划</span>}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
