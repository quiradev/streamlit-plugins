//Source for CrossOriginInterface class.
//Build with terser:
//  npx terser CrossOriginInterface.js --compress --mangle 'pure_funcs=["console.debug"]' --output ../build/CrossOriginInterface.min.js
class CrossOriginInterface {
    static instances = {};
    constructor(componentName, key, isNavigation, defaultPageId, positionMode, isSticky) {
        if (CrossOriginInterface.instances[key]) {
            console.debug('CrossOriginInterface instance already exists with key', key);
            let that = CrossOriginInterface.instances[key];
            console.info("Changing", positionMode, isSticky);
            that.init(positionMode, isSticky);
            return that;
        }
        CrossOriginInterface.instances[key] = this;
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
        this.init(positionMode, isSticky);
        this.pageId = defaultPageId;

        window.addEventListener("message", this.handleComponentMessage.bind(this));
    }

    init(positionMode, isSticky) {
        this.iframeSelector = 'div.st-key-'+this.key+' > iframe[title="' + this.componentName + '"]';
        this.positionMode = positionMode;
        this.isSticky = isSticky;
        // this.setIframeState();
        this.isExpanded = document.body.classList.contains("side-nav-open");

        if (this.isNavigation) {
            this.setNavState(
                this.pageId,
                document.body.dataset.expandSubMenu || false,
                document.body.dataset.selectedSubMenu || null
            );
            document.body.dataset.navPosition = positionMode;
            document.body.dataset.navIsSticky = isSticky;
            // Add css property to body to set the width of the sidebar
            document.body.style.setProperty('--sidebar-width', '150px');
        }

        // Se crea el expander al lado del iframeSelector
        if (positionMode === "side") {
            let expander = document.getElementById('expander-' + this.key);
            if (!expander) {
                let expander = document.createElement('span');
                expander.id = 'expander-' + this.key;
                let isBeingExpanding = false;
                let mouseClickX = null;
                expander.addEventListener('mousedown', (event) => {
                    isBeingExpanding = true;
                    expander.classList.add('expander-active');
                    mouseClickX = event.clientX;
                    const mouseUpHandler = () => {
                        isBeingExpanding = false;
                        expander.classList.remove('expander-active');
                        document.body.removeEventListener('mouseup', mouseUpHandler);
                        document.body.removeEventListener('mousemove', mouseMoveHandler);
                    };
                    const mouseMoveHandler = (event) => {
                        if (isBeingExpanding) {
                            let distX = event.clientX - mouseClickX;
                            mouseClickX = event.clientX;
                            let actualSideWidth = parseInt(document.body.style.getPropertyValue('--sidebar-width'));
                            document.body.style.setProperty('--sidebar-width', Math.max(150, Math.min(300, actualSideWidth + distX)) + 'px');
                        }
                    }
                    // Quiero eliminar el listener una vez que se suelte el mouse
                    document.body.addEventListener('mouseup', mouseUpHandler);
                    document.body.addEventListener('mousemove', mouseMoveHandler);
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
                console.error('Must register component with this CrossOriginInterface before calling other methods', event.data);
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
                let { iframePositionMode, isSticky } = event.data;
                this.init(iframePositionMode, isSticky);
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
function instantiateCrossOriginInterface(componentName, key, isNavigation, defaultPageId, positionMode, isSticky) {
    return new CrossOriginInterface(componentName, key, isNavigation, defaultPageId, positionMode, isSticky);
}