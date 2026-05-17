#!/usr/bin/env python
"""预置学习数据一键导入脚本

将 data/seed/ 下的学习内容导入到 ~/.learningAgent/，包括：
- 学习计划 (plan.md)
- 知识文章 (knowledge/*.md)
- RAG 向量索引（可选）
- 长期记忆（可选）

使用方法：
    python seed_data.py            # 导入所有预置领域
    python seed_data.py --list     # 查看可用领域
    python seed_data.py 编程启蒙    # 只导入指定领域
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# 项目根目录和种子数据目录
PROJECT_ROOT = Path(__file__).parent
SEED_DIR = PROJECT_ROOT / "data" / "seed"


def get_available_domains():
    """获取所有可用的预置领域"""
    if not SEED_DIR.exists():
        return []
    return sorted([
        d.name for d in SEED_DIR.iterdir()
        if d.is_dir() and (d / "plan.md").exists()
    ])


def count_knowledge_files(domain_path):
    """统计知识文件数量"""
    knowledge_dir = domain_path / "knowledge"
    if not knowledge_dir.exists():
        return 0
    return len(list(knowledge_dir.glob("*.md")))


def import_domain(domain_name, force=False):
    """
    导入单个领域的学习数据

    Args:
        domain_name: 领域名称
        force: 是否覆盖已存在的领域

    Returns:
        (success, message)
    """
    seed_path = SEED_DIR / domain_name
    if not seed_path.exists():
        return False, f"❌ 种子数据不存在：{domain_name}"

    # 使用 FileManager 的目录结构
    from core.file_manager import FileManager
    fm = FileManager()

    target_path = fm.BASE_DIR / domain_name

    # 检查是否已存在
    if target_path.exists() and not force:
        existing_knowledge = list((target_path / "knowledge").glob("*.md")) if (target_path / "knowledge").exists() else []
        # 排除 summary 文件
        existing_knowledge = [f for f in existing_knowledge if f.name != "knowledge_summary.md"]
        if existing_knowledge:
            return False, f"⏭️  跳过「{domain_name}」（已有 {len(existing_knowledge)} 篇知识，用 --force 覆盖）"

    # 1. 创建领域目录结构
    fm.create_domain(domain_name)

    # 2. 复制学习计划
    plan_file = seed_path / "plan.md"
    if plan_file.exists():
        plan_content = plan_file.read_text(encoding="utf-8")
        fm.save_plan(domain_name, plan_content)

    # 3. 复制知识文件
    knowledge_src = seed_path / "knowledge"
    imported_count = 0
    if knowledge_src.exists():
        for md_file in sorted(knowledge_src.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            fm.save_knowledge(domain_name, md_file.name, content)
            imported_count += 1

    # 4. 尝试建立 RAG 索引
    rag_count = 0
    try:
        from core.rag.chunker import Chunker
        from core.rag.vector_store import VectorStore
        from core.rag.embedder import Embedder

        chunker = Chunker()
        embedder = Embedder()
        vector_store = VectorStore(embedder=embedder)

        for md_file in sorted(knowledge_src.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            chunks = chunker.chunk(
                content,
                metadata={
                    "domain": domain_name,
                    "source": md_file.name,
                    "category": "seed",
                },
            )
            count = vector_store.index_chunks(domain_name, chunks)
            rag_count += count
    except Exception:
        pass  # RAG 不可用时静默跳过

    # 5. 尝试写入长期记忆
    memory_count = 0
    try:
        from core.memory_store import MemoryStore
        from core.memory_schema import MemoryRecord
        from core.entity_extractor import extract_entities

        memory_store = MemoryStore()

        for md_file in sorted(knowledge_src.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            # 提取摘要（第一段非空非标题行）
            summary_lines = []
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith(">") and not line.startswith("---"):
                    summary_lines.append(line)
                    if len(summary_lines) >= 2:
                        break
            summary = " ".join(summary_lines)[:300]

            memory_store.add(MemoryRecord(
                content=summary,
                domain=domain_name,
                memory_type="fact",
                entities=extract_entities(content),
                importance=0.5,
                source=f"seed:{md_file.name}",
                metadata={"category": "seed", "filename": md_file.name},
            ))
            memory_count += 1
    except Exception:
        pass  # Memory 不可用时静默跳过

    # 构建结果信息
    parts = [f"✅ 「{domain_name}」导入完成"]
    parts.append(f"   📋 学习计划: 1 份")
    parts.append(f"   📝 知识文章: {imported_count} 篇")
    if rag_count > 0:
        parts.append(f"   🔍 RAG 索引: {rag_count} 个语义块")
    if memory_count > 0:
        parts.append(f"   🧠 长期记忆: {memory_count} 条")

    return True, "\n".join(parts)


def main():
    args = sys.argv[1:]

    # 显示帮助
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    # 列出可用领域
    if "--list" in args:
        domains = get_available_domains()
        if not domains:
            print("❌ 没有找到预置学习数据")
            return 1
        print("\n📚 可用的预置学习领域：\n")
        for d in domains:
            seed_path = SEED_DIR / d
            n = count_knowledge_files(seed_path)
            print(f"  • {d}（{n} 篇知识文章）")
        print(f"\n使用方法：python seed_data.py [领域名]")
        print(f"导入全部：python seed_data.py")
        return 0

    force = "--force" in args
    args = [a for a in args if not a.startswith("--")]

    # 确定要导入的领域
    all_domains = get_available_domains()
    if not all_domains:
        print("❌ data/seed/ 目录下没有找到学习数据")
        return 1

    if args:
        # 只导入指定领域
        target_domains = []
        for name in args:
            if name in all_domains:
                target_domains.append(name)
            else:
                print(f"⚠️  未知领域「{name}」，可用领域：{', '.join(all_domains)}")
        if not target_domains:
            return 1
    else:
        target_domains = all_domains

    # 开始导入
    print("\n" + "=" * 60)
    print("🌱 LearningAgent 预置学习数据导入")
    print("=" * 60)
    print(f"\n📦 待导入领域：{', '.join(target_domains)}\n")

    success_count = 0
    for domain in target_domains:
        ok, msg = import_domain(domain, force=force)
        print(msg)
        print()
        if ok:
            success_count += 1

    # 汇总
    print("=" * 60)
    print(f"📊 导入完成：{success_count}/{len(target_domains)} 个领域")
    if success_count > 0:
        print("\n💡 现在可以开始学习了：")
        print("   python main.py")
        print("   > /list          # 查看所有领域")
        print("   > /vibe 编程启蒙   # 开始互动学习")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
