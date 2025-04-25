//Source for NavbarCOI class.
//Build with terser:
//  npx terser NavbarCOI.js --compress --mangle 'pure_funcs=["console.debug"]' --output ../build/NavbarCOI.min.js
class NavbarCOI {
    static instances = {};
    constructor(componentName, key, isNavigation, defaultPageId, positionMode, isSticky) {
        if (NavbarCOI.instances[key]) {
            console.debug('NavbarCOI instance already exists with key', key);
            let that = NavbarCOI.instances[key];
            console.info("Changing", positionMode, isSticky);
            that.init(positionMode, isSticky);
            return that;
        }
        NavbarCOI.instances[key] = this;
        console.info("Init", positionMode, isSticky);
        this.component = null;
        this.componentName = componentName;
        this.key = key;

        // AQUI SE CAMBIAN COSAS INICIALES UNICAMENTE
        // this.sortedAnchors = [];
        // this.trackedAnchors = new Set();
        // this.anchorVisibleStates = {};
        // this.activeAnchorId = null;
        // this.autoUpdateAnchor = false;
        // this.styles = null;
        // this.disable_scroll = false;
        // this.updateId = 0
        // this.enroute = false;

        // AQUI EN EL INIT SE LE PASAN LOS PARAMETROS ACTUALIZABLES
        this.isNavigation = isNavigation;
        this.init(positionMode, isSticky, null);
        this.pageId = defaultPageId;

        window.addEventListener("message", this.handleComponentMessage.bind(this));
    }

    init(positionMode, isSticky, iframeHeight) {
        this.iframeSelector = 'div.st-key-'+this.key+' iframe[title="' + this.componentName + '"]';
        this.positionMode = positionMode;
        this.isSticky = isSticky;
        this.isExpanded = document.body.classList.contains("side-nav-open");

        if (this.isNavigation) {
            let iframe = document.querySelector(this.iframeSelector);
            if (iframe) {
                if (iframeHeight) {
                    iframe.height = iframeHeight;
                }
            }

            this.setNavState(
                this.pageId,
                document.body.dataset.expandSubMenu || false,
                document.body.dataset.selectedSubMenu || null
            );
            document.body.dataset.navPosition = positionMode;
            document.body.dataset.navIsSticky = isSticky;
            // Leer la propiedad actual del ancho del sidebar
            const currentSidebarWidth = document.body.style.getPropertyValue('--sidebar-width') || "150px";
            // Add css property to body to set the width of the sidebar
            document.body.style.setProperty('--sidebar-width', currentSidebarWidth);
        }

        // Se crea el expander al lado del iframeSelector
        if (positionMode === "side") {
            let expander = document.getElementById('expander-' + this.key);
            if (!expander) {
                let expander = document.createElement('span');
                expander.id = 'expander-' + this.key;
                let isBeingExpanding = false;
                let initialX = null;
                let initialSidebarWidth = null;

                const startDrag = (event) => {
                    isBeingExpanding = true;
                    expander.classList.add('expander-active');
                    // Use clientX for mouse events and touches[0].clientX for touch events
                    initialX = event.type.includes('touch') ? event.touches[0].clientX : event.clientX;
                    initialSidebarWidth = parseInt(document.body.style.getPropertyValue('--sidebar-width'));
                };

                const onDrag = (event) => {
                    if (isBeingExpanding) {
                        // Use clientX for mouse events and touches[0].clientX for touch events
                        const currentX = event.type.includes('touch') ? event.touches[0].clientX : event.clientX;
                        const deltaX = currentX - initialX;
                        const newWidth = Math.max(150, Math.min(300, initialSidebarWidth + deltaX));
                        document.body.style.setProperty('--sidebar-width', newWidth + 'px');
                    }
                };

                const endDrag = () => {
                    isBeingExpanding = false;
                    expander.classList.remove('expander-active');
                    document.body.removeEventListener('mouseup', endDrag);
                    document.body.removeEventListener('mousemove', onDrag);
                    document.body.removeEventListener('touchend', endDrag);
                    document.body.removeEventListener('touchmove', onDrag);
                };

                // Mouse events
                expander.addEventListener('mousedown', (event) => {
                    startDrag(event);
                    document.body.addEventListener('mouseup', endDrag);
                    document.body.addEventListener('mousemove', onDrag);
                });

                // Touch events
                expander.addEventListener('touchstart', (event) => {
                    startDrag(event);
                    document.body.addEventListener('touchend', endDrag);
                    document.body.addEventListener('touchmove', onDrag);
                });

                let iframe = document.querySelector(this.iframeSelector);
                if (iframe) {
                    iframe.parentNode.appendChild(expander);
                }
            }
        }
        else {
            let expander = document.getElementById('expander-' + this.key);
            if (expander) {
                expander.remove();
            }
        }
    }

