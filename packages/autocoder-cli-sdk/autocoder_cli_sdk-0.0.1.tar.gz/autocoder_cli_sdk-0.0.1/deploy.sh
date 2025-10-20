#!/bin/bash
# AutoCoder CLI Python SDK 发布脚本
# 
# 使用 twine 发布到 PyPI
#
# 使用方法:
#   ./deploy.sh        # 发布到 PyPI (正式版)
#   ./deploy.sh test   # 发布到 TestPyPI (测试版)

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在正确的目录
if [ ! -f "pyproject.toml" ]; then
    print_error "请在 cli-sdks/python 目录下运行此脚本"
    exit 1
fi

# 确定发布目标
TARGET=${1:-"pypi"}  # 默认发布到 PyPI

if [ "$TARGET" = "test" ]; then
    REPOSITORY="testpypi"
    REPOSITORY_URL="https://test.pypi.org/legacy/"
    print_info "目标: TestPyPI"
else
    REPOSITORY="pypi"
    REPOSITORY_URL="https://upload.pypi.org/legacy/"
    print_info "目标: PyPI"
fi

print_info "========================================="
print_info "  AutoCoder CLI Python SDK 发布流程"
print_info "========================================="

# 1. 检查必要的工具
print_info "1. 检查必要的工具..."

# 优先使用 uv
USE_UV=false
if command -v uv &> /dev/null; then
    print_info "   ✓ uv 已安装（推荐）"
    USE_UV=true
else
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 python3，请先安装 Python 3"
        exit 1
    fi
    print_info "   ✓ Python 3 已安装"
    print_warning "   建议安装 uv: pip install uv"
fi

# 检查并升级 twine 和 pkginfo（发布必需）
if ! command -v twine &> /dev/null; then
    print_warning "   twine 未安装，正在安装..."
    if [ "$USE_UV" = true ]; then
        uv pip install --upgrade twine pkginfo
    else
        pip3 install --user --upgrade twine pkginfo
    fi
else
    print_info "   ✓ twine 已安装"
    # 升级到最新版本以支持 Metadata-Version 2.4
    print_info "   升级 twine 和 pkginfo 到最新版本..."
    if [ "$USE_UV" = true ]; then
        uv pip install --upgrade twine pkginfo >/dev/null 2>&1
    else
        pip3 install --user --upgrade twine pkginfo >/dev/null 2>&1
    fi
fi
print_info "   ✓ twine 和 pkginfo 已就绪"

# 2. 清理旧的构建文件
print_info "2. 清理旧的构建文件..."
rm -rf dist/ build/ *.egg-info
print_info "   ✓ 清理完成"

# 3. 读取版本号
print_info "3. 读取版本号..."
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
print_info "   当前版本: ${VERSION}"

# 4. 运行测试
print_info "4. 运行代码检查..."
if command -v black &> /dev/null; then
    print_info "   运行 black 格式化检查..."
    black --check autocoder_cli_sdk/ || {
        print_warning "   代码格式不符合 black 规范"
        read -p "是否继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    }
fi

# 5. 构建发布包
print_info "5. 构建发布包..."
if [ "$USE_UV" = true ]; then
    uv build
else
    python3 -m build
fi
print_info "   ✓ 构建完成"

# 6. 检查构建的包
print_info "6. 检查构建的包..."
twine check dist/* > /tmp/twine_check_cli.log 2>&1
TWINE_EXIT_CODE=$?

# 检查输出内容
if grep -q "missing required fields" /tmp/twine_check_cli.log; then
    # 检查是否实际包含 Name 和 Version
    if python3 -m zipfile -e dist/autocoder_cli_sdk-*.whl /tmp/test_metadata_cli 2>/dev/null; then
        if grep -q "^Name: " /tmp/test_metadata_cli/autocoder_cli_sdk-*.dist-info/METADATA 2>/dev/null && \
           grep -q "^Version: " /tmp/test_metadata_cli/autocoder_cli_sdk-*.dist-info/METADATA 2>/dev/null; then
            print_warning "   ⚠️  twine 报告缺少字段，但实际包含 Name 和 Version"
            print_warning "   这是 Metadata-Version 2.4 格式的兼容性问题"
            print_info "   ✓ 包内容验证通过，可以安全上传"
        else
            print_error "包检查失败：真的缺少 Name 或 Version 字段"
            cat /tmp/twine_check_cli.log
            exit 1
        fi
    else
        print_warning "   ⚠️  无法验证元数据，但继续执行"
        print_info "   注意: 如果上传失败，请检查 pyproject.toml 配置"
    fi
elif [ $TWINE_EXIT_CODE -ne 0 ]; then
    print_error "包检查失败"
    cat /tmp/twine_check_cli.log
    exit 1
else
    print_info "   ✓ 包检查通过"
fi

# 清理临时文件
rm -rf /tmp/test_metadata_cli /tmp/twine_check_cli.log

# 7. 列出将要上传的文件
print_info "7. 将要上传的文件:"
ls -lh dist/

# 8. 确认发布
echo ""
print_warning "即将发布到 ${REPOSITORY}，版本: ${VERSION}"
if [ "$TARGET" != "test" ]; then
    print_warning "⚠️  这是正式发布！发布后无法撤回！"
fi
read -p "确认继续? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "已取消发布"
    exit 0
fi

# 9. 上传到 PyPI
print_info "9. 上传到 ${REPOSITORY}..."

if [ "$TARGET" = "test" ]; then
    twine upload --repository testpypi dist/*
else
    twine upload dist/*
fi

if [ $? -eq 0 ]; then
    print_info "========================================="
    print_info "✅ 发布成功！"
    print_info "========================================="
    echo ""
    print_info "版本: ${VERSION}"
    if [ "$TARGET" = "test" ]; then
        print_info "TestPyPI: https://test.pypi.org/project/autocoder-cli-sdk/${VERSION}/"
        echo ""
        print_info "测试安装:"
        echo "  pip install -i https://test.pypi.org/simple/ autocoder-cli-sdk==${VERSION}"
    else
        print_info "PyPI: https://pypi.org/project/autocoder-cli-sdk/${VERSION}/"
        echo ""
        print_info "安装命令:"
        echo "  pip install autocoder-cli-sdk==${VERSION}"
    fi
    echo ""
else
    print_error "发布失败，请检查错误信息"
    exit 1
fi

