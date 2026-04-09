# core/memory_compressor.py
"""记忆压缩器 - 智能压缩和总结记忆"""

from typing import List, Dict, Optional
from datetime import datetime
import re


class MemoryCompressor:
    """
    记忆压缩器
    
    功能：
    1. 提取关键信息
    2. 去除冗余内容
    3. 合并相似记忆
    4. 生成摘要
    """
    
    def __init__(self, compression_ratio: float = 0.3):
        """
        初始化记忆压缩器
        
        Args:
            compression_ratio: 压缩比例（0-1），越小压缩越多
        """
        self.compression_ratio = compression_ratio
        self.stop_words = self._load_stop_words()
    
    def _load_stop_words(self) -> set:
        """加载停用词"""
        # 常见中文停用词
        return {
            '的', '了', '是', '在', '我', '有', '和', '就',
            '不', '人', '都', '一', '一个', '上', '也', '很',
            '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这', '那', '她', '他', '它',
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'shall', 'can', 'need', 'dare'
        }
    
    def compress(self, content: str, preserve_keywords: bool = True) -> str:
        """
        压缩单个记忆内容
        
        Args:
            content: 原始内容
            preserve_keywords: 是否保留关键词
            
        Returns:
            压缩后的内容
        """
        if not content or len(content) < 50:
            return content
        
        # 1. 提取关键句子
        sentences = self._extract_sentences(content)
        key_sentences = self._identify_key_sentences(sentences)
        
        # 2. 根据压缩比例选择句子
        target_length = int(len(content) * self.compression_ratio)
        compressed = self._select_sentences(key_sentences, target_length)
        
        # 3. 清理和格式化
        compressed = self._clean_text(compressed)
        
        return compressed
    
    def _extract_sentences(self, text: str) -> List[str]:
        """提取句子"""
        # 按句号、问号、感叹号分割
        sentences = re.split(r'[。！？.!?]+', text)
        
        # 过滤空句子
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _identify_key_sentences(self, sentences: List[str]) -> List[tuple]:
        """
        识别关键句子
        
        Returns:
            [(句子, 重要性分数, 原始索引), ...]
        """
        scored_sentences = []
        
        for idx, sentence in enumerate(sentences):
            score = 0.0
            
            # 1. 长度得分（中等长度更重要）
            length = len(sentence)
            if 10 <= length <= 50:
                score += 0.3
            elif 50 < length <= 100:
                score += 0.2
            else:
                score += 0.1
            
            # 2. 关键词得分
            keywords = self._extract_keywords(sentence)
            score += len(keywords) * 0.1
            
            # 3. 位置得分（开头和结尾更重要）
            total = len(sentences)
            if idx < total * 0.2:  # 前20%
                score += 0.2
            elif idx > total * 0.8:  # 后20%
                score += 0.1
            
            # 4. 特殊标记得分
            if any(marker in sentence for marker in ['重要', '关键', '核心', '重点', 'important', 'key']):
                score += 0.3
            
            scored_sentences.append((sentence, score, idx))
        
        # 按分数排序
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        return scored_sentences
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取：去除停用词后的词
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', text)
        
        keywords = [
            word for word in words
            if word.lower() not in self.stop_words and len(word) > 1
        ]
        
        return keywords
    
    def _select_sentences(self, scored_sentences: List[tuple], target_length: int) -> str:
        """选择句子以达到目标长度"""
        selected = []
        current_length = 0
        
        for sentence, score, idx in scored_sentences:
            if current_length + len(sentence) <= target_length:
                selected.append((sentence, score, idx))
                current_length += len(sentence)
            elif current_length >= target_length * 0.8:
                # 达到目标的80%就停止
                break
        
        # 按原始顺序重新排序
        selected.sort(key=lambda x: x[2])
        
        return '。'.join([s[0] for s in selected]) + '。'
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除重复标点
        text = re.sub(r'([。！？，、])\1+', r'\1', text)
        
        return text.strip()
    
    def batch_compress(self, memories: List[Dict]) -> Dict[str, str]:
        """
        批量压缩记忆
        
        Args:
            memories: 记忆列表
            
        Returns:
            {记忆ID: 压缩后的内容}
        """
        compressed = {}
        
        for memory in memories:
            memory_id = memory.get('id')
            content = memory.get('content', '')
            
            if memory_id and content:
                compressed[memory_id] = self.compress(content)
        
        return compressed
    
    def merge_similar(self, memories: List[Dict], similarity_threshold: float = 0.7) -> List[Dict]:
        """
        合并相似记忆
        
        Args:
            memories: 记忆列表
            similarity_threshold: 相似度阈值
            
        Returns:
            合并后的记忆列表
        """
        if not memories:
            return []
        
        merged = []
        used = set()
        
        for i, memory1 in enumerate(memories):
            if i in used:
                continue
            
            # 找到所有与当前记忆相似的记忆
            similar_group = [memory1]
            
            for j, memory2 in enumerate(memories[i+1:], start=i+1):
                if j in used:
                    continue
                
                similarity = self._calculate_similarity(
                    memory1.get('content', ''),
                    memory2.get('content', '')
                )
                
                if similarity > similarity_threshold:
                    similar_group.append(memory2)
                    used.add(j)
            
            # 合并相似记忆
            if len(similar_group) > 1:
                merged_memory = self._merge_memory_group(similar_group)
                merged.append(merged_memory)
            else:
                merged.append(memory1)
            
            used.add(i)
        
        return merged
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简单版本）"""
        # 提取关键词
        keywords1 = set(self._extract_keywords(text1))
        keywords2 = set(self._extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # Jaccard 相似度
        intersection = keywords1 & keywords2
        union = keywords1 | keywords2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _merge_memory_group(self, memories: List[Dict]) -> Dict:
        """合并一组相似记忆"""
        # 选择重要性最高的作为基础
        base_memory = max(memories, key=lambda m: m.get('importance', 0))
        
        # 合并内容
        all_contents = [m.get('content', '') for m in memories]
        merged_content = self._merge_contents(all_contents)
        
        # 创建合并后的记忆
        merged_memory = base_memory.copy()
        merged_memory['content'] = merged_content
        merged_memory['merged_from'] = [m.get('id') for m in memories if m.get('id') != base_memory.get('id')]
        merged_memory['merge_count'] = len(memories)
        
        return merged_memory
    
    def _merge_contents(self, contents: List[str]) -> str:
        """合并多个内容"""
        # 去重
        unique_lines = set()
        for content in contents:
            lines = content.split('\n')
            for line in lines:
                line_stripped = line.strip()
                if line_stripped:
                    unique_lines.add(line_stripped)
        
        # 按长度排序（短的在前）
        sorted_lines = sorted(unique_lines, key=len)
        
        return '\n'.join(sorted_lines)
    
    def summarize(self, memories: List[Dict], max_length: int = 200) -> str:
        """
        生成记忆摘要
        
        Args:
            memories: 记忆列表
            max_length: 最大长度
            
        Returns:
            摘要文本
        """
        if not memories:
            return "暂无记忆"
        
        # 提取所有内容
        all_contents = [m.get('content', '') for m in memories]
        
        # 合并内容
        combined = '\n\n'.join(all_contents)
        
        # 压缩到目标长度
        summary = self.compress(combined)
        
        # 如果还是太长，再次压缩
        if len(summary) > max_length:
            # 提取关键句子
            sentences = self._extract_sentences(summary)
            key_sentences = self._identify_key_sentences(sentences)
            
            # 选择最重要的句子
            selected = []
            current_length = 0
            
            for sentence, score in key_sentences:
                if current_length + len(sentence) <= max_length:
                    selected.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            summary = '。'.join(selected) + '。'
        
        return summary
    
    def get_compression_stats(self, original: str, compressed: str) -> Dict:
        """
        获取压缩统计信息
        
        Args:
            original: 原始文本
            compressed: 压缩后文本
            
        Returns:
            统计信息
        """
        return {
            'original_length': len(original),
            'compressed_length': len(compressed),
            'compression_ratio': len(compressed) / len(original) if original else 0,
            'space_saved': len(original) - len(compressed),
            'space_saved_percentage': (1 - len(compressed) / len(original)) * 100 if original else 0
        }
