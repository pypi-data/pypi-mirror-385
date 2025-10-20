#!/bin/bash
# Demo: Advanced RAG Testing on Large Real-World Repositories
# Tests complex queries on major open source projects

set -e

REPO_URL="https://github.com/mlflow/mlflow"
REPO_NAME="mlflow"
CLONE_DIR=".cloned_repos/${REPO_NAME}"
MODEL="claude-3-5-sonnet-20241022"  # Use more powerful model for complex analysis

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "Advanced RAG Testing on Large Repositories"
echo "=========================================="
echo ""
echo "Target Repository: ${REPO_URL}"
echo "Model: ${MODEL}"
echo ""

# Clone repository if not exists
if [ ! -d "${CLONE_DIR}" ]; then
    echo -e "${BLUE}Cloning repository (this may take a few minutes)...${NC}"
    git clone --depth=1 "${REPO_URL}" "${CLONE_DIR}"
    echo -e "${GREEN}Repository cloned successfully${NC}"
else
    echo -e "${YELLOW}Repository already cloned, using existing copy${NC}"
fi

cd "${CLONE_DIR}"
echo ""
echo "Repository Stats:"
echo "  - Python files: $(find . -name "*.py" | wc -l)"
echo "  - Total files: $(find . -type f | wc -l)"
echo "  - Size: $(du -sh . | cut -f1)"
echo ""

# Return to project root
cd - > /dev/null

echo "=========================================="
echo "Test 1: Security Vulnerability Analysis"
echo "=========================================="
echo ""
echo "Query: Identify potential security vulnerabilities"
echo ""

python cli.py rag \
    --patterns "${CLONE_DIR}/**/*.py" \
    --query "作为安全专家，分析这个代码库并识别潜在的安全漏洞。重点关注：
1. SQL注入风险（原始SQL查询、字符串拼接）
2. 路径遍历漏洞（文件路径操作）
3. 命令注入（subprocess、os.system调用）
4. 身份认证和授权问题
5. 敏感数据泄露（日志、错误消息）
6. 不安全的反序列化（pickle、yaml.load）
7. SSRF风险（URL请求）

对于每个发现的问题，提供：
- 文件路径和具体代码位置
- 漏洞描述和潜在影响
- 修复建议和安全最佳实践" \
    --format xml \
    --cxml \
    --model "${MODEL}" \
    > /tmp/rag_security_analysis.txt 2>&1

echo -e "${GREEN}Security analysis completed${NC}"
echo "Results saved to: /tmp/rag_security_analysis.txt"
echo ""

# Show summary
echo "Summary (first 50 lines):"
head -50 /tmp/rag_security_analysis.txt | tail -40
echo ""
echo "..."
echo ""

sleep 2

echo "=========================================="
echo "Test 2: Architecture Deep Dive"
echo "=========================================="
echo ""
echo "Query: Comprehensive architecture analysis"
echo ""

python cli.py rag \
    --patterns "${CLONE_DIR}/**/*.py" \
    --patterns "${CLONE_DIR}/README.md" \
    --patterns "${CLONE_DIR}/docs/**/*.md" \
    --query "作为架构师，对MLflow进行深度架构分析：

1. **核心架构模式**：
   - 识别主要的架构模式（MVC、微服务、事件驱动等）
   - 模块间的依赖关系和通信方式
   - 数据流和控制流

2. **关键组件分析**：
   - Tracking Server的架构设计
   - Model Registry的实现机制
   - Projects和Models的组织方式
   - 存储后端（FileStore、SQLAlchemy）的抽象层

3. **可扩展性设计**：
   - Plugin机制和扩展点
   - 自定义Backend的支持
   - REST API的设计

4. **数据持久化**：
   - 元数据存储方案
   - Artifact存储策略
   - 数据库schema设计

5. **潜在架构问题**：
   - 紧耦合的地方
   - 循环依赖
   - 单点故障风险

请提供详细的架构图描述和改进建议。" \
    --format markdown \
    --model "${MODEL}" \
    > /tmp/rag_architecture_analysis.txt 2>&1

