"""Install this portable skill into shared storage and existing agent skill roots."""
import argparse
import hashlib
import os
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
NAME = 'handdraw-tech-icons'


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p.suffix != '.pyc'}


def install(home):
    shared = home / '.agents/skills' / NAME
    codex_home = (Path(os.environ.get('CODEX_HOME', str(home / '.codex')))
                  if home == Path.home().resolve() else home / '.codex')
    targets = [codex_home / 'skills' / NAME]
    targets += [home / agent / 'skills' / NAME
                for agent in ('.claude', '.cursor', '.gemini') if (home / agent).is_dir()]
    # Check collisions before any write; never overwrite another installed skill.
    if shared.is_symlink() or shared.exists():
        if not shared.is_dir() or inventory(shared) != inventory(SOURCE):
            raise FileExistsError(f'已有不同版本，未覆盖：{shared}')
    for target in targets:
        if (target.exists() or target.is_symlink()) and target.resolve() != shared.resolve():
            raise FileExistsError(f'已有其他文件，未覆盖：{target}')
    if not shared.exists():
        shared.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE, shared, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for target in targets:
        if not (target.exists() or target.is_symlink()):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(shared, target_is_directory=True)
        assert (target / 'SKILL.md').is_file()
    print(f'共享技能：{shared}')
    for target in targets:
        print(f'Agent 入口：{target}')
    print('文件安装完成；各应用是否已刷新发现列表需在对应会话确认。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home(), help='Home root; override for isolated validation.')
    install(parser.parse_args().home.expanduser().resolve())
