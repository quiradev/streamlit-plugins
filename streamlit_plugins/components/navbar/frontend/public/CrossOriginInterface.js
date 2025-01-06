//Source for CrossOriginInterface class.
//Build with terser:
//  npx terser CrossOriginInterface.js --compress --mangle 'pure_funcs=["console.debug"]' --output ../build/CrossOriginInterface.min.js
class CrossOriginInterface {
    static instances = {};
    constructor(key) {
        if (CrossOriginInterface.instances[key]) {
            console.info('CrossOriginInterface instance already exists with key', key);
            return CrossOriginInterface.instances[key];
        }

        CrossOriginInterface.instances[key] = this;
        // this.sortedAnchors = [];
        // this.trackedAnchors = new Set();
        // this.anchorVisibleStates = {};
        // this.activeAnchorId = null;
        this.component = null;
        // this.autoUpdateAnchor = false;
        this.key = key;
        // this.styles = null;
        // this.disable_scroll = false;
        // this.updateId = 0
        // this.enroute = false;
        this.navState = "nav-open";
        window.addEventListener("message", this.handleMessage.bind(this));
    }

    register(component, navState)     {
        this.component = component;
        this.navState = navState;
        // this.autoUpdateAnchor = autoUpdateAnchor;
        // this.emphasisStyle = emphasisStyle;
        console.debug('Registered component for key ', this.key, ": ", component, navState);
    }

    // Toggle left margin of streamlit application
    sidebarToggle(navState) {
        // Agrega a la clase del body la clase nav-open
        if (navState == "nav-open") {
            document.body.classList.toggle(navState);
            console.debug('Toggled navState to', navState);
        }
        else {
            document.body.classList.remove("nav-open");
            console.debug('Removed navState to', navState);
        }
    }

    themeToggle(theme_data, themeName="Custom") {
        // Se lanza un post message a la ventana principal con el tema seleccionado
        // El evento tiene un data con este formato
        // {"stCommVersion":1,"type":"SET_THEME_CONFIG","themeInfo":{"primaryColor":"#ff4b4b","backgroundColor":"#0e1117","secondaryBackgroundColor":"#262730","textColor":"#fafafa","base":"dark","font":"\"Source Sans Pro\", sans-serif","linkText":"hsla(209, 100%, 59%, 1)","fadedText05":"rgba(250, 250, 250, 0.1)","fadedText10":"rgba(250, 250, 250, 0.2)","fadedText20":"rgba(250, 250, 250, 0.3)","fadedText40":"rgba(250, 250, 250, 0.4)","fadedText60":"rgba(250, 250, 250, 0.6)","bgMix":"rgba(26, 28, 36, 1)","darkenedBgMix100":"hsla(228, 16%, 72%, 1)","darkenedBgMix25":"rgba(172, 177, 195, 0.25)","darkenedBgMix15":"rgba(172, 177, 195, 0.15)","lightenedBg05":"hsla(220, 24%, 10%, 1)"}}

        // Se crea el data
        const data = {
            stCommVersion: 1,
            type: "SET_CUSTOM_THEME_CONFIG",
            // type: "SET_THEME_CONFIG", // No funciona solo si el origen es el mismo Streamlit
            themeInfo: theme_data.themeInfo,
            themeName: theme_data.name || themeName
        }
        let themeInput = {
            "name": themeName,
            "themeInput": theme_data.themeInfo
        };
        // Se guarda en el Local Storage el tema seleccionado
        // con clave stActiveTheme-/-v1 y valor theme
        localStorage.setItem('stActiveTheme-/-v1', JSON.stringify(themeInput));
        // Se comunica con el padre
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

    //Send a message to the component
    postMessage(COMPONENT_method, data = { anchor_id = null, update_id = null} = {}) {
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
    handleMessage(event) {
        const { COI_method, key} = event.data;

        //Check if message is intended for COI
        if (!COI_method || !key) {
            return;
        }
        //Check if message is intended for this COI instance
        if (key !== this.key) {
            return;
        }
        console.debug("COI with key", key, "received message", event.data);

        //If component is not registered, only allow registration method
        if (this.component === null) {
            if (COI_method === 'register') {
                const {navState} = event.data;
                this.register(event.source, navState);
            }
            else {
                console.error('Must register component with this CrossOriginInterface before calling other methods', event.data);
            }
        }

        switch (COI_method) {
            case 'register':
                console.debug('Register can only be called once per key.');
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
            case 'themeToggle':
                const { theme_data } = event.data;
                this.themeToggle(theme_data);
                break;
            
            case 'sidebarToggle':
                const { navState } = event.data;
                this.sidebarToggle(navState);
                break;

            break;
                default:
                console.error('Unknown method', COI_method);
        }
    }
}
function instantiateCrossOriginInterface(key) {
    return new CrossOriginInterface(key);
}