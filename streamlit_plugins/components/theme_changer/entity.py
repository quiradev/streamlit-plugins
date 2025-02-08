from pydantic import BaseModel


class FontFace(BaseModel):
    family: str
    url: str
    weight: int

class ThemeBaseLight:
    base = 0
    primaryColor="#FF4B4B"
    backgroundColor="#FFFFFF"
    secondaryBackgroundColor="#F0F2F6"
    textColor="#31333F"
    font=0
    widgetBackgroundColor="#625625"
    widgetBorderColor="#079E5A"
    skeletonBackgroundColor="#545B3C"
    bodyFont='"Victor Mono Italic", Source Sans Pro, sans-serif'
    codeFont='"Victor Mono", Source Code Pro, monospace'
    fontFaces=[
        FontFace(
            family="Inter",
            url="https://rsms.me/inter/font-files/Inter-Regular.woff2?v=3.19",
            weight=400
        ),
        FontFace(
            family="Victor Mono",
            url="https://rubjo.github.io/victor-mono/fonts/VictorMono-Regular.80e21ec6.woff",
            weight=400
        ),
        FontFace(
            family="Victor Mono Italic",
            url="https://rubjo.github.io/victor-mono/fonts/VictorMono-Italic.ab9b5a67.woff",
            weight=400,
        )
    ]
    radii={
        "checkboxRadius": 3,
        "baseWidgetRadius": 6
    }
    fontSizes={
        "tinyFontSize": 10,
        "smallFontSize": 12,
        "baseFontSize": 14
    }

class ThemeBaseDark:
    base = 1
    primaryColor = "#FF4B4B"
    backgroundColor = "#0E1117"
    secondaryBackgroundColor = "#262730"
    textColor = "#FAFAFA"
    font=0
    widgetBackgroundColor = "#0E1117"
    widgetBorderColor = "#FAFAFA33"
    skeletonBackgroundColor = "#000000"
    bodyFont='"Victor Mono Italic", Source Sans Pro, sans-serif'
    codeFont='"Victor Mono", Source Code Pro, monospace'
    fontFaces=[
        FontFace(
            family="Inter",
            url="https://rsms.me/inter/font-files/Inter-Regular.woff2?v=3.19",
            weight=400
        ),
        FontFace(
            family="Victor Mono",
            url="https://rubjo.github.io/victor-mono/fonts/VictorMono-Regular.80e21ec6.woff",
            weight=400
        ),
        FontFace(
            family="Victor Mono Italic",
            url="https://rubjo.github.io/victor-mono/fonts/VictorMono-Italic.ab9b5a67.woff",
            weight=400,
        )
    ]
    radii = {
        "checkboxRadius": 3,
        "baseWidgetRadius": 6
    }
    fontSizes = {
        "tinyFontSize": 10,
        "smallFontSize": 12,
        "baseFontSize": 14
    }



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
    radii: dict[str, int] = ThemeBaseLight.radii.copy()
    fontSizes: dict[str, int] = ThemeBaseLight.fontSizes.copy()


class ThemeInput(BaseModel):
    name: str
    icon: str
    order: int
    themeInfo: ThemeInfo