echo -e "${GREEN}Architecture analysis completed${NC}"
echo "Results saved to: /tmp/rag_architecture_analysis.txt"
echo ""

# Show summary
echo "Summary (first 60 lines):"
head -60 /tmp/rag_architecture_analysis.txt | tail -50
echo ""
echo "..."
echo ""

sleep 2

echo "=========================================="
echo "Test 3: Migration Guide Generation"
echo "=========================================="
echo ""
echo "Query: Generate upgrade/migration guide"
echo ""

python cli.py rag \
    --patterns "${CLONE_DIR}/mlflow/**/*.py" \
    --patterns "${CLONE_DIR}/CHANGELOG.md" \
    --query "基于当前代码库，生成一份详细的迁移指南，用于帮助用户从旧版本升级：

1. **Breaking Changes检测**：
   - API签名变更
   - 已弃用的函数和类
   - 配置文件格式变更
   - 数据库schema变更

2. **迁移步骤**：
   - 数据备份建议
   - 升级顺序和依赖
   - 配置文件更新
   - 数据迁移脚本

3. **兼容性处理**：
   - 向后兼容的代码示例
   - 渐进式迁移策略
   - 回滚方案

4. **常见问题**：
   - 已知的迁移陷阱
   - 性能影响
   - 故障排查指南

格式：Markdown，包含代码示例和清晰的步骤说明。" \
    --format markdown \
    --line-numbers \
    --model "${MODEL}" \
    > /tmp/rag_migration_guide.txt 2>&1

echo -e "${GREEN}Migration guide completed${NC}"
echo "Results saved to: /tmp/rag_migration_guide.txt"
echo ""

sleep 2

echo "=========================================="
echo "Test 4: Performance Bottleneck Analysis"
echo "=========================================="
echo ""
echo "Query: Identify performance issues"
echo ""

python cli.py rag \
    --patterns "${CLONE_DIR}/mlflow/**/*.py" \
    --query "作为性能工程师，分析代码库中的性能瓶颈和优化机会：

1. **计算密集型代码**：
   - 循环中的重复计算
   - 低效的数据结构使用
   - 缺少缓存的地方
   - 可以并行化的串行操作

2. **I/O密集型操作**：
   - 频繁的文件系统访问
   - 数据库查询优化机会（N+1问题、缺少索引）
   - 网络请求优化
   - 大文件处理

3. **内存使用**：
   - 内存泄漏风险
   - 大对象加载
   - 不必要的数据复制
   - 生成器vs列表的使用

4. **优化建议**：
   - 具体的代码改进方案
   - 架构层面的优化
   - 配置调优建议
   - 估算的性能提升

请为每个问题提供具体的文件位置、代码片段和改进前后的对比。" \
    --format xml \
    --cxml \
    --line-numbers \
    --model "${MODEL}" \
    > /tmp/rag_performance_analysis.txt 2>&1

echo -e "${GREEN}Performance analysis completed${NC}"
echo "Results saved to: /tmp/rag_performance_analysis.txt"
echo ""

sleep 2

echo "=========================================="
echo "Test 5: API Usage Documentation"
echo "=========================================="
echo ""
echo "Query: Generate comprehensive API documentation"
echo ""

python cli.py rag \
    --patterns "${CLONE_DIR}/mlflow/tracking/**/*.py" \
    --patterns "${CLONE_DIR}/mlflow/models/**/*.py" \
    --query "基于源代码，生成MLflow核心API的使用文档：

1. **Tracking API**：
   - mlflow.start_run()的详细用法
   - 参数记录（log_param、log_metric）
   - Artifact管理
   - 嵌套runs和实验管理

2. **Models API**：
   - 模型保存和加载
   - 自定义模型包装
   - Model签名和输入示例
   - 模型部署workflow

3. **使用示例**：
   - 完整的端到端示例代码
   - 最佳实践和设计模式
   - 常见错误和解决方案
   - 性能优化技巧

4. **高级用法**：
   - 自定义Backend
   - Plugin开发
   - 分布式训练集成
   - CI/CD集成

