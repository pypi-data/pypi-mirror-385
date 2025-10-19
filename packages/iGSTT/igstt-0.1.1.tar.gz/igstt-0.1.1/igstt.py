import argparse
import os
import re

from google import genai

# 常量定义
GEMINI_STT_MODEL = "gemini-2.5-flash"
DEFAULT_PROMPT = "Generate LRC, LRC content format: [minutes:seconds.milliseconds] English | Simplified Chinese"
DEFAULT_INPUT = "input.mp3"

def extract_lrc_content(text: str) -> str | None:
    """提取 Markdown 中 ```lrc``` 块内容"""
    match = re.search(r"```lrc\s*(.*?)\s*```", text, re.S)
    return match.group(1).strip() if match else text.strip()

def write_file(content: str, filename: str) -> None:
    """写入 LRC 文件"""
    lrc = extract_lrc_content(content or "")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(lrc)
    print(f"✅ 已写入到 {filename}")

def gemini_stt(prompt: str, input_file: str, output_file: str) -> None:
    """调用 Gemini 语音识别并生成 LRC"""
    client = genai.Client()
    file_info = client.files.upload(file=input_file)
    response = client.models.generate_content(
        model=GEMINI_STT_MODEL,
        contents=[prompt, file_info],
    )

    print("🤖 Gemini 返回：")
    print(response.text)
    print("####################")
    write_file(response.text, output_file)

def main():
    parser = argparse.ArgumentParser(description="🎧 Gemini 语音转文本（STT）工具")
    parser.add_argument("text", nargs="?", default=DEFAULT_PROMPT, help="提示信息")
    parser.add_argument("-i", "--input", default=DEFAULT_INPUT, help="音频文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径（默认与输入同名 .lrc）")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ 错误：找不到文件 '{args.input}'")
        return

    output_file = args.output or os.path.splitext(args.input)[0] + ".lrc"

    print(f"提示信息: {args.text}")
    print(f"音频文件: {args.input}")
    print(f"输出文件: {output_file}")

    gemini_stt(args.text, args.input, output_file)

if __name__ == "__main__":
    main()
