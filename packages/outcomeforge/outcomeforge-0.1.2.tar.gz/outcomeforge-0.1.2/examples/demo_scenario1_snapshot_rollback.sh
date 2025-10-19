#!/usr/bin/env bash
# 场景① 完整演示：本地快照与回滚
# 演示「成功 ↔ 失败 ↔ 修复成功」完整闭环

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ok() { echo -e "${GREEN}$*${NC}"; }
fail() { echo -e "${RED}$*${NC}"; }
warn() { echo -e "${YELLOW}$*${NC}"; }
info() { echo -e "${BLUE}$*${NC}"; }

echo "========================================"
echo "场景① 演示：本地快照与回滚"
echo "========================================"
echo ""

# 检查 API Key
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    warn "ANTHROPIC_API_KEY not set, using Mock mode"
    USE_REAL_LLM=false
else
    ok "ANTHROPIC_API_KEY is set"
    USE_REAL_LLM=true
fi

# Step 1: 创建初始快照
info "Step 1: Creating initial snapshot..."
python3 cli.py snapshot --patterns "**/*.py" --model "claude-3-haiku-20240307" > /tmp/snap1.log 2>&1

SNAPSHOT1=$(ls -t .ai-snapshots/snapshot-*.json 2>/dev/null | head -1)
if [ -n "$SNAPSHOT1" ]; then
    SNAPSHOT1_ID=$(basename "$SNAPSHOT1" | sed 's/snapshot-//; s/.json//')
    ok "Snapshot created: $SNAPSHOT1_ID"
else
    fail "Failed to create snapshot"
    exit 1
fi

# Step 2: 修改一些文件
info "Step 2: Modifying files..."

# 备份原始文件
cp cli.py cli.py.backup

# 修改 cli.py 添加注释
cat >> cli.py << 'EOF'

# This is a test modification for snapshot demo
# Should be removed by rollback
EOF

ok "Modified cli.py"

# Step 3: 创建第二个快照
info "Step 3: Creating second snapshot after modification..."
python3 cli.py snapshot --patterns "**/*.py" --model "claude-3-haiku-20240307" > /tmp/snap2.log 2>&1

SNAPSHOT2=$(ls -t .ai-snapshots/snapshot-*.json 2>/dev/null | head -1)
if [ -n "$SNAPSHOT2" ] && [ "$SNAPSHOT2" != "$SNAPSHOT1" ]; then
    SNAPSHOT2_ID=$(basename "$SNAPSHOT2" | sed 's/snapshot-//; s/.json//')
    ok "Second snapshot created: $SNAPSHOT2_ID"
else
    fail "Failed to create second snapshot"
    mv cli.py.backup cli.py
    exit 1
fi

# Step 4: 列出所有快照
info "Step 4: Listing all snapshots..."
python3 cli.py snapshot-list
echo ""

# Step 5: 计算修改后的文件哈希
info "Step 5: Computing file hash before rollback..."
HASH_BEFORE=$(sha256sum cli.py | awk '{print $1}')
echo "Hash before rollback: $HASH_BEFORE"
echo ""

# Step 6: 从第一个快照回滚
info "Step 6: Restoring from first snapshot..."
python3 cli.py snapshot-restore "$SNAPSHOT1_ID"
echo ""

# Step 7: 计算回滚后的文件哈希
info "Step 7: Computing file hash after rollback..."
HASH_AFTER=$(sha256sum cli.py | awk '{print $1}')
echo "Hash after rollback: $HASH_AFTER"
echo ""

# Step 8: 验证哈希（简化：比较快照1和当前文件的哈希）
info "Step 8: Verifying hash matches original snapshot..."

# 从快照1中获取 cli.py 的原始哈希
EXPECTED_HASH=$(python3 -c "
import json
with open('$SNAPSHOT1', 'r') as f:
    data = json.load(f)
# Find cli.py in files
for fpath, fdata in data['files'].items():
    if fpath.endswith('cli.py'):
        print(fdata['hash'])
        break
")

echo "Expected hash (from snapshot 1): $EXPECTED_HASH"
echo "Actual hash (after rollback):    $HASH_AFTER"

if [ "$HASH_AFTER" = "$EXPECTED_HASH" ]; then
    ok "Hash verification PASSED - Files restored exactly"
else
    fail "Hash verification FAILED - Files don't match"
    mv cli.py.backup cli.py 2>/dev/null || true
    exit 1
fi

# 清理
rm -f cli.py.backup

echo ""
echo "========================================"
echo "演示总结"
echo "========================================"
echo "Created 2 snapshots"
echo "Modified files and created snapshot"
echo "Restored from snapshot successfully"
echo "Hash verification passed (byte-for-byte match)"
echo ""
echo "场景① 验证完成：快照与回滚功能正常"
echo "========================================"
