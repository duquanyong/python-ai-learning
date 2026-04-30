"""
Day 4 Project: 数据分析与可视化工具
功能：读取CSV数据，进行统计分析，生成可视化图表
作者：duquanyong
日期：2026-04-30
"""
import csv
import os
from datetime import datetime
from collections import Counter


class DataAnalyzer:
    """数据分析器 - 分析销售/成绩/任何表格数据"""

    def __init__(self, filename="sample_data.csv"):
        self.filename = filename
        self.data = []
        self.headers = []
        self.load_data()

    def load_data(self):
        """从CSV文件加载数据"""
        if not os.path.exists(self.filename):
            print(f"📝 未找到 {self.filename}，将创建示例数据...")
            self._create_sample_data()

        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.headers = reader.fieldnames
                self.data = list(reader)
            print(f"✅ 已加载 {len(self.data)} 条数据，共 {len(self.headers)} 个字段")
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            self.data = []
            self.headers = []

    def _create_sample_data(self):
        """创建示例销售数据"""
        sample_data = [
            ["日期", "产品", "类别", "销量", "单价", "地区"],
            ["2026-01", "笔记本电脑", "电子产品", "15", "5999", "北京"],
            ["2026-01", "无线鼠标", "电子产品", "120", "89", "北京"],
            ["2026-01", "机械键盘", "电子产品", "45", "299", "上海"],
            ["2026-01", "显示器", "电子产品", "30", "1299", "广州"],
            ["2026-02", "笔记本电脑", "电子产品", "18", "5999", "上海"],
            ["2026-02", "无线鼠标", "电子产品", "150", "89", "北京"],
            ["2026-02", "机械键盘", "电子产品", "50", "299", "广州"],
            ["2026-02", "显示器", "电子产品", "35", "1299", "北京"],
            ["2026-02", "办公椅", "家具", "20", "899", "上海"],
            ["2026-02", "书桌", "家具", "12", "1599", "广州"],
            ["2026-03", "笔记本电脑", "电子产品", "22", "5799", "北京"],
            ["2026-03", "无线鼠标", "电子产品", "180", "89", "上海"],
            ["2026-03", "机械键盘", "电子产品", "60", "279", "北京"],
            ["2026-03", "显示器", "电子产品", "40", "1299", "广州"],
            ["2026-03", "办公椅", "家具", "25", "899", "北京"],
            ["2026-03", "书桌", "家具", "15", "1599", "上海"],
            ["2026-03", "台灯", "家具", "50", "129", "广州"],
        ]

        with open(self.filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(sample_data)
        print(f"✅ 已创建示例数据文件: {self.filename}")

    def show_data_preview(self, n=5):
        """显示数据预览"""
        print("\n" + "=" * 60)
        print("📋 数据预览（前 {} 行）".format(n))
        print("=" * 60)

        # 打印表头
        print(" | ".join(self.headers))
        print("-" * 60)

        # 打印数据
        for row in self.data[:n]:
            print(" | ".join(row.get(h, "") for h in self.headers))

        print(f"\n... 共 {len(self.data)} 行数据 ...")

    def calculate_total_sales(self):
        """计算总销售额"""
        total = 0
        for row in self.data:
            try:
                quantity = int(row.get("销量", 0))
                price = float(row.get("单价", 0))
                total += quantity * price
            except (ValueError, TypeError):
                continue
        return total

    def sales_by_product(self):
        """按产品统计销售额"""
        product_sales = {}
        for row in self.data:
            product = row.get("产品", "未知")
            try:
                quantity = int(row.get("销量", 0))
                price = float(row.get("单价", 0))
                sales = quantity * price
                product_sales[product] = product_sales.get(product, 0) + sales
            except (ValueError, TypeError):
                continue
        return product_sales

    def sales_by_region(self):
        """按地区统计销售额"""
        region_sales = {}
        for row in self.data:
            region = row.get("地区", "未知")
            try:
                quantity = int(row.get("销量", 0))
                price = float(row.get("单价", 0))
                sales = quantity * price
                region_sales[region] = region_sales.get(region, 0) + sales
            except (ValueError, TypeError):
                continue
        return region_sales

    def sales_by_month(self):
        """按月统计销售额"""
        month_sales = {}
        for row in self.data:
            month = row.get("日期", "未知")
            try:
                quantity = int(row.get("销量", 0))
                price = float(row.get("单价", 0))
                sales = quantity * price
                month_sales[month] = month_sales.get(month, 0) + sales
            except (ValueError, TypeError):
                continue
        return month_sales

    def category_distribution(self):
        """统计类别分布"""
        categories = Counter()
        for row in self.data:
            category = row.get("类别", "未知")
            try:
                quantity = int(row.get("销量", 0))
                categories[category] += quantity
            except (ValueError, TypeError):
                continue
        return categories

    def show_statistics(self):
        """显示综合统计报告"""
        print("\n" + "=" * 60)
        print("📊 数据分析报告")
        print("=" * 60)

        # 总销售额
        total = self.calculate_total_sales()
        print(f"\n💰 总销售额: ¥{total:,.2f}")

        # 按产品统计
        print("\n📦 产品销售额排名:")
        product_sales = self.sales_by_product()
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
        for i, (product, sales) in enumerate(sorted_products, 1):
            print(f"  {i}. {product}: ¥{sales:,.2f}")

        # 按地区统计
        print("\n🌍 地区销售额分布:")
        region_sales = self.sales_by_region()
        for region, sales in sorted(region_sales.items(), key=lambda x: x[1], reverse=True):
            percentage = (sales / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 5)
            print(f"  {region}: ¥{sales:,.2f} ({percentage:.1f}%) {bar}")

        # 按月统计
        print("\n📅 月度销售趋势:")
        month_sales = self.sales_by_month()
        for month, sales in sorted(month_sales.items()):
            print(f"  {month}: ¥{sales:,.2f}")

        # 类别分布
        print("\n🏷️ 类别销量分布:")
        categories = self.category_distribution()
        for category, count in categories.most_common():
            print(f"  {category}: {count} 件")

        print("=" * 60)

    def export_report(self, output_file="report.txt"):
        """导出分析报告到文本文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("数据分析报告\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")

                total = self.calculate_total_sales()
                f.write(f"总销售额: ¥{total:,.2f}\n\n")

                f.write("产品销售额排名:\n")
                product_sales = self.sales_by_product()
                for product, sales in sorted(product_sales.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"  {product}: ¥{sales:,.2f}\n")

                f.write("\n地区销售额分布:\n")
                region_sales = self.sales_by_region()
                for region, sales in sorted(region_sales.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"  {region}: ¥{sales:,.2f}\n")

            print(f"✅ 报告已导出到: {output_file}")
        except Exception as e:
            print(f"❌ 导出失败: {e}")


def main():
    """主程序 - 数据分析工具"""
    print("=" * 60)
    print("📊 数据分析与可视化工具 - Day 4 学习成果")
    print("=" * 60)

    # 创建分析器实例
    analyzer = DataAnalyzer()

    while True:
        print("\n" + "-" * 60)
        print("🔧 操作菜单:")
        print("1. 预览数据")
        print("2. 查看统计报告")
        print("3. 导出报告")
        print("4. 退出")
        print("-" * 60)

        choice = input("\n请选择操作 (1-4): ").strip()

        if choice == '1':
            n = input("显示前多少行（默认5行）: ").strip()
            n = int(n) if n.isdigit() else 5
            analyzer.show_data_preview(n)

        elif choice == '2':
            analyzer.show_statistics()

        elif choice == '3':
            filename = input("请输入导出文件名（默认report.txt）: ").strip()
            if not filename:
                filename = "report.txt"
            analyzer.export_report(filename)

        elif choice == '4':
            print("\n👋 再见！明天继续学习！")
            break

        else:
            print("❌ 无效的选择，请重新输入！")


if __name__ == "__main__":
    main()
