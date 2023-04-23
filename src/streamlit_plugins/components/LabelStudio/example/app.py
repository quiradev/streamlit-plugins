import datetime
import json
import os.path
from dataclasses import dataclass
from enum import Enum
from typing import List

import streamlit as st
# from .. import STLabelStudioNER, LSTaskNER, ResultLSNER, st_labelstudio, LabelStudioUser
from components.LabelStudio import STLabelStudioNER, LSTaskNER, ResultLSNER, st_labelstudio, LabelStudioUser
# from streamlit_labelstudio import st_labelstudio

# make it look nice from the start
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')



class TaskState(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


if __name__ == '__main__':
    with open("data.json", "r") as reader:
        data = json.load(reader)
        task_id = data.get("task_id", 1)
        task = [
            LSTaskNER(
                id=task.get("id"),
                text=task.get("text"),
                annotations=[
                    ResultLSNER(
                        start=ann.get("start"),
                        end=ann.get("end"),
                        text=ann.get("text"),
                        labels=ann.get("labels")
                    )
                    for ann in task.get("annotations", [])
                ],
                predictions=[]
            )
            for task in data.get("tasks", [])
            if (
                task.get("state") == TaskState.PENDING.value and
                task.get("id") == task_id
            )
        ]
        if task:
            task = task[0]

        else:
            st.write("No pending task")

    col1, col2 = st.columns(2)
    prev_task = col1.button(label="<-")
    next_task = col2.button(label="->")

    if next_task or prev_task:
        with open("data.json", "w") as writer:
            if next_task:
                task_id += 1
            if prev_task:
                task_id -= 1

            data["actual_task"] = task_id
            writer.write(json.dumps(data, indent=2))

    labels = ['PER', 'ORG', 'NAME', 'SURNAME']
    interfaces = [
        "panel",  # Enable navigaion panel for the current task with buttons: undo, redo and reset.
        "submit",  # Show a button to submit or update the current annotation.
        "update",  # Show a button to update the current task after submitting.
        "skip",  # Show a button to skip the current task.
        "controls"  # Enable panel with controls (submit, update, skip).
        "infobar",  # A show button for information.
        "topbar",  # A labeling interface that lists the top-level items in the Label Studio UI.
        "instruction",  # A button for the instructions.
        "side-column",  # Show a column on the left or right side of the Label Studio UI.
        "annotations:history",  # A show button for annotation history.
        "annotations:tabs",  # A show button for annotation tabs.
        "annotations:menu",  # A show button for the annotation menu.
        "annotations:current",  # A show button for the current annotation.
        "annotations:add-new",  # A show button to add new annotations.
        "annotations:delete",  # A show button to delete the current annotation.
        "annotations:view-all",  # A show button to view all annotations.
        "predictions:tabs",  # Show predictions tabs.
        "predictions:menu",  # Show predictions menu.
        "auto-annotation",  # Show auto annotations.
        "edit-history"  # Show edit history.
    ]
    user = {
        'pk': 1,
        'firstName': "James",
        'lastName': "Dean"
    }
    st.header("Label Studio")
    config_img = """
                      <View>
                        <View style="padding: 25px; box-shadow: 2px 2px 8px #AAA;">
                          <Image name="img" value="$image" width="100%" maxWidth="100%" brightnessControl="true" contrastControl="true" zoomControl="true" rotateControl="true"></Image>
                        </View>
                        <RectangleLabels name="tag" toName="img">
                          <Label value="Hello"></Label>
                          <Label value="Moon"></Label>
                        </RectangleLabels>
                      </View>
                    """
    config_txt = """
                    <View>
                      <Labels name="label" toName="text">
                        <Label value="PER" background="red"/>
                        <Label value="ORG" background="darkorange"/>
                        <Label value="LOC" background="orange"/>
                        <Label value="MISC" background="green"/>
                      </Labels>
                      <Text name="text" value="$text"/>
                    </View>
                """

    interfaces = [
        "panel",  # Enable navigaion panel for the current task with buttons: undo, redo and reset.
        "submit",  # Show a button to submit or update the current annotation.
        "update",  # Show a button to update the current task after submitting.
        "skip",  # Show a button to skip the current task.
        "controls"  # Enable panel with controls (submit, update, skip).
        "infobar",  # A show button for information.
        "topbar",  # A labeling interface that lists the top-level items in the Label Studio UI.
        "instruction",  # A button for the instructions.
        "side-column",  # Show a column on the left or right side of the Label Studio UI.
        "annotations:history",  # A show button for annotation history.
        "annotations:tabs",  # A show button for annotation tabs.
        "annotations:menu",  # A show button for the annotation menu.
        "annotations:current",  # A show button for the current annotation.
        "annotations:add-new",  # A show button to add new annotations.
        "annotations:delete",  # A show button to delete the current annotation.
        "annotations:view-all",  # A show button to view all annotations.
        "predictions:tabs",  # Show predictions tabs.
        "predictions:menu",  # Show predictions menu.
        "auto-annotation",  # Show auto annotations.
        "edit-history"  # Show edit history.
    ]

    st_label_ner = STLabelStudioNER(task, ['PER', 'ORG', 'NAME', 'SURNAME'])

    results = {}
    res = st_label_ner.run_task(task)

    if res:
        st.write(res)
        # Actualizar la tarea del fichero json
        # with open("tasks.json", "w") as writer

    # if results is not None:
    #     areas = [v for k, v in results['areas'].items()]
    #
    #     results = []
    #     for a in areas:
    #         results.append({
    #             'id': a['id'],
    #             'x': a['x'], 'y': a['y'],
    #             'width': a['width'], 'height': a['height'],
    #             'label': a['results'][0]['value']['rectanglelabels'][0]
    #         })
    #
    #     st.table(results)
