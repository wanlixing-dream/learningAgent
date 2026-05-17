import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, BookOpen, MessageSquare, BarChart3, Send, Search } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { api } from '../api';
import type { MasteryData, KnowledgeFile, MemoryResult } from '../api';

type Tab = 'plan' | 'knowledge' | 'practice' | 'progress';

export default function DomainDetail() {
  const { name } = useParams<{ name: string }>();
  const domain = decodeURIComponent(name || '');
  const [tab, setTab] = useState<Tab>('plan');

  const tabs: { key: Tab; label: string; icon: any }[] = [
    { key: 'plan', label: '学习计划', icon: BookOpen },
    { key: 'knowledge', label: '知识库', icon: BookOpen },
    { key: 'practice', label: '互动学习', icon: MessageSquare },
    { key: 'progress', label: '掌握度', icon: BarChart3 },
  ];

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Back + Title */}
      <div className="flex items-center gap-3 mb-6">
        <Link to="/" className="text-gray-400 hover:text-gray-600 transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{domain}</h1>
          <p className="text-sm text-gray-500">领域详情</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors flex-1 justify-center
              ${tab === key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      {tab === 'plan' && <PlanTab domain={domain} />}
      {tab === 'knowledge' && <KnowledgeTab domain={domain} />}
      {tab === 'practice' && <PracticeTab domain={domain} />}
      {tab === 'progress' && <ProgressTab domain={domain} />}
    </div>
  );
}

/* ========== Plan Tab ========== */
function PlanTab({ domain }: { domain: string }) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getPlan(domain)
      .then((d) => setContent(d.content))
      .catch(() => setContent('暂无学习计划。使用 `/create` 命令创建。'))
      .finally(() => setLoading(false));
  }, [domain]);

  if (loading) return <Loading />;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 prose prose-sm max-w-none">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}

