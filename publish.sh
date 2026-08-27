#!/bin/bash
# najieip.com 一键发布脚本
# 用法：
#   bash publish.sh                # 默认提交信息
#   bash publish.sh "发布XXX文章"   # 自定义提交信息
set -e
cd "$(dirname "$0")"

echo "==> 1/3 更新 sitemap"
python update-sitemap.py

echo "==> 2/3 推送百度（增量，配额用完会自动跳过）"
python push-baidu.py || true   # 推送失败不阻断部署

echo "==> 3/3 提交并部署到 GitHub Pages"
git add -A
MSG="${1:-发布：更新 sitemap + 新文章}"
git commit -m "$MSG" || { echo "没有需要提交的改动，跳过"; exit 0; }
git push origin main

echo ""
echo "✅ 完成：sitemap 已更新、百度已推送、站点已部署。"
