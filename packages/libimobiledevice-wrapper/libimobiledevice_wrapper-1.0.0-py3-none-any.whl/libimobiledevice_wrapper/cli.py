#!/usr/bin/env python3

import asyncio
import json
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import utils
from .core import LibiMobileDevice, LibiMobileDeviceError

console = Console()


@click.group()
@click.version_option()
def main():
    """libimobiledevice-wrapper - iOS 设备管理工具"""
    pass


@main.command()
@click.option('--json', 'output_json', is_flag=True, help='以 JSON 格式输出')
def list_devices(output_json: bool):
    """列出连接的设备"""
    try:
        device = LibiMobileDevice()
        devices = device.list_devices()

        if output_json:
            enriched = []
            for udid in devices:
                name = "-"
                try:
                    info = device.get_device_info(udid)
                    name = info.get("DeviceName", "-")
                except Exception:
                    pass
                enriched.append({"name": name, "udid": udid})

            click.echo(json.dumps(enriched, indent=2, ensure_ascii=False))
        else:
            if devices:
                table = Table(title="连接的设备")
                table.add_column("序号", style="cyan")
                table.add_column("设备名称", style="yellow")
                table.add_column("UDID", style="green")

                for i, udid in enumerate(devices, 1):
                    name = "-"
                    try:
                        _info = device.get_device_info(udid)
                        name = _info.get("DeviceName", "-")
                    except Exception:
                        pass

                    table.add_row(str(i), name, udid)

                console.print(table)
            else:
                console.print("[yellow]未发现连接的设备[/yellow]")

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--json', 'output_json', is_flag=True, help='以 JSON 格式输出')
def info(udid: str, output_json: bool):
    """获取设备信息"""
    try:
        if not utils.validate_udid(udid):
            console.print(f"[red]无效的 UDID 格式: {udid}[/red]")
            sys.exit(1)

        device = LibiMobileDevice()
        _info = device.get_device_info(udid)

        if output_json:
            click.echo(json.dumps(_info, indent=2, ensure_ascii=False))
        else:
            formatted_info = utils.format_device_info(_info)
            console.print(Panel(formatted_info, title=f"设备信息 - {udid}", border_style="green"))

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--json', 'output_json', is_flag=True, help='以 JSON 格式输出')
def apps(udid: str, output_json: bool):
    """列出已安装应用"""
    try:
        device = LibiMobileDevice()
        _apps = device.list_apps(udid)

        if output_json:
            click.echo(json.dumps(_apps, indent=2, ensure_ascii=False))
        else:
            if _apps:
                formatted_apps = utils.format_apps_list(_apps)
                console.print(Panel(formatted_apps, title=f"已安装应用 - {udid}", border_style="blue"))
            else:
                console.print("[yellow]未发现已安装的应用[/yellow]")

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--app-path', required=True, type=click.Path(exists=True), help='应用文件路径')
def install(udid: str, app_path: str):
    """安装应用"""
    try:
        device = LibiMobileDevice()

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("正在安装应用...", total=None)

            device.install_app(udid, app_path)
            progress.update(task, description="[green]应用安装完成!")

        console.print(f"[green]✓ 应用安装成功: {app_path}[/green]")

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--bundle-id', required=True, help='应用 Bundle ID')
def uninstall(udid: str, bundle_id: str):
    """卸载应用"""
    try:
        device = LibiMobileDevice()

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("正在卸载应用...", total=None)

            device.uninstall_app(udid, bundle_id)
            progress.update(task, description="[green]应用卸载完成!")

        console.print(f"[green]✓ 应用卸载成功: {bundle_id}[/green]")

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--bundle-id', required=True, help='应用 Bundle ID')
@click.option('--json', 'output_json', is_flag=True, help='以 JSON 格式输出')
def app_info(udid: str, bundle_id: str, output_json: bool):
    """获取指定应用的详细信息"""
    try:
        device = LibiMobileDevice()
        _app_info = device.get_app_info(udid, bundle_id)

        if output_json:
            click.echo(json.dumps(_app_info, indent=2, ensure_ascii=False))
        else:
            if 'error' in _app_info:
                console.print(f"[red]错误: {_app_info['error']}[/red]")
            elif not _app_info:
                console.print(f"[yellow]⚠️  应用 '{bundle_id}' 未在设备上安装[/yellow]")
                console.print(f"[blue]💡 请先安装应用，然后重试[/blue]")
            else:
                table = Table(title=f"应用详细信息 - {bundle_id}")
                table.add_column("属性", style="cyan")
                table.add_column("值", style="green")

                # 显示常用属性
                common_keys = [
                    'CFBundleIdentifier', 'CFBundleName', 'CFBundleDisplayName',
                    'CFBundleVersion', 'CFBundleShortVersionString',
                    'CFBundleExecutable', 'CFBundlePackageType',
                    'CFBundleInfoDictionaryVersion', 'CFBundleSignature',
                    'LSRequiresIPhoneOS', 'UISupportedInterfaceOrientations',
                    'CFBundleSupportedPlatforms', 'MinimumOSVersion'
                ]

                for key in common_keys:
                    if key in _app_info:
                        value = _app_info[key]
                        if isinstance(value, (list, dict)):
                            value = json.dumps(value, ensure_ascii=False)
                        table.add_row(key, str(value))

                console.print(table)

                # 如果有其他属性，显示在单独的面板中
                other_keys = [k for k in _app_info.keys() if k not in common_keys]
                if other_keys:
                    other_info = {k: _app_info[k] for k in other_keys}
                    console.print(Panel(
                        json.dumps(other_info, indent=2, ensure_ascii=False),
                        title="其他属性",
                        border_style="blue"
                    ))

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--bundle-id', required=True, help='应用 Bundle ID')
def launch(udid: str, bundle_id: str):
    """启动应用"""
    try:
        device = LibiMobileDevice()

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("正在启动应用...", total=None)

            device.launch_app(udid, bundle_id)
            progress.update(task, description="[green]应用启动完成!")

        console.print(f"[green]✓ 应用启动成功: {bundle_id}[/green]")

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--remote-path', required=True, help='设备上的文件路径')
@click.option('--local-path', required=True, type=click.Path(), help='本地保存路径')
def pull(udid: str, remote_path: str, local_path: str):
    """从设备拉取文件"""
    try:
        device = LibiMobileDevice()

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("正在拉取文件...", total=None)

            device.pull_file(udid, remote_path, local_path)
            progress.update(task, description="[green]文件拉取完成!")

        console.print(f"[green]✓ 文件拉取成功: {remote_path} -> {local_path}[/green]")

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--local-path', required=True, type=click.Path(exists=True), help='本地文件路径')
@click.option('--remote-path', required=True, help='设备上的保存路径')
def push(udid: str, local_path: str, remote_path: str):
    """推送文件到设备"""
    try:
        device = LibiMobileDevice()

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("正在推送文件...", total=None)

            device.push_file(udid, local_path, remote_path)
            progress.update(task, description="[green]文件推送完成!")

        console.print(f"[green]✓ 文件推送成功: {local_path} -> {remote_path}[/green]")

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--duration', type=int, help='监控时长（秒），不指定则持续监控直到手动停止')
@click.option('--keywords', help='关键字过滤（用逗号分隔）')
@click.option('--output', type=click.Path(), help='日志输出文件路径')
def device_logs(udid: str, duration: Optional[int], keywords: Optional[str],
                output: Optional[str]):
    """获取设备日志"""
    try:
        device = LibiMobileDevice()

        # 解析关键字
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            if duration:
                task = progress.add_task(f"正在监控设备日志 ({duration}秒)...", total=None)
            else:
                task = progress.add_task("正在监控设备日志 (持续监控，按 Ctrl+C 停止)...", total=None)

            # 准备输出文件
            output_file = None
            if output:
                try:
                    output_file = open(output, 'w', encoding='utf-8')
                    console.print(f"[green]日志将保存到: {output}[/green]")
                except Exception as e:
                    console.print(f"[red]无法创建输出文件 {output}: {e}[/red]")
                    raise click.Abort()

            # 实时输出日志
            def log_callback(log_entry):
                """实时日志回调函数"""
                timestamp = log_entry['timestamp']
                level = log_entry['level']
                process = log_entry['process']
                message = log_entry['message']

                # 格式化日志行
                log_line = f"{timestamp} {level} {process}: {message}\n"

                if output_file:
                    try:
                        output_file.write(log_line)
                        output_file.flush()
                    except Exception as ex:
                        console.print(f"[red]写入文件错误: {ex}[/red]")

                level_color = {
                    'Error': 'red',
                    'Warning': 'yellow',
                    'Info': 'green',
                    'Debug': 'blue',
                    'Notice': 'cyan'
                }.get(level, 'white')

                console.print(f"[dim]{timestamp}[/dim] [{level_color}]{level}[/{level_color}] {process}: {message}")

            monitor = device.monitor_device_logs(udid, keyword_list, log_callback)
            monitor.start()

            import time
            try:
                if duration:
                    time.sleep(duration)
                else:
                    while monitor.is_running():
                        time.sleep(1)
            except KeyboardInterrupt:
                console.print("\n[yellow]监控已停止[/yellow]")
            finally:
                monitor.stop()
                if output_file:
                    try:
                        output_file.close()
                        console.print(f"[green]日志已保存到: {output}[/green]")
                    except Exception as e:
                        console.print(f"[red]关闭文件错误: {e}[/red]")

            progress.update(task, description="[green]日志监控完成!")

    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        raise click.Abort()


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
def reboot(udid: str):
    """重启设备"""
    try:
        device = LibiMobileDevice()

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("正在重启设备...", total=None)

            device.reboot_device(udid)
            progress.update(task, description="[green]设备重启命令已发送!")

        console.print(f"[green]✓ 设备重启命令已发送: {udid}[/green]")

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--udid', required=True, help='设备 UDID')
def shutdown(udid: str):
    """关机设备"""
    try:
        device = LibiMobileDevice()

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("正在关机设备...", total=None)

            device.shutdown_device(udid)
            progress.update(task, description="[green]设备关机命令已发送!")

        console.print(f"[green]✓ 设备关机命令已发送: {udid}[/green]")

    except LibiMobileDeviceError as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