    register(component, positionMode, isExpanded, themeData, themeName="Custom") {
        this.component = component;

        this.saveTheme(themeData, themeName);

        this.isExpanded = isExpanded;
        if (this.isNavigation) {
            this.sidebarToggle(positionMode, isExpanded);
        }

        // this.autoUpdateAnchor = autoUpdateAnchor;
        // this.emphasisStyle = emphasisStyle;
        // console.debug('Registered component for key ', this.key, ": ", component, isExpanded);
    }

    // Toggle left margin of streamlit application
    sidebarToggle(positionMode, isExpanded) {
        if (positionMode !== "side") {
            document.body.classList.remove("side-nav-open");
            document.body.classList.remove("side-nav-closed");
        }
        else {
            // Agrega a la clase del body la clase nav-open
            if (isExpanded) {
                document.body.classList.add("side-nav-open");
                document.body.classList.remove("side-nav-closed");
                // console.debug('Toggled isExpanded to', isExpanded);
            }
            else {
                document.body.classList.add("side-nav-closed");
                document.body.classList.remove("side-nav-open");
                // console.debug('Removed isExpanded to', isExpanded);
            }
        }
    }
    setNavState(pageId, expandSubMenu, selectedSubMenu) {
        document.body.dataset.pageId = pageId;
        document.body.dataset.expandSubMenu = expandSubMenu;
        document.body.dataset.selectedSubMenu = selectedSubMenu;
    }
    saveTheme(themeData, themeName="Custom") {
        // Se lanza un post message a la ventana principal con el tema seleccionado
        // El evento tiene un data con este formato
        // {"stCommVersion":1,"type":"SET_THEME_CONFIG","themeInfo":{"primaryColor":"#ff4b4b","backgroundColor":"#0e1117","secondaryBackgroundColor":"#262730","textColor":"#fafafa","base":"dark","font":"\"Source Sans Pro\", sans-serif","linkText":"hsla(209, 100%, 59%, 1)","fadedText05":"rgba(250, 250, 250, 0.1)","fadedText10":"rgba(250, 250, 250, 0.2)","fadedText20":"rgba(250, 250, 250, 0.3)","fadedText40":"rgba(250, 250, 250, 0.4)","fadedText60":"rgba(250, 250, 250, 0.6)","bgMix":"rgba(26, 28, 36, 1)","darkenedBgMix100":"hsla(228, 16%, 72%, 1)","darkenedBgMix25":"rgba(172, 177, 195, 0.25)","darkenedBgMix15":"rgba(172, 177, 195, 0.15)","lightenedBg05":"hsla(220, 24%, 10%, 1)"}}

        // Se crea el data
        let themeInput = {
            "name": themeName,
            "themeInput": themeData.themeInfo
        };
        // Se guarda en el Local Storage el tema seleccionado
        // con clave stActiveTheme-/-v1 y valor theme
        localStorage.setItem('stActiveTheme-/-v1', JSON.stringify(themeInput));
        document.body.dataset.themeName = themeData.name || themeName;
    }
    themeToggle(themeData, themeName="Custom") {
        // Se guarda el tema seleccionado
        this.saveTheme(themeData, themeName);

        // Se comunica con el padre
        const data = {
            stCommVersion: 1,
            type: "SET_CUSTOM_THEME_CONFIG",
            // type: "SET_THEME_CONFIG", // No funciona solo si el origen es el mismo Streamlit
            themeInfo: themeData.themeInfo,
            themeName: themeData.name || themeName
        }
        window.parent.postMessage(data, "*");
        window.postMessage(data, "*");

        // Opcionalmente se deberia saber si hay que actualizar los iconos del toolbar
        const dataIconsLight = {
            "type": "SET_TOOLBAR_ITEMS",
            "items": [
                {
                    "key": "share",
                    "label": "Share",
                    "borderless": false
                },
                {
                    "key": "favorite",
                    "icon": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0iY3VycmVudENvbG9yIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGNvbG9yPSIjMzEzMzNGIj48ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfM18yKSI+PHBhdGggZD0iTTE0LjcwMjYgNS41MjAzN0wxMC40NjEyIDUuMTM1NDJMOC44MDQ5NSAxLjA1NjhDOC41MDcwMSAwLjMxNDQgNy40OTA0NCAwLjMxNDQgNy4xOTI1MSAxLjA1NjhMNS41MzYyNCA1LjE0NDU5TDEuMzAzNTYgNS41MjAzN0MwLjUzMjM4NyA1LjU4NDUzIDAuMjE2OTA4IDYuNTkyNzMgMC44MDQwNSA3LjEyNDMxTDQuMDIwMTggMTAuMDM4OUwzLjA1NjIyIDE0LjM2NUMyLjg4MDk1IDE1LjE1MzIgMy42OTU5NCAxNS43NzY1IDQuMzYxOTUgMTUuMzU0OUw3Ljk5ODY5IDEzLjA2MzZMMTEuNjM1NSAxNS4zNjQxQzEyLjMwMTUgMTUuNzg1NyAxMy4xMTY1IDE1LjE2MjQgMTIuOTQxMiAxNC4zNzQyTDExLjk3NzMgMTAuMDM4OUwxNS4xOTM0IDcuMTI0MzFDMTUuNzgwNSA2LjU5MjczIDE1LjQ3MzggNS41ODQ1MyAxNC43MDI2IDUuNTIwMzdaTTcuOTk4NjkgMTEuMzQ5Nkw0LjcwMzcyIDEzLjQzMDFMNS41ODAwNSA5LjUwNzMxTDIuNjcwNjMgNi44Njc2OUw2LjUwODk2IDYuNTE5NEw3Ljk5ODY5IDIuODI1NzNMOS40OTcyNiA2LjUyODU3TDEzLjMzNTYgNi44NzY4N0wxMC40MjYxIDkuNTE2NUwxMS4zMDI1IDEzLjQzOTNMNy45OTg2OSAxMS4zNDk2WiI+PC9wYXRoPjwvZz48ZGVmcz48Y2xpcFBhdGggaWQ9ImNsaXAwXzNfMiI+PHJlY3Qgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2Ij48L3JlY3Q+PC9jbGlwUGF0aD48L2RlZnM+PC9zdmc+",
                    "borderless": true
                },
                {
                    "key": "edit",
                    "icon": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2IiBmaWxsPSJjdXJyZW50Q29sb3IiIGNvbG9yPSIjMzEzMzNGIj48ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfNzMwXzMxMjMpIj48cGF0aCBkPSJNMiAxMS42Mzk3VjEzLjY2NjRDMiAxMy44NTMgMi4xNDY2NyAxMy45OTk3IDIuMzMzMzMgMTMuOTk5N0g0LjM2QzQuNDQ2NjcgMTMuOTk5NyA0LjUzMzMzIDEzLjk2NjQgNC41OTMzMyAxMy44OTk3TDExLjg3MzMgNi42MjYzOEw5LjM3MzMzIDQuMTI2MzhMMi4xIDExLjM5OTdDMi4wMzMzMyAxMS40NjY0IDIgMTEuNTQ2NCAyIDExLjYzOTdaTTEzLjgwNjcgNC42OTMwNUMxNC4wNjY3IDQuNDMzMDUgMTQuMDY2NyA0LjAxMzA1IDEzLjgwNjcgMy43NTMwNUwxMi4yNDY3IDIuMTkzMDVDMTEuOTg2NyAxLjkzMzA1IDExLjU2NjcgMS45MzMwNSAxMS4zMDY3IDIuMTkzMDVMMTAuMDg2NyAzLjQxMzA1TDEyLjU4NjcgNS45MTMwNUwxMy44MDY3IDQuNjkzMDVWNC42OTMwNVoiPjwvcGF0aD48L2c+PGRlZnM+PGNsaXBQYXRoIGlkPSJjbGlwMF83MzBfMzEyMyI+PHJlY3Qgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2IiBmaWxsPSJ3aGl0ZSI+PC9yZWN0PjwvY2xpcFBhdGg+PC9kZWZzPjwvc3ZnPg==",
                    "borderless": true
                },
                {
                    "key": "source",
                    "icon": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0iY3VycmVudENvbG9yIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGNvbG9yPSIjMzEzMzNGIj48cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTguMDA2NjIgMC4zNTAwMDZDMy41NzkxNyAwLjM1MDAwNiAwIDMuODU1NCAwIDguMTkyMDZDMCAxMS42NTg2IDIuMjkzMjkgMTQuNTkyOSA1LjQ3NDcgMTUuNjMxNUM1Ljg3MjQ2IDE1LjcwOTUgNi4wMTgxNiAxNS40NjI3IDYuMDE4MTYgMTUuMjU1MUM2LjAxODE2IDE1LjA3MzMgNi4wMDUwNSAxNC40NTAxIDYuMDA1MDUgMTMuODAwOUMzLjc3NzggMTQuMjY4MyAzLjMxMzk5IDEyLjg2NiAzLjMxMzk5IDEyLjg2NkMyLjk1NjA2IDExLjk1NzIgMi40MjU3MiAxMS43MjM2IDIuNDI1NzIgMTEuNzIzNkMxLjY5Njc0IDExLjI0MzIgMi40Nzg4MiAxMS4yNDMyIDIuNDc4ODIgMTEuMjQzMkMzLjI4NzQ0IDExLjI5NTEgMy43MTE3NSAxMi4wNDgyIDMuNzExNzUgMTIuMDQ4MkM0LjQyNzQ1IDEzLjI0MjUgNS41ODA3NCAxMi45MDUxIDYuMDQ0NzEgMTIuNjk3M0M2LjExMDkyIDEyLjE5MDkgNi4zMjMxNSAxMS44NDA0IDYuNTQ4NSAxMS42NDU3QzQuNzcyMTEgMTEuNDYzOSAyLjkwMzEyIDEwLjc4ODggMi45MDMxMiA3Ljc3NjUxQzIuOTAzMTIgNi45MTk2IDMuMjIxMDcgNi4yMTg1MiAzLjcyNDg2IDUuNjczMjdDMy42NDUzOCA1LjQ3ODU2IDMuMzY2OTMgNC42NzM0NCAzLjgwNDUxIDMuNTk1ODRDMy44MDQ1MSAzLjU5NTg0IDQuNDgwNTUgMy4zODgwNyA2LjAwNDg4IDQuNDAwODFDNi42NTc1IDQuMjI5MTUgNy4zMzA1NCA0LjE0MTgzIDguMDA2NjIgNC4xNDEwOUM4LjY4MjY2IDQuMTQxMDkgOS4zNzE4MSA0LjIzMjA3IDEwLjAwODIgNC40MDA4MUMxMS41MzI3IDMuMzg4MDcgMTIuMjA4NyAzLjU5NTg0IDEyLjIwODcgMy41OTU4NEMxMi42NDYzIDQuNjczNDQgMTIuMzY3NyA1LjQ3ODU2IDEyLjI4ODIgNS42NzMyN0MxMi44MDUzIDYuMjE4NTIgMTMuMTEwMSA2LjkxOTYgMTMuMTEwMSA3Ljc3NjUxQzEzLjExMDEgMTAuNzg4OCAxMS4yNDExIDExLjQ1MDggOS40NTE0NiAxMS42NDU3QzkuNzQzMTggMTEuODkyMyA5Ljk5NDkyIDEyLjM1OTcgOS45OTQ5MiAxMy4wOTk4QzkuOTk0OTIgMTQuMTUxNCA5Ljk4MTgxIDE0Ljk5NTQgOS45ODE4MSAxNS4yNTVDOS45ODE4MSAxNS40NjI3IDEwLjEyNzcgMTUuNzA5NSAxMC41MjUzIDE1LjYzMTZDMTMuNzA2NyAxNC41OTI4IDE2IDExLjY1ODYgMTYgOC4xOTIwNkMxNi4wMTMxIDMuODU1NCAxMi40MjA4IDAuMzUwMDA2IDguMDA2NjIgMC4zNTAwMDZaIj48L3BhdGg+PC9zdmc+",
                    "borderless": true
                }
            ],
            "stCommVersion": 1
        }
    }
    applyNavbarStyles(styles, customStyles) {
        if (!document.getElementById(`navbar-styles-${this.key}`) && this.isNavigation) {
            let style = document.createElement('style');
            style.id = `navbar-styles-${this.key}`;
            style.innerHTML = styles;
            document.head.appendChild(style);
        }

        if (document.getElementById(`navbar-styles-custom-${this.key}`)) {
            const stylesHeadNode = document.getElementById(`navbar-styles-custom-${this.key}`);
            stylesHeadNode.remove();
        }
        if (customStyles) {
            let cStyleNode = document.createElement('style');
            cStyleNode.id = `navbar-styles-custom-${this.key}`;
            cStyleNode.innerHTML = customStyles;
            document.head.appendChild(cStyleNode);
        }
    }

