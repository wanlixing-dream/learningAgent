# LearningAgent 高级Agent系统技术规划

**创建日期:** 2026-04-10
**版本:** 2.0
**状态:** 规划阶段

---

## 目录

1. [现状评估](#现状评估)
2. [问题分析与解决方案](#问题分析与解决方案)
3. [技术架构升级](#技术架构升级)
4. [实施路线图](#实施路线图)
5. [技术选型](#技术选型)

---

## 现状评估

### ✅ 已解决的问题

#### 1. 记忆更新策略（部分解决）
- **当前实现**: [summary_manager.py](file:///home/wanlixing/桌面/learningAgent/core/summary_manager.py)
- **解决方案**: 混合策略（<5个文件完全重写，≥5个增量更新）
- **优点**: 减少了不必要的全量重写
- **不足**: 没有真正的索引机制，检索效率低

#### 2. 记忆压缩（部分解决）
- **当前实现**: 使用LLM生成压缩摘要
- **压缩率**: 控制在原内容的20-30%
- **不足**: 压缩策略简单，没有考虑重要性权重

#### 3. 大型Agent系统架构（部分解决）
- **当前实现**: 三层架构（协调层、功能层、专业层）
- **优点**: 职责分离，可扩展性好
- **不足**: 缺少统一的记忆管理和上下文隔离机制

### ❌ 未解决的问题

#### 1. 记忆冲突解决
- **问题**: 多次添加相似知识时没有冲突检测
- **影响**: 知识冗余、版本混乱
- **优先级**: 高

#### 2. 长短期记忆管理
- **问题**: 所有记忆平等对待，没有区分重要性
- **影响**: 关键信息被淹没，检索效率低
- **优先级**: 高

#### 3. 复杂场景记忆检索
- **问题**: 只能通过文件名查找，无法语义检索
- **影响**: 知识利用率低，重复学习
- **优先级**: 高

#### 4. KV Cache碎片化
- **问题**: 长上下文场景下内存碎片化严重
- **影响**: 性能下降，内存浪费
- **优先级**: 中

#### 5. Memory Benchmark设计
- **问题**: 缺少性能评估体系
- **影响**: 无法量化优化效果
- **优先级**: 中

#### 6. 子Agent上下文污染
- **问题**: 子Agent之间共享上下文，可能相互干扰
- **影响**: 决策错误，输出不稳定
- **优先级**: 高

#### 7. Skill和MCP集成
- **问题**: 没有模块化的技能系统
- **影响**: 功能扩展困难
- **优先级**: 中

---

## 问题分析与解决方案

### 1. 记忆冲突解决

#### 问题描述
当用户多次添加相似或冲突的知识时，系统无法识别和处理冲突。

#### 解决方案

##### 1.1 基于向量相似度的冲突检测
```python
# 新增文件: core/memory_conflict_resolver.py

from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MemoryConflictResolver:
    """
    记忆冲突检测和解决器
    
    策略：
    1. 向量化所有知识条目
    2. 计算新知识与现有知识的相似度
    3. 相似度 > 0.8 视为冲突
    4. 提供三种解决策略：合并、覆盖、保留两者
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer()
        
    def detect_conflicts(self, new_content: str, existing_contents: List[str]) -> List[Tuple[int, float, str]]:
        """
        检测冲突
        
        Args:
            new_content: 新知识内容
            existing_contents: 现有知识列表
            
        Returns:
            冲突列表: [(索引, 相似度, 冲突类型), ...]
        """
        if not existing_contents:
            return []
        
        # 向量化
        all_contents = [new_content] + existing_contents
        tfidf_matrix = self.vectorizer.fit_transform(all_contents)
        
        # 计算相似度
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        
        # 识别冲突
        conflicts = []
        for idx, sim in enumerate(similarities):
            if sim > self.similarity_threshold:
                conflict_type = self._classify_conflict(new_content, existing_contents[idx])
                conflicts.append((idx, sim, conflict_type))
        
        return conflicts
    
    def _classify_conflict(self, content1: str, content2: str) -> str:
        """
        分类冲突类型
        
        Returns:
            'duplicate': 完全重复
            'update': 更新版本
            'contradiction': 矛盾冲突
            'supplement': 补充信息
        """
        # 使用LLM分类冲突类型
        # 简化实现：基于规则
        if content1.strip() == content2.strip():
            return 'duplicate'
        elif '更新' in content1 or '新版本' in content1:
            return 'update'
        elif '但是' in content1 or '然而' in content1:
            return 'contradiction'
        else:
            return 'supplement'
    
    def resolve_conflict(self, new_content: str, existing_content: str, 
                        conflict_type: str, strategy: str = 'auto') -> str:
        """
        解决冲突
        
        Args:
            strategy: 'merge' | 'overwrite' | 'keep_both' | 'auto'
            
        Returns:
            解决后的内容
        """
        if strategy == 'auto':
            strategy = self._auto_select_strategy(conflict_type)
        
        if strategy == 'merge':
            return self._merge_contents(new_content, existing_content)
        elif strategy == 'overwrite':
            return new_content
        elif strategy == 'keep_both':
            return f"{existing_content}\n\n---\n\n{new_content}"
        
        return new_content
```

##### 1.2 集成到AddKnowledgeProcessor
```python
# 修改 processors/add_knowledge.py

class AddKnowledgeProcessor:
    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager):
        self.llm = llm
        self.file_manager = file_manager
        self.summary_manager = SummaryManager(file_manager)
        self.conflict_resolver = MemoryConflictResolver()  # 新增
    
    def add(self, domain: str, input_data: str, input_type: str = None) -> str:
        # ... 现有代码 ...
        
        # 新增：冲突检测
        existing_knowledge = self._load_existing_knowledge(domain)
        conflicts = self.conflict_resolver.detect_conflicts(content, existing_knowledge)
        
        if conflicts:
            return self._handle_conflicts(content, conflicts, domain)
        
        # ... 继续保存 ...
```

---

### 2. 长短期记忆管理

#### 问题描述
所有知识平等存储，没有区分重要性和时效性，导致关键信息难以快速访问。

#### 解决方案

##### 2.1 分层记忆架构
```python
# 新增文件: core/memory_hierarchy.py

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

class MemoryHierarchy:
    """
    分层记忆管理系统
    
    记忆层级：
    1. 工作记忆 (Working Memory) - 当前会话，临时存储
    2. 短期记忆 (Short-term Memory) - 最近7天，快速访问
    3. 长期记忆 (Long-term Memory) - 永久存储，压缩归档
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.working_memory = {}  # 当前会话
        self.short_term_cache = {}  # 最近访问
        
    def store(self, domain: str, content: str, importance: float = 0.5) -> str:
        """
        存储记忆
        
        Args:
            importance: 重要性权重 (0-1)
            
        Returns:
            记忆ID
        """
        memory_id = self._generate_memory_id()
        timestamp = datetime.now()
        
        memory_entry = {
            'id': memory_id,
            'content': content,
            'domain': domain,
            'importance': importance,
            'created_at': timestamp.isoformat(),
            'access_count': 0,
            'last_accessed': timestamp.isoformat()
        }
        
        # 根据重要性决定存储层级
        if importance > 0.8:
            # 高重要性 -> 工作记忆 + 长期记忆
            self._store_working(memory_id, memory_entry)
            self._store_long_term(domain, memory_entry)
        elif importance > 0.5:
            # 中等重要性 -> 短期记忆
            self._store_short_term(domain, memory_entry)
        else:
            # 低重要性 -> 仅长期记忆
            self._store_long_term(domain, memory_entry)
        
        return memory_id
    
    def retrieve(self, domain: str, query: str, top_k: int = 5) -> List[Dict]:
        """
        检索记忆
        
        检索顺序：
        1. 工作记忆（最快）
        2. 短期记忆缓存
        3. 长期记忆（语义检索）
        """
        results = []
        
        # 1. 检查工作记忆
        results.extend(self._search_working(domain, query))
        
        # 2. 检查短期记忆
        results.extend(self._search_short_term(domain, query))
        
        # 3. 检索长期记忆
        if len(results) < top_k:
            results.extend(self._search_long_term(domain, query, top_k - len(results)))
        
        # 更新访问计数
        for item in results:
            self._update_access_count(item['id'])
        
        return results[:top_k]
    
    def decay_short_term_memory(self):
        """
        短期记忆衰减
        
        策略：
        - 7天未访问 -> 降级到长期记忆
        - 访问次数 > 10 -> 升级到长期记忆（高优先级）
        """
        now = datetime.now()
        to_demote = []
        
        for memory_id, entry in self.short_term_cache.items():
            last_accessed = datetime.fromisoformat(entry['last_accessed'])
            days_since_access = (now - last_accessed).days
            
            if days_since_access > 7 or entry['access_count'] > 10:
                to_demote.append(memory_id)
        
        for memory_id in to_demote:
            entry = self.short_term_cache.pop(memory_id)
            self._store_long_term(entry['domain'], entry)
    
    def _store_working(self, memory_id: str, entry: Dict):
        """存储到工作记忆"""
        self.working_memory[memory_id] = entry
        
    def _store_short_term(self, domain: str, entry: Dict):
        """存储到短期记忆"""
        self.short_term_cache[entry['id']] = entry
        
        # 持久化到文件
        cache_file = self.base_dir / domain / 'memory' / 'short_term_cache.json'
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.short_term_cache, f, ensure_ascii=False, indent=2)
    
    def _store_long_term(self, domain: str, entry: Dict):
        """存储到长期记忆"""
        # 压缩后存储
        compressed = self._compress_memory(entry)
        
        memory_file = self.base_dir / domain / 'memory' / 'long_term' / f"{entry['id']}.json"
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(compressed, f, ensure_ascii=False, indent=2)
```

##### 2.2 重要性评估
```python
# 新增文件: core/importance_evaluator.py

class ImportanceEvaluator:
    """
    记忆重要性评估器
    
    评估维度：
    1. 内容质量（完整性、准确性）
    2. 访问频率
    3. 关联度（与其他知识的连接数）
    4. 时效性
    """
    
    def evaluate(self, content: str, metadata: Dict) -> float:
        """
        评估重要性 (0-1)
        """
        scores = {
            'quality': self._evaluate_quality(content),
            'frequency': self._evaluate_frequency(metadata.get('access_count', 0)),
            'connectivity': self._evaluate_connectivity(metadata.get('links', [])),
            'timeliness': self._evaluate_timeliness(metadata.get('created_at'))
        }
        
        # 加权平均
        weights = {'quality': 0.4, 'frequency': 0.3, 'connectivity': 0.2, 'timeliness': 0.1}
        
        importance = sum(scores[k] * weights[k] for k in scores)
        return min(1.0, importance)
```

---

### 3. 复杂场景记忆检索

#### 问题描述
当前只能通过文件名查找，无法进行语义检索和智能推荐。

#### 解决方案

##### 3.1 向量化记忆索引
```python
# 新增文件: core/memory_index.py

from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class MemoryIndex:
    """
    向量化记忆索引
    
    使用 FAISS 进行高效向量检索
    """
    
    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(embedding_model)
        self.index = None
        self.id_to_memory = {}
        
    def build_index(self, memories: List[Dict]):
        """
        构建向量索引
        
        Args:
            memories: 记忆列表 [{'id': str, 'content': str, ...}, ...]
        """
        # 编码
        contents = [m['content'] for m in memories]
        embeddings = self.encoder.encode(contents)
        
        # 构建FAISS索引
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        # 建立ID映射
        self.id_to_memory = {i: m for i, m in enumerate(memories)}
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        语义检索
        
        Args:
            query: 查询文本
            top_k: 返回数量
            
        Returns:
            [(记忆条目, 相似度分数), ...]
        """
        # 编码查询
        query_embedding = self.encoder.encode([query])
        
        # 检索
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # 返回结果
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx in self.id_to_memory:
                results.append((self.id_to_memory[idx], float(dist)))
        
        return results
    
    def update_index(self, new_memory: Dict):
        """
        增量更新索引
        """
        # 编码新记忆
        embedding = self.encoder.encode([new_memory['content']])
        
        # 添加到索引
        new_id = len(self.id_to_memory)
        self.index.add(embedding.astype('float32'))
        self.id_to_memory[new_id] = new_memory
```

##### 3.2 混合检索策略
```python
# 新增文件: core/hybrid_retriever.py

class HybridRetriever:
    """
    混合检索策略
    
    结合多种检索方法：
    1. 关键词检索（TF-IDF）
    2. 语义检索（向量相似度）
    3. 时间检索（最近访问）
    4. 关联检索（知识图谱）
    """
    
    def __init__(self):
        self.keyword_retriever = KeywordRetriever()
        self.semantic_retriever = MemoryIndex()
        self.temporal_retriever = TemporalRetriever()
        self.graph_retriever = KnowledgeGraphRetriever()
    
    def retrieve(self, domain: str, query: str, strategy: str = 'hybrid') -> List[Dict]:
        """
        混合检索
        
        Args:
            strategy: 'keyword' | 'semantic' | 'temporal' | 'graph' | 'hybrid'
        """
        if strategy == 'hybrid':
            # 混合策略：融合多种检索结果
            keyword_results = self.keyword_retriever.search(domain, query)
            semantic_results = self.semantic_retriever.search(query)
            temporal_results = self.temporal_retriever.search(domain)
            
            # 融合排序
            return self._merge_results(
                keyword_results, semantic_results, temporal_results
            )
        else:
            # 单一策略
            return getattr(self, f'{strategy}_retriever').search(domain, query)
    
    def _merge_results(self, *result_sets) -> List[Dict]:
        """
        融合多个检索结果
        
        使用 Reciprocal Rank Fusion (RRF) 算法
        """
        merged_scores = {}
        k = 60  # RRF参数
        
        for results in result_sets:
            for rank, item in enumerate(results):
                memory_id = item['id']
                if memory_id not in merged_scores:
                    merged_scores[memory_id] = 0
                merged_scores[memory_id] += 1 / (k + rank + 1)
        
        # 排序
        sorted_items = sorted(merged_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [item for item, score in sorted_items]
```

---

### 4. KV Cache碎片化解决

#### 问题描述
长上下文场景下，KV Cache碎片化导致内存浪费和性能下降。

#### 解决方案

##### 4.1 PagedAttention机制
```python
# 新增文件: core/kv_cache_manager.py

from typing import Dict, List, Optional
import torch

class PagedKVCache:
    """
    分页式KV Cache管理
    
    类似 vLLM 的 PagedAttention：
    - 将KV Cache分成固定大小的页
    - 按需分配，避免预分配浪费
    - 支持内存共享（相同前缀）
    """
    
    def __init__(self, page_size: int = 16, max_pages: int = 1000):
        self.page_size = page_size
        self.max_pages = max_pages
        self.pages = {}  # page_id -> KV tensor
        self.page_table = {}  # sequence_id -> list of page_ids
        self.free_pages = list(range(max_pages))
        
    def allocate(self, sequence_id: str, initial_size: int = 0) -> List[int]:
        """
        为序列分配KV Cache页
        
        Args:
            sequence_id: 序列ID
            initial_size: 初始大小（token数）
            
        Returns:
            分配的页ID列表
        """
        num_pages_needed = (initial_size + self.page_size - 1) // self.page_size
        
        if num_pages_needed > len(self.free_pages):
            # 内存不足，触发压缩或驱逐
            self._evict_lru_pages(num_pages_needed - len(self.free_pages))
        
        # 分配页
        allocated_pages = self.free_pages[:num_pages_needed]
        self.free_pages = self.free_pages[num_pages_needed:]
        
        self.page_table[sequence_id] = allocated_pages
        
        return allocated_pages
    
    def append(self, sequence_id: str, new_tokens: int):
        """
        追加新token，可能需要分配新页
        """
        current_pages = self.page_table.get(sequence_id, [])
        current_size = len(current_pages) * self.page_size
        
        # 计算需要的新页数
        new_size = current_size + new_tokens
        new_pages_needed = (new_size + self.page_size - 1) // self.page_size - len(current_pages)
        
        if new_pages_needed > 0:
            # 分配新页
            new_pages = self.free_pages[:new_pages_needed]
            self.free_pages = self.free_pages[new_pages_needed:]
            self.page_table[sequence_id].extend(new_pages)
    
    def share_prefix(self, sequence_id: str, prefix_sequence_id: str):
        """
        共享前缀的KV Cache
        
        用于多轮对话或beam search
        """
        prefix_pages = self.page_table.get(prefix_sequence_id, [])
        
        # 复制页引用（不复制数据）
        self.page_table[sequence_id] = prefix_pages.copy()
        
        # 增加引用计数
        for page_id in prefix_pages:
            if page_id not in self.pages:
                self.pages[page_id] = {'ref_count': 0, 'data': None}
            self.pages[page_id]['ref_count'] += 1
    
    def _evict_lru_pages(self, num_pages: int):
        """
        驱逐最近最少使用的页
        """
        # 简化实现：随机驱逐
        # 实际应使用LRU策略
        for _ in range(num_pages):
            if self.free_pages:
                return
            
            # 找到引用计数为0的页
            for page_id, page_info in self.pages.items():
                if page_info['ref_count'] == 0:
                    self.free_pages.append(page_id)
                    del self.pages[page_id]
                    break
```

##### 4.2 滑动窗口注意力
```python
# 新增文件: core/sliding_window_attention.py

class SlidingWindowAttention:
    """
    滑动窗口注意力机制
    
    只保留最近的W个token的KV Cache
    """
    
    def __init__(self, window_size: int = 4096):
        self.window_size = window_size
        self.kv_cache = []
        
    def update(self, new_kv):
        """
        更新KV Cache
        """
        self.kv_cache.append(new_kv)
        
        # 保持窗口大小
        if len(self.kv_cache) > self.window_size:
            self.kv_cache = self.kv_cache[-self.window_size:]
```

---

### 5. Memory Benchmark设计

#### 解决方案

##### 5.1 性能指标体系
```python
# 新增文件: benchmarks/memory_benchmark.py

from typing import Dict, List
import time
import psutil
import json

class MemoryBenchmark:
    """
    记忆系统性能基准测试
    
    测试维度：
    1. 检索性能（延迟、吞吐量）
    2. 存储性能（写入速度）
    3. 内存占用
    4. 准确性（召回率、精确率）
    5. 可扩展性
    """
    
    def __init__(self):
        self.results = {}
        
    def run_all_benchmarks(self) -> Dict:
        """
        运行所有基准测试
        """
        return {
            'retrieval_latency': self.benchmark_retrieval_latency(),
            'storage_throughput': self.benchmark_storage_throughput(),
            'memory_usage': self.benchmark_memory_usage(),
            'accuracy': self.benchmark_accuracy(),
            'scalability': self.benchmark_scalability()
        }
    
    def benchmark_retrieval_latency(self) -> Dict:
        """
        检索延迟测试
        """
        test_queries = self._generate_test_queries(100)
        
        latencies = []
        for query in test_queries:
            start = time.time()
            # 执行检索
            results = memory_system.retrieve(query)
            latency = time.time() - start
            latencies.append(latency)
        
        return {
            'mean': np.mean(latencies),
            'median': np.median(latencies),
            'p95': np.percentile(latencies, 95),
            'p99': np.percentile(latencies, 99)
        }
    
    def benchmark_storage_throughput(self) -> Dict:
        """
        存储吞吐量测试
        """
        test_memories = self._generate_test_memories(1000)
        
        start = time.time()
        for memory in test_memories:
            memory_system.store(memory)
        duration = time.time() - start
        
        return {
            'items_per_second': len(test_memories) / duration,
            'bytes_per_second': sum(len(m['content']) for m in test_memories) / duration
        }
    
    def benchmark_memory_usage(self) -> Dict:
        """
        内存占用测试
        """
        process = psutil.Process()
        
        return {
            'rss_mb': process.memory_info().rss / 1024 / 1024,
            'vms_mb': process.memory_info().vms / 1024 / 1024,
            'percent': process.memory_percent()
        }
    
    def benchmark_accuracy(self) -> Dict:
        """
        准确性测试
        """
        # 准备测试数据集
        test_dataset = self._load_test_dataset()
        
        precision_scores = []
        recall_scores = []
        f1_scores = []
        
        for query, ground_truth in test_dataset:
            # 检索
            results = memory_system.retrieve(query)
            
            # 计算指标
            precision = self._calculate_precision(results, ground_truth)
            recall = self._calculate_recall(results, ground_truth)
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            precision_scores.append(precision)
            recall_scores.append(recall)
            f1_scores.append(f1)
        
        return {
            'precision': np.mean(precision_scores),
            'recall': np.mean(recall_scores),
            'f1': np.mean(f1_scores)
        }
    
    def benchmark_scalability(self) -> Dict:
        """
        可扩展性测试
        """
        memory_sizes = [100, 1000, 10000, 100000]
        results = {}
        
        for size in memory_sizes:
            # 构建指定大小的记忆库
            self._build_memory_store(size)
            
            # 测试检索性能
            latency = self.benchmark_retrieval_latency()
            results[size] = latency
        
        return results
```

##### 5.2 量化指标
```python
# 新增文件: benchmarks/metrics.py

class MemoryMetrics:
    """
    记忆系统量化指标
    
    分类：
    1. 性能指标
    2. 质量指标
    3. 效率指标
    4. 可靠性指标
    """
    
    @staticmethod
    def calculate_all_metrics(memory_system) -> Dict:
        """
        计算所有指标
        """
        return {
            # 性能指标
            'retrieval_latency_p50': Metrics.retrieval_latency(memory_system, percentile=50),
            'retrieval_latency_p95': Metrics.retrieval_latency(memory_system, percentile=95),
            'retrieval_latency_p99': Metrics.retrieval_latency(memory_system, percentile=99),
            'storage_throughput': Metrics.storage_throughput(memory_system),
            
            # 质量指标
            'retrieval_precision': Metrics.retrieval_precision(memory_system),
            'retrieval_recall': Metrics.retrieval_recall(memory_system),
            'retrieval_f1': Metrics.retrieval_f1(memory_system),
            'compression_ratio': Metrics.compression_ratio(memory_system),
            
            # 效率指标
            'memory_efficiency': Metrics.memory_efficiency(memory_system),
            'index_efficiency': Metrics.index_efficiency(memory_system),
            'cache_hit_rate': Metrics.cache_hit_rate(memory_system),
            
            # 可靠性指标
            'conflict_resolution_rate': Metrics.conflict_resolution_rate(memory_system),
            'data_integrity_score': Metrics.data_integrity_score(memory_system),
            'availability': Metrics.availability(memory_system)
        }
```

---

### 6. 子Agent上下文污染避免

#### 解决方案

##### 6.1 上下文隔离机制
```python
# 新增文件: core/context_isolator.py

from typing import Dict, List, Any
import copy

class ContextIsolator:
    """
    Agent上下文隔离器
    
    策略：
    1. 每个子Agent拥有独立的上下文空间
    2. 父子Agent通过消息传递通信
    3. 敏感信息加密存储
    4. 上下文生命周期管理
    """
    
    def __init__(self):
        self.agent_contexts = {}  # agent_id -> context
        self.shared_memory = {}  # 共享内存（只读）
        
    def create_isolated_context(self, agent_id: str, parent_context: Dict = None) -> Dict:
        """
        创建隔离的上下文
        
        Args:
            agent_id: Agent ID
            parent_context: 父上下文（可选）
            
        Returns:
            新的隔离上下文
        """
        # 创建独立上下文
        context = {
            'agent_id': agent_id,
            'local_memory': {},
            'message_queue': [],
            'permissions': self._get_default_permissions(),
            'created_at': time.time()
        }
        
        # 如果有父上下文，复制只读的共享信息
        if parent_context:
            context['shared_memory'] = copy.deepcopy(parent_context.get('shared_memory', {}))
        
        self.agent_contexts[agent_id] = context
        return context
    
    def send_message(self, from_agent: str, to_agent: str, message: Dict):
        """
        Agent间消息传递
        """
        if to_agent not in self.agent_contexts:
            raise ValueError(f"Agent {to_agent} not found")
        
        # 验证权限
        if not self._check_permission(from_agent, to_agent, 'send_message'):
            raise PermissionError(f"Agent {from_agent} cannot send message to {to_agent}")
        
        # 添加到目标Agent的消息队列
        self.agent_contexts[to_agent]['message_queue'].append({
            'from': from_agent,
            'message': message,
            'timestamp': time.time()
        })
    
    def receive_message(self, agent_id: str) -> List[Dict]:
        """
        接收消息
        """
        if agent_id not in self.agent_contexts:
            return []
        
        messages = self.agent_contexts[agent_id]['message_queue']
        self.agent_contexts[agent_id]['message_queue'] = []
        
        return messages
    
    def cleanup_context(self, agent_id: str):
        """
        清理上下文（Agent结束时）
        """
        if agent_id in self.agent_contexts:
            del self.agent_contexts[agent_id]
```

##### 6.2 集成到MainAgent
```python
# 修改 core/main_agent.py

class MainAgent(SimpleAgent):
    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager):
        # ... 现有代码 ...
        self.context_isolator = ContextIsolator()  # 新增
    
    def _route_to_create_plan(self, input_data: str) -> str:
        # 创建隔离上下文
        agent_id = f"create_plan_{int(time.time())}"
        context = self.context_isolator.create_isolated_context(
            agent_id, 
            parent_context={'domain': self._extract_domain(input_data)}
        )
        
        try:
            agent = CreatePlanAgent(self.llm, streaming=self.streaming)
            result = agent.run(input_data)
            
            # 清理上下文
            self.context_isolator.cleanup_context(agent_id)
            
            return result
        except Exception as e:
            self.context_isolator.cleanup_context(agent_id)
            raise
```

---

### 7. 提示词工程技巧

#### 解决方案

##### 7.1 提示词模板库
```python
# 新增文件: utils/prompt_templates.py

class PromptTemplates:
    """
    提示词模板库
    
    包含常用的提示词工程技巧：
    1. Chain-of-Thought (CoT)
    2. Few-Shot Learning
    3. Self-Consistency
    4. Tree-of-Thought
    5. ReAct
    """
    
    @staticmethod
    def chain_of_thought(task: str, examples: List[Dict] = None) -> str:
        """
        思维链提示
        
        Args:
            task: 任务描述
            examples: 示例列表
            
        Returns:
            完整提示词
        """
        prompt = f"""请一步步思考并解决以下问题：

任务：{task}

请按照以下格式回答：
1. 首先，分析问题的关键点
2. 然后，列出可能的解决方案
3. 接着，评估每个方案的优缺点
4. 最后，给出最优解决方案

让我们开始：
"""
        
        if examples:
            prompt = "以下是几个示例：\n\n" + \
                    "\n\n".join([f"示例{i+1}:\n{ex['input']}\n答案：{ex['output']}" 
                                for i, ex in enumerate(examples)]) + \
                    "\n\n现在请解决新问题：\n\n" + prompt
        
        return prompt
    
    @staticmethod
    def few_shot(task: str, examples: List[Dict], new_input: str) -> str:
        """
        少样本学习提示
        
        Args:
            task: 任务描述
            examples: 示例列表 [{'input': str, 'output': str}, ...]
            new_input: 新输入
        """
        prompt = f"任务：{task}\n\n"
        prompt += "以下是几个示例：\n\n"
        
        for i, example in enumerate(examples, 1):
            prompt += f"示例{i}：\n"
            prompt += f"输入：{example['input']}\n"
            prompt += f"输出：{example['output']}\n\n"
        
        prompt += f"现在请处理：\n输入：{new_input}\n输出："
        
        return prompt
    
    @staticmethod
    def self_consistency(task: str, num_samples: int = 5) -> str:
        """
        自一致性提示
        
        生成多个推理路径，然后投票选择最一致的答案
        """
        prompt = f"""请为以下问题生成{num_samples}个不同的推理路径：

任务：{task}

请分别从不同角度思考，生成{num_samples}个独立的答案。
然后分析这些答案的一致性，给出最终结论。

格式：
推理路径1：...
推理路径2：...
...
推理路径{num_samples}：...

一致性分析：...
最终答案：...
"""
        return prompt
    
    @staticmethod
    def tree_of_thought(task: str, branching_factor: int = 3) -> str:
        """
        思维树提示
        
        探索多个思维分支，评估每个分支的价值
        """
        prompt = f"""请使用思维树方法解决以下问题：

任务：{task}

步骤1：生成{branching_factor}个初始想法
步骤2：评估每个想法的可行性（0-10分）
步骤3：选择最有前景的想法继续探索
步骤4：重复以上步骤，直到找到解决方案

请按照以下格式思考：

第1轮：
- 想法1：... （评分：X/10）
- 想法2：... （评分：X/10）
- 想法3：... （评分：X/10）
选择：想法X

第2轮：
基于想法X，继续探索...

最终解决方案：...
"""
        return prompt
    
    @staticmethod
    def react_prompt(task: str, tools: List[str]) -> str:
        """
        ReAct提示（推理+行动）
        
        Args:
            task: 任务描述
            tools: 可用工具列表
        """
        prompt = f"""请使用ReAct方法解决以下问题：

任务：{task}

可用工具：{', '.join(tools)}

按照以下格式思考和行动：

Thought: 思考当前情况
Action: 工具名[参数]
Observation: 工具返回结果
... (重复Thought/Action/Observation)
Thought: 我现在知道最终答案了
Finish: [最终答案]

开始：
"""
        return prompt
```

##### 7.2 提示词优化器
```python
# 新增文件: utils/prompt_optimizer.py

class PromptOptimizer:
    """
    提示词优化器
    
    功能：
    1. 自动优化提示词
    2. A/B测试
    3. 效果评估
    """
    
    def optimize_prompt(self, base_prompt: str, test_cases: List[Dict]) -> str:
        """
        自动优化提示词
        
        Args:
            base_prompt: 基础提示词
            test_cases: 测试用例
            
        Returns:
            优化后的提示词
        """
        # 生成变体
        variants = self._generate_variants(base_prompt)
        
        # 测试每个变体
        scores = []
        for variant in variants:
            score = self._evaluate_prompt(variant, test_cases)
            scores.append((variant, score))
        
        # 选择最佳变体
        best_variant = max(scores, key=lambda x: x[1])
        
        return best_variant[0]
    
    def _generate_variants(self, prompt: str) -> List[str]:
        """
        生成提示词变体
        """
        variants = []
        
        # 变体1：添加示例
        variants.append(prompt + "\n\n示例：...")
        
        # 变体2：改变语气
        variants.append(prompt.replace("请", "你需要"))
        
        # 变体3：添加约束
        variants.append(prompt + "\n\n注意：答案必须简洁明了。")
        
        return variants
    
    def _evaluate_prompt(self, prompt: str, test_cases: List[Dict]) -> float:
        """
        评估提示词效果
        """
        correct = 0
        for test_case in test_cases:
            # 使用提示词生成答案
            answer = llm.invoke([{"role": "user", "content": prompt + "\n\n" + test_case['input']}])
            
            # 检查答案
            if self._check_answer(answer, test_case['expected']):
                correct += 1
        
        return correct / len(test_cases)
```

---

### 8. Skill和MCP集成

#### 解决方案

##### 8.1 Skill系统设计
```python
# 新增文件: core/skill_system.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Skill(ABC):
    """
    Skill基类
    
    Skill是可复用的功能模块，可以被Agent调用
    """
    
    @abstractmethod
    def name(self) -> str:
        """Skill名称"""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Skill描述"""
        pass
    
    @abstractmethod
    def parameters(self) -> Dict:
        """参数定义"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行Skill"""
        pass

class SkillRegistry:
    """
    Skill注册中心
    """
    
    def __init__(self):
        self.skills = {}
    
    def register(self, skill: Skill):
        """注册Skill"""
        self.skills[skill.name()] = skill
    
    def get(self, name: str) -> Skill:
        """获取Skill"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict]:
        """列出所有Skill"""
        return [
            {
                'name': skill.name(),
                'description': skill.description(),
                'parameters': skill.parameters()
            }
            for skill in self.skills.values()
        ]

# 示例Skill
class WebSearchSkill(Skill):
    """网络搜索Skill"""
    
    def name(self) -> str:
        return "web_search"
    
    def description(self) -> str:
        return "搜索互联网获取信息"
    
    def parameters(self) -> Dict:
        return {
            'query': {'type': 'string', 'description': '搜索查询'},
            'num_results': {'type': 'int', 'description': '返回结果数量', 'default': 5}
        }
    
    def execute(self, query: str, num_results: int = 5) -> List[Dict]:
        # 实现搜索逻辑
        pass

class PDFParserSkill(Skill):
    """PDF解析Skill"""
    
    def name(self) -> str:
        return "pdf_parser"
    
    def description(self) -> str:
        return "解析PDF文件提取文本"
    
    def parameters(self) -> Dict:
        return {
            'file_path': {'type': 'string', 'description': 'PDF文件路径'}
        }
    
    def execute(self, file_path: str) -> str:
        # 实现PDF解析逻辑
        pass
```

##### 8.2 MCP (Model Context Protocol) 集成
```python
# 新增文件: core/mcp_integration.py

from typing import Dict, Any, List
import json

class MCPClient:
    """
    MCP客户端
    
    MCP是一种标准化的Agent通信协议
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.context = {}
    
    def send_request(self, method: str, params: Dict) -> Dict:
        """
        发送MCP请求
        
        Args:
            method: 方法名
            params: 参数
            
        Returns:
            响应结果
        """
        request = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': self._generate_request_id()
        }
        
        # 发送请求（通过某种传输机制）
        response = self._send(request)
        
        return response
    
    def handle_notification(self, notification: Dict):
        """
        处理MCP通知
        """
        method = notification.get('method')
        params = notification.get('params', {})
        
        if method == 'context/update':
            self._update_context(params)
        elif method == 'skill/register':
            self._register_skill(params)
    
    def _update_context(self, context_update: Dict):
        """
        更新上下文
        """
        self.context.update(context_update)

class MCPServer:
    """
    MCP服务器
    
    管理多个Agent之间的通信
    """
    
    def __init__(self):
        self.agents = {}
        self.skills = SkillRegistry()
    
    def register_agent(self, agent_id: str, client: MCPClient):
        """注册Agent"""
        self.agents[agent_id] = client
    
    def route_message(self, from_agent: str, to_agent: str, message: Dict):
        """
        路由消息
        """
        if to_agent in self.agents:
            self.agents[to_agent].handle_notification({
                'method': 'message/receive',
                'params': {
                    'from': from_agent,
                    'message': message
                }
            })
    
    def broadcast_context(self, context: Dict):
        """
        广播上下文更新
        """
        for agent_id, client in self.agents.items():
            client.handle_notification({
                'method': 'context/update',
                'params': context
            })
```

##### 8.3 集成到LearningAgent
```python
# 修改 core/main_agent.py

class MainAgent(SimpleAgent):
    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager):
        # ... 现有代码 ...
        
        # 初始化Skill系统
        self.skill_registry = SkillRegistry()
        self._register_default_skills()
        
        # 初始化MCP
        self.mcp_client = MCPClient(agent_id="main_agent")
    
    def _register_default_skills(self):
        """注册默认Skills"""
        self.skill_registry.register(WebSearchSkill())
        self.skill_registry.register(PDFParserSkill())
        # ... 注册更多Skills ...
    
    def execute_skill(self, skill_name: str, **kwargs) -> Any:
        """
        执行Skill
        """
        skill = self.skill_registry.get(skill_name)
        if not skill:
            raise ValueError(f"Skill {skill_name} not found")
        
        return skill.execute(**kwargs)
```

---

## 技术架构升级

### 升级后的整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      应用层 (Application Layer)               │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MainAgent (协调层)                        │   │
│  │  - 意图识别和路由                                      │   │
│  │  - 会话管理                                            │   │
│  │  - 上下文隔离                                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  功能层       │    │              │    │              │
│              │    │              │    │              │
│ ┌──────────┐ │    │ ┌──────────┐ │    │┌──────────┐ │
│ │CreatePlan│ │    │ │VibeLearn│ │    │ │ Summary  │ │
│ │  Agent   │ │    │ │  Agent   │ │    │ │  Agent   │ │
│ └──────────┘ │    │ └──────────┘ │    │└──────────┘ │
│              │    │              │    │              │
│ ┌──────────┐ │    │              │    │              │
│ │AddKnow   │ │    │              │    │              │
│ │Processor │ │    │              │    │              │
│ └──────────┘ │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    记忆层 (Memory Layer)                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Memory       │  │ Memory       │  │ Memory       │     │
│  │ Hierarchy    │  │ Index        │  │ Conflict     │     │
│  │ (长短期记忆)  │  │ (向量索引)    │  │ Resolver     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Hybrid       │  │ Importance   │  │ Compression  │     │
│  │ Retriever    │  │ Evaluator    │  │ Manager      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   基础设施层 (Infrastructure Layer)           │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ KV Cache     │  │ Context      │  │ Skill        │     │
│  │ Manager      │  │ Isolator     │  │ System       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ MCP          │  │ Prompt       │  │ Benchmark    │     │
│  │ Integration  │  │ Templates    │  │ System       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 实施路线图

### Phase 1: 核心记忆系统 (2-3周)

**目标**: 建立完善的记忆管理系统

**任务**:
1. ✅ 实现记忆冲突检测和解决
2. ✅ 实现长短期记忆分层
3. ✅ 实现向量化记忆索引
4. ✅ 实现混合检索策略
5. ✅ 实现重要性评估

**交付物**:
- `core/memory_conflict_resolver.py`
- `core/memory_hierarchy.py`
- `core/memory_index.py`
- `core/hybrid_retriever.py`
- `core/importance_evaluator.py`

### Phase 2: 性能优化 (1-2周)

**目标**: 优化系统性能和资源使用

**任务**:
1. ✅ 实现PagedAttention KV Cache
2. ✅ 实现滑动窗口注意力
3. ✅ 实现记忆压缩优化
4. ✅ 实现Memory Benchmark

**交付物**:
- `core/kv_cache_manager.py`
- `core/sliding_window_attention.py`
- `benchmarks/memory_benchmark.py`
- `benchmarks/metrics.py`

### Phase 3: Agent架构增强 (1-2周)

**目标**: 增强Agent系统的健壮性

**任务**:
1. ✅ 实现上下文隔离机制
2. ✅ 实现提示词模板库
3. ✅ 实现提示词优化器
4. ✅ 集成到现有Agent

**交付物**:
- `core/context_isolator.py`
- `utils/prompt_templates.py`
- `utils/prompt_optimizer.py`

### Phase 4: 模块化系统 (1-2周)

**目标**: 建立可扩展的模块化系统

**任务**:
1. ✅ 实现Skill系统
2. ✅ 实现MCP集成
3. ✅ 迁移现有功能到Skill
4. ✅ 编写文档和示例

**交付物**:
- `core/skill_system.py`
- `core/mcp_integration.py`
- `skills/` 目录（包含各种Skill）
- 文档和示例代码

### Phase 5: 测试和优化 (1周)

**目标**: 全面测试和性能优化

**任务**:
1. ✅ 编写单元测试
2. ✅ 编写集成测试
3. ✅ 运行Benchmark
4. ✅ 性能调优
5. ✅ 文档完善

**交付物**:
- 完整的测试套件
- Benchmark报告
- 性能优化报告
- 用户文档

---

## 技术选型

### 核心依赖

| 组件 | 技术选型 | 版本要求 | 用途 |
|------|---------|---------|------|
| 向量检索 | FAISS | >=1.7.0 | 高效向量相似度搜索 |
| 向量化 | sentence-transformers | >=2.2.0 | 文本向量化 |
| 相似度计算 | scikit-learn | >=1.0.0 | TF-IDF和余弦相似度 |
| 性能监控 | psutil | >=5.8.0 | 内存和CPU监控 |
| 数据处理 | numpy | >=1.21.0 | 数值计算 |
| 测试框架 | pytest | >=7.0.0 | 单元测试 |
| 性能测试 | pytest-benchmark | >=4.0.0 | 性能基准测试 |

### 可选依赖

| 组件 | 技术选型 | 用途 |
|------|---------|------|
| 图数据库 | Neo4j | 知识图谱存储 |
| 缓存 | Redis | 短期记忆缓存 |
| 消息队列 | RabbitMQ | Agent间通信 |
| 监控 | Prometheus | 系统监控 |

---

## 总结

本规划文档详细分析了LearningAgent项目在高级Agent系统方面的现状和不足，并提出了系统化的解决方案。通过实施这些改进，项目将具备：

1. **完善的记忆管理系统** - 支持长短期记忆、冲突检测、智能检索
2. **高效的性能优化** - KV Cache优化、记忆压缩、性能监控
3. **健壮的Agent架构** - 上下文隔离、提示词工程、模块化设计
4. **可扩展的模块系统** - Skill系统、MCP集成、标准化接口

这些改进将使LearningAgent成为一个真正企业级的智能学习助手系统。
