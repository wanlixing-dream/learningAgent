# core/memory_conflict_resolver.py
"""记忆冲突检测和解决器 - 检测并解决知识冲突"""

from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class MemoryConflictResolver:
    """
    记忆冲突检测和解决器
    
    策略：
    1. 向量化所有知识条目
    2. 计算新知识与现有知识的相似度
    3. 相似度 > threshold 视为冲突
    4. 提供三种解决策略：合并、覆盖、保留两者
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        初始化冲突检测器
        
        Args:
            similarity_threshold: 相似度阈值，超过此值视为冲突
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,
            ngram_range=(1, 2)
        )
        
    def detect_conflicts(
        self, 
        new_content: str, 
        existing_contents: List[str]
    ) -> List[Tuple[int, float, str]]:
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
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_contents)
            
            # 计算相似度（新内容与所有现有内容）
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            
            # 识别冲突
            conflicts = []
            for idx, sim in enumerate(similarities):
                if sim > self.similarity_threshold:
                    conflict_type = self._classify_conflict(
                        new_content, 
                        existing_contents[idx]
                    )
                    conflicts.append((idx, float(sim), conflict_type))
            
            return conflicts
            
        except Exception as e:
            # 如果向量化失败，使用简单的字符串匹配
            return self._simple_conflict_detection(new_content, existing_contents)
    
    def _simple_conflict_detection(
        self, 
        new_content: str, 
        existing_contents: List[str]
    ) -> List[Tuple[int, float, str]]:
        """
        简单的冲突检测（降级方案）
        
        使用字符串包含关系判断
        """
        conflicts = []
        new_lower = new_content.lower().strip()
        
        for idx, existing in enumerate(existing_contents):
            existing_lower = existing.lower().strip()
            
            # 完全相同
            if new_lower == existing_lower:
                conflicts.append((idx, 1.0, 'duplicate'))
            # 包含关系
            elif new_lower in existing_lower or existing_lower in new_lower:
                conflicts.append((idx, 0.9, 'update'))
        
        return conflicts
    
    def _classify_conflict(self, content1: str, content2: str) -> str:
        """
        分类冲突类型
        
        Args:
            content1: 内容1
            content2: 内容2
            
        Returns:
            冲突类型：
            - 'duplicate': 完全重复
            - 'update': 更新版本
            - 'contradiction': 矛盾冲突
            - 'supplement': 补充信息
        """
        # 标准化内容
        c1 = content1.lower().strip()
        c2 = content2.lower().strip()
        
        # 完全重复
        if c1 == c2:
            return 'duplicate'
        
        # 检查更新关键词
        update_keywords = ['更新', '新版本', '修改', '更正', 'update', 'new version', 'modified']
        if any(keyword in c1 for keyword in update_keywords):
            return 'update'
        
        # 检查矛盾关键词
        contradiction_keywords = ['但是', '然而', '不过', '相反', '错误', 'but', 'however', 'wrong', 'incorrect']
        if any(keyword in c1 for keyword in contradiction_keywords):
            return 'contradiction'
        
        # 默认为补充信息
        return 'supplement'
    
    def resolve_conflict(
        self, 
        new_content: str, 
        existing_content: str, 
        conflict_type: str, 
        strategy: str = 'auto'
    ) -> Tuple[str, str]:
        """
        解决冲突
        
        Args:
            new_content: 新内容
            existing_content: 现有内容
            conflict_type: 冲突类型
            strategy: 解决策略
                - 'merge': 合并内容
                - 'overwrite': 覆盖现有内容
                - 'keep_both': 保留两者
                - 'auto': 自动选择策略
                
        Returns:
            (解决后的内容, 使用的策略)
        """
        if strategy == 'auto':
            strategy = self._auto_select_strategy(conflict_type)
        
        if strategy == 'merge':
            merged = self._merge_contents(new_content, existing_content)
            return merged, 'merge'
        elif strategy == 'overwrite':
            return new_content, 'overwrite'
        elif strategy == 'keep_both':
            combined = f"{existing_content}\n\n---\n\n**补充内容：**\n\n{new_content}"
            return combined, 'keep_both'
        else:
            return new_content, 'overwrite'
    
    def _auto_select_strategy(self, conflict_type: str) -> str:
        """
        根据冲突类型自动选择策略
        
        Args:
            conflict_type: 冲突类型
            
        Returns:
            推荐的策略
        """
        strategy_map = {
            'duplicate': 'overwrite',      # 重复：覆盖
            'update': 'overwrite',          # 更新：覆盖
            'contradiction': 'keep_both',   # 矛盾：保留两者
            'supplement': 'merge'           # 补充：合并
        }
        
        return strategy_map.get(conflict_type, 'overwrite')
    
    def _merge_contents(self, content1: str, content2: str) -> str:
        """
        合并两个内容
        
        Args:
            content1: 内容1
            content2: 内容2
            
        Returns:
            合并后的内容
        """
        # 简单合并策略：保留两者，添加分隔符
        lines1 = content1.strip().split('\n')
        lines2 = content2.strip().split('\n')
        
        # 去重
        unique_lines = []
        seen = set()
        
        for line in lines1 + lines2:
            line_stripped = line.strip()
            if line_stripped and line_stripped not in seen:
                unique_lines.append(line)
                seen.add(line_stripped)
        
        return '\n'.join(unique_lines)
    
    def batch_detect_conflicts(
        self, 
        new_contents: List[str], 
        existing_contents: List[str]
    ) -> Dict[int, List[Tuple[int, float, str]]]:
        """
        批量检测冲突
        
        Args:
            new_contents: 新知识列表
            existing_contents: 现有知识列表
            
        Returns:
            冲突映射: {新内容索引: [(现有内容索引, 相似度, 冲突类型), ...]}
        """
        if not existing_contents or not new_contents:
            return {}
        
        # 向量化所有内容
        all_contents = new_contents + existing_contents
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_contents)
            
            # 计算相似度矩阵
            num_new = len(new_contents)
            similarity_matrix = cosine_similarity(
                tfidf_matrix[:num_new], 
                tfidf_matrix[num_new:]
            )
            
            # 识别冲突
            conflicts_map = {}
            for new_idx in range(num_new):
                conflicts = []
                for exist_idx, sim in enumerate(similarity_matrix[new_idx]):
                    if sim > self.similarity_threshold:
                        conflict_type = self._classify_conflict(
                            new_contents[new_idx],
                            existing_contents[exist_idx]
                        )
                        conflicts.append((exist_idx, float(sim), conflict_type))
                
                if conflicts:
                    conflicts_map[new_idx] = conflicts
            
            return conflicts_map
            
        except Exception as e:
            # 降级：逐个检测
            conflicts_map = {}
            for new_idx, new_content in enumerate(new_contents):
                conflicts = self.detect_conflicts(new_content, existing_contents)
                if conflicts:
                    conflicts_map[new_idx] = conflicts
            
            return conflicts_map