    setURLPath(urlPath) {
        const updateURL = (url, state, replace = false) =>
            replace
                ? window.history.replaceState(state, '', url)
                : window.history.pushState(state, '', url);

        // Eliminar las barras al principio y al final de urlPath
        let regexp = new RegExp("^/+|/+$", "g");
        const cleanedUrlPath = urlPath.replace(regexp, '');

        const fullURL = `${window.location.origin}/${cleanedUrlPath}`;

        updateURL(fullURL, {
            additionalInformation: 'Updated the URL with JS',
        });
    }

    setPages(appPages) {
        // this.appNav.hostCommunicationMgr.sendMessageToHost({
        //     type: "SET_APP_PAGES",
        //     appPages: this.appPages
        // });
        // appPages = {
        //     icon: ""
        //     isDefault: true,
        //     pageName: "app",
        //     pageScriptHash: "d965c522969fa9f32813cdbd0c58ccae",
        //     urlPathname: "app"
        // }
        const data = {
            stCommVersion: 1,
            type: "SET_APP_PAGES",
            appPages: appPages,
        }
        window.parent.postMessage(data, "*");
    }

    setCurrentPage(currentPageName, currentPageScriptHash, isDefault) {
        // this.appNav.hostCommunicationMgr.sendMessageToHost({
        //     type: "SET_CURRENT_PAGE_NAME",
        //     currentPageName: isDefault ? "" : currentPageName,
        //     currentPageScriptHash: currentPageScriptHash
        // });
        const data = {
            stCommVersion: 1,
            type: "SET_CURRENT_PAGE_NAME",
            currentPageName: isDefault ? "" : currentPageName,
            currentPageScriptHash: currentPageScriptHash
        }
        window.parent.postMessage(data, "*");
    }

