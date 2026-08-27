# 昇格タスク用の汎用ランナー。
# runner_cmd.txt に書かれたスクリプト名(このフォルダ直下の .py のみ)を実行し、
# 出力を runner_out.txt に書く。Claude が UAC なしで採寸・スキャンを回すための仕組み。
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent

def main() -> int:
    out = HERE / 'runner_out.txt'
    try:
        target = (HERE / 'runner_cmd.txt').read_text(encoding='utf-8').strip()
    except OSError:
        out.write_text('ERROR: runner_cmd.txt not found', encoding='utf-8')
        return 1

    script = (HERE / target).resolve()
    if script.parent != HERE.resolve() or script.suffix != '.py' or not script.is_file():
        out.write_text(f'ERROR: refusing to run {target!r} (must be a .py directly in this folder)', encoding='utf-8')
        return 1

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace',
        env={**__import__('os').environ, 'PYTHONUTF8': '1'}
    )
    out.write_text(f'EXIT: {result.returncode}\n{result.stdout}\n{result.stderr}', encoding='utf-8')
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())
