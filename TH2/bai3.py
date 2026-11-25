# Bài 3: Xây dựng chỉ mục ngược và tìm kiếm trên tập 10 tài liệu
import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, NUMERIC
from whoosh.qparser import QueryParser, OrGroup
from pyvi import ViTokenizer

# 1. Gõ trực tiếp một tập tài liệu D gồm 10 tài liệu vào trong code.
# Tạo hai danh sách: một danh sách lưu các tiêu đề và danh sách kia lưu các nội dung tương ứng.
titles = [
    "Giới thiệu về Trí tuệ nhân tạo",
    "Học máy và các ứng dụng thực tế",
    "Xử lý ngôn ngữ tự nhiên tiếng Việt",
    "Truy hồi thông tin và công cụ tìm kiếm web",
    "Cấu trúc dữ liệu chỉ mục ngược trong tìm kiếm",
    "Mạng nơ-ron nhân tạo và Học sâu",
    "Thị giác máy tính trong nhận diện hình ảnh",
    "Khai phá dữ liệu và Phân tích dữ liệu lớn",
    "Hệ thống gợi ý sản phẩm thương mại điện tử",
    "An toàn và bảo mật thông tin trên mạng"
]

contents = [
    "Trí tuệ nhân tạo là một lĩnh vực của khoa học máy tính tập trung vào việc tạo ra các cỗ máy thông minh có khả năng suy nghĩ và học hỏi như con người.",
    "Học máy là một nhánh của trí tuệ nhân tạo cho phép hệ thống tự động học và cải thiện từ kinh nghiệm mà không cần được lập trình tường minh.",
    "Xử lý ngôn ngữ tự nhiên giúp máy tính hiểu, phân tích và tạo ra ngôn ngữ của con người. Với tiếng Việt, bài toán tách từ ghép bằng thư viện pyvi rất quan trọng.",
    "Truy hồi thông tin nghiên cứu cách tìm kiếm tài liệu, thông tin bên trong các tài liệu và siêu dữ liệu từ cơ sở dữ liệu văn bản lớn hoặc trên môi trường web.",
    "Chỉ mục ngược là cấu trúc dữ liệu cốt lõi của các hệ thống tìm kiếm hiện đại, ánh xạ từ mỗi từ khóa sang danh sách các tài liệu chứa từ khóa đó.",
    "Học sâu sử dụng các mạng nơ-ron nhiều lớp để mô hình hóa các biểu diễn dữ liệu phức tạp, đạt hiệu quả cao trong nhận dạng giọng nói và dịch máy.",
    "Thị giác máy tính giúp máy tính có khả năng thu nhận, xử lý và hiểu hình ảnh kỹ thuật số hoặc video để phục vụ xe tự lái và nhận diện khuôn mặt.",
    "Khai phá dữ liệu là quá trình khám phá các mẫu thông tin hữu ích và tri thức tiềm ẩn trong các tập dữ liệu lớn phục vụ việc ra quyết định.",
    "Hệ thống gợi ý sử dụng thuật toán lọc cộng tác và lọc dựa trên nội dung để đề xuất các mặt hàng, bộ phim hoặc tin tức phù hợp với sở thích người dùng.",
    "An toàn thông tin bảo vệ dữ liệu và hệ thống mạng khỏi các cuộc tấn công mạng, truy cập trái phép, đánh cắp hoặc phá hủy dữ liệu quan trọng."
]


def build_index(index_dir="indexdir_bai3"):
    # 2. Xây dựng chỉ mục ngược trên tập tài liệu D:
    # - Lưu mã tài liệu (doc_id: chỉ số của phần tử tương ứng trong danh sách ở bước 1)
    # - Lưu phần tiêu đề (title: stored=True)
    # - KHÔNG lưu phần nội dung (content: stored=False vì kích thước lớn)
    schema = Schema(
        doc_id=NUMERIC(stored=True),
        title=TEXT(stored=True),
        content=TEXT(stored=False)
    )

    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    ix = create_in(index_dir, schema)
    writer = ix.writer()

    for idx in range(len(titles)):
        # Tách từ tiếng Việt trước khi đưa vào Whoosh
        tokenized_content = ViTokenizer.tokenize(contents[idx])
        writer.add_document(
            doc_id=idx,
            title=titles[idx],
            content=tokenized_content
        )

    writer.commit()
    return ix


def main():
    ix = build_index()

    # 3. Nhập vào (từ bàn phím) một câu truy vấn gồm nhiều từ.
    query_str = input("Nhập vào câu truy vấn gồm nhiều từ: ").strip()
    if not query_str:
        print("Câu truy vấn trống!")
        return

    # Tách từ tiếng Việt trên câu truy vấn trước khi đưa vào Whoosh
    tokenized_query = ViTokenizer.tokenize(query_str)

    # 4. Xử lý câu truy vấn và hiển thị kết quả theo quy cách:
    # Dòng đầu tiên là số kết quả, còn mỗi dòng tiếp theo gồm số thứ tự (bắt đầu từ 1)
    # và phần tiêu đề của mỗi kết quả.
    with ix.searcher() as searcher:
        parser = QueryParser("content", ix.schema, group=OrGroup)
        query = parser.parse(tokenized_query)
        results = searcher.search(query)

        num_results = len(results)
        print(num_results)

        if num_results == 0:
            print("Không tìm thấy tài liệu nào phù hợp.")
            return

        # Lưu lại danh sách kết quả để truy xuất ở bước 5 & 6
        saved_results = []
        for i, hit in enumerate(results, start=1):
            print(f"{i}. {hit['title']}")
            saved_results.append({
                "doc_id": hit["doc_id"],
                "title": hit["title"]
            })

        # 5. Nhập vào (từ bàn phím) số thứ tự của một kết quả.
        try:
            choice = int(input(f"\nNhập số thứ tự kết quả muốn xem nội dung (1 - {num_results}): ").strip())
            if 1 <= choice <= num_results:
                # 6. Hiển thị phần nội dung của kết quả đã chọn
                # (dùng mã tài liệu có lưu trong kết quả để truy nhập danh sách ở bước 1).
                selected_doc_id = saved_results[choice - 1]["doc_id"]
                print(contents[selected_doc_id])
            else:
                print("Số thứ tự không hợp lệ!")
        except ValueError:
            print("Vui lòng nhập một số nguyên hợp lệ!")


if __name__ == "__main__":
    main()
