import os

# 文件夹路径
folder_path = "Wordlist"
anki_output = []

# 读取每个文件内容并整理
for file_index, file_name in enumerate(sorted(os.listdir(folder_path))):
    if file_name.endswith(".md"):
        with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as file:
            lines = file.readlines()
            unit_index = 1  # 每个文件内的Unit编号
            words = []
            for line in lines:
                line = line.strip()
                if line.startswith("## Unit"):
                    if words:  # 如果有之前的 Unit 信息，保存
                        # 添加文件编号和Unit编号，避免重复
                        unit_name = f"Unit {file_index + 1}.{unit_index}"
                        anki_output.append(f"{unit_name}\t{', '.join(words)}")
                        unit_index += 1  # Unit编号递增
                    words = []  # 重置单词列表
                elif line and not line.startswith("-"):  # 非空行且非分隔符
                    words.append(line)
            # 保存最后一个 Unit
            if words:
                unit_name = f"Unit {file_index + 1}.{unit_index}"
                anki_output.append(f"{unit_name}\t{', '.join(words)}")

# 输出为 Anki 文件
output_file = "anki_wordlist.txt"
with open(output_file, "w", encoding="utf-8") as out_file:
    out_file.write("\n".join(anki_output))

print(f"生成的Anki文件已保存为：{output_file}")
