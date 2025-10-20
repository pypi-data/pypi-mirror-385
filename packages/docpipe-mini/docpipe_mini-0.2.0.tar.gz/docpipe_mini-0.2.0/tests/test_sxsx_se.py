from docpipe.loaders._xlsx import XlsxSerializer

serializer = XlsxSerializer()

file_path = "tests\\excel\\销售统计表.xlsx"
print(f"Testing with: {file_path}")

print("\n1. Testing header_row=1 (should extract actual Chinese headers):")

for chunk in serializer.iterate_chunks(file_path, header_row=1):
    print(chunk)



   