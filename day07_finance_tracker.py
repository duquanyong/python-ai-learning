"""
Day 7 Project: 个人财务管理工具
功能：记录收支、分类统计、预算管理、月度报表
作者：duquanyong
日期：2026-05-03
"""
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter


class Transaction:
    """交易记录类"""

    def __init__(self, amount, category, description, date=None, transaction_type="expense"):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.type = transaction_type  # "income" 或 "expense"

    def __str__(self):
        icon = "💰" if self.type == "income" else "💸"
        return f"{icon} [{self.date}] {self.category}: ¥{self.amount:,.2f} ({self.description})"

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data):
        t = cls(
            data["amount"],
            data["category"],
            data["description"],
            data["date"],
            data["type"]
        )
        t.id = data.get("id", t.id)
        return t


class Budget:
    """预算类"""

    def __init__(self, category, limit, period="monthly"):
        self.category = category
        self.limit = float(limit)
        self.period = period
        self.spent = 0.0

    def update_spent(self, amount):
        """更新已花费金额"""
        self.spent += float(amount)

    def get_remaining(self):
        """获取剩余预算"""
        return self.limit - self.spent

    def get_percentage(self):
        """获取使用百分比"""
        if self.limit <= 0:
            return 0
        return (self.spent / self.limit) * 100

    def is_exceeded(self):
        """是否超支"""
        return self.spent > self.limit

    def __str__(self):
        status = "⚠️ 超支" if self.is_exceeded() else "✅ 正常"
        bar = self._get_progress_bar()
        return f"{self.category}: ¥{self.spent:,.2f} / ¥{self.limit:,.2f} {bar} {status}"

    def _get_progress_bar(self):
        """生成进度条"""
        percentage = min(self.get_percentage(), 100)
        filled = int(percentage / 5)
        empty = 20 - filled
        return "█" * filled + "░" * empty + f" {percentage:.1f}%"

    def to_dict(self):
        return {
            "category": self.category,
            "limit": self.limit,
            "period": self.period,
            "spent": self.spent
        }

    @classmethod
    def from_dict(cls, data):
        budget = cls(data["category"], data["limit"], data.get("period", "monthly"))
        budget.spent = data.get("spent", 0)
        return budget


