from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from pyvi import ViTokenizer
import os
import sys

# Đảm bảo hiển thị tiếng Việt UTF-8 trên terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Tập tài liệu
docs = {
    "D1":  "Con cáo nâu nhanh nhẹn nhảy qua con chó lười",
    "D2":  "Một con cáo màu nâu chạy băng qua cánh đồng",
    "D3":  "Chó là loài vật trung thành và là bạn tốt của con người",
    "D4":  "Mèo là loài độc lập nhưng cũng rất tình cảm",
    "D5":  "Python là ngôn ngữ lập trình phổ biến cho người mới bắt đầu",
    "D6":  "Học máy giúp máy tính học hỏi từ dữ liệu",
    "D7":  "Học sâu là nhánh của học máy sử dụng mạng nơ-ron",
    "D8":  "Khoa học dữ liệu kết hợp thống kê, lập trình và hiểu biết lĩnh vực",
    "D9":  "Trí tuệ nhân tạo đang thay đổi công nghệ hiện đại",
    "D10": "Con cáo chạy nhanh qua khu rừng rậm",
    "D11": "Con chó lười đang ngủ cạnh bờ sông",
    "D12": "Học tăng cường là một lĩnh vực của học máy",
    "D13": "Mạng nơ-ron là mô hình mạnh mẽ cho nhận dạng hình ảnh",
    "D14": "Xử lý ngôn ngữ tự nhiên giúp máy tính hiểu văn bản",
    "D15": "Công cụ tìm kiếm như Google sử dụng thuật toán xếp hạng",
    "D16": "Con mèo đuổi theo con chuột quanh ngôi nhà",
    "D17": "Thư viện Python như NumPy và Pandas rất cần thiết cho phân tích dữ liệu",
    "D18": "Thị giác máy tính nghiên cứu cách máy hiểu hình ảnh",
    "D19": "Chó và mèo có thể sống hòa thuận nếu được huấn luyện tốt",
    "D20": "Con cáo nâu và con chó lười là bạn trong câu chuyện",
}

# Tập câu truy vấn (gồm Q1-Q5 ban đầu và Q6-Q10 mới thêm ở Yêu cầu 2)
queries = {
    "Q1":  "con cáo nâu",
    "Q2":  "học máy",
    "Q3":  "lập trình python",
    "Q4":  "chó và mèo",
    "Q5":  "công cụ tìm kiếm",
    # Câu truy vấn mới (Yêu cầu 2)
    "Q6":  "dữ liệu",
    "Q7":  "mạng nơ-ron",
    "Q8":  "nhận dạng hình ảnh",
    "Q9":  "con chó lười",
    "Q10": "xử lý ngôn ngữ tự nhiên",
}

# Tập con tài liệu phù hợp cho mỗi câu truy vấn
# VD: Câu truy vấn Q1 có các tài liệu phù hợp là D1, D2, D10, D20
qrels = {
    "Q1":  ["D1", "D2", "D10", "D20"],
    "Q2":  ["D6", "D7", "D12", "D13"],
    "Q3":  ["D5", "D8", "D17"],
    "Q4":  ["D1", "D3", "D4", "D11", "D16", "D19", "D20"],
    "Q5":  ["D15"],
    # Tập tài liệu phù hợp cho các câu truy vấn mới (Yêu cầu 2)
    "Q6":  ["D6", "D8", "D17"],
    "Q7":  ["D7", "D13"],
    "Q8":  ["D13", "D18"],
    "Q9":  ["D1", "D11", "D20"],
    "Q10": ["D14"],
}

# Xây dựng chỉ mục (Yêu cầu 3: Tách từ ghép tiếng Việt bằng pyvi)
if not os.path.exists('indexdir'):
    os.mkdir("indexdir")

schema = Schema(id=ID(stored=True), content=TEXT(stored=True))
ix = create_in("indexdir", schema)
writer = ix.writer()

for doc_id, text in docs.items():
    # Chuyển về chữ thường và tách từ ghép tiếng Việt bằng pyvi trước khi đánh chỉ mục
    tokenized_text = ViTokenizer.tokenize(text.lower())
    writer.add_document(id=doc_id, content=tokenized_text)
writer.commit()

# Xử lý câu truy vấn (Yêu cầu 3: Tách từ ghép tiếng Việt trên câu truy vấn)
def run_query(ix, query_str, topk=10):
    results = []
    with ix.searcher() as searcher:
        qp = QueryParser("content", schema=ix.schema)
        tokenized_query = ViTokenizer.tokenize(query_str.lower())
        q = qp.parse(tokenized_query)
        hits = searcher.search(q, limit=topk)
        for hit in hits:
            results.append(hit['id'])
    return results

# Các độ đo đánh giá
def precision_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    rel = sum(1 for d in retrieved_k if d in relevant)
    return rel / k if k > 0 else 0.0

def recall(retrieved, relevant):
    rel = sum(1 for d in retrieved if d in relevant)
    return rel / len(relevant) if relevant else 0.0

def f1_score(p, r):
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

def r_precision(retrieved, relevant):
    R = len(relevant)
    retrieved_R = retrieved[:R]
    rel = sum(1 for d in retrieved_R if d in relevant)
    return rel / R if R > 0 else 0.0

# Đánh giá từng câu truy vấn và tính trung bình (Yêu cầu 4)
total_p5 = 0.0
total_r = 0.0
total_f1 = 0.0
total_rprec = 0.0
num_queries = len(queries)

for qid, query in queries.items():
    retrieved = run_query(ix, query, topk=10)
    relevant = qrels[qid]

    p5 = precision_at_k(retrieved, relevant, 5)
    r = recall(retrieved, relevant)
    f1 = f1_score(p5, r)
    rprec = r_precision(retrieved, relevant)

    total_p5 += p5
    total_r += r
    total_f1 += f1
    total_rprec += rprec

    tokenized_query = ViTokenizer.tokenize(query.lower())
    print(f"Câu truy vấn ({qid}): {query} [Tách từ: {tokenized_query}]")
    print(f"    Kết quả tìm kiếm: {retrieved}")
    print(f"    Kết quả đúng:     {relevant}")
    print(f"    Precision@5 = {p5:.3f} | Recall = {r:.3f} | F1 = {f1:.3f} | R-Precision = {rprec:.3f}")

# Tính giá trị trung bình của các độ đo đánh giá trên tất cả các câu truy vấn (Yêu cầu 4)
avg_p5 = total_p5 / num_queries if num_queries > 0 else 0.0
avg_r = total_r / num_queries if num_queries > 0 else 0.0
avg_f1 = total_f1 / num_queries if num_queries > 0 else 0.0
avg_rprec = total_rprec / num_queries if num_queries > 0 else 0.0

print("-" * 75)
print(f"Giá trị trung bình trên tất cả {num_queries} câu truy vấn:")
print(f"    Mean Precision@5 = {avg_p5:.3f} | Mean Recall = {avg_r:.3f} | Mean F1 = {avg_f1:.3f} | Mean R-Precision = {avg_rprec:.3f}")
