#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 推送重试脚本
当网络恢复后自动推送未上传的提交
"""

import subprocess
import time
import sys

def retry_push(max_attempts=5, delay=5):
    """重试推送到 GitHub"""
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔄 推送尝试 {attempt}/{max_attempts}...")
        
        try:
            result = subprocess.run(
                ['git', 'push', 'origin', 'main', '-v'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ 推送成功！")
                print(result.stdout)
                return True
            else:
                print(f"❌ 推送失败 (尝试 {attempt}):")
                print(result.stderr)
                
                if attempt < max_attempts:
                    print(f"⏳ {delay} 秒后重试...\n")
                    time.sleep(delay)
                    delay *= 2  # 指数退避
        
        except subprocess.TimeoutExpired:
            print(f"⏱️  推送超时 (尝试 {attempt})")
            if attempt < max_attempts:
                print(f"⏳ {delay} 秒后重试...\n")
                time.sleep(delay)
        
        except Exception as e:
            print(f"💥 错误: {e}")
            if attempt < max_attempts:
                time.sleep(delay)
    
    print(f"\n❌ 尝试 {max_attempts} 次后仍未成功")
    print("💡 建议：")
    print("   1. 检查网络连接：ping github.com")
    print("   2. 检查 Git 配置：git remote -v")
    print("   3. 尝试 SSH 推送：git push -u origin main (需配置 SSH 密钥)")
    print("   4. 稍后重试：python retry_push.py")
    return False

if __name__ == "__main__":
    print("="*60)
    print("GitHub 推送重试工具")
    print("="*60)
    
    # 检查状态
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        print("⚠️  工作目录有未提交的更改，请先提交")
        sys.exit(1)
    
    result = subprocess.run(
        ['git', 'log', 'origin/main..HEAD', '--oneline'],
        capture_output=True,
        text=True
    )
    
    commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
    
    if not commits or not commits[0]:
        print("✅ 所有提交已上传到 GitHub")
        sys.exit(0)
    
    print(f"\n📊 本地有 {len(commits)} 个待推送的提交：\n")
    for commit in commits:
        print(f"   {commit}")
    
    print(f"\n开始推送...")
    success = retry_push(max_attempts=5, delay=3)
    
    sys.exit(0 if success else 1)
