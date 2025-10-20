from pathlib import Path

import click
from rich.console import Console

from sbkube.models.config_model import (
    AppInfoScheme,
    AppInstallHelmSpec,
    AppPullHelmSpec,
)
from sbkube.utils.cli_check import check_helm_installed_or_exit
from sbkube.utils.common import run_command
from sbkube.utils.file_loader import load_config_file

console = Console()


@click.command(name="template")
@click.option(
    "--app-dir",
    "app_config_dir_name",
    default="config",
    help="앱 설정 파일이 위치한 디렉토리 이름 (base-dir 기준)",
)
@click.option(
    "--output-dir",
    "output_dir_name",
    default="rendered",
    help="렌더링된 YAML을 저장할 디렉토리 (app-dir 기준 또는 절대경로)",
)
@click.option(
    "--base-dir",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="프로젝트 루트 디렉토리",
)
@click.option(
    "--namespace",
    "cli_namespace",
    default=None,
    help="템플릿 생성 시 적용할 기본 네임스페이스 (없으면 앱별 설정 따름)",
)
@click.option(
    "--config-file",
    "config_file_name",
    default=None,
    help="사용할 설정 파일 이름 (app-dir 내부, 기본값: config.yaml 자동 탐색)",
)
@click.option(
    "--app",
    "app_name",
    default=None,
    help="템플릿을 생성할 특정 앱 이름 (지정하지 않으면 모든 앱 처리)",
)
def cmd(
    app_config_dir_name: str,
    output_dir_name: str,
    base_dir: str,
    cli_namespace: str,
    config_file_name: str,
    app_name: str,
):
    """빌드된 Helm 차트를 YAML로 렌더링합니다 (helm template). `build` 명령 이후에 실행해야 합니다."""

    console.print(
        f"[bold blue]✨ `template` 작업 시작 (앱 설정: '{app_config_dir_name}', 기준 경로: '{base_dir}') ✨[/bold blue]",
    )
    check_helm_installed_or_exit()

    BASE_DIR = Path(base_dir).resolve()
    APP_CONFIG_DIR = BASE_DIR / app_config_dir_name

    BUILD_DIR = APP_CONFIG_DIR / "build"
    VALUES_DIR = APP_CONFIG_DIR / "values"

    OUTPUT_DIR = Path(output_dir_name)
    if not OUTPUT_DIR.is_absolute():
        OUTPUT_DIR = APP_CONFIG_DIR / output_dir_name

    console.print(f"[cyan]ℹ️ 렌더링된 YAML 출력 디렉토리: {OUTPUT_DIR}[/cyan]")
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✅ 출력 디렉토리 준비 완료: {OUTPUT_DIR}[/green]")
    except OSError as e:
        console.print(
            f"[red]❌ 출력 디렉토리 생성 실패: {e}. 권한 등을 확인하세요.[/red]",
        )
        raise click.Abort()
    console.print("")

    config_file_path = None
    if config_file_name:
        config_file_path = APP_CONFIG_DIR / config_file_name
        if not config_file_path.exists() or not config_file_path.is_file():
            console.print(
                f"[red]❌ 지정된 설정 파일을 찾을 수 없습니다: {config_file_path}[/red]",
            )
            raise click.Abort()
    else:
        # 1차 시도: APP_CONFIG_DIR에서 찾기
        for ext in [".yaml", ".yml", ".toml"]:
            candidate = APP_CONFIG_DIR / f"config{ext}"
            if candidate.exists() and candidate.is_file():
                config_file_path = candidate
                break

        # 2차 시도 (fallback): BASE_DIR에서 찾기
        if not config_file_path:
            for ext in [".yaml", ".yml", ".toml"]:
                candidate = BASE_DIR / f"config{ext}"
                if candidate.exists() and candidate.is_file():
                    config_file_path = candidate
                    break

        if not config_file_path:
            console.print(
                f"[red]❌ 앱 목록 설정 파일을 찾을 수 없습니다: {APP_CONFIG_DIR}/config.[yaml|yml|toml] 또는 {BASE_DIR}/config.[yaml|yml|toml][/red]",
            )
            raise click.Abort()
    console.print(f"[green]ℹ️ 앱 목록 설정 파일 사용: {config_file_path}[/green]")

    apps_config_dict = load_config_file(str(config_file_path))

    template_total_apps = 0
    template_success_apps = 0

    app_info_list_to_template = []
    for app_dict in apps_config_dict.get("apps", []):
        try:
            app_info = AppInfoScheme(**app_dict)
            if app_info.type in ["install-helm", "install-yaml"]:
                if app_name is None or app_info.name == app_name:
                    app_info_list_to_template.append(app_info)
        except Exception as e:
            app_name_for_error = app_dict.get("name", "알 수 없는 앱")
            console.print(
                f"[red]❌ 앱 정보 '{app_name_for_error}' 처리 중 오류 (AppInfoScheme 변환 실패): {e}[/red]",
            )
            console.print(
                f"    [yellow]L 해당 앱 설정을 건너뜁니다: {app_dict}[/yellow]",
            )
            continue

    if app_name is not None and not app_info_list_to_template:
        console.print(
            f"[red]❌ 지정된 앱 '{app_name}'을 찾을 수 없거나 template 대상이 아닙니다.[/red]",
        )
        raise click.Abort()

    if not app_info_list_to_template:
        console.print(
            "[yellow]⚠️ 템플릿을 생성할 Helm 관련 앱이 설정 파일에 없습니다.[/yellow]",
        )
        console.print(
            "[bold blue]✨ `template` 작업 완료 (처리할 앱 없음) ✨[/bold blue]",
        )
        return

    for app_info in app_info_list_to_template:
        template_total_apps += 1
        app_name = app_info.name
        app_type = app_info.type

        console.print(
            f"[magenta]➡️  앱 '{app_name}' (타입: {app_type}) 템플릿 생성 시작...[/magenta]",
        )

        if app_type == "install-yaml":
            # install-yaml 타입은 빌드된 YAML 파일을 출력 디렉토리로 복사
            built_yaml_dir = BUILD_DIR / app_name

            if not built_yaml_dir.exists() or not built_yaml_dir.is_dir():
                console.print(
                    f"[red]❌ 앱 '{app_name}': 빌드된 YAML 디렉토리를 찾을 수 없습니다: {built_yaml_dir}[/red]",
                )
                console.print(
                    f"    [yellow]L 'sbkube build' 명령을 먼저 실행하여 '{app_name}' 앱을 빌드했는지 확인하세요.[/yellow]",
                )
                console.print("")
                continue

            # 빌드 디렉토리의 모든 YAML 파일 찾기
            yaml_files = []
            for yaml_file in built_yaml_dir.glob("*.yaml"):
                yaml_files.append(yaml_file)
            for yaml_file in built_yaml_dir.glob("*.yml"):
                yaml_files.append(yaml_file)

            if not yaml_files:
                console.print(
                    f"[yellow]⚠️  앱 '{app_name}': 빌드 디렉토리에 YAML 파일이 없습니다: {built_yaml_dir}[/yellow]",
                )
                console.print("")
                continue

            # 모든 YAML 파일을 하나로 결합
            combined_yaml_content = ""
            for yaml_file in yaml_files:
                try:
                    content = yaml_file.read_text(encoding="utf-8")
                    if combined_yaml_content:
                        combined_yaml_content += "\n---\n"
                    combined_yaml_content += content
                    console.print(
                        f"    [green]✓ YAML 파일 처리: {yaml_file.name}[/green]",
                    )
                except Exception as e:
                    console.print(
                        f"    [yellow]⚠️  YAML 파일 읽기 실패 (건너뜀): {yaml_file.name} - {e}[/yellow]",
                    )
                    continue

            if combined_yaml_content:
                output_file_path = OUTPUT_DIR / f"{app_name}.yaml"
                try:
                    output_file_path.write_text(combined_yaml_content, encoding="utf-8")
                    console.print(
                        f"[green]✅ 앱 '{app_name}' 템플릿 생성 완료: {output_file_path}[/green]",
                    )
                    template_success_apps += 1
                except OSError as e:
                    console.print(
                        f"[red]❌ 앱 '{app_name}': 템플릿 파일 저장 실패: {output_file_path}[/red]",
                    )
                    console.print(f"    [red]L 상세: {e}[/red]")

            console.print("")
            continue

        built_chart_path = BUILD_DIR / app_name

        if not built_chart_path.exists() or not built_chart_path.is_dir():
            console.print(
                f"[red]❌ 앱 '{app_name}': 빌드된 Helm 차트 디렉토리를 찾을 수 없습니다: {built_chart_path}[/red]",
            )
            console.print(
                f"    [yellow]L 'sbkube build' 명령을 먼저 실행하여 '{app_name}' 앱을 빌드했는지 확인하세요.[/yellow]",
            )
            console.print("")
            continue

        helm_template_cmd = ["helm", "template", app_name, str(built_chart_path)]

        current_ns_for_template = None
        if cli_namespace:
            current_ns_for_template = cli_namespace
        elif app_info.namespace and app_info.namespace not in [
            "!ignore",
            "!none",
            "!false",
            "",
        ]:
            current_ns_for_template = app_info.namespace

        if current_ns_for_template:
            helm_template_cmd.extend(["--namespace", current_ns_for_template])
            console.print(
                f"    [grey]ℹ️ 네임스페이스 적용: {current_ns_for_template}[/grey]",
            )

        values_from_spec = []
        try:
            if app_type == "install-helm":
                if app_info.specs:
                    spec_obj = AppInstallHelmSpec(**app_info.specs)
                    values_from_spec = spec_obj.values
            elif app_type in ["pull-helm", "pull-helm-oci"]:
                if app_info.specs:
                    if app_type == "pull-helm":
                        spec_obj = AppPullHelmSpec(**app_info.specs)
                    else:
                        spec_obj = AppPullHelmSpec(**app_info.specs)
                    values_from_spec = spec_obj.values
        except Exception as e:
            console.print(
                f"[yellow]⚠️ 앱 '{app_name}': Spec에서 values 정보 추출 중 오류 (무시하고 진행): {e}[/yellow]",
            )
            values_from_spec = []

        if values_from_spec:
            console.print("    [grey]🔩 Values 파일 적용 시도...[/grey]")
            for vf_rel_path in values_from_spec:
                abs_vf_path = Path(vf_rel_path)
                if not abs_vf_path.is_absolute():
                    abs_vf_path = VALUES_DIR / vf_rel_path

                if abs_vf_path.exists() and abs_vf_path.is_file():
                    helm_template_cmd.extend(["--values", str(abs_vf_path)])
                    console.print(
                        f"        [green]✓ Values 파일 사용: {abs_vf_path}[/green]",
                    )
                else:
                    console.print(
                        f"        [yellow]⚠️  Values 파일 없음 (건너뜀): {abs_vf_path} (원본: '{vf_rel_path}')[/yellow]",
                    )

        console.print(f"    [cyan]$ {' '.join(helm_template_cmd)}[/cyan]")
        try:
            return_code, stdout, stderr = run_command(
                helm_template_cmd,
                check=False,
                timeout=60,
            )

            if return_code == 0:
                output_file_path = OUTPUT_DIR / f"{app_name}.yaml"
                try:
                    output_file_path.write_text(stdout, encoding="utf-8")
                    console.print(
                        f"[green]✅ 앱 '{app_name}' 템플릿 생성 완료: {output_file_path}[/green]",
                    )
                    template_success_apps += 1
                except OSError as e:
                    console.print(
                        f"[red]❌ 앱 '{app_name}': 렌더링된 YAML 파일 저장 실패: {output_file_path}[/red]",
                    )
                    console.print(f"    [red]L 상세: {e}[/red]")
            else:
                console.print(
                    f"[red]❌ 앱 '{app_name}': `helm template` 실행 실패 (exit code: {return_code}):[/red]",
                )
                if stdout:
                    console.print(f"    [blue]STDOUT:[/blue] {stdout.strip()}")
                if stderr:
                    console.print(f"    [red]STDERR:[/red] {stderr.strip()}")

        except Exception as e:
            console.print(
                f"[red]❌ 앱 '{app_name}': 템플릿 생성 중 예상치 못한 오류: {e}[/red]",
            )
            import traceback

            console.print(f"[grey]{traceback.format_exc()}[/grey]")
        finally:
            console.print("")

    if template_total_apps > 0:
        console.print(
            f"[bold green]✅ `template` 작업 요약: 총 {template_total_apps}개 앱 중 {template_success_apps}개 성공.[/bold green]",
        )

    console.print(
        f"[bold blue]✨ `template` 작업 완료 (결과물 위치: {OUTPUT_DIR}) ✨[/bold blue]",
    )
