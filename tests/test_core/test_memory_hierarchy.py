# tests/test_core/test_memory_hierarchy.py
"""长短期记忆管理器单元测试"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from core.memory_hierarchy import MemoryHierarchy


class TestMemoryHierarchy:
    """测试记忆层次管理器"""
    
    @pytest.fixture
    def temp_base_dir(self, tmp_path):
        """创建临时基础目录"""
        return tmp_path / "test_memory"
    
    @pytest.fixture
    def memory_hierarchy(self, temp_base_dir):
        """创建记忆层次管理器实例"""
        return MemoryHierarchy(temp_base_dir)
    
    def test_initialization(self, memory_hierarchy, temp_base_dir):
        """测试初始化"""
        # 检查目录结构
        assert (temp_base_dir / "memory" / "short_term").exists()
        assert (temp_base_dir / "memory" / "long_term").exists()
        
        # 检查工作记忆和短期缓存
        assert memory_hierarchy.working_memory == {}
        assert memory_hierarchy.short_term_cache == {}
    
    def test_store_low_importance(self, memory_hierarchy):
        """测试存储低重要性记忆"""
        memory_id = memory_hierarchy.store(
            domain="python",
            content="Python是一种编程语言",
            importance=0.3
        )
        
        # 检查记忆ID格式
        assert memory_id.startswith("python_")
        
        # 检查工作记忆
        assert "python" in memory_hierarchy.working_memory
        assert len(memory_hierarchy.working_memory["python"]) == 1
        
        # 检查短期记忆
        assert "python" in memory_hierarchy.short_term_cache
        assert len(memory_hierarchy.short_term_cache["python"]) == 1
    
    def test_store_high_importance(self, memory_hierarchy):
        """测试存储高重要性记忆"""
        memory_id = memory_hierarchy.store(
            domain="python",
            content="Python核心概念",
            importance=0.8
        )
        
        # 检查工作记忆
        assert "python" in memory_hierarchy.working_memory
        
        # 检查长期记忆文件
        long_term_file = memory_hierarchy.long_term_dir / "python" / f"{memory_id}.json"
        assert long_term_file.exists()
        
        # 检查长期记忆索引
        index_file = memory_hierarchy.long_term_index
        assert index_file.exists()
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        assert "python" in index_data
        assert len(index_data["python"]) == 1
    
    def test_retrieve_from_working_memory(self, memory_hierarchy):
        """测试从工作记忆检索"""
        memory_hierarchy.store(
            domain="python",
            content="工作记忆测试",
            importance=0.5
        )
        
        memories = memory_hierarchy.retrieve(
            domain="python",
            include_working=True,
            include_short_term=False,
            include_long_term=False
        )
        
        assert len(memories) == 1
        assert memories[0]['content'] == "工作记忆测试"
    
    def test_retrieve_from_short_term(self, memory_hierarchy):
        """测试从短期记忆检索"""
        memory_hierarchy.store(
            domain="python",
            content="短期记忆测试",
            importance=0.5
        )
        
        memories = memory_hierarchy.retrieve(
            domain="python",
            include_working=False,
            include_short_term=True,
            include_long_term=False
        )
        
        assert len(memories) == 1
        assert memories[0]['content'] == "短期记忆测试"
    
    def test_retrieve_from_long_term(self, memory_hierarchy):
        """测试从长期记忆检索"""
        memory_hierarchy.store(
            domain="python",
            content="长期记忆测试",
            importance=0.9
        )
        
        memories = memory_hierarchy.retrieve(
            domain="python",
            include_working=False,
            include_short_term=False,
            include_long_term=True
        )
        
        assert len(memories) == 1
        assert memories[0]['content'] == "长期记忆测试"
    
    def test_retrieve_all_sources(self, memory_hierarchy):
        """测试从所有来源检索"""
        # 存储到不同层次
        memory_hierarchy.store(domain="python", content="工作记忆", importance=0.3)
        memory_hierarchy.store(domain="python", content="短期记忆", importance=0.5)
        memory_hierarchy.store(domain="python", content="长期记忆", importance=0.9)
        
        memories = memory_hierarchy.retrieve(domain="python", top_k=10)
        
        # 应该检索到3个记忆
        assert len(memories) == 3
        
        # 应该按重要性排序
        assert memories[0]['importance'] >= memories[1]['importance']
        assert memories[1]['importance'] >= memories[2]['importance']
    
    def test_update_importance(self, memory_hierarchy):
        """测试更新重要性"""
        memory_id = memory_hierarchy.store(
            domain="python",
            content="测试内容",
            importance=0.5
        )
        
        # 更新重要性
        memory_hierarchy.update_importance(memory_id, "python", delta=0.2)
        
        # 检查工作记忆中的重要性
        memories = memory_hierarchy.retrieve(
            domain="python",
            include_working=True,
            include_short_term=False,
            include_long_term=False
        )
        
        assert memories[0]['importance'] == 0.7
    
    def test_forget_memory(self, memory_hierarchy):
        """测试遗忘记忆"""
        memory_id = memory_hierarchy.store(
            domain="python",
            content="要遗忘的内容",
            importance=0.5
        )
        
        # 遗忘记忆
        result = memory_hierarchy.forget(memory_id, "python")
        assert result is True
        
        # 检查是否已删除
        memories = memory_hierarchy.retrieve(domain="python")
        assert len(memories) == 0
    
    def test_clear_working_memory(self, memory_hierarchy):
        """测试清空工作记忆"""
        memory_hierarchy.store(domain="python", content="内容1", importance=0.5)
        memory_hierarchy.store(domain="java", content="内容2", importance=0.5)
        
        # 清空特定领域
        memory_hierarchy.clear_working_memory("python")
        
        assert "python" not in memory_hierarchy.working_memory
        assert "java" in memory_hierarchy.working_memory
        
        # 清空所有
        memory_hierarchy.clear_working_memory()
        assert len(memory_hierarchy.working_memory) == 0
    
    def test_get_memory_stats(self, memory_hierarchy):
        """测试获取记忆统计"""
        memory_hierarchy.store(domain="python", content="内容1", importance=0.5)
        memory_hierarchy.store(domain="python", content="内容2", importance=0.8)
        memory_hierarchy.store(domain="python", content="内容3", importance=0.9)
        
        stats = memory_hierarchy.get_memory_stats("python")
        
        assert stats['working_memory_count'] == 3
        assert stats['short_term_count'] == 2  # 只有低重要性的进入短期记忆
        assert stats['long_term_count'] == 1   # 高重要性的进入长期记忆
    
    def test_memory_with_metadata(self, memory_hierarchy):
        """测试带元数据的记忆"""
        metadata = {
            'source': 'user_input',
            'tags': ['python', 'programming'],
            'author': 'test_user'
        }
        
        memory_id = memory_hierarchy.store(
            domain="python",
            content="带元数据的内容",
            importance=0.5,
            metadata=metadata
        )
        
        memories = memory_hierarchy.retrieve(domain="python")
        
        assert len(memories) == 1
        assert memories[0]['metadata'] == metadata
    
    def test_top_k_limit(self, memory_hierarchy):
        """测试top_k限制"""
        # 存储10个记忆
        for i in range(10):
            memory_hierarchy.store(
                domain="python",
                content=f"内容{i}",
                importance=i / 10.0
            )
        
        # 检索top 5
        memories = memory_hierarchy.retrieve(domain="python", top_k=5)
        
        assert len(memories) == 5
        
        # 应该是最重要的5个
        importances = [m['importance'] for m in memories]
        assert importances == sorted(importances, reverse=True)
    
    def test_multiple_domains(self, memory_hierarchy):
        """测试多个领域"""
        memory_hierarchy.store(domain="python", content="Python内容", importance=0.5)
        memory_hierarchy.store(domain="java", content="Java内容", importance=0.5)
        memory_hierarchy.store(domain="javascript", content="JavaScript内容", importance=0.5)
        
        # 检索不同领域
        python_memories = memory_hierarchy.retrieve(domain="python")
        java_memories = memory_hierarchy.retrieve(domain="java")
        js_memories = memory_hierarchy.retrieve(domain="javascript")
        
        assert len(python_memories) == 1
        assert len(java_memories) == 1
        assert len(js_memories) == 1
        
        assert python_memories[0]['content'] == "Python内容"
        assert java_memories[0]['content'] == "Java内容"
        assert js_memories[0]['content'] == "JavaScript内容"
    
    def test_importance_bounds(self, memory_hierarchy):
        """测试重要性边界"""
        # 测试最小值
        memory_hierarchy.update_importance("test_id", "python", delta=-10.0)
        
        # 测试最大值
        memory_hierarchy.store(
            domain="python",
            content="测试",
            importance=1.5  # 超过1.0
        )
        
        memories = memory_hierarchy.retrieve(domain="python")
        # 重要性应该在0-1之间
        for memory in memories:
            assert 0.0 <= memory['importance'] <= 1.0
    
    def test_persistence(self, temp_base_dir):
        """测试持久化"""
        # 创建并存储记忆
        hierarchy1 = MemoryHierarchy(temp_base_dir)
        memory_id = hierarchy1.store(
            domain="python",
            content="持久化测试",
            importance=0.8
        )
        
        # 创建新实例，应该加载之前的记忆
        hierarchy2 = MemoryHierarchy(temp_base_dir)
        
        # 检查长期记忆是否持久化
        memories = hierarchy2.retrieve(
            domain="python",
            include_working=False,
            include_short_term=False,
            include_long_term=True
        )
        
        assert len(memories) == 1
        assert memories[0]['content'] == "持久化测试"
