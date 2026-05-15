from __future__ import annotations

from typing import Sequence

SKELETON_SHIMMER_CSS = """
<style>
.stSkeleton {
    position: relative;
    overflow: hidden;
}

.stSkeleton::after {
    content: "";
    position: absolute;
    top: 0;
    left: -150%;
    width: 150%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
    animation: loading-animation 1.5s infinite;
}

@keyframes loading-animation {
    from {
        left: -150%;
    }

    to {
        left: 100%;
    }
}
</style>
"""


class StreamlitSkeletonBuilder:
    """Builder HTML para plantillas skeleton reutilizables."""

    _LINE_WIDTHS: tuple[int, ...] = (95, 100, 70, 85, 90)

    def __init__(self) -> None:
        self._parts: list[str] = []

    def add(self, html: str) -> "StreamlitSkeletonBuilder":
        self._parts.append(html)
        return self

    def clear(self) -> "StreamlitSkeletonBuilder":
        self._parts.clear()
        return self

    def build(self) -> str:
        return "".join(self._parts)

    def with_shimmer_css(self) -> "StreamlitSkeletonBuilder":
        self._parts.insert(0, SKELETON_SHIMMER_CSS)
        return self

    def title(self) -> str:
        return '<div class="stSkeleton" style="width: 60%; height: 48px; border-radius: 8px; margin-bottom: 24px;"></div>'

    def header(self) -> str:
        return '<div class="stSkeleton" style="width: 50%; height: 36px; border-radius: 6px; margin-bottom: 20px;"></div>'

    def subheader(self) -> str:
        return '<div class="stSkeleton" style="width: 40%; height: 28px; border-radius: 5px; margin-bottom: 16px;"></div>'

    def markdown(self, lines: int = 3) -> str:
        line_count = max(1, lines)
        line_html = '<div class="stSkeleton" style="width: {width}%; height: 16px; border-radius: 4px;"></div>'
        html = '<div style="display: flex; flex-direction: column; gap: 8px;">'
        for index in range(line_count):
            html += line_html.format(width=self._LINE_WIDTHS[index % len(self._LINE_WIDTHS)])
        html += "</div>"
        return html

    def metric(self) -> str:
        return """
<div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px;">
    <div class="stSkeleton" style="width: 50%; height: 14px; border-radius: 4px; margin-bottom: 12px;"></div>
    <div class="stSkeleton" style="width: 75%; height: 36px; border-radius: 6px; margin-bottom: 12px;"></div>
    <div class="stSkeleton" style="width: 30%; height: 14px; border-radius: 4px;"></div>
</div>
"""

    def dataframe(self, rows: int = 3, cols: int = 3) -> str:
        row_count = max(1, rows)
        col_count = max(1, cols)
        header = (
            '<div style="display: flex; gap: 12px;">'
            + "".join(
                [
                    '<div class="stSkeleton" style="flex: 1; height: 24px; border-radius: 4px;"></div>'
                    for _ in range(col_count)
                ]
            )
            + "</div>"
        )
        row_html = (
            '<div style="display: flex; gap: 12px;">'
            + "".join(
                [
                    '<div class="stSkeleton" style="flex: 1; height: 20px; border-radius: 4px;"></div>'
                    for _ in range(col_count)
                ]
            )
            + "</div>"
        )

        html = (
            '<div style="display: flex; flex-direction: column; gap: 12px; border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px;">'
            f"{header}"
        )
        for _ in range(row_count):
            html += row_html
        html += "</div>"
        return html

    def button(self) -> str:
        return '<div class="stSkeleton" style="width: 120px; height: 38px; border-radius: 24px;"></div>'

    def selectbox(self, label: bool = True) -> str:
        label_html = (
            '<div class="stSkeleton" style="width: 30%; height: 16px; border-radius: 4px;"></div>'
            if label
            else ""
        )
        return f"""
<div style="display: flex; flex-direction: column; gap: 8px;">
    {label_html}
    <div class="stSkeleton" style="width: 100%; height: 38px; border-radius: 8px;"></div>
</div>
"""

    def text_input(self, label: bool = True) -> str:
        return self.selectbox(label=label)

    def slider(self, label: bool = True) -> str:
        label_html = (
            '<div class="stSkeleton" style="width: 30%; height: 16px; border-radius: 4px;"></div>'
            if label
            else ""
        )
        return f"""
<div style="display: flex; flex-direction: column; gap: 12px;">
    {label_html}
    <div style="display: flex; align-items: center; gap: 12px;">
        <div class="stSkeleton" style="flex-grow: 1; height: 4px; border-radius: 2px;"></div>
        <div class="stSkeleton" style="width: 40px; height: 24px; border-radius: 4px;"></div>
    </div>
</div>
"""

    def chart(self, height: int = 400) -> str:
        resolved_height = max(60, height)
        return f'<div class="stSkeleton" style="width: 100%; height: {resolved_height}px; border-radius: 8px;"></div>'

    def image(self, height: int = 300) -> str:
        resolved_height = max(60, height)
        return f'<div class="stSkeleton" style="width: 100%; height: {resolved_height}px; border-radius: 8px;"></div>'

    def columns(self, specs: Sequence[Sequence[str]], gap_px: int = 16) -> str:
        if not specs:
            raise ValueError("specs no puede estar vacio")

        gap = max(0, gap_px)
        flex_basis = 100 / len(specs)
        html = f'<div style="display: flex; gap: {gap}px; width: 100%;">'
        for col_content_list in specs:
            html += (
                f'<div style="flex: {flex_basis}%; display: flex; flex-direction: column; gap: {gap}px;">'
                + "".join(col_content_list)
                + "</div>"
            )
        html += "</div>"
        return html


__all__ = ["SKELETON_SHIMMER_CSS", "StreamlitSkeletonBuilder"]