    //Styles from ScrollNavigationBar.tsx
    // updateConfig(styles, disable_scroll) {
    //     this.styles = styles;
    //     this.disable_scroll = disable_scroll;
    //     console.debug('Updated config', styles, disable_scroll);
    // }

    //Scroll to the anchor with the provided anchorId and call updateActiveAnchor
    // scroll(anchorId) {
    //     const element = document.getElementById(anchorId);
    //     console.debug('Scrolling to', anchorId);
    //     if (element) {
    //         //Apply smooth or instant scrolling
    //         const behavior = this.disable_scroll ? 'instant' : 'smooth';
    //         //If anchorId isn't on page yet, set enroute flag
    //         if (!this.anchorVisibleStates[anchorId]) {
    //             this.enroute = true;
    //         }
    //         this.updateActiveAnchor(anchorId);
    //         element.scrollIntoView({ behavior , block: 'start'});
    //     }
    //     this.emphasize(anchorId);

    // }

    //Emphasize the anchor by scaling it up and down
    // emphasize(anchorId) {
    //     const element = document.getElementById(anchorId);
    //     if (element) {
    //         if (this.styles === null) {
    //             console.error('Styles have not been set');
    //             return;
    //         }

    //         const emphasisStyle = this.styles["anchorEmphasis"] || null;
    //         if (emphasisStyle === null) {
    //             console.error('emphasisStyle has not been set');
    //             return;
    //         }
    //         console.debug('Emphasizing', anchorId, emphasisStyle);

