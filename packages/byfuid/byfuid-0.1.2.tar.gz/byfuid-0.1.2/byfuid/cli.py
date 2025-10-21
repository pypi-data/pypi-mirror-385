#!/usr/bin/env python3
"""
BYFUID 命令行工具
"""

import argparse
import sys
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("错误: 请安装 rich 库: pip3 install rich")
    sys.exit(1)

from byfuid import generate_byfuid, validate_byfuid_length, RUST_AVAILABLE


class ByfuidCLI:
    """BYFUID 命令行接口"""
    
    def __init__(self):
        self.console = Console()
    
    def print_error(self, message: str):
        """打印错误信息"""
        if RICH_AVAILABLE:
            self.console.print(f"[bold red]错误:[/bold red] {message}")
        else:
            print(f"错误: {message}")
    
    def print_success(self, message: str):
        """打印成功信息"""
        if RICH_AVAILABLE:
            self.console.print(f"[bold green]成功:[/bold green] {message}")
        else:
            print(f"成功: {message}")
    
    def print_info(self, message: str):
        """打印信息"""
        if RICH_AVAILABLE:
            self.console.print(f"[bold blue]信息:[/bold blue] {message}")
        else:
            print(f"信息: {message}")
    
    def print_warning(self, message: str):
        """打印警告信息"""
        if RICH_AVAILABLE:
            self.console.print(f"[bold yellow]警告:[/bold yellow] {message}")
        else:
            print(f"警告: {message}")
    
    def validate_user_data(self, user_data: str) -> bool:
        """验证用户数据"""
        if len(user_data) != 12:
            self.print_error(f"用户数据必须为12字符，当前为 {len(user_data)} 字符")
            return False
        return True
    
    def validate_custom_data(self, custom_data: str) -> bool:
        """验证自定义数据"""
        if len(custom_data) > 201:
            self.print_warning(f"自定义数据超过201字符，将被截断")
        return True
    
    def generate_byfuid(self, user_data: Optional[str], custom_data: Optional[str], show_details: bool = False):
        """生成 BYFUID"""
        try:
            # 验证用户数据
            if user_data and not self.validate_user_data(user_data):
                return 1
            
            # 验证自定义数据
            if custom_data and not self.validate_custom_data(custom_data):
                return 1
            
            # 生成 BYFUID
            byfuid = generate_byfuid(user_data, custom_data)
            
            # 显示结果
            if RICH_AVAILABLE:
                # 创建结果面板
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("属性", style="cyan", width=15)
                table.add_column("值", style="white")
                
                table.add_row("BYFUID 长度", f"{len(byfuid)} 字符")
                table.add_row("生成引擎", "Rust" if RUST_AVAILABLE else "Python")
                if user_data:
                    table.add_row("用户数据", user_data)
                if custom_data:
                    display_custom = custom_data[:50] + "..." if len(custom_data) > 50 else custom_data
                    table.add_row("自定义数据", display_custom)
                
                self.console.print(Panel.fit(
                    table,
                    title="[bold green]BYFUID 生成成功[/bold green]",
                    border_style="green"
                ))
                
                # 显示 BYFUID
                self.console.print("\n[bold]生成的 BYFUID:[/bold]")
                syntax = Syntax(byfuid, "text", word_wrap=True)
                self.console.print(syntax)
                
                if show_details:
                    self.console.print("\n[bold]详细信息:[/bold]")
                    detail_table = Table(show_header=True, header_style="bold blue")
                    detail_table.add_column("段", style="cyan")
                    detail_table.add_column("长度", style="yellow")
                    detail_table.add_column("描述", style="white")
                    
                    detail_table.add_row("用户自由数据", "12 字符", "用户自定义或随机生成的12字符数据")
                    detail_table.add_row("自定义数据", "201 字符", "支持中英文的自定义内容")
                    detail_table.add_row("时间戳", "13 字符", "毫秒级时间戳")
                    detail_table.add_row("数据校验", "24 字符", "SHA256校验和的前24字符")
                    detail_table.add_row("总计", "250 字符", "编码前原始数据长度")
                    detail_table.add_row("最终BYFUID", "512 字符", "Base64编码后的最终结果")
                    
                    self.console.print(detail_table)
            else:
                print(f"生成的 BYFUID ({len(byfuid)} 字符):")
                print(byfuid)
            
            return 0
            
        except ValueError as e:
            self.print_error(str(e))
            return 1
        except Exception as e:
            self.print_error(f"生成 BYFUID 时发生未知错误: {str(e)}")
            return 1
    
    def validate_byfuid(self, byfuid: str):
        """验证 BYFUID"""
        try:
            is_valid = validate_byfuid_length(byfuid)
            
            if RICH_AVAILABLE:
                if is_valid:
                    self.console.print(
                        Panel.fit(
                            f"BYFUID 长度验证通过\n长度: {len(byfuid)} 字符",
                            title="[bold green]验证成功[/bold green]",
                            border_style="green"
                        )
                    )
                else:
                    self.console.print(
                        Panel.fit(
                            f"BYFUID 长度无效\n当前长度: {len(byfuid)} 字符\n期望长度: 512 字符",
                            title="[bold red]验证失败[/bold red]",
                            border_style="red"
                        )
                    )
            else:
                if is_valid:
                    print(f"验证通过: BYFUID 长度为 {len(byfuid)} 字符")
                else:
                    print(f"验证失败: BYFUID 长度应为 512 字符，当前为 {len(byfuid)} 字符")
            
            return 0 if is_valid else 1
            
        except Exception as e:
            self.print_error(f"验证 BYFUID 时发生错误: {str(e)}")
            return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="BYFUID 生成器 - 高性能 BYFUID 生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
生成的ByFuid可能包含换行，请去除那些换行，以保证生成的ByFuid是标准的ByFuid
示例:
  %(prog)s generate                                 # 生成随机 BYFUID
  %(prog)s generate -u "user12345678"               # 使用指定用户数据
  %(prog)s generate -c "我的自定义数据"             # 使用自定义数据
  %(prog)s generate -u "test12345678" -c "hello"    # 使用用户数据和自定义数据
  %(prog)s validate "BYFUID字符串"                  # 验证 BYFUID 长度
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # generate 子命令
    generate_parser = subparsers.add_parser('generate', help='生成 BYFUID')
    generate_parser.add_argument('-u', '--user-data', help='12字符用户自由数据')
    generate_parser.add_argument('-c', '--custom-data', help='自定义数据（最多201字符）')
    generate_parser.add_argument('-d', '--details', action='store_true', help='显示详细信息')
    
    # validate 子命令
    validate_parser = subparsers.add_parser('validate', help='验证 BYFUID')
    validate_parser.add_argument('byfuid', help='要验证的 BYFUID 字符串')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = ByfuidCLI()
    
    if args.command == 'generate':
        return cli.generate_byfuid(args.user_data, args.custom_data, args.details)
    elif args.command == 'validate':
        return cli.validate_byfuid(args.byfuid)


if __name__ == '__main__':
    sys.exit(main())