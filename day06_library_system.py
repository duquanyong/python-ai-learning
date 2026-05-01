"""
Day 6 Project: 简易图书管理系统
功能：图书的增删改查、借阅归还、用户管理
作者：duquanyong
日期：2026-05-02
"""
import json
import os
from datetime import datetime, timedelta


class Person:
    """人员基类"""

    def __init__(self, name, id_card):
        self.name = name
        self.id_card = id_card

    def __str__(self):
        return f"{self.name}({self.id_card})"

    def to_dict(self):
        return {
            "name": self.name,
            "id_card": self.id_card,
            "type": self.__class__.__name__
        }

    @classmethod
    def from_dict(cls, data):
        if data.get("type") == "Reader":
            return Reader(data["name"], data["id_card"])
        elif data.get("type") == "Librarian":
            return Librarian(data["name"], data["id_card"], data.get("employee_id", ""))
        return cls(data["name"], data["id_card"])


class Reader(Person):
    """读者类"""

    def __init__(self, name, id_card):
        super().__init__(name, id_card)
        self.borrowed_books = []  # 已借图书列表
        self.max_books = 5        # 最大借阅数量

    def can_borrow(self):
        """检查是否还能借书"""
        return len(self.borrowed_books) < self.max_books

    def borrow_book(self, book_id):
        """借阅图书"""
        if self.can_borrow():
            self.borrowed_books.append(book_id)
            return True
        return False

    def return_book(self, book_id):
        """归还图书"""
        if book_id in self.borrowed_books:
            self.borrowed_books.remove(book_id)
            return True
        return False

    def to_dict(self):
        data = super().to_dict()
        data["borrowed_books"] = self.borrowed_books
        data["max_books"] = self.max_books
        return data


class Librarian(Person):
    """图书管理员类"""

    def __init__(self, name, id_card, employee_id):
        super().__init__(name, id_card)
        self.employee_id = employee_id

    def to_dict(self):
        data = super().to_dict()
        data["employee_id"] = self.employee_id
        return data


class Book:
    """图书类"""

    def __init__(self, book_id, title, author, category, total_copies=1):
        self.book_id = book_id          # 图书编号
        self.title = title              # 书名
        self.author = author            # 作者
        self.category = category        # 分类
        self.total_copies = total_copies  # 总册数
        self.available = total_copies   # 可借册数
        self.borrow_records = []        # 借阅记录

    def is_available(self):
        """是否有可借副本"""
        return self.available > 0

    def borrow(self, reader_id):
        """借出一本"""
        if self.is_available():
            self.available -= 1
            record = {
                "reader_id": reader_id,
                "borrow_date": datetime.now().strftime("%Y-%m-%d"),
                "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "return_date": None
            }
            self.borrow_records.append(record)
            return True
        return False

    def return_book(self, reader_id):
        """归还一本"""
        for record in self.borrow_records:
            if record["reader_id"] == reader_id and record["return_date"] is None:
                record["return_date"] = datetime.now().strftime("%Y-%m-%d")
                self.available += 1
                return True
        return False

    def __str__(self):
        status = "可借" if self.is_available() else "已借完"
        return f"[{self.book_id}] {self.title} - {self.author} ({status}: {self.available}/{self.total_copies})"

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "total_copies": self.total_copies,
            "available": self.available,
            "borrow_records": self.borrow_records
        }

    @classmethod
    def from_dict(cls, data):
        book = cls(
            data["book_id"],
            data["title"],
            data["author"],
            data["category"],
            data.get("total_copies", 1)
        )
        book.available = data.get("available", book.total_copies)
        book.borrow_records = data.get("borrow_records", [])
        return book


