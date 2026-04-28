"""
Day 2 Project: 待办事项管理器
功能：添加、查看、完成、删除待办事项，数据保存到文件
作者：duquanyong
日期：2026-04-28
"""
import json
import os
from datetime import datetime


class TodoManager:
    """待办事项管理器"""
    
    def __init__(self, filename="todos.json"):
        self.filename = filename
        self.todos = []
        self.load_todos()  # 启动时加载已保存的数据
    
    def load_todos(self):
        """从文件加载待办事项"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.todos = json.load(f)
                print(f"✅ 已加载 {len(self.todos)} 个待办事项")
            except Exception as e:
                print(f"⚠️ 加载失败: {e}")
                self.todos = []
        else:
            print("📝 新的待办事项列表")
            self.todos = []
    
    def save_todos(self):
        """保存待办事项到文件"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存 {len(self.todos)} 个待办事项到文件")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def add_todo(self, title, priority="中"):
        """添加待办事项"""
        todo = {
            "id": len(self.todos) + 1,
            "title": title,
            "completed": False,
            "priority": priority,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.todos.append(todo)
        self.save_todos()
        print(f"✅ 已添加: {title} [优先级: {priority}]")
        return todo
    
    def view_todos(self, show_all=True):
        """查看所有待办事项"""
        if not self.todos:
            print("\n📭 暂无待办事项，添加一些吧！")
            return
        
        print("\n" + "=" * 50)
        print("📋 待办事项列表")
        print("=" * 50)
        
        if show_all:
            todos_to_show = self.todos
        else:
            # 只显示未完成的
            todos_to_show = [t for t in self.todos if not t['completed']]
        
        for todo in todos_to_show:
            status = "✅" if todo['completed'] else "⬜"
            priority_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(todo['priority'], "⚪")
            print(f"{status} {todo['id']}. {priority_icon} {todo['title']}")
            print(f"   创建时间: {todo['created_at']}")
        
        print("=" * 50)
        print(f"总计: {len(self.todos)} 个, "
              f"已完成: {sum(1 for t in self.todos if t['completed'])} 个, "
              f"待完成: {sum(1 for t in self.todos if not t['completed'])} 个")
    
    def complete_todo(self, todo_id):
        """标记待办事项为完成"""
        for todo in self.todos:
            if todo['id'] == todo_id:
                if todo['completed']:
                    print(f"⚠️ 该事项已完成: {todo['title']}")
                else:
                    todo['completed'] = True
                    todo['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.save_todos()
                    print(f"🎉 恭喜完成: {todo['title']}")
                return
        print(f"❌ 未找到ID为 {todo_id} 的待办事项")
    
    def delete_todo(self, todo_id):
        """删除待办事项"""
        for i, todo in enumerate(self.todos):
            if todo['id'] == todo_id:
                removed = self.todos.pop(i)
                self.save_todos()
                print(f"🗑️  已删除: {removed['title']}")
                return
        print(f"❌ 未找到ID为 {todo_id} 的待办事项")
    
    def get_statistics(self):
        """获取统计信息"""
        total = len(self.todos)
        completed = sum(1 for t in self.todos if t['completed'])
        pending = total - completed
        
        # 按优先级统计
        high_priority = sum(1 for t in self.todos if t['priority'] == '高' and not t['completed'])
        
        print("\n" + "=" * 50)
        print("📊 统计信息")
        print("=" * 50)
        print(f"总事项: {total}")
        print(f"已完成: {completed} ({completed/total*100 if total > 0 else 0:.1f}%)")
        print(f"待完成: {pending}")
        print(f"高优先级待办: {high_priority}")
        print("=" * 50)


def main():
    """主程序 - 交互式待办事项管理"""
    print("=" * 50)
    print("📝 待办事项管理器 - Day 2 学习成果")
    print("=" * 50)
    
    manager = TodoManager()
    
    while True:
        print("\n" + "-" * 50)
        print("🔧 操作菜单:")
        print("1. 查看所有待办事项")
        print("2. 查看未完成事项")
        print("3. 添加待办事项")
        print("4. 完成待办事项")
        print("5. 删除待办事项")
        print("6. 查看统计信息")
        print("7. 退出")
        print("-" * 50)
        
        choice = input("\n请选择操作 (1-7): ").strip()
        
        if choice == '1':
            manager.view_todos(show_all=True)
        
        elif choice == '2':
            manager.view_todos(show_all=False)
        
        elif choice == '3':
            title = input("请输入待办事项: ").strip()
            if title:
                priority = input("请选择优先级 (高/中/低，默认中): ").strip() or "中"
                manager.add_todo(title, priority)
            else:
                print("❌ 事项不能为空！")
        
        elif choice == '4':
            manager.view_todos(show_all=False)
            try:
                todo_id = int(input("请输入要完成的事项ID: "))
                manager.complete_todo(todo_id)
            except ValueError:
                print("❌ 请输入有效的数字！")
        
        elif choice == '5':
            manager.view_todos(show_all=True)
            try:
                todo_id = int(input("请输入要删除的事项ID: "))
                manager.delete_todo(todo_id)
            except ValueError:
                print("❌ 请输入有效的数字！")
        
        elif choice == '6':
            manager.get_statistics()
        
        elif choice == '7':
            print("\n👋 再见！明天继续学习！")
            break
        
        else:
            print("❌ 无效的选择，请重新输入！")


if __name__ == "__main__":
    main()

