# core/memory_hierarchy.py
"""长短期记忆管理器 - 分层记忆存储和检索"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import shutil


class MemoryHierarchy:
    """
    记忆层次结构管理器
    
    三层记忆结构：
    1. 工作记忆（Working Memory）：当前会话，内存中
    2. 短期记忆（Short-term Memory）：最近7天，快速访问
    3. 长期记忆（Long-term Memory）：永久存储，按重要性归档
    """
    
    def __init__(self, base_dir: Path, compression_ratio: float = 0.3):
        """
        初始化记忆层次管理器
        
        Args:
            base_dir: 基础目录
            compression_ratio: 压缩比例
        """
        self.base_dir = Path(base_dir)
        self.working_memory: Dict[str, List[Dict]] = {}  # 当前会话
        self.short_term_cache: Dict[str, List[Dict]] = {}  # 最近7天
        
        # 延迟导入，避免循环依赖
        from core.memory_compressor import MemoryCompressor
        self.compressor = MemoryCompressor(compression_ratio)
        
        # 创建目录结构
        self._setup_directories()
        
        # 加载短期记忆缓存
        self._load_short_term_cache()
    
    def _setup_directories(self):
        """设置目录结构"""
        # 短期记忆目录
        self.short_term_dir = self.base_dir / "memory" / "short_term"
        self.short_term_dir.mkdir(parents=True, exist_ok=True)
        
        # 长期记忆目录
        self.long_term_dir = self.base_dir / "memory" / "long_term"
        self.long_term_dir.mkdir(parents=True, exist_ok=True)
        
        # 索引文件
        self.short_term_index = self.short_term_dir / "index.json"
        self.long_term_index = self.long_term_dir / "index.json"
    
    def _load_short_term_cache(self):
        """加载短期记忆缓存"""
        if not self.short_term_index.exists():
            return
        
        try:
            with open(self.short_term_index, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
                
            # 过滤过期的短期记忆（超过7天）
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for domain, memories in index_data.items():
                valid_memories = []
                for memory in memories:
                    memory_time = datetime.fromisoformat(memory['timestamp'])
                    if memory_time > cutoff_time:
                        valid_memories.append(memory)
                    else:
                        # 迁移到长期记忆
                        self._migrate_to_long_term(domain, memory)
                
                if valid_memories:
                    self.short_term_cache[domain] = valid_memories
            
            # 更新索引文件
            self._save_short_term_index()
            
        except Exception as e:
            print(f"加载短期记忆缓存失败：{e}")
    
    def _save_short_term_index(self):
        """保存短期记忆索引"""
        try:
            with open(self.short_term_index, 'w', encoding='utf-8') as f:
                json.dump(self.short_term_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存短期记忆索引失败：{e}")
    
    def store(
        self, 
        domain: str, 
        content: str, 
        importance: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        存储记忆
        
        Args:
            domain: 领域名称
            content: 记忆内容
            importance: 重要性评分（0-1）
            metadata: 元数据
            
        Returns:
            记忆ID
        """
        # 边界检查
        importance = max(0.0, min(1.0, importance))
        # 生成记忆ID
        memory_id = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # 创建记忆对象
        memory = {
            'id': memory_id,
            'content': content,
            'importance': importance,
            'timestamp': datetime.now().isoformat(),
            'access_count': 0,
            'metadata': metadata or {}
        }
        
        # 1. 添加到工作记忆
        if domain not in self.working_memory:
            self.working_memory[domain] = []
        self.working_memory[domain].append(memory)
        
        # 2. 根据重要性决定存储位置
        if importance >= 0.7:
            # 高重要性：直接存储到长期记忆
            self._store_long_term(domain, memory)
        else:
            # 低重要性：存储到短期记忆
            self._store_short_term(domain, memory)
        
        return memory_id
    
    def _store_short_term(self, domain: str, memory: Dict):
        """存储到短期记忆"""
        if domain not in self.short_term_cache:
            self.short_term_cache[domain] = []
        
        self.short_term_cache[domain].append(memory)
        
        # 保存到文件
        memory_file = self.short_term_dir / f"{memory['id']}.json"
        try:
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存短期记忆文件失败：{e}")
        
        # 更新索引
        self._save_short_term_index()
    
    def _store_long_term(self, domain: str, memory: Dict):
        """存储到长期记忆"""
        # 创建领域目录
        domain_dir = self.long_term_dir / domain
        domain_dir.mkdir(exist_ok=True)
        
        # 保存记忆文件
        memory_file = domain_dir / f"{memory['id']}.json"
        try:
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存长期记忆文件失败：{e}")
        
        # 更新长期记忆索引
        self._update_long_term_index(domain, memory)
    
    def _update_long_term_index(self, domain: str, memory: Dict):
        """更新长期记忆索引"""
        index_data = {}
        
        if self.long_term_index.exists():
            try:
                with open(self.long_term_index, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            except Exception:
                pass
        
        if domain not in index_data:
            index_data[domain] = []
        
        # 添加索引条目（不包含完整内容）
        index_entry = {
            'id': memory['id'],
            'importance': memory['importance'],
            'timestamp': memory['timestamp'],
            'access_count': memory['access_count'],
            'metadata': memory['metadata']
        }
        
        index_data[domain].append(index_entry)
        
        # 按重要性排序
        index_data[domain].sort(key=lambda x: x['importance'], reverse=True)
        
        # 保存索引
        try:
            with open(self.long_term_index, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存长期记忆索引失败：{e}")
    
    def _migrate_to_long_term(self, domain: str, memory: Dict):
        """迁移到长期记忆"""
        # 更新重要性（根据访问次数）
        memory['importance'] = min(1.0, memory['importance'] + memory['access_count'] * 0.1)
        
        # 存储到长期记忆
        self._store_long_term(domain, memory)
        
        # 从短期记忆删除
        memory_file = self.short_term_dir / f"{memory['id']}.json"
        if memory_file.exists():
            memory_file.unlink()
    
    def retrieve(
        self, 
        domain: str, 
        query: Optional[str] = None,
        top_k: int = 5,
        include_working: bool = True,
        include_short_term: bool = True,
        include_long_term: bool = True
    ) -> List[Dict]:
        """
        检索记忆
        
        Args:
            domain: 领域名称
            query: 查询字符串（可选）
            top_k: 返回数量
            include_working: 是否包含工作记忆
            include_short_term: 是否包含短期记忆
            include_long_term: 是否包含长期记忆
            
        Returns:
            记忆列表
        """
        all_memories = []
        seen_ids = set()
        
        # 1. 从工作记忆检索
        if include_working and domain in self.working_memory:
            for memory in self.working_memory[domain]:
                if memory['id'] not in seen_ids:
                    all_memories.append(memory)
                    seen_ids.add(memory['id'])
        
        # 2. 从短期记忆检索
        if include_short_term and domain in self.short_term_cache:
            for memory in self.short_term_cache[domain]:
                if memory['id'] not in seen_ids:
                    all_memories.append(memory)
                    seen_ids.add(memory['id'])
        
        # 3. 从长期记忆检索
        if include_long_term:
            long_term_memories = self._retrieve_long_term(domain, top_k)
            for memory in long_term_memories:
                if memory['id'] not in seen_ids:
                    all_memories.append(memory)
                    seen_ids.add(memory['id'])
        
        # 按重要性排序
        all_memories.sort(key=lambda x: x['importance'], reverse=True)
        
        # 返回top_k
        return all_memories[:top_k]
    
    def _retrieve_long_term(self, domain: str, top_k: int) -> List[Dict]:
        """从长期记忆检索"""
        memories = []
        
        if not self.long_term_index.exists():
            return memories
        
        try:
            with open(self.long_term_index, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            if domain not in index_data:
                return memories
            
            # 获取top_k个记忆
            for entry in index_data[domain][:top_k]:
                memory_file = self.long_term_dir / domain / f"{entry['id']}.json"
                if memory_file.exists():
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        memory = json.load(f)
                        memories.append(memory)
                        
                        # 更新访问计数
                        memory['access_count'] = memory.get('access_count', 0) + 1
                        with open(memory_file, 'w', encoding='utf-8') as f_write:
                            json.dump(memory, f_write, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"检索长期记忆失败：{e}")
        
        return memories
    
    def update_importance(self, memory_id: str, domain: str, delta: float = 0.1):
        """
        更新记忆重要性
        
        Args:
            memory_id: 记忆ID
            domain: 领域名称
            delta: 重要性变化值
        """
        # 在工作记忆中查找
        if domain in self.working_memory:
            for memory in self.working_memory[domain]:
                if memory['id'] == memory_id:
                    memory['importance'] = max(0.0, min(1.0, memory['importance'] + delta))
                    return
        
        # 在短期记忆中查找
        if domain in self.short_term_cache:
            for memory in self.short_term_cache[domain]:
                if memory['id'] == memory_id:
                    memory['importance'] = max(0.0, min(1.0, memory['importance'] + delta))
                    self._save_short_term_index()
                    return
        
        # 在长期记忆中查找
        memory_file = self.long_term_dir / domain / f"{memory_id}.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
                
                memory['importance'] = max(0.0, min(1.0, memory['importance'] + delta))
                
                with open(memory_file, 'w', encoding='utf-8') as f:
                    json.dump(memory, f, ensure_ascii=False, indent=2)
                
                # 更新索引
                self._update_long_term_index(domain, memory)
                
            except Exception as e:
                print(f"更新长期记忆重要性失败：{e}")
    
    def forget(self, memory_id: str, domain: str) -> bool:
        """
        遗忘记忆
        
        Args:
            memory_id: 记忆ID
            domain: 领域名称
            
        Returns:
            是否成功
        """
        # 从工作记忆删除
        if domain in self.working_memory:
            self.working_memory[domain] = [
                m for m in self.working_memory[domain] if m['id'] != memory_id
            ]
        
        # 从短期记忆删除
        if domain in self.short_term_cache:
            self.short_term_cache[domain] = [
                m for m in self.short_term_cache[domain] if m['id'] != memory_id
            ]
            self._save_short_term_index()
            
            # 删除文件
            memory_file = self.short_term_dir / f"{memory_id}.json"
            if memory_file.exists():
                memory_file.unlink()
        
        # 从长期记忆删除
        memory_file = self.long_term_dir / domain / f"{memory_id}.json"
        if memory_file.exists():
            memory_file.unlink()
            
            # 更新索引
            if self.long_term_index.exists():
                try:
                    with open(self.long_term_index, 'r', encoding='utf-8') as f:
                        index_data = json.load(f)
                    
                    if domain in index_data:
                        index_data[domain] = [
                            entry for entry in index_data[domain] 
                            if entry['id'] != memory_id
                        ]
                        
                        with open(self.long_term_index, 'w', encoding='utf-8') as f:
                            json.dump(index_data, f, ensure_ascii=False, indent=2)
                
                except Exception as e:
                    print(f"更新长期记忆索引失败：{e}")
        
        return True
    
    def clear_working_memory(self, domain: Optional[str] = None):
        """
        清空工作记忆
        
        Args:
            domain: 领域名称（可选，None表示清空所有）
        """
        if domain:
            self.working_memory.pop(domain, None)
        else:
            self.working_memory.clear()
    
    def get_memory_stats(self, domain: str) -> Dict:
        """
        获取记忆统计信息
        
        Args:
            domain: 领域名称
            
        Returns:
            统计信息
        """
        stats = {
            'working_memory_count': len(self.working_memory.get(domain, [])),
            'short_term_count': len(self.short_term_cache.get(domain, [])),
            'long_term_count': 0,
            'total_importance': 0.0,
            'avg_importance': 0.0
        }
        
        # 统计长期记忆
        if self.long_term_index.exists():
            try:
                with open(self.long_term_index, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                if domain in index_data:
                    stats['long_term_count'] = len(index_data[domain])
                    
                    # 计算平均重要性
                    if index_data[domain]:
                        total = sum(entry['importance'] for entry in index_data[domain])
                        stats['total_importance'] = total
                        stats['avg_importance'] = total / len(index_data[domain])
            
            except Exception:
                pass
        
        return stats
    
    def compress_memories(self, domain: str, target_count: int = 10) -> Dict:
        """
        压缩记忆
        
        Args:
            domain: 领域名称
            target_count: 目标记忆数量
            
        Returns:
            压缩统计信息
        """
        # 获取所有记忆
        all_memories = self.retrieve(domain, top_k=100)
        
        if len(all_memories) <= target_count:
            return {
                'original_count': len(all_memories),
                'compressed_count': len(all_memories),
                'compressed': False
            }
        
        # 合并相似记忆
        merged_memories = self.compressor.merge_similar(all_memories)
        
        # 批量压缩
        compressed_contents = self.compressor.batch_compress(merged_memories)
        
        # 更新记忆内容
        for memory in merged_memories:
            if memory['id'] in compressed_contents:
                memory['content'] = compressed_contents[memory['id']]
        
        # 清空现有记忆
        self.clear_working_memory(domain)
        self.short_term_cache.pop(domain, None)
        
        # 重新存储压缩后的记忆
        for memory in merged_memories[:target_count]:
            if domain not in self.working_memory:
                self.working_memory[domain] = []
            self.working_memory[domain].append(memory)
        
        return {
            'original_count': len(all_memories),
            'compressed_count': len(merged_memories[:target_count]),
            'compressed': True,
            'space_saved': len(all_memories) - len(merged_memories[:target_count])
        }
    
    def get_memory_summary(self, domain: str, max_length: int = 200) -> str:
        """
        获取记忆摘要
        
        Args:
            domain: 领域名称
            max_length: 最大长度
            
        Returns:
            摘要文本
        """
        memories = self.retrieve(domain, top_k=20)
        return self.compressor.summarize(memories, max_length)
