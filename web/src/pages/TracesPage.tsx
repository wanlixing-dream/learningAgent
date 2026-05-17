import { useEffect, useState } from 'react';
import { Activity, CheckCircle, XCircle, Clock, ChevronDown, ChevronRight } from 'lucide-react';
import { api } from '../api';
import type { TraceItem } from '../api';

export default function TracesPage() {
  const [traces, setTraces] = useState<TraceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [detail, setDetail] = useState<{ trace: any; evaluation: any } | null>(null);

  useEffect(() => {
    api.getTraces(50)
      .then(setTraces)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const toggle = async (id: string) => {
    if (expanded === id) {
      setExpanded(null);
      setDetail(null);
      return;
    }
    setExpanded(id);
    try {
      const d = await api.getTrace(id);
      setDetail(d);
    } catch {
      setDetail(null);
    }
  };

  const statusIcon = (s: string) =>
    s === 'success' ? <CheckCircle size={14} className="text-green-500" />
    : s === 'error' ? <XCircle size={14} className="text-red-500" />
    : <Clock size={14} className="text-amber-500" />;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">执行追踪</h1>
        <p className="text-sm text-gray-500 mt-1">Agent 链路追踪和评估</p>
      </div>

      {loading && <div className="text-center py-20 text-gray-400">加载中...</div>}

      {!loading && traces.length === 0 && (
        <div className="text-center py-20 text-gray-400">
          <Activity size={40} className="mx-auto mb-3" />
          <p>暂无追踪记录</p>
          <p className="text-xs mt-1">通过 CLI 或 MCP 执行命令后会产生追踪</p>
        </div>
      )}

      <div className="space-y-2">
        {traces.map((t) => (
          <div key={t.trace_id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <button
              onClick={() => toggle(t.trace_id)}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left"
            >
              {expanded === t.trace_id ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              {statusIcon(t.status)}
              <span className="text-sm font-medium text-gray-800 flex-1 truncate">{t.user_input}</span>
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{t.intent}</span>
              <span className="text-xs text-gray-400">{t.agent}</span>
              <span className="text-xs text-gray-400">{new Date(t.started_at).toLocaleString()}</span>
            </button>

            {expanded === t.trace_id && detail && (
              <div className="border-t border-gray-100 px-4 py-4 bg-gray-50 space-y-4">
                {/* Evaluation Scores */}
                {detail.evaluation && detail.evaluation.checks && (
                  <div>
                    <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">评估结果</h4>
                    <div className="flex gap-3 flex-wrap">
                      {detail.evaluation.checks.map((check: any, i: number) => (
                        <div key={i} className="flex items-center gap-2">
                          {check.passed
                            ? <CheckCircle size={14} className="text-green-500" />
                            : <XCircle size={14} className="text-red-400" />
                          }
                          <span className="text-xs text-gray-600">{check.name}</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-2">
                      <span className="text-sm font-bold text-indigo-600">
                        总分: {(detail.evaluation.score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                )}

                {/* Trace Steps */}
                {detail.trace?.steps && detail.trace.steps.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">执行步骤</h4>
                    <div className="space-y-1">
                      {detail.trace.steps.map((step: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 text-xs text-gray-600">
                          <span className="w-5 h-5 bg-gray-200 rounded-full flex items-center justify-center text-gray-500 text-[10px]">
                            {i + 1}
                          </span>
                          <span>{step.action || step.name || JSON.stringify(step).slice(0, 80)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Error */}
                {t.error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                    {t.error}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