    //         //Apply each key in styles to the element
    //         for (const key in emphasisStyle) {
    //             element.style[key] = emphasisStyle[key];
    //         }
    //         console.debug('Emphasis applied', anchorId, emphasisStyle);

    //         // Remove the effect after the animation completes
    //         setTimeout(() => {
    //             //Reset scale
    //             //We need to keep element.transition to have animation
    //             element.style.transform = 'scale(1)';
    //             console.debug('Emphasis removed', anchorId);
    //         }, 600);
    //     }
    //     else {
    //         console.debug('Element does not exist for emphasis', anchorId);
    //     }
    // }

    //Update the active anchor to the provided anchorId
    // updateActiveAnchor(anchorId) {
    //     if (this.trackedAnchors.has(anchorId)) {
    //         this.activeAnchorId = anchorId;
    //         console.debug('Updated active anchor', anchorId);
    //     }
    //     else {
    //         console.error('Anchor is not being tracked', anchorId ?? 'null');
    //     }
    // }

    //Check if the current active anchor is still visible, if not find the closest visible anchor to make active
    // checkBestAnchor(){
    //     //If enroute, don't change active anchor
    //     if (this.enroute) {
    //         return;
    //     }

    //     if (this.activeAnchorId) {
    //         //Check if active anchor is visible, if not we need a new active anchor
    //         if (this.anchorVisibleStates[this.activeAnchorId]) {
    //             return;
    //         }

