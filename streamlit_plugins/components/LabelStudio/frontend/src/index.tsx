import { Streamlit, RenderData } from "streamlit-component-lib"
import LabelStudio from "@heartexlabs/label-studio"
import '@heartexlabs/label-studio/build/static/css/main.css';

const span = document.body.appendChild(document.createElement("span"))
const ls_div = span.appendChild(document.createElement("div"))
ls_div.setAttribute("id", "label-studio");

let labelStudio: any

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event: Event): void {
  if (labelStudio) {
    console.debug("Already rendered")
    Streamlit.setFrameHeight();
    return
  }

  const data = (event as CustomEvent<RenderData>).detail
  const { config, interfaces, user, task } = data.args
  // config: data.args["config"],
  // interfaces: data.args["interfaces"][0],
  // user: data.args["user"][0],
  // task: data.args["task"],

  labelStudio = new LabelStudio("label-studio", {config, interfaces, user, task});
  labelStudio.on("labelStudioLoad", (LS: any) => {
    console.debug("loaded");
    // var c = LS.annotationStore.addAnnotation({
    //   userGenerate: true
    // });
    // LS.annotationStore.selectAnnotation(c.id);
    Streamlit.setFrameHeight();
  });

  labelStudio.on("submitAnnotation", (LS: any, annotation: Record<string, any>) => {
    console.debug("submitted");
    //annotation = JSON.parse(JSON.stringify(annotation));
    Streamlit.setComponentValue(annotation.serializeAnnotation());
    Streamlit.setFrameHeight();
  });

  labelStudio.on("updateAnnotation", (LS: any, annotation: Record<string, any>) => {
    console.debug("updated")
    annotation = JSON.parse(JSON.stringify(annotation));
    Streamlit.setComponentValue(annotation);
   // We tell Streamlit to update our frameHeight after each update event, in case
   // it has changed. (This isn't strictly necessary if the results sidebar is not
   // rendered because the component height stays fixed. But this is a low-cost
   // function, so there's no harm in doing it redundantly.)
    Streamlit.setFrameHeight();
  });

  labelStudio.on("deleteAnnotation", (LS: any, annotation: Record<string, any>) => {
    console.debug("deleted");
    annotation = JSON.parse(JSON.stringify(annotation));
    Streamlit.setComponentValue(annotation);
    Streamlit.setFrameHeight();
  });

  // labelStudio.on('event', callback);
  // Finally, tell Streamlit to update our initial height. We omit the
  // `height` parameter here to have it default to our scrollHeight.
  setTimeout(() => Streamlit.setFrameHeight(), 500);
}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()
Streamlit.setFrameHeight();

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
// function onRender(event: Event): void {
//   const data = (event as CustomEvent<RenderData>).detail;
//
//   var labelStudio = new LabelStudio('label-studio', {
//     config: data.args["config"],
//     interfaces: data.args["interfaces"][0],
//     user: data.args["user"][0],
//     task: data.args["task"],
//
//     onLabelStudioLoad: function(LS) {
//       const c = LS.completionStore.addCompletion({
//         userGenerate: true
//       });
//       LS.completionStore.selectCompletion(c.id);
//     },
//
//     onSubmitCompletion: function(LS, completion) {
//       // console.log(LS)
//       completion = JSON.parse(JSON.stringify(completion));
//       Streamlit.setComponentValue(completion);
//     },
//
//
//   });
//
//   // We tell Streamlit to update our frameHeight after each render event, in
//   // case it has changed. (This isn't strictly necessary for the example
//   // because our height stays fixed, but this is a low-cost function, so
//   // there's no harm in doing it redundantly.)
//   Streamlit.setFrameHeight();
// }
//
//
// // Attach our `onRender` handler to Streamlit's render event.
// Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
// // Tell Streamlit we're ready to start receiving data. We won't get our
// // first RENDER_EVENT until we call this function.
// Streamlit.setComponentReady();
//
// // Finally, tell Streamlit to update our initial height. We omit the
// // `height` parameter here to have it default to our scrollHeight.
// Streamlit.setFrameHeight();
