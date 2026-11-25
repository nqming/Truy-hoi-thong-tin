# Bài 1: Đọc hiểu rồi chạy thử chương trình xây dựng chỉ mục ngược và tìm kiếm với Whoosh
import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

# "stored=True" nghĩa là sẽ lưu trữ trường này trong chỉ mục;
# kiểu trường "ID" nghĩa là không đánh chỉ mục (không tách từ) trên trường này.
schema = Schema(
    title=TEXT(stored=True),
    path=ID(stored=True),
    content=TEXT
)

# Đảm bảo thư mục "indexdir" tồn tại trong thư mục hiện hành trước
# khi chạy câu lệnh bên dưới
index_dir = "indexdir"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

ix = create_in(index_dir, schema)
writer = ix.writer()
writer.add_document(
    title="First document",
    path="/a",
    content="This is the first document we've added!"
)
writer.add_document(
    title="Second document",
    path="/b",
    content="The second one is even more interesting!"
)
writer.commit()

with ix.searcher() as searcher:
    query = QueryParser("content", ix.schema).parse("first")
    results = searcher.search(query)
    print("Number of results:", len(results))
    print(results[0]["title"])