    //         //Search sorted anchors closest to the current active anchor for first visible
    //         let newActiveAnchorId = null;
    //         const activeAnchorIndex = this.sortedAnchors.indexOf(this.activeAnchorId);
    //         // If anchor dissapeared above screen, find the next anchor below that is visible.
    //         for (let i = activeAnchorIndex + 1; i < this.sortedAnchors.length; i++) {
    //             const anchorId = this.sortedAnchors[i];
    //             if (this.anchorVisibleStates[anchorId]) {
    //                 newActiveAnchorId = anchorId;
    //                 break;
    //             }
    //         }
    //         if (newActiveAnchorId === null) {
    //             // If anchor dissapeared below screen, find the next anchor above that is visible.
    //             for (let i = activeAnchorIndex - 1; i >= 0; i--) {
    //                 const anchorId = this.sortedAnchors[i];
    //                 if (this.anchorVisibleStates[anchorId]) {
    //                     newActiveAnchorId = anchorId;
    //                     break;
    //                 }
    //             }
    //         }

    //         //If new anchor found, update the component's active anchor
    //         if (newActiveAnchorId !== null) {
    //             this.activeAnchorId = newActiveAnchorId;
    //             this.postUpdateActiveAnchor(this.activeAnchorId);
    //         }
    //     }
    // }

    // postUpdateActiveAnchor(anchor_id) {
    //     this.postMessage(
    //         'updateActiveAnchor',
    //         {anchor_id, update_id: this.updateId++}
    //     );
    // }

    postSidebarState() {
        // Investigar si el estado de la barra se puede mantener en algun sitio sin que se elimine, sobre todo en navegacion mutiple
        const isSideOpen = document.body.classList.contains("side-nav-open");
        const pageId = document.body.dataset.pageId;
        const expandSubMenu = document.body.dataset.expandSubMenu;
        const selectedSubMenu = document.body.dataset.selectedSubMenu;
        this.postComponentMessage(
            'sidebarResponseInfo',
            {
                'isSideOpen': isSideOpen,
                'pageId': pageId,
                'expandSubMenu': expandSubMenu,
                'selectedSubMenu': selectedSubMenu
            }
        );
    }

    setVisualPageId(pageId) {
        this.postComponentMessage(
            'setVisualPageId',
            {'pageId': pageId}
        );
    }

    //Send a message to the component
    postComponentMessage(COMPONENT_method, data = { anchor_id = null, update_id = null} = {}) {
        if (this.component === null) {
            console.error('Component has not been registered');
            return;
        }
        this.component.postMessage({ COMPONENT_method: COMPONENT_method, key: this.key, ...data}, '*');
    }


    // observer = new IntersectionObserver((entries) => {
    //     entries.forEach(entry => {
    //         const anchorId = entry.target.id;
    //         if (entry.isIntersecting) {
    //             this.anchorVisibleStates[anchorId] = true;
    //             if (this.activeAnchorId === anchorId) {
    //                 this.enroute = false;
    //             }
    //         } else {
    //             this.anchorVisibleStates[anchorId] = false;
    //             // Rerun checkBestAnchor if the active anchor is no longer visible
    //             if (this.activeAnchorId === anchorId) {
    //                 //run checkBestAnchor after 0ms to ensure anchors update
    //                 setTimeout(() => {
    //                     this.checkBestAnchor();
    //                 },0);

    //             }
    //         }
    //     });
    // }, { threshold: [0,1] });

    //Start tracking anchors for visibility
    // trackAnchors(anchor_ids) {
    //     for (const anchorId of anchor_ids) {
    //         if (this.trackedAnchors.has(anchorId)) {
    //             console.debug('Anchor is already being tracked', anchorId);
    //             return;
    //         }

