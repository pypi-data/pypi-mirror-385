from docpipe.loaders._xlsx import XlsxSerializer
from pathlib import Path

serializer = XlsxSerializer()

# # 1. 默认（自动检测第1行）
# chunks = list(serializer.serialize("data.xlsx"))

# # 2. 指定行号作为header
# chunks = list(serializer.serialize("data.xlsx", header_row=3))

# # 3. 使用自定义headers
# chunks = list(serializer.serialize("data.xlsx", custom_headers=["ID", "Name", "Price"]))

# 4. RAG格式同样支持
rag_lines = list(serializer.serialize_as_rag_jsonl("tests/excel/销售统计表.xlsx", custom_headers=["ID", "Name", "Price"]))

for chunk in rag_lines:
    print(chunk)