class Library:
    """图书馆类 - 管理图书和读者"""

    def __init__(self, name="中央图书馆"):
        self.name = name
        self.books = {}      # book_id -> Book
        self.readers = {}    # id_card -> Reader
        self.librarians = {} # id_card -> Librarian
        self.data_file = "library_data.json"
        self.load_data()

    def load_data(self):
        """从文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 加载图书
                for book_data in data.get("books", []):
                    book = Book.from_dict(book_data)
                    self.books[book.book_id] = book

                # 加载读者
                for reader_data in data.get("readers", []):
                    reader = Reader.from_dict(reader_data)
                    self.readers[reader.id_card] = reader

                # 加载管理员
                for lib_data in data.get("librarians", []):
                    librarian = Librarian.from_dict(lib_data)
                    self.librarians[librarian.id_card] = librarian

                print(f"✅ 已加载 {len(self.books)} 本图书, {len(self.readers)} 位读者")
            except Exception as e:
                print(f"⚠️ 加载数据失败: {e}")

    def save_data(self):
        """保存数据到文件"""
        data = {
            "books": [book.to_dict() for book in self.books.values()],
            "readers": [reader.to_dict() for reader in self.readers.values()],
            "librarians": [lib.to_dict() for lib in self.librarians.values()]
        }
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ 数据已保存")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

    # 图书管理
    def add_book(self, book_id, title, author, category, copies=1):
        """添加图书"""
        if book_id in self.books:
            print(f"⚠️ 图书编号 {book_id} 已存在")
            return False

        book = Book(book_id, title, author, category, copies)
        self.books[book_id] = book
        self.save_data()
        print(f"✅ 添加图书: {title}")
        return True

    def remove_book(self, book_id):
        """删除图书"""
        if book_id not in self.books:
            print(f"❌ 图书 {book_id} 不存在")
            return False

        book = self.books[book_id]
        if book.available < book.total_copies:
            print(f"⚠️ 图书 {book.title} 还有未归还的副本，无法删除")
            return False

        del self.books[book_id]
        self.save_data()
        print(f"✅ 删除图书: {book.title}")
        return True

    def list_books(self, category=None):
        """列出图书"""
        books = self.books.values()
        if category:
            books = [b for b in books if b.category == category]

        if not books:
            print("📭 暂无图书")
            return

        print("\n" + "=" * 60)
        print("📚 图书列表")
        print("=" * 60)
        for book in sorted(books, key=lambda x: x.book_id):
            print(f"  {book}")
        print(f"\n总计: {len(books)} 本")

    def search_books(self, keyword):
        """搜索图书"""
        results = []
        for book in self.books.values():
            if (keyword.lower() in book.title.lower() or
                keyword.lower() in book.author.lower() or
                keyword.lower() in book.category.lower()):
                results.append(book)

        if not results:
            print(f"🔍 未找到包含 '{keyword}' 的图书")
            return

        print(f"\n🔍 搜索结果 ({len(results)} 本):")
        for book in results:
            print(f"  {book}")

    # 读者管理
    def add_reader(self, name, id_card):
        """添加读者"""
        if id_card in self.readers:
            print(f"⚠️ 读者 {id_card} 已存在")
            return False

        reader = Reader(name, id_card)
        self.readers[id_card] = reader
        self.save_data()
        print(f"✅ 添加读者: {name}")
        return True

    def list_readers(self):
        """列出读者"""
        if not self.readers:
            print("📭 暂无读者")
            return

        print("\n" + "=" * 60)
        print("👥 读者列表")
        print("=" * 60)
        for reader in self.readers.values():
            borrowed = len(reader.borrowed_books)
            print(f"  {reader.name}({reader.id_card}) - 已借 {borrowed} 本")
        print(f"\n总计: {len(self.readers)} 位")

    # 借阅管理
    def borrow_book(self, book_id, reader_id):
        """借阅图书"""
        if book_id not in self.books:
            print(f"❌ 图书 {book_id} 不存在")
            return False

        if reader_id not in self.readers:
            print(f"❌ 读者 {reader_id} 不存在")
            return False

        book = self.books[book_id]
        reader = self.readers[reader_id]

        if not reader.can_borrow():
            print(f"⚠️ {reader.name} 已达到最大借阅数量 ({reader.max_books} 本)")
            return False

        if not book.is_available():
            print(f"⚠️ 《{book.title}》已借完")
            return False

        if book.borrow(reader_id) and reader.borrow_book(book_id):
            self.save_data()
            print(f"✅ {reader.name} 成功借阅 《{book.title}》")
            print(f"   应还日期: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}")
            return True

        return False

    def return_book(self, book_id, reader_id):
        """归还图书"""
        if book_id not in self.books:
            print(f"❌ 图书 {book_id} 不存在")
            return False

        if reader_id not in self.readers:
            print(f"❌ 读者 {reader_id} 不存在")
            return False

        book = self.books[book_id]
        reader = self.readers[reader_id]

        if book.return_book(reader_id) and reader.return_book(book_id):
            self.save_data()
            print(f"✅ {reader.name} 成功归还 《{book.title}》")
            return True
        else:
            print(f"⚠️ 该读者没有借阅 《{book.title}》")
            return False

    def show_borrow_records(self, book_id=None):
        """显示借阅记录"""
        print("\n" + "=" * 60)
        print("📋 借阅记录")
        print("=" * 60)

        books_to_show = [self.books[book_id]] if book_id else self.books.values()

        for book in books_to_show:
            if book.borrow_records:
                print(f"\n《{book.title}》:")
                for record in book.borrow_records:
                    status = "已还" if record["return_date"] else "借阅中"
                    print(f"  读者: {record['reader_id']}")
                    print(f"  借阅: {record['borrow_date']}  应还: {record['due_date']}  状态: {status}")

    def show_statistics(self):
        """显示统计信息"""
        print("\n" + "=" * 60)
        print("📊 图书馆统计")
        print("=" * 60)

        total_books = len(self.books)
        total_copies = sum(b.total_copies for b in self.books.values())
        available_copies = sum(b.available for b in self.books.values())
        borrowed_copies = total_copies - available_copies

        print(f"图书种类: {total_books}")
        print(f"图书总册: {total_copies}")
        print(f"可借册数: {available_copies}")
        print(f"借出册数: {borrowed_copies}")
        print(f"注册读者: {len(self.readers)}")

        # 分类统计
        categories = {}
        for book in self.books.values():
            categories[book.category] = categories.get(book.category, 0) + 1

        if categories:
            print("\n分类统计:")
            for cat, count in sorted(categories.items()):
                print(f"  {cat}: {count} 种")


def init_sample_data(library):
    """初始化示例数据"""
    # 添加图书
    sample_books = [
        ("B001", "Python编程：从入门到实践", "Eric Matthes", "计算机", 3),
        ("B002", "流畅的Python", "Luciano Ramalho", "计算机", 2),
        ("B003", "深入理解计算机系统", "Randal E. Bryant", "计算机", 2),
        ("B004", "三体", "刘慈欣", "科幻小说", 5),
        ("B005", "流浪地球", "刘慈欣", "科幻小说", 3),
        ("B006", "活着", "余华", "文学", 4),
        ("B007", "百年孤独", "加西亚·马尔克斯", "文学", 2),
        ("B008", "人类简史", "尤瓦尔·赫拉利", "历史", 3),
    ]

    for book_data in sample_books:
        library.add_book(*book_data)

    # 添加读者
    library.add_reader("张三", "R001")
    library.add_reader("李四", "R002")
    library.add_reader("王五", "R003")

    print("\n✅ 示例数据初始化完成！")


def main():
    """主程序 - 图书管理系统"""
    print("=" * 60)
    print("📚 简易图书管理系统 - Day 6 学习成果")
    print("=" * 60)

    library = Library()

    # 如果没有数据，初始化示例
    if not library.books:
        print("\n📝 首次运行，创建示例数据...")
        init_sample_data(library)

    while True:
        print("\n" + "-" * 60)
        print("🔧 主菜单:")
        print("1. 图书管理")
        print("2. 读者管理")
        print("3. 借阅/归还")
        print("4. 查询统计")
        print("5. 退出")
        print("-" * 60)

        choice = input("\n请选择 (1-5): ").strip()

        if choice == '1':
            # 图书管理子菜单
            print("\n  1. 列出所有图书")
            print("  2. 添加图书")
            print("  3. 删除图书")
            print("  4. 搜索图书")
            sub = input("  请选择: ").strip()

            if sub == '1':
                library.list_books()
            elif sub == '2':
                book_id = input("  图书编号: ").strip()
                title = input("  书名: ").strip()
                author = input("  作者: ").strip()
                category = input("  分类: ").strip()
                copies = input("  册数(默认1): ").strip()
                copies = int(copies) if copies.isdigit() else 1
                library.add_book(book_id, title, author, category, copies)
            elif sub == '3':
                book_id = input("  图书编号: ").strip()
                library.remove_book(book_id)
            elif sub == '4':
                keyword = input("  搜索关键词: ").strip()
                library.search_books(keyword)

        elif choice == '2':
            # 读者管理子菜单
            print("\n  1. 列出所有读者")
            print("  2. 添加读者")
            sub = input("  请选择: ").strip()

            if sub == '1':
                library.list_readers()
            elif sub == '2':
                name = input("  姓名: ").strip()
                id_card = input("  身份证号: ").strip()
                library.add_reader(name, id_card)

        elif choice == '3':
            # 借阅/归还
            print("\n  1. 借阅图书")
            print("  2. 归还图书")
            sub = input("  请选择: ").strip()

            if sub == '1':
                book_id = input("  图书编号: ").strip()
                reader_id = input("  读者编号: ").strip()
                library.borrow_book(book_id, reader_id)
            elif sub == '2':
                book_id = input("  图书编号: ").strip()
                reader_id = input("  读者编号: ").strip()
                library.return_book(book_id, reader_id)

        elif choice == '4':
            # 查询统计
            print("\n  1. 借阅记录")
            print("  2. 统计信息")
            sub = input("  请选择: ").strip()

            if sub == '1':
                book_id = input("  图书编号(留空查看全部): ").strip()
                library.show_borrow_records(book_id if book_id else None)
            elif sub == '2':
                library.show_statistics()

        elif choice == '5':
            print("\n👋 感谢使用图书管理系统！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
