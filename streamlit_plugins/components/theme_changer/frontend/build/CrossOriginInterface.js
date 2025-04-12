class ThemeChangerCOI {
    static instances = {};
    constructor(key) {
        if (ThemeChangerCOI.instances[key]) {
            console.info('ThemeChangerCOI instance already exists with key', key);
            return ThemeChangerCOI.instances[key];
        }

        ThemeChangerCOI.instances[key] = this;
        this.key = key;
    }

    themeToggle(themeData, themeName="Custom") {

        // Se crea el data
        const data = {
            stCommVersion: 1,
            type: "SET_CUSTOM_THEME_CONFIG",
            // type: "SET_THEME_CONFIG", // No funciona solo si el origen es el mismo Streamlit
            themeInfo: themeData.themeInfo,
            themeName: themeData.name || themeName
        }
        let themeInput = {
            "name": themeName,
            "themeInput": themeData.themeInfo
        };
        // Se guarda en el Local Storage el tema seleccionado
        // con clave stActiveTheme-/-v1 y valor theme
        localStorage.setItem('stActiveTheme-/-v1', JSON.stringify(themeInput));
        // Se comunica con el padre
        window.parent.postMessage(data, "*");
        window.postMessage(data, "*");
    }
}

function changeThemeWithCOI(key, themeData) {
    console.info("Theme Changed");
    theme_coi = new ThemeChangerCOI(key);
    theme_coi.themeToggle(themeData);
}
window.changeThemeWithCOI = changeThemeWithCOI;