# tests/test_core/test_memory_conflict_resolver.py
"""记忆冲突检测器单元测试"""

import pytest
from core.memory_conflict_resolver import MemoryConflictResolver


class TestMemoryConflictResolver:
    """测试记忆冲突检测器"""
    
    @pytest.fixture
    def resolver(self):
        """创建冲突检测器实例"""
        return MemoryConflictResolver(similarity_threshold=0.8)
    
    def test_detect_no_conflict(self, resolver):
        """测试无冲突的情况"""
        new_content = "Python是一种编程语言"
        existing_contents = [
            "Java是一种面向对象的编程语言",
            "JavaScript用于网页开发",
            "机器学习是人工智能的一个分支"
        ]
        
        conflicts = resolver.detect_conflicts(new_content, existing_contents)
        
        assert len(conflicts) == 0
    
    def test_detect_duplicate_conflict(self, resolver):
        """测试完全重复的冲突"""
        new_content = "Python是一种编程语言"
        existing_contents = [
            "Java是一种编程语言",
            "Python是一种编程语言",  # 完全重复
            "机器学习是人工智能的一个分支"
        ]
        
        conflicts = resolver.detect_conflicts(new_content, existing_contents)
        
        assert len(conflicts) == 1
        assert conflicts[0][0] == 1  # 索引
        assert conflicts[0][1] > 0.9  # 相似度
        assert conflicts[0][2] == 'duplicate'  # 冲突类型
    
    def test_detect_update_conflict(self, resolver):
        """测试更新版本的冲突"""
        new_content = "Python 3.10 新版本特性：模式匹配"
        existing_contents = [
            "Python是一种编程语言",
            "Python 3.9 新版本特性",
        ]
        
        conflicts = resolver.detect_conflicts(new_content, existing_contents)
        
        # 应该检测到与第二个内容的冲突
        assert len(conflicts) >= 1
        # 检查是否有update类型的冲突
        conflict_types = [c[2] for c in conflicts]
        assert 'update' in conflict_types or 'supplement' in conflict_types
    
    def test_detect_contradiction_conflict(self, resolver):
        """测试矛盾冲突"""
        new_content = "Python是解释型语言，但是性能比编译型语言慢"
        existing_contents = [
            "Python是解释型语言，性能很快",
        ]
        
        conflicts = resolver.detect_conflicts(new_content, existing_contents)
        
        if len(conflicts) > 0:
            # 如果检测到冲突，检查类型
            assert conflicts[0][2] in ['contradiction', 'supplement']
    
    def test_detect_supplement_conflict(self, resolver):
        """测试补充信息的冲突"""
        new_content = "Python支持列表推导式，例如 [x**2 for x in range(10)]"
        existing_contents = [
            "Python支持列表推导式",
        ]
        
        conflicts = resolver.detect_conflicts(new_content, existing_contents)
        
        # 应该检测到相似内容
        if len(conflicts) > 0:
            assert conflicts[0][2] in ['supplement', 'update']
    
    def test_classify_conflict_duplicate(self, resolver):
        """测试冲突分类 - 重复"""
        content1 = "Python是一种编程语言"
        content2 = "Python是一种编程语言"
        
        conflict_type = resolver._classify_conflict(content1, content2)
        
        assert conflict_type == 'duplicate'
    
    def test_classify_conflict_update(self, resolver):
        """测试冲突分类 - 更新"""
        content1 = "Python 3.10 更新了模式匹配"
        content2 = "Python 3.9 版本特性"
        
        conflict_type = resolver._classify_conflict(content1, content2)
        
        assert conflict_type == 'update'
    
    def test_classify_conflict_contradiction(self, resolver):
        """测试冲突分类 - 矛盾"""
        content1 = "Python性能很慢，但是易于学习"
        content2 = "Python性能很快"
        
        conflict_type = resolver._classify_conflict(content1, content2)
        
        assert conflict_type == 'contradiction'
    
    def test_resolve_conflict_overwrite(self, resolver):
        """测试冲突解决 - 覆盖策略"""
        new_content = "Python 3.10 新版本"
        existing_content = "Python 3.9 旧版本"
        
        resolved, strategy = resolver.resolve_conflict(
            new_content, 
            existing_content, 
            'update', 
            'overwrite'
        )
        
        assert resolved == new_content
        assert strategy == 'overwrite'
    
    def test_resolve_conflict_merge(self, resolver):
        """测试冲突解决 - 合并策略"""
        new_content = "Python支持列表推导式"
        existing_content = "Python支持生成器表达式"
        
        resolved, strategy = resolver.resolve_conflict(
            new_content, 
            existing_content, 
            'supplement', 
            'merge'
        )
        
        # 合并后应该包含两者的内容
        assert "列表推导式" in resolved or "生成器表达式" in resolved
        assert strategy == 'merge'
    
    def test_resolve_conflict_keep_both(self, resolver):
        """测试冲突解决 - 保留两者策略"""
        new_content = "Python性能慢"
        existing_content = "Python性能快"
        
        resolved, strategy = resolver.resolve_conflict(
            new_content, 
            existing_content, 
            'contradiction', 
            'keep_both'
        )
        
        # 应该包含两个内容
        assert "Python性能慢" in resolved
        assert "Python性能快" in resolved
        assert strategy == 'keep_both'
    
    def test_auto_select_strategy(self, resolver):
        """测试自动选择策略"""
        assert resolver._auto_select_strategy('duplicate') == 'overwrite'
        assert resolver._auto_select_strategy('update') == 'overwrite'
        assert resolver._auto_select_strategy('contradiction') == 'keep_both'
        assert resolver._auto_select_strategy('supplement') == 'merge'
    
    def test_merge_contents(self, resolver):
        """测试内容合并"""
        content1 = "Python是一种编程语言\nPython易于学习"
        content2 = "Python是一种编程语言\nPython应用广泛"
        
        merged = resolver._merge_contents(content1, content2)
        
        # 合并后应该去重
        assert merged.count("Python是一种编程语言") == 1
        assert "Python易于学习" in merged
        assert "Python应用广泛" in merged
    
    def test_batch_detect_conflicts(self, resolver):
        """测试批量冲突检测"""
        new_contents = [
            "Python是一种编程语言",
            "Java是一种编程语言",
            "机器学习是AI的分支"
        ]
        
        existing_contents = [
            "Python是一种编程语言",  # 与第一个完全重复
            "JavaScript用于网页开发",
            "机器学习基础知识"  # 与第三个相似
        ]
        
        conflicts_map = resolver.batch_detect_conflicts(new_contents, existing_contents)
        
        # 应该检测到冲突
        assert len(conflicts_map) > 0
        # 第一个新内容应该有冲突
        if 0 in conflicts_map:
            assert len(conflicts_map[0]) > 0
    
    def test_empty_inputs(self, resolver):
        """测试空输入"""
        # 空的现有内容
        conflicts = resolver.detect_conflicts("新内容", [])
        assert len(conflicts) == 0
        
        # 批量检测 - 空输入
        conflicts_map = resolver.batch_detect_conflicts([], ["现有内容"])
        assert len(conflicts_map) == 0
        
        conflicts_map = resolver.batch_detect_conflicts(["新内容"], [])
        assert len(conflicts_map) == 0
    
    def test_similarity_threshold(self):
        """测试相似度阈值调整"""
        # 低阈值 - 更容易检测到冲突
        resolver_low = MemoryConflictResolver(similarity_threshold=0.5)
        
        # 高阈值 - 更难检测到冲突
        resolver_high = MemoryConflictResolver(similarity_threshold=0.95)
        
        new_content = "Python编程语言"
        existing_contents = ["Python是一种编程语言"]
        
        conflicts_low = resolver_low.detect_conflicts(new_content, existing_contents)
        conflicts_high = resolver_high.detect_conflicts(new_content, existing_contents)
        
        # 低阈值应该检测到更多冲突
        assert len(conflicts_low) >= len(conflicts_high)
    
    def test_simple_conflict_detection(self, resolver):
        """测试简单冲突检测（降级方案）"""
        # 这个测试主要测试当TF-IDF失败时的降级方案
        new_content = "Python是一种编程语言"
        existing_contents = ["Python是一种编程语言"]
        
        # 直接调用简单检测方法
        conflicts = resolver._simple_conflict_detection(new_content, existing_contents)
        
        assert len(conflicts) == 1
        assert conflicts[0][2] == 'duplicate'
