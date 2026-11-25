# Bài 2: Sửa chương trình trong Bài 1 để chạy thử trên dữ liệu tiếng Việt với thư viện pyvi
import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from pyvi import ViTokenizer

# Tạo lược đồ Schema cho chỉ mục ngược
schema = Schema(
    title=TEXT(stored=True),
    path=ID(stored=True),
    content=TEXT(stored=True)
)

# Tạo thư mục chứa chỉ mục cho Bài 2
index_dir = "indexdir_bai2"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

ix = create_in(index_dir, schema)
writer = ix.writer()

# Dữ liệu tiếng Việt mẫu
docs = [
    {
        "title": "Giới thiệu Đại học Thủy Lợi",
        "path": "/tlu",
        "content": "Trường Đại học Thủy Lợi là trường đại học công lập đào tạo đa ngành tại Việt Nam."
    },
    {
        "title": "Khoa Công nghệ thông tin",
        "path": "/cntt",
        "content": "Khoa Công nghệ thông tin thuộc Đại học Thủy Lợi đào tạo ngành Kỹ thuật phần mềm và Hệ thống thông tin."
    },
    {
        "title": "Môn Truy hồi thông tin",
        "path": "/ir",
        "content": "Môn học Truy hồi thông tin và tìm kiếm web hướng dẫn xây dựng chỉ mục ngược với thư viện Whoosh."
    }
]

# Dùng pyvi (ViTokenizer.tokenize) để tách từ ghép tiếng Việt trước khi đưa vào Whoosh
for doc in docs:
    tokenized_content = ViTokenizer.tokenize(doc["content"])
    print(f"[Tách từ tài liệu '{doc['title']}']: {tokenized_content}")
    writer.add_document(
        title=doc["title"],
        path=doc["path"],
        content=tokenized_content
    )

writer.commit()
print("-" * 60)

# Tìm kiếm trên dữ liệu tiếng Việt
raw_query_str = "Đại học Thủy Lợi"
tokenized_query_str = ViTokenizer.tokenize(raw_query_str)
print(f"Câu truy vấn gốc      : {raw_query_str}")
print(f"Câu truy vấn tách từ  : {tokenized_query_str}")
print("-" * 60)

with ix.searcher() as searcher:
    query = QueryParser("content", ix.schema).parse(tokenized_query_str)
    results = searcher.search(query)
    print("Number of results:", len(results))
    for i, hit in enumerate(results, start=1):
        print(f"{i}. {hit['title']} (path: {hit['path']})")
