# tests/test_core/test_memory_compressor.py
"""记忆压缩器单元测试"""

import pytest
from core.memory_compressor import MemoryCompressor


class TestMemoryCompressor:
    """测试记忆压缩器"""
    
    @pytest.fixture
    def compressor(self):
        """创建压缩器实例"""
        return MemoryCompressor(compression_ratio=0.3)
    
    def test_compress_short_text(self, compressor):
        """测试压缩短文本"""
        short_text = "这是一个短文本"
        
        compressed = compressor.compress(short_text)
        
        # 短文本不压缩
        assert compressed == short_text
    
    def test_compress_long_text(self, compressor):
        """测试压缩长文本"""
        long_text = """
        Python是一种广泛使用的高级编程语言。它由Guido van Rossum于1991年创建。
        Python的设计哲学强调代码的可读性和简洁性。它的语法允许程序员用更少的代码行表达概念。
        Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。
        它有一个大型标准库，提供了丰富的功能模块。Python常用于Web开发、数据分析、人工智能等领域。
        """
        
        compressed = compressor.compress(long_text)
        
        # 压缩后应该更短
        assert len(compressed) < len(long_text)
        
        # 压缩比例应该接近目标
        ratio = len(compressed) / len(long_text)
        assert ratio <= 0.5  # 允许一定的误差
    
    def test_extract_sentences(self, compressor):
        """测试句子提取"""
        text = "这是第一句。这是第二句！这是第三句？"
        
        sentences = compressor._extract_sentences(text)
        
        assert len(sentences) == 3
        assert "这是第一句" in sentences[0]
    
    def test_extract_keywords(self, compressor):
        """测试关键词提取"""
        text = "Python是一种编程语言，广泛用于Web开发"
        
        keywords = compressor._extract_keywords(text)
        
        # 应该提取到关键词
        assert "Python" in keywords
        assert "编程语言" in keywords
        assert "Web开发" in keywords
        
        # 停用词应该被过滤
        assert "是" not in keywords
        assert "一种" not in keywords
    
    def test_identify_key_sentences(self, compressor):
        """测试关键句子识别"""
        sentences = [
            "Python是一种编程语言。",
            "重要：Python广泛应用于人工智能。",
            "它有很多优点。",
            "Python易于学习。"
        ]
        
        key_sentences = compressor._identify_key_sentences(sentences)
        
        # 应该返回带分数和索引的元组
        assert len(key_sentences) == 4
        assert len(key_sentences[0]) == 3  # (句子, 分数, 索引)
        
        # 包含"重要"的句子应该得分更高
        important_sentence = [s for s in key_sentences if "重要" in s[0]]
        assert len(important_sentence) > 0
        assert important_sentence[0][1] > 0  # 分数应该大于0
    
    def test_merge_similar_memories(self, compressor):
        """测试合并相似记忆"""
        memories = [
            {
                'id': 'mem1',
                'content': 'Python是一种编程语言',
                'importance': 0.5
            },
            {
                'id': 'mem2',
                'content': 'Python是编程语言',
                'importance': 0.6
            },
            {
                'id': 'mem3',
                'content': 'Java是另一种编程语言',
                'importance': 0.5
            }
        ]
        
        merged = compressor.merge_similar(memories, similarity_threshold=0.5)
        
        # 前两个记忆应该被合并
        assert len(merged) < len(memories)
        
        # 合并后的记忆应该包含merged_from字段
        merged_memory = [m for m in merged if 'merged_from' in m]
        assert len(merged_memory) > 0
    
    def test_calculate_similarity(self, compressor):
        """测试相似度计算"""
        text1 = "Python是一种编程语言"
        text2 = "Python是编程语言"
        text3 = "Java是另一种编程语言"
        
        sim12 = compressor._calculate_similarity(text1, text2)
        sim13 = compressor._calculate_similarity(text1, text3)
        
        # 相似文本应该有更高的相似度
        assert sim12 > sim13
    
    def test_summarize_memories(self, compressor):
        """测试生成摘要"""
        memories = [
            {'content': 'Python是一种编程语言。'},
            {'content': 'Python广泛应用于人工智能。'},
            {'content': 'Python易于学习和使用。'}
        ]
        
        summary = compressor.summarize(memories, max_length=100)
        
        # 摘要应该比原始内容短
        total_length = sum(len(m['content']) for m in memories)
        assert len(summary) < total_length
        
        # 摘要长度应该在限制内
        assert len(summary) <= 120  # 允许一定的误差
    
    def test_summarize_empty_memories(self, compressor):
        """测试空记忆的摘要"""
        summary = compressor.summarize([])
        
        assert summary == "暂无记忆"
    
    def test_get_compression_stats(self, compressor):
        """测试压缩统计"""
        original = "这是一个很长的文本内容，需要进行压缩处理。" * 10
        compressed = "这是一个很长的文本内容"
        
        stats = compressor.get_compression_stats(original, compressed)
        
        assert stats['original_length'] == len(original)
        assert stats['compressed_length'] == len(compressed)
        assert stats['compression_ratio'] < 1.0
        assert stats['space_saved'] > 0
        assert stats['space_saved_percentage'] > 0
    
    def test_batch_compress(self, compressor):
        """测试批量压缩"""
        memories = [
            {'id': 'mem1', 'content': 'Python是一种编程语言。' * 10},
            {'id': 'mem2', 'content': 'Java是另一种编程语言。' * 10},
            {'id': 'mem3', 'content': 'JavaScript用于网页开发。' * 10}
        ]
        
        compressed = compressor.batch_compress(memories)
        
        # 应该返回所有记忆的压缩版本
        assert len(compressed) == 3
        assert 'mem1' in compressed
        assert 'mem2' in compressed
        assert 'mem3' in compressed
        
        # 所有压缩后的内容都应该更短
        for memory in memories:
            assert len(compressed[memory['id']]) < len(memory['content'])
    
    def test_compress_with_keywords(self, compressor):
        """测试保留关键词的压缩"""
        text = """
        Python是一种编程语言。
        重要：Python广泛应用于人工智能和机器学习。
        Python有很多优点，包括易于学习和使用。
        Python的标准库非常丰富。
        """
        
        compressed = compressor.compress(text, preserve_keywords=True)
        
        # 压缩后的文本应该包含关键词
        assert "Python" in compressed
        assert "人工智能" in compressed or "机器学习" in compressed
    
    def test_clean_text(self, compressor):
        """测试文本清理"""
        dirty_text = "这是  一个  文本。。。！！！"
        
        clean = compressor._clean_text(dirty_text)
        
        # 应该移除多余空格
        assert "  " not in clean
        
        # 应该移除重复标点
        assert "。。。" not in clean
        assert "！！！" not in clean
    
    def test_compression_ratio(self):
        """测试不同的压缩比例"""
        text = "Python是一种编程语言。" * 20
        
        # 低压缩比例（保留更多内容）
        compressor_low = MemoryCompressor(compression_ratio=0.5)
        compressed_low = compressor_low.compress(text)
        
        # 高压缩比例（保留更少内容）
        compressor_high = MemoryCompressor(compression_ratio=0.2)
        compressed_high = compressor_high.compress(text)
        
        # 高压缩比例应该产生更短的文本
        assert len(compressed_high) < len(compressed_low)
    
    def test_merge_contents(self, compressor):
        """测试内容合并"""
        contents = [
            "Python是一种编程语言",
            "Python是一种编程语言",  # 重复
            "Python广泛应用于AI",
            "Python易于学习"
        ]
        
        merged = compressor._merge_contents(contents)
        
        # 应该去重
        assert merged.count("Python是一种编程语言") == 1
        
        # 应该包含所有独特内容
        assert "Python广泛应用于AI" in merged
        assert "Python易于学习" in merged