# 异步命令组
@main.group()
def async_cmd():
    """异步命令（实验性功能）"""
    pass


@async_cmd.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--json', 'output_json', is_flag=True, help='以 JSON 格式输出')
def info(udid: str, output_json: bool):
    """异步获取设备信息"""

    async def _get_info():
        try:
            device = LibiMobileDevice()
            info = await device.get_device_info_async(udid)

            if output_json:
                click.echo(json.dumps(info, indent=2, ensure_ascii=False))
            else:
                table = Table(title=f"设备信息 - {udid}")
                table.add_column("属性", style="cyan")
                table.add_column("值", style="green")

                for key, value in info.items():
                    table.add_row(key, value)

                console.print(table)

        except LibiMobileDeviceError as e:
            console.print(f"[red]错误: {e}[/red]")
            sys.exit(1)

    asyncio.run(_get_info())


@async_cmd.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--bundle-id', required=True, help='应用 Bundle ID')
@click.option('--json', 'output_json', is_flag=True, help='以 JSON 格式输出')
def app_info(udid: str, bundle_id: str, output_json: bool):
    """异步获取指定应用的详细信息"""

    async def _get_app_info():
        try:
            device = LibiMobileDevice()
            app_info = await device.get_app_info_async(udid, bundle_id)

            if output_json:
                click.echo(json.dumps(app_info, indent=2, ensure_ascii=False))
            else:
                if 'error' in app_info:
                    console.print(f"[red]错误: {app_info['error']}[/red]")
                elif not app_info:
                    console.print(f"[yellow]⚠️  应用 '{bundle_id}' 未在设备上安装[/yellow]")
                    console.print(f"[blue]💡 请先安装应用，然后重试[/blue]")
                else:
                    table = Table(title=f"应用详细信息 - {bundle_id}")
                    table.add_column("属性", style="cyan")
                    table.add_column("值", style="green")

                    common_keys = [
                        'CFBundleIdentifier', 'CFBundleName', 'CFBundleDisplayName',
                        'CFBundleVersion', 'CFBundleShortVersionString',
                        'CFBundleExecutable', 'CFBundlePackageType',
                        'CFBundleInfoDictionaryVersion', 'CFBundleSignature',
                        'LSRequiresIPhoneOS', 'UISupportedInterfaceOrientations',
                        'CFBundleSupportedPlatforms', 'MinimumOSVersion'
                    ]

                    for key in common_keys:
                        if key in app_info:
                            value = app_info[key]
                            if isinstance(value, (list, dict)):
                                value = json.dumps(value, ensure_ascii=False)
                            table.add_row(key, str(value))

                    console.print(table)

                    other_keys = [k for k in app_info.keys() if k not in common_keys]
                    if other_keys:
                        other_info = {k: app_info[k] for k in other_keys}
                        console.print(Panel(
                            json.dumps(other_info, indent=2, ensure_ascii=False),
                            title="其他属性",
                            border_style="blue"
                        ))

        except LibiMobileDeviceError as e:
            console.print(f"[red]错误: {e}[/red]")
            sys.exit(1)

    asyncio.run(_get_app_info())


@async_cmd.command()
@click.option('--udid', required=True, help='设备 UDID')
@click.option('--app-path', required=True, type=click.Path(exists=True), help='应用文件路径')
def install(udid: str, app_path: str):
    """异步安装应用"""

    async def _install():
        try:
            device = LibiMobileDevice()

            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
            ) as progress:
                task = progress.add_task("正在异步安装应用...", total=None)

                await device.install_app_async(udid, app_path)
                progress.update(task, description="[green]应用安装完成!")

            console.print(f"[green]✓ 应用安装成功: {app_path}[/green]")

        except LibiMobileDeviceError as e:
            console.print(f"[red]错误: {e}[/red]")
            sys.exit(1)

    asyncio.run(_install())


if __name__ == '__main__':
    main()
