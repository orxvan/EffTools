import subprocess
import json
import requests
import os
import typer
from dotenv import load_dotenv

app = typer.Typer()

load_dotenv()
gemini_key = os.getenv("GEMINI_KEY")
proxy_port = os.getenv("PROXY_PORT")
proxy_user = os.getenv("PROXY_USER")
proxy_pass = os.getenv("PROXY_PASS")
proxy_ip = os.getenv("PROXY_IP")

def get_git_diff():
    # 获取当前工作目录
    current_directory = os.getcwd()

    try:
        # 执行 git diff 命令并获取输出，cwd指定工作目录
        result = subprocess.run(
            ['git', 'diff', 'HEAD'], 
            capture_output=True, 
            text=True, 
            check=True, 
            cwd=current_directory  # 确保在当前目录下执行
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error while executing git diff: {e}")
        return None


# 渲染模板
def render_template(diff):
    template = '''
你的任务是产生一个遵循 Conventional Commits 规范的 git commit message，使用中文的流畅语言和 emoji。 Conventional Commits 规范是一种轻量级的 commit message 约定，用于创建明确的提交历史记录。

以下是要提交的变更的 git diff：

<diff>
{{diff}}
</diff>

仔细分析 diff 以理解所做的更改。请注意：
- 被修改、新增或删除的文件
- 更改的性质（例如：错误修复、新功能、重构等）
- 任何破坏性更改

根据你的分析，请按照以下步骤产生 commit message：

1. 确定适当的提交类型。常见类型包括：
- 🎉 init: 初始化
- 🚀 release: 发布新版本
- 🎨 style: 代码风格修改（不影响代码运行的变动）
- ✨ feat: 添加新功能
- 🐛 fix: 修复 bug
- 📝 docs: 对文档进行修改
- ♻️ refactor: 代码重构（既不是新增功能，也不是修改 bug 的代码变动）
- ⚡ perf: 提高性能的代码修改
- 🧑‍💻 dx: 优化开发体验
- 🔨 workflow: 工作流变动
- 🏷️ types: 类型声明修改
- 🚧 wip: 工作正在进行中
- ✅ test: 测试用例添加及修改
- 🔨 build: 影响构建系统或外部依赖关系的更改
- 👷 ci: 更改 CI 配置文件和脚本
- ❓ chore: 其它不涉及源码以及测试的修改
- ⬆️ deps: 依赖项修改
- 🔖 release: 发布新版本

2. 如果提交引入了破坏性更改，在类型/范围后面加上感叹号。

3. 在主题行中提供一个简短的、祈使语气的更改描述。

4. 如果需要，在提交正文中添加更详细的更改说明，解释更改的动机并与先前的行为进行对比。

5. 如果有破坏性更改，请在提交正文的末尾描述它们，以"破坏性更改："开头。

按以下格式输出你的回应：

<commit_message>
[emoji][类型][可选范围]: [描述]

[可选正文]

[可选页脚]
</commit_message>

确保 commit message 遵守以下规则：
- 主题行不应超过 50 个字符
- 正文应在 72 个字元处换行
- 在主题行中使用祈使句和现在式
- 主题行结尾不要加句号
- 用空白行将主题与正文分开
- 使用正文解释做了什么和为什么，而不是如何做

记住，一个好的 commit message 应该能够完成以下句子："如果应用，这个提交将 [你的主题行]"。

请确保使用中文的流畅语言编写 commit message，并在适当的地方加入 emoji 以增强可读性和表达力。
    '''
    # 使用 Python 的 string replace 方法来渲染模板
    return template.replace('{{diff}}', diff)

# 调用 API
def call_api_aisino(content):
    url = 'http://172.16.21.190:8060/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "Default",
        "strategy": "Bare",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "stream": "false",
        "trace_id": "123",
        "max_new_tokens": 2000,
        "super_search": True
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            # print("API Response:", response.json())
            # 提取并打印返回内容中的 'content' 部分
            content_response = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            print(content_response)
        else:
            print(f"Failed to call API. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error while calling the API: {e}")

def call_api_gemini(content):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": content
                    }
                ]
            }
        ]
    }
    
    # 使用你的 API 密钥
    api_key = gemini_key
    params = {"key": api_key}

    proxies = {
        'http': f'socks5://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}',
        'https': f'socks5://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}'
    }

    # print(proxies)
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, json=payload, params=params, proxies=proxies)
        if response.status_code == 200:
            # 打印响应内容
            content_response = response.json()
            # print("API Response Content:\n", content_response)
            res_txt = content_response['candidates'][0]['content']['parts'][0]['text']
            print(res_txt)
        else:
            print(f"Failed to call API. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error while calling the API: {e}")

# def call_api(content):
#     # call_api_gemini(content)
#     call_api_aisino(content)

@app.command('g', help='gen commit,type can be aisino or gemini')
def gencmt(type: str='aisino'):
    # 获取 git diff 输出
    diff = get_git_diff()
    
    if diff:
        # 渲染模板
        content = render_template(diff)
        # print("Rendered content:\n", content)
        
        # 调用 API
        if type == 'aisino' or type == 'a':
            call_api_aisino(content)
        elif type == 'gemini' or type == 'g':
            call_api_gemini(content)
        else:
            print(f"wrong type: {type},try aisino")
            call_api_aisino(content)

if __name__ == "__main__":
    # main()
    app()
