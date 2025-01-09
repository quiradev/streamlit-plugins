from pydantic import BaseModel


class FontFace(BaseModel):
    family: str
    url: str
    weight: int

class ThemeInfo(BaseModel):
    base: int
    primaryColor: str = None
    backgroundColor: str = None
    secondaryBackgroundColor: str = None
    textColor: str = None
    font: int = None
    widgetBackgroundColor: str = None
    widgetBorderColor: str = None
    skeletonBackgroundColor: str = None
    bodyFont: str = None
    codeFont: str = None
    fontFaces: list[FontFace] = None
    radii: dict[str, int] = None
    fontSizes: dict[str, int] = None


class ThemeInput(BaseModel):
    name: str
    icon: str
    order: int
    themeInfo: ThemeInfo