格式：Markdown，包含可运行的代码示例、参数说明和返回值文档。" \
    --format markdown \
    --line-numbers \
    --model "${MODEL}" \
    > /tmp/rag_api_docs.txt 2>&1

echo -e "${GREEN}API documentation completed${NC}"
echo "Results saved to: /tmp/rag_api_docs.txt"
echo ""

sleep 2

echo "=========================================="
echo "Test 6: Code Quality Assessment"
echo "=========================================="
echo ""
echo "Query: Comprehensive code quality review"
echo ""

python cli.py rag \
    --patterns "${CLONE_DIR}/mlflow/**/*.py" \
    --query "作为代码审查专家，对代码质量进行全面评估：

1. **代码风格和一致性**：
   - PEP 8合规性
   - 命名规范
   - 文档字符串质量
   - 类型注解覆盖率

2. **设计原则**：
   - SOLID原则遵循情况
   - DRY违反（代码重复）
   - 职责单一性
   - 抽象层次

3. **错误处理**：
   - 异常处理的完整性
   - 错误消息的清晰度
   - 资源清理（上下文管理器）
   - 边界情况处理

4. **可测试性**：
   - 依赖注入
   - Mock友好的设计
   - 纯函数vs有副作用的函数
   - 测试覆盖率gaps

5. **技术债务**：
   - TODO/FIXME注释分析
   - 临时解决方案（hacks）
   - 过时的代码
   - 重构机会

请提供：
- 代码质量评分（1-10）
- Top 10改进优先级
- 具体的重构建议
- 长期维护建议" \
    --format markdown \
    --model "${MODEL}" \
    > /tmp/rag_quality_assessment.txt 2>&1

echo -e "${GREEN}Code quality assessment completed${NC}"
echo "Results saved to: /tmp/rag_quality_assessment.txt"
echo ""

echo "=========================================="
echo "Test 7: Dependency Analysis"
echo "=========================================="
echo ""
echo "Query: Analyze dependencies and suggest improvements"
echo ""

python cli.py rag \
    --patterns "${CLONE_DIR}/setup.py" \
    --patterns "${CLONE_DIR}/requirements*.txt" \
    --patterns "${CLONE_DIR}/mlflow/**/__init__.py" \
    --query "分析项目的依赖关系并提供优化建议：

1. **依赖清单**：
   - 直接依赖vs传递依赖
   - 版本约束分析
   - 可选依赖的使用

2. **风险评估**：
   - 已知漏洞的依赖（需要升级）
   - 维护状态不佳的库
   - 许可证兼容性问题
   - 依赖冲突

3. **优化建议**：
   - 可以移除的未使用依赖
   - 可以用标准库替代的依赖
   - 轻量级替代方案
   - 依赖版本更新建议

4. **内部依赖**：
   - 模块间的耦合度
   - 循环导入检测
   - 建议的模块重组

提供依赖关系图的文字描述和具体的改进action items。" \
    --format markdown \
    --model "${MODEL}" \
    > /tmp/rag_dependency_analysis.txt 2>&1

echo -e "${GREEN}Dependency analysis completed${NC}"
echo "Results saved to: /tmp/rag_dependency_analysis.txt"
echo ""

echo "=========================================="
echo "Summary of All Tests"
echo "=========================================="
echo ""
echo "All test results have been saved to /tmp/rag_*.txt files:"
echo ""
ls -lh /tmp/rag_*.txt 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
echo ""
echo -e "${GREEN}All advanced RAG tests completed successfully!${NC}"
echo ""
echo "To view detailed results:"
echo "  cat /tmp/rag_security_analysis.txt"
echo "  cat /tmp/rag_architecture_analysis.txt"
echo "  cat /tmp/rag_migration_guide.txt"
echo "  cat /tmp/rag_performance_analysis.txt"
echo "  cat /tmp/rag_api_docs.txt"
echo "  cat /tmp/rag_quality_assessment.txt"
echo "  cat /tmp/rag_dependency_analysis.txt"
echo ""
echo "=========================================="