    //         const anchor = document.getElementById(anchorId);

    //         if (!anchor) {
    //             console.error('Anchor does not exist', anchorId);
    //             return
    //         }
    //         this.trackedAnchors.add(anchorId);

    //         //Insert anchor into sortedAnchors based on its position in the document
    //         let inserted = false;
    //         for (let i = 0; i < this.sortedAnchors.length; i++) {
    //             const currentAnchor = document.getElementById(this.sortedAnchors[i]);
    //             if (anchor.compareDocumentPosition(currentAnchor) & Node.DOCUMENT_POSITION_FOLLOWING) {
    //                 this.sortedAnchors.splice(i, 0, anchorId);
    //                 inserted = true;
    //                 break;
    //             }
    //         }
    //         if (!inserted) {
    //             this.sortedAnchors.push(anchorId);
    //         }
    //         this.sortedAnchors.push(anchorId);

    //         this.observer.observe(anchor);
    //         console.debug('Started tracking anchor', anchorId);
    //     }
    // }

    //Handle messages from the component

    handleComponentMessage(event) {
        const { COI_method, key} = event.data;

        //Check if message is intended for COI
        if (!COI_method || !key) {
            return;
        }
        //Check if message is intended for this COI instance
        if (key !== this.key) {
            return;
        }
        // console.debug("COI with key", key, "received message", event.data);

        //If component is not registered, only allow registration method
        if (this.component === null) {
            if (COI_method === 'register') {
                const { positionMode, isExpanded, themeData } = event.data;
                this.register(event.source, positionMode, isExpanded, themeData);
                return;
            }
            else {
                console.error('Must register component with this NavbarCOI before calling other methods', event.data);
            }
        }
        switch (COI_method) {
            case 'register':
                // Se actualiza el componente para poder comunicar mensajes si se desmonta
                this.component = event.source;
                // console.debug('Register can only be called once per key.');
                // Si el componente se desmonta y se intenta registrar se pasa
                //  la pagina que deberia tener el componente
                this.setVisualPageId(this.pageId);
                break;
            // case 'updateConfig':
            //     const {styles, disable_scroll} = event.data;
            //     this.updateConfig(styles, disable_scroll);
            //     break;
            // case 'scroll':
            //     const { anchor_id: scrollAnchorId } = event.data;
            //     this.scroll(scrollAnchorId);
            //     break;
            // case 'trackAnchors':
            //     const { anchor_ids } = event.data;
            //     this.trackAnchors(anchor_ids);
            //     break;
            // case 'updateActiveAnchor':
            //     const { anchor_id: updateAnchorId } = event.data;
            //     this.updateActiveAnchor(updateAnchorId);
            case 'setPages':
                // TODO: Enviar desde el componente las paginas (para evitar usar el st.navigation)
                let { appPages } = event.data;
                this.setPages(appPages);
                break;
            case 'themeToggle':
                let { themeData } = event.data;
                this.themeToggle(themeData);
                break;
            case 'sidebarRequestInfo':
                if (this.isNavigation) this.postSidebarState();
                break;
            case 'sidebarToggle':
                let { positionMode, isExpanded } = event.data;
                if (this.isNavigation) this.sidebarToggle(positionMode, isExpanded);
                break;
            case 'navbarState':
                let { pageId, expandSubMenu, selectedSubMenu } = event.data;
                this.pageId = pageId;
                if (this.isNavigation) this.setNavState(pageId, expandSubMenu, selectedSubMenu);
                break;
            case 'iframeState':
                let { iframePositionMode, isSticky, iframeHeight } = event.data;
                this.init(iframePositionMode, isSticky, iframeHeight);
                break;
            case 'setStyles':
                let { styles, customStyles } = event.data;
                this.applyNavbarStyles(styles, customStyles);
                break;
            case 'setCurrentPage':
                let { currentPageName, currentPageScriptHash, isDefault } = event.data;
                if (this.isNavigation) this.setCurrentPage(currentPageName, currentPageScriptHash, isDefault);
                break;
            default:
                console.error('Unknown method', COI_method);
        }
    }
}
function instantiateNavbarCOI(componentName, key, isNavigation, defaultPageId, positionMode, isSticky) {
    return new NavbarCOI(componentName, key, isNavigation, defaultPageId, positionMode, isSticky);
}