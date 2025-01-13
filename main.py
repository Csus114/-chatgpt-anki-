import requests
import openai

# 设置 OpenAI API 密钥和自定义 API 地址
openai.api_key = " "  # 替换为你的 API Key
openai.base_url = "https://api.gpt.ge/v1/"
openai.default_headers = {"x-foo": "true"}

# 定义 AnkiConnect 的默认 URL
ANKI_CONNECT_URL = "http://localhost:8765"

# 从文件读取单词列表
def read_word_list(file_path):
    word_units = {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    unit, words = line.split("\t")
                    word_units[unit.strip()] = [word.strip() for word in words.split(",")]
        return word_units
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# 检查指定的单元是否已存在
def check_unit_exists(unit):
    # 确保标签格式正确，避免空格等干扰
    unit_tag = unit.strip()
    query = f'tag:"{unit_tag}"'  # 查询卡组是否包含指定标签（与Anki中的标签格式匹配）
    response = requests.post(ANKI_CONNECT_URL, json={
        "action": "findNotes",
        "version": 6,
        "params": {"query": query}
    })
    try:
        result = response.json()
        if result.get("error"):
            print(f"Error checking unit existence: {result['error']}")
            return False
        return len(result.get("result", [])) > 0
    except Exception as e:
        print(f"Error communicating with AnkiConnect: {e}")
        return False

# 调用 ChatGPT 生成英文段落和单词解释
def generate_content(words):
    prompt = (
        f"Using the following words, generate a meaningful paragraph in English: {', '.join(words)}.\n"
        "Then provide the explanation for each word in English. Format as follows:\n\n"
        "Paragraph: [Generated paragraph]\n\nExplanations:\n[word1]: [definition1]\n[word2]: [definition2]\n..."
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating content for words {words}: {e}")
        return None

# 将内容添加到 Anki 中
def add_to_anki(deck_name, unit, paragraph, explanations):
    # 格式化单词解释，每个单词解释占一行
    formatted_explanations = "\n".join(explanations.splitlines())

    # 设置卡片内容
    front = f"{unit}\n\n{paragraph}"  # 英文段落作为问题页面
    back = f"Word explanations:\n{formatted_explanations}"  # 单词解释逐行显示作为答案页面

    # 检查是否已存在
    if check_unit_exists(unit):
        print(f"Skipping {unit}: already exists in Anki.")
        return

    # 构建请求体
    note = {
        "note": {
            "deckName": deck_name,
            "modelName": "Basic",  # 使用Anki的Basic模板
            "fields": {
                "Front": front,
                "Back": back
            },
            "tags": [unit]  # 添加单元名称为标签
        }
    }

    # 调用 AnkiConnect 添加卡片
    response = requests.post(ANKI_CONNECT_URL, json={
        "action": "addNote",
        "version": 6,
        "params": note
    })
    try:
        result = response.json()
        if result.get("error"):
            print(f"Error adding note to Anki: {result['error']}")
        else:
            print(f"Note added to Anki for {unit}!")
    except Exception as e:
        print(f"Error communicating with AnkiConnect: {e}")

# 主函数
def main():
    # 输入文件路径
    file_path = "anki_wordlist.txt"  # 替换为你的文件路径
    deck_name = "GRE Vocabulary"  # 替换为你的Anki卡组名称

    # 读取单词列表
    word_units = read_word_list(file_path)
    if not word_units:
        print("Error: Failed to read word list. Check the file path and format.")
        return

    # 遍历每个单元
    for unit, words in word_units.items():
        print(f"Processing {unit}...")
        if check_unit_exists(unit):
            print(f"Skipping {unit}: already exists in Anki.")
            continue
        generated_content = generate_content(words)
        if generated_content:
            try:
                # 分离生成的段落和单词解释
                paragraph, explanations = generated_content.split("\n\nExplanations:\n")
                add_to_anki(deck_name, unit, paragraph, explanations)
            except ValueError:
                print(f"Failed to parse generated content: {generated_content}")
        else:
            print(f"Failed to generate content for {unit}")

if __name__ == "__main__":
    main()

