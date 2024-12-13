import tkinter as tk
from tkinter import messagebox, ttk
from pymongo import MongoClient

# 連接 MongoDB 雲端資料庫
client = MongoClient("mongodb+srv://cathy:G222442841@cluster0.3is10.mongodb.net")
db = client['book_manager']  # 書籍管理資料庫
collection = db['books']     # 書籍集合

def add_book():
    """新增書籍"""
    title = title_entry.get()
    author = author_entry.get()
    tags = tags_entry.get().split(',') if tags_entry.get() else []  # Handle empty tags
    status = status_entry.get() or '未讀'  # Default status if not specified
    rating = rating_entry.get() or '未評分'  # Default rating if not specified
    notes = notes_entry.get() or '無備註'  # Default notes if not specified

    if not title or not author:
        messagebox.showwarning("警告", "請填寫完整的書籍資訊！")
        return

    book = {
        "title": title,
        "author": author,
        "tags": tags,
        "status": status,
        "rating": rating,
        "notes": notes
    }
    collection.insert_one(book)
    messagebox.showinfo("成功", f"書籍 '{title}' 已新增！")
    clear_entries()
    update_book_list()

def delete_book():
    """刪除選定的書籍"""
    selected_item = tree.selection()
    
    if not selected_item:
        messagebox.showwarning("警告", "請選擇要刪除的書籍！")
        return

    # 取得選定行的書名
    item = tree.item(selected_item)
    title = item["values"][1]  # 假設第二欄是書名

    # 刪除資料庫中的記錄
    result = collection.delete_one({"title": title})

    if result.deleted_count > 0:
        messagebox.showinfo("成功", f"書籍 '{title}' 已刪除！")
        update_book_list()
    else:
        messagebox.showwarning("失敗", f"未找到書籍 '{title}'，無法刪除。")


def clear_entries():
    """清空輸入框"""
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    tags_entry.delete(0, tk.END)
    status_entry.delete(0, tk.END)
    rating_entry.delete(0, tk.END)
    notes_entry.delete(0, tk.END)

def update_book_list(filters=None):
    """刷新書籍列表，根據條件篩選"""
    for item in tree.get_children():
        tree.delete(item)  # 清空表格
    query = filters if filters else {}
    books = collection.find(query)

    for i, book in enumerate(books, start=1):
        tree.insert("", "end", values=(
            f"{i}",
            book.get('title', '未命名'),
            book.get('author', '未知'),
            ', '.join(book.get('tags', [])),
            book.get('status', '未知'),
            book.get('rating', '未知'),
            book.get('notes', '無備註')
        ))

def query_books():
    """根據多條件篩選書籍"""
    filters = {}
    tags = tag_filter_entry.get().split(',') if tag_filter_entry.get() else None
    status = status_filter_entry.get()
    author = author_filter_entry.get()

    if tags:
        filters["tags"] = {"$all": tags}  # 必須包含所有標籤
    if status:
        filters["status"] = status
    if author:
        filters["author"] = author

    update_book_list(filters)

def reset_filters():
    """重置篩選條件，顯示所有書籍"""
    update_book_list()

# GUI 設計
app = tk.Tk()
app.title("個人書籍管理系統")

# 輸入區
input_frame = tk.LabelFrame(app, text="新增/刪除書籍", padx=10, pady=10)
input_frame.pack(padx=10, pady=5, fill="x")

fields = ["書名：", "作者：", "標籤 (以逗號分隔)：", "狀態：", "評分：", "筆記："]
entries = []

for i, field in enumerate(fields):
    tk.Label(input_frame, text=field).grid(row=i, column=0, padx=10, pady=5)
    entry = tk.Entry(input_frame, width=50)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries.append(entry)

title_entry, author_entry, tags_entry, status_entry, rating_entry, notes_entry = entries

# 按鈕
button_frame = tk.Frame(input_frame)
button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

add_button = tk.Button(button_frame, text="新增書籍", command=add_book)
add_button.pack(side="left", padx=5)

delete_button = tk.Button(button_frame, text="刪除書籍", command=delete_book)
delete_button.pack(side="right", padx=5)

# 書籍列表
list_frame = tk.LabelFrame(app, text="書籍列表", padx=10, pady=10)
list_frame.pack(padx=10, pady=5, fill="both", expand=True)

columns = ("id", "title", "author", "tags", "status", "rating", "notes")
tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
tree.pack(side="left", fill="both", expand=True)

# 設定表頭
for col in columns:
    tree.heading(col, text=col, anchor="center")
    tree.column(col, width=100, anchor="center")

# 滾動條
scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# 查詢區
query_frame = tk.LabelFrame(app, text="查詢功能", padx=10, pady=10)
query_frame.pack(padx=10, pady=5, fill="x")

# 查詢欄位
tk.Label(query_frame, text="狀態：").grid(row=0, column=0, padx=10, pady=5)
status_filter_entry = tk.Entry(query_frame, width=20)
status_filter_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(query_frame, text="標籤：").grid(row=1, column=0, padx=10, pady=5)
tag_filter_entry = tk.Entry(query_frame, width=20)
tag_filter_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(query_frame, text="作者：").grid(row=2, column=0, padx=10, pady=5)
author_filter_entry = tk.Entry(query_frame, width=20)
author_filter_entry.grid(row=2, column=1, padx=10, pady=5)

# 查詢按鈕
tk.Button(query_frame, text="查詢", command=query_books).grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(query_frame, text="重置篩選", command=reset_filters).grid(row=3, column=2, columnspan=2, pady=10)

# 初始化書籍列表
update_book_list()

# 運行應用
app.mainloop()
