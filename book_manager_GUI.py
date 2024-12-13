# 導入模組
import tkinter as tk  # 引入 Tkinter 模組，建立 GUI
from tkinter import messagebox, ttk  # 引入 Tkinter 的子模組，顯示提示框和表格
from pymongo import MongoClient  # 引入 pymongo，與 MongoDB 交互

# 連接 MongoDB 雲端資料庫
client = MongoClient("mongodb+srv://cathy:G222442841@cluster0.3is10.mongodb.net")  # 連接到 MongoDB 雲端
db = client['book_manager']  # 指定使用資料庫'book_manager'
collection = db['books']  # 指定要操作的集合'books'

# 函式一：新增書籍功能
def add_book():
    """新增書籍"""
    title = title_entry.get()  # 從輸入框中取得書名
    author = author_entry.get()  # 從輸入框中取得作者
    tags = tags_entry.get().split(',') if tags_entry.get() else []  # 若標籤不為空，分割成清單
    status = status_entry.get() or '未讀'  # 若狀態未填，預設為 '未讀'
    rating = rating_entry.get() or '未評分'  # 若評分未填，預設為 '未評分'
    notes = notes_entry.get() or '無備註'  # 若筆記未填，預設為 '無備註'

    if not title or not author:  # 檢查書名與作者是否已填寫
        messagebox.showwarning("警告", "請填寫完整的書籍資訊！")  # 顯示警告框
        return

    book = {
        "title": title,
        "author": author,
        "tags": tags,
        "status": status,
        "rating": rating,
        "notes": notes
    }  # 構建書籍資料字典
    collection.insert_one(book)  # 將書籍資料插入 MongoDB 集合
    messagebox.showinfo("成功", f"書籍 '{title}' 已新增！")  # 顯示成功訊息
    clear_entries()  # 清空輸入框
    update_book_list()  # 更新書籍列表

# 函式二：刪除書籍功能
def delete_book():
    """刪除選定的書籍"""
    selected_item = tree.selection()  # 取得表格中被選中的項目

    if not selected_item:  # 如果未選擇任何項目
        messagebox.showwarning("警告", "請選擇要刪除的書籍！")  # 顯示警告框
        return

    item = tree.item(selected_item)  # 取得選定行的資料
    title = item["values"][1]  # 假設第二欄是書名

    result = collection.delete_one({"title": title})  # 從 MongoDB 集合中刪除該書籍

    if result.deleted_count > 0:  # 若刪除成功
        messagebox.showinfo("成功", f"書籍 '{title}' 已刪除！")  # 顯示成功訊息
        update_book_list()  # 更新書籍列表
    else:  # 若未找到書籍
        messagebox.showwarning("失敗", f"未找到書籍 '{title}'，無法刪除。")  # 顯示失敗訊息

# 函式三：清空輸入框
def clear_entries():
    """清空輸入框"""
    title_entry.delete(0, tk.END)  # 清空書名輸入框
    author_entry.delete(0, tk.END)  # 清空作者輸入框
    tags_entry.delete(0, tk.END)  # 清空標籤輸入框
    status_entry.delete(0, tk.END)  # 清空狀態輸入框
    rating_entry.delete(0, tk.END)  # 清空評分輸入框
    notes_entry.delete(0, tk.END)  # 清空筆記輸入框

# 函式四：更新書籍列表
def update_book_list(filters=None):
    """刷新書籍列表，根據條件篩選"""
    for item in tree.get_children():  # 清空表格內容
        tree.delete(item)
    query = filters if filters else {}  # 使用篩選條件，若無則取全部
    books = collection.find(query)  # 從 MongoDB 集合中查詢書籍

    for i, book in enumerate(books, start=1):  # 遍歷每本書
        tree.insert("", "end", values=(
            f"{i}",
            book.get('title', '未命名'),
            book.get('author', '未知'),
            ', '.join(book.get('tags', [])),
            book.get('status', '未知'),
            book.get('rating', '未知'),
            book.get('notes', '無備註')
        ))  # 將書籍資料插入表格

# 函式五：多條件查詢書籍
def query_books():
    """根據多條件篩選書籍"""
    filters = {}
    tags = tag_filter_entry.get().split(',') if tag_filter_entry.get() else None
    status = status_filter_entry.get()
    author = author_filter_entry.get()
    if tags:
        filters["tags"] = {"$all": tags}  # 必須包含所有標籤
    if status:
        filters["status"] = status  # 篩選狀態
    if author:
        filters["author"] = author  # 篩選作者

    update_book_list(filters)  # 更新書籍列表

# 函式六：重置篩選
def reset_filters():
    """重置篩選條件，顯示所有書籍"""
    update_book_list()

# GUI 介面設計
app = tk.Tk()  # 創建主視窗
app.title("個人書籍管理系統")  # 設定視窗標題

input_frame = tk.LabelFrame(app, text="新增/刪除書籍", padx=10, pady=10)  # 新增/刪除區域
input_frame.pack(padx=10, pady=5, fill="x")

# 輸入欄位與按鈕
fields = ["書名：", "作者：", "標籤 (以逗號分隔)：", "狀態：", "評分：", "筆記："]
entries = []

for i, field in enumerate(fields):  # 為每個欄位建立輸入框
    tk.Label(input_frame, text=field).grid(row=i, column=0, padx=10, pady=5)
    entry = tk.Entry(input_frame, width=50)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries.append(entry)

title_entry, author_entry, tags_entry, status_entry, rating_entry, notes_entry = entries  # 解包輸入框

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

#主程序運行
update_book_list() # 初始化書籍列表
app.mainloop()  # 運行應用