/* ========== Knowledge Tab ========== */
function KnowledgeTab({ domain }: { domain: string }) {
  const [files, setFiles] = useState<KnowledgeFile[]>([]);
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<MemoryResult[]>([]);

  useEffect(() => {
    api.getKnowledge(domain)
      .then((d) => { setFiles(d.files); setSummary(d.summary); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [domain]);

  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    api.searchMemory(domain, searchQuery).then(setSearchResults);
  };

  if (loading) return <Loading />;

  return (
    <div className="space-y-4">
      {/* Memory Search */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex gap-2">
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="语义搜索记忆..."
            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-indigo-400"
          />
          <button onClick={handleSearch} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors">
            <Search size={16} />
          </button>
        </div>
        {searchResults.length > 0 && (
          <div className="mt-3 space-y-2">
            {searchResults.map((r, i) => (
              <div key={i} className="p-3 bg-indigo-50 rounded-lg text-sm">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span className="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded">{r.type}</span>
                  <span>相关度: {(r.score * 100).toFixed(0)}%</span>
                </div>
                <p className="text-gray-700">{r.content}</p>
                {r.entities.length > 0 && (
                  <div className="flex gap-1 mt-2">
                    {r.entities.map((e, j) => (
                      <span key={j} className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">{e}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Summary */}
      {summary && (
        <div className="bg-white rounded-xl border border-gray-200 p-5 prose prose-sm max-w-none">
          <h3 className="text-base font-semibold text-gray-800 mb-2">知识摘要</h3>
          <ReactMarkdown>{summary}</ReactMarkdown>
        </div>
      )}

      {/* File List */}
      {files.length === 0 ? (
        <div className="text-center py-12 text-gray-400">暂无知识笔记</div>
      ) : (
        <div className="space-y-3">
          {files.map((f) => (
            <div key={f.name} className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-800">{f.name}</span>
                <span className="text-xs text-gray-400">{(f.size / 1024).toFixed(1)} KB</span>
              </div>
              <p className="text-sm text-gray-600 line-clamp-3">{f.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ========== Practice Tab ========== */
function PracticeTab({ domain }: { domain: string }) {
  const [messages, setMessages] = useState<{ role: 'user' | 'bot'; text: string }[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  const send = () => {
    if (!input.trim() || sending) return;
    const userMsg = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text: userMsg }]);
    setSending(true);
    api.chat(domain, userMsg)
      .then((d) => setMessages((prev) => [...prev, { role: 'bot', text: d.reply }]))
      .catch((e) => setMessages((prev) => [...prev, { role: 'bot', text: `❌ ${e.message}` }]))
      .finally(() => setSending(false));
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 flex flex-col" style={{ height: '60vh' }}>
      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <MessageSquare size={32} className="mx-auto mb-3" />
            <p>输入问题开始互动学习</p>
            <p className="text-xs mt-1">基于记忆检索提供上下文回答</p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm whitespace-pre-wrap
              ${m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              {m.text}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-500 px-4 py-2.5 rounded-2xl text-sm animate-pulse">思考中...</div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-gray-100 p-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="输入你的问题..."
          className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-indigo-400"
        />
        <button
          onClick={send}
          disabled={sending}
          className="px-4 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}

/* ========== Progress Tab ========== */
function ProgressTab({ domain }: { domain: string }) {
  const [data, setData] = useState<MasteryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [memStats, setMemStats] = useState<{ total: number; by_type: Record<string, number> } | null>(null);

  useEffect(() => {
    Promise.all([
      api.getMastery(domain),
      api.getMemoryStats(domain),
    ])
      .then(([m, s]) => { setData(m); setMemStats(s); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [domain]);

  if (loading) return <Loading />;
  if (!data || data.concepts.length === 0) {
    return (
      <div className="text-center py-20 text-gray-400">
        <BarChart3 size={40} className="mx-auto mb-3" />
        <p>暂无掌握度数据</p>
        <p className="text-xs mt-1">通过互动学习积累数据</p>
      </div>
    );
  }

  const barColors = (mastery: number) =>
    mastery >= 70 ? '#22c55e' : mastery >= 40 ? '#f59e0b' : '#ef4444';

  const radarData = data.concepts.slice(0, 8).map((c) => ({
    subject: c.concept.length > 10 ? c.concept.slice(0, 10) + '…' : c.concept,
    mastery: c.mastery,
    confidence: c.confidence,
  }));

  return (
    <div className="space-y-6">
      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p className="text-3xl font-bold text-gray-900">{data.concepts.length}</p>
          <p className="text-xs text-gray-500 mt-1">总概念数</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p className="text-3xl font-bold text-red-500">{data.weak_count}</p>
          <p className="text-xs text-gray-500 mt-1">薄弱概念</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p className="text-3xl font-bold text-amber-500">{data.due_count}</p>
          <p className="text-xs text-gray-500 mt-1">待复习</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        {/* Bar Chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">概念掌握度</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.concepts.slice(0, 12)} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} />
              <YAxis dataKey="concept" type="category" width={100} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="mastery" radius={[0, 4, 4, 0]}>
                {data.concepts.slice(0, 12).map((c, i) => (
                  <Cell key={i} fill={barColors(c.mastery)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Radar Chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">能力雷达</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10 }} />
              <PolarRadiusAxis domain={[0, 100]} />
              <Radar name="掌握度" dataKey="mastery" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
              <Radar name="置信度" dataKey="confidence" stroke="#a855f7" fill="#a855f7" fillOpacity={0.15} />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Weak Concepts */}
      {data.weak_concepts.length > 0 && (
        <div className="bg-red-50 rounded-xl border border-red-200 p-4">
          <h3 className="text-sm font-semibold text-red-700 mb-2">⚠️ 薄弱概念</h3>
          <div className="flex flex-wrap gap-2">
            {data.weak_concepts.map((c, i) => (
              <span key={i} className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs">{c}</span>
            ))}
          </div>
        </div>
      )}

      {/* Memory Stats */}
      {memStats && memStats.total > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">记忆统计</h3>
          <div className="flex gap-3">
            <span className="text-sm text-gray-500">总计: <strong>{memStats.total}</strong></span>
            {Object.entries(memStats.by_type).map(([type, count]) => (
              <span key={type} className="text-xs bg-violet-50 text-violet-700 px-2 py-1 rounded">
                {type}: {count}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Loading() {
  return (
    <div className="flex items-center justify-center py-20 text-gray-400 text-sm">
      加载中...
    </div>
  );
}
