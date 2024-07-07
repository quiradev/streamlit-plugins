import datetime
import json
import os.path
from dataclasses import dataclass
from enum import Enum
from typing import List

import streamlit as st
# from .. import STLabelStudioNER, LSTaskNER, ResultLSNER, st_labelstudio, LabelStudioUser
# from streamlit_labelstudio import st_labelstudio

from streamlit_plugins.components.label_studio import STLabelStudioNER, LSTaskNER, ResultLSNER, st_labelstudio, LabelStudioUser
# make it look nice from the start
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')


class TaskState(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


if __name__ == '__main__':
    with open("data.json", "r", encoding="utf8") as reader:
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
        with open("data.json", "w", encoding="utf8") as writer:
            if next_task:
                task_id += 1
            if prev_task:
                task_id -= 1

            data["actual_task"] = task_id
            writer.write(json.dumps(data, indent=2))

    labels = ['PER', 'ORG', 'NAME', 'SURNAME']

    st.header("Label Studio")

    st_label_ner = STLabelStudioNER(task, labels)

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
