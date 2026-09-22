"""Compile a small component brief into a fixed image prompt; no LLM or API call."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compile_prompt(brief):
    required = {'component', 'responsibility', 'semantics', 'glyphs', 'secondary',
                'must_preserve', 'forbidden', 'accent', 'label'}
    if set(brief) != required:
        raise ValueError(f'字段不匹配：缺少 {sorted(required-set(brief))}；多余 {sorted(set(brief)-required)}')
    for field in ('component', 'responsibility', 'secondary', 'accent', 'label'):
        if not isinstance(brief[field], str):
            raise ValueError(f'{field} 必须是字符串')
    for field in ('component', 'responsibility', 'accent'):
        if not brief[field].strip():
            raise ValueError(f'{field} 不能为空')
    for field, maximum in [('semantics', 3), ('glyphs', 4), ('must_preserve', 6), ('forbidden', 15)]:
        value = brief[field]
        if not isinstance(value, list) or not 1 <= len(value) <= maximum:
            raise ValueError(f'{field} 需要 1–{maximum} 项')
        if not all(isinstance(item, str) and item.strip() for item in value):
            raise ValueError(f'{field} 中每项必须是非空字符串')
    glyphs = '\n'.join(f'- {item}' for item in brief['glyphs'])
    invariants = '\n'.join(f'- {item}' for item in brief['must_preserve'])
    label = (f'仅在方框下方写这个标签：{json.dumps(brief["label"], ensure_ascii=False)}。'
             if brief['label'] else '图内图外均不出现文字、字母或数字。')
    return f'''生成一个软件架构组件的手绘 icon，组件名称用于理解主题：{brief['component']}。
职责：{brief['responsibility']}
只表达这些核心语义：{'；'.join(brief['semantics'])}。

实际画面仅由以下主体图形构成：
{glyphs}
辅助元素：{brief['secondary'] or '无'}
必须保持的关系：
{invariants}

固定视觉规范：一个居中的正方形图标，正方形黑色外框，框内{brief['accent']}铅笔交叉排线底，主体白底、黑色轮廓。四周留白。平面 2D，线条简单、轮廓清晰，缩小后仍易辨认。自然轻微的笔压变化、不规则抖动与少量近距离复描，不能像机械矢量，也不能刻意画成波浪线。主体不被排线淹没。仅一个 icon，不做多方案拼图。
{label}
不画人物故事、风景、海报、整张架构流程图，不加商标或装饰。特别禁止：{'、'.join(brief['forbidden'])}。

所附图片仅用于参考画风。只提取参考图的风格特征，例如线条、笔触、媒介、材质、色彩倾向和整体视觉语言；不要使用、复制或延续参考图中的任何主体、人物、动物、服装、道具、动作、姿态、场景、背景、构图、布局、文字或故事。最终画面内容完全以用户提供的主题为准。
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('brief', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    prompt = compile_prompt(json.loads(args.brief.read_text()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(prompt)
    print(f'已生成提示词：{args.out.resolve()}')
    print(f'调用绘图工具时附上参考图：{ROOT / "assets/style-reference.png"}')
    print('此脚本不生成图片；下一步必须实际调用图像生成工具。')


if __name__ == '__main__':
    main()
