from docpipe import DocxSerializer

serializer = DocxSerializer()
serializer.configure_logging(enable_performance_logging=True, log_level="DEBUG")
file_path = "tests\\data\\word\\AI行业报告.docx"
print(f"Testing with: {file_path}")

print("\n1. Testing header_row=1 (should extract actual Chinese headers):")
chunk_count = 0
for chunk in serializer.iterate_chunks(file_path):
    print(chunk.type)