class FinanceTracker:
    """财务管理器"""

    # 预定义分类
    INCOME_CATEGORIES = ["工资", "奖金", "投资", "兼职", "其他收入"]
    EXPENSE_CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "住房", "医疗", "教育", "其他支出"]

    def __init__(self, data_file="finance_data.json"):
        self.data_file = data_file
        self.transactions = []
        self.budgets = {}
        self.load_data()

    def load_data(self):
        """加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 加载交易记录
                for t_data in data.get("transactions", []):
                    self.transactions.append(Transaction.from_dict(t_data))

                # 加载预算
                for cat, b_data in data.get("budgets", {}).items():
                    self.budgets[cat] = Budget.from_dict(b_data)

                print(f"✅ 已加载 {len(self.transactions)} 条交易记录, {len(self.budgets)} 个预算")
            except Exception as e:
                print(f"⚠️ 加载数据失败: {e}")

    def save_data(self):
        """保存数据"""
        data = {
            "transactions": [t.to_dict() for t in self.transactions],
            "budgets": {cat: b.to_dict() for cat, b in self.budgets.items()}
        }
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ 数据已保存")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

    # 交易管理
    def add_transaction(self, amount, category, description, date=None, transaction_type="expense"):
        """添加交易记录"""
        try:
            amount = float(amount)
            if amount <= 0:
                print("❌ 金额必须大于0")
                return False

            transaction = Transaction(amount, category, description, date, transaction_type)
            self.transactions.append(transaction)

            # 更新预算
            if transaction_type == "expense" and category in self.budgets:
                self.budgets[category].update_spent(amount)

            self.save_data()
            print(f"✅ 添加记录: {transaction}")
            return True

        except ValueError:
            print("❌ 金额格式错误")
            return False

    def delete_transaction(self, transaction_id):
        """删除交易记录"""
        for i, t in enumerate(self.transactions):
            if t.id == transaction_id:
                # 如果删除的是支出，恢复预算
                if t.type == "expense" and t.category in self.budgets:
                    self.budgets[t.category].spent -= t.amount

                del self.transactions[i]
                self.save_data()
                print(f"✅ 删除记录: {transaction_id}")
                return True

        print(f"❌ 未找到记录: {transaction_id}")
        return False

    def list_transactions(self, transaction_type=None, days=None):
        """列出交易记录"""
        transactions = self.transactions

        # 按类型筛选
        if transaction_type:
            transactions = [t for t in transactions if t.type == transaction_type]

        # 按时间筛选
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            transactions = [t for t in transactions if t.date >= cutoff]

        # 按日期排序（最新的在前）
        transactions = sorted(transactions, key=lambda x: x.date, reverse=True)

        if not transactions:
            print("📭 暂无交易记录")
            return

        print("\n" + "=" * 70)
        print("📋 交易记录")
        print("=" * 70)
        for i, t in enumerate(transactions, 1):
            print(f"{i}. {t}")
        print(f"\n总计: {len(transactions)} 条")

    # 统计报表
    def show_monthly_report(self, year=None, month=None):
        """显示月度报表"""
        year = year or datetime.now().year
        month = month or datetime.now().month

        # 筛选当月交易
        month_str = f"{year}-{month:02d}"
        month_transactions = [t for t in self.transactions if t.date.startswith(month_str)]

        if not month_transactions:
            print(f"📭 {year}年{month}月暂无交易记录")
            return

        # 计算收支
        income = sum(t.amount for t in month_transactions if t.type == "income")
        expense = sum(t.amount for t in month_transactions if t.type == "expense")
        balance = income - expense

        # 分类统计
        income_by_category = defaultdict(float)
        expense_by_category = defaultdict(float)

        for t in month_transactions:
            if t.type == "income":
                income_by_category[t.category] += t.amount
            else:
                expense_by_category[t.category] += t.amount

        # 显示报表
        print("\n" + "=" * 70)
        print(f"📊 {year}年{month}月 财务报表")
        print("=" * 70)

        print(f"\n💰 总收入: ¥{income:,.2f}")
        if income_by_category:
            print("  分类明细:")
            for cat, amount in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True):
                print(f"    {cat}: ¥{amount:,.2f}")

        print(f"\n💸 总支出: ¥{expense:,.2f}")
        if expense_by_category:
            print("  分类明细:")
            for cat, amount in sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / expense * 100) if expense > 0 else 0
                bar = "█" * int(percentage / 5)
                print(f"    {cat}: ¥{amount:,.2f} ({percentage:.1f}%) {bar}")

        print(f"\n📈 结余: ¥{balance:,.2f}")
        if balance >= 0:
            print("  ✅ 盈余")
        else:
            print("  ⚠️ 赤字")

    def show_yearly_report(self, year=None):
        """显示年度报表"""
        year = year or datetime.now().year

        # 筛选当年交易
        year_transactions = [t for t in self.transactions if t.date.startswith(str(year))]

        if not year_transactions:
            print(f"📭 {year}年暂无交易记录")
            return

        # 按月统计
        monthly_income = defaultdict(float)
        monthly_expense = defaultdict(float)

        for t in year_transactions:
            month = t.date[5:7]
            if t.type == "income":
                monthly_income[month] += t.amount
            else:
                monthly_expense[month] += t.amount

        # 显示报表
        print("\n" + "=" * 70)
        print(f"📊 {year}年 年度报表")
        print("=" * 70)

        all_months = sorted(set(list(monthly_income.keys()) + list(monthly_expense.keys())))

        print(f"\n{'月份':<8} {'收入':>12} {'支出':>12} {'结余':>12}")
        print("-" * 50)

        total_income = 0
        total_expense = 0

        for month in all_months:
            income = monthly_income.get(month, 0)
            expense = monthly_expense.get(month, 0)
            balance = income - expense
            total_income += income
            total_expense += expense

            print(f"{month}月    ¥{income:>10,.2f} ¥{expense:>10,.2f} ¥{balance:>10,.2f}")

        print("-" * 50)
        print(f"{'合计':<8} ¥{total_income:>10,.2f} ¥{total_expense:>10,.2f} ¥{total_income - total_expense:>10,.2f}")

    # 预算管理
    def set_budget(self, category, limit):
        """设置预算"""
        try:
            limit = float(limit)
            if limit <= 0:
                print("❌ 预算必须大于0")
                return False

            # 计算该分类已花费
            spent = sum(t.amount for t in self.transactions
                       if t.type == "expense" and t.category == category
                       and t.date.startswith(datetime.now().strftime("%Y-%m")))

            budget = Budget(category, limit)
            budget.spent = spent
            self.budgets[category] = budget
            self.save_data()

            print(f"✅ 设置预算: {category} ¥{limit:,.2f}")
            return True

        except ValueError:
            print("❌ 金额格式错误")
            return False

    def show_budgets(self):
        """显示预算状态"""
        if not self.budgets:
            print("📭 暂无预算设置")
            return

        print("\n" + "=" * 70)
        print("📊 预算执行情况")
        print("=" * 70)

        for budget in self.budgets.values():
            print(f"\n{budget}")

    # 资产概览
    def show_overview(self):
        """显示资产概览"""
        total_income = sum(t.amount for t in self.transactions if t.type == "income")
        total_expense = sum(t.amount for t in self.transactions if t.type == "expense")
        balance = total_income - total_expense

        # 本月数据
        this_month = datetime.now().strftime("%Y-%m")
        month_income = sum(t.amount for t in self.transactions
                          if t.type == "income" and t.date.startswith(this_month))
        month_expense = sum(t.amount for t in self.transactions
                           if t.type == "expense" and t.date.startswith(this_month))

        print("\n" + "=" * 70)
        print("💰 资产总览")
        print("=" * 70)
        print(f"\n累计收入: ¥{total_income:,.2f}")
        print(f"累计支出: ¥{total_expense:,.2f}")
        print(f"总资产:   ¥{balance:,.2f}")
        print(f"\n本月收入: ¥{month_income:,.2f}")
        print(f"本月支出: ¥{month_expense:,.2f}")
        print(f"本月结余: ¥{month_income - month_expense:,.2f}")

        # 显示最近5笔交易
        recent = sorted(self.transactions, key=lambda x: x.date, reverse=True)[:5]
        if recent:
            print(f"\n最近交易:")
            for t in recent:
                print(f"  {t}")


def init_sample_data(tracker):
    """初始化示例数据"""
    sample_transactions = [
        (8000, "工资", "3月工资", "2026-03-01", "income"),
        (1500, "奖金", "项目奖金", "2026-03-05", "income"),
        (200, "投资", "股票收益", "2026-03-10", "income"),
        (1200, "住房", "房租", "2026-03-01", "expense"),
        (800, "餐饮", "日常餐饮", "2026-03-02", "expense"),
        (300, "交通", "地铁+打车", "2026-03-03", "expense"),
        (500, "购物", "衣服", "2026-03-05", "expense"),
        (200, "娱乐", "电影", "2026-03-08", "expense"),
        (100, "医疗", "感冒药", "2026-03-12", "expense"),
        (8000, "工资", "4月工资", "2026-04-01", "income"),
        (1200, "住房", "房租", "2026-04-01", "expense"),
        (900, "餐饮", "日常餐饮", "2026-04-02", "expense"),
        (350, "交通", "地铁+打车", "2026-04-03", "expense"),
        (800, "购物", "电子产品", "2026-04-05", "expense"),
        (300, "娱乐", "KTV", "2026-04-08", "expense"),
    ]

    for amount, category, desc, date, t_type in sample_transactions:
        tracker.add_transaction(amount, category, desc, date, t_type)

    # 设置预算
    tracker.set_budget("餐饮", 1000)
    tracker.set_budget("交通", 500)
    tracker.set_budget("购物", 1000)
    tracker.set_budget("娱乐", 500)

    print("\n✅ 示例数据初始化完成！")


def main():
    """主程序 - 财务管理工具"""
    print("=" * 70)
    print("💰 个人财务管理工具 - Day 7 学习成果 (Phase 1 综合项目)")
    print("=" * 70)

    tracker = FinanceTracker()

    # 如果没有数据，初始化示例
    if not tracker.transactions:
        print("\n📝 首次运行，创建示例数据...")
        init_sample_data(tracker)

    while True:
        print("\n" + "-" * 70)
        print("🔧 主菜单:")
        print("1. 记一笔 (收入/支出)")
        print("2. 查看交易记录")
        print("3. 删除记录")
        print("4. 月度报表")
        print("5. 年度报表")
        print("6. 预算管理")
        print("7. 资产总览")
        print("8. 退出")
        print("-" * 70)

        choice = input("\n请选择 (1-8): ").strip()

        if choice == '1':
            print("\n  1. 收入")
            print("  2. 支出")
            t_type = "income" if input("  请选择: ").strip() == "1" else "expense"

            categories = tracker.INCOME_CATEGORIES if t_type == "income" else tracker.EXPENSE_CATEGORIES
            print(f"\n  分类: {', '.join(categories)}")
            category = input("  分类: ").strip()

            amount = input("  金额: ").strip()
            description = input("  描述: ").strip()
            date = input("  日期(默认今天): ").strip()
            date = date if date else None

            tracker.add_transaction(amount, category, description, date, t_type)

        elif choice == '2':
            print("\n  1. 全部")
            print("  2. 收入")
            print("  3. 支出")
            print("  4. 最近7天")
            print("  5. 最近30天")
            sub = input("  请选择: ").strip()

            if sub == '1':
                tracker.list_transactions()
            elif sub == '2':
                tracker.list_transactions("income")
            elif sub == '3':
                tracker.list_transactions("expense")
            elif sub == '4':
                tracker.list_transactions(days=7)
            elif sub == '5':
                tracker.list_transactions(days=30)

        elif choice == '3':
            tracker.list_transactions()
            trans_id = input("\n  请输入记录ID: ").strip()
            tracker.delete_transaction(trans_id)

        elif choice == '4':
            year = input("  年份(默认今年): ").strip()
            month = input("  月份(默认本月): ").strip()
            tracker.show_monthly_report(
                int(year) if year else None,
                int(month) if month else None
            )

        elif choice == '5':
            year = input("  年份(默认今年): ").strip()
            tracker.show_yearly_report(int(year) if year else None)

        elif choice == '6':
            print("\n  1. 设置预算")
            print("  2. 查看预算")
            sub = input("  请选择: ").strip()

            if sub == '1':
                print(f"  分类: {', '.join(tracker.EXPENSE_CATEGORIES)}")
                category = input("  分类: ").strip()
                limit = input("  预算金额: ").strip()
                tracker.set_budget(category, limit)
            elif sub == '2':
                tracker.show_budgets()

        elif choice == '7':
            tracker.show_overview()

        elif choice == '8':
            print("\n👋 感谢使用财务管理工具！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
