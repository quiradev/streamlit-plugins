import streamlit as st

from streamlit_plugins.components.navbar import get_pages_info, st_switch_page, st_which_page

st.title("Dashboard")
st.subheader("Welcome to the dashboard!")

(
    pages_map,
    default_page_id,
    menu_pages, menu_account_pages,
    login_page_id, logout_page_id, account_page_id, settings_page_id
) = get_pages_info()

def distribute_sections(sections, max_columns=3):
    grid = []
    current_row = []
    available_space = max_columns
    section_details = {}
    
    for section in sections:
        if section.get("is_page", False):
            num_elements = 1
            elements = [section]
        else:
            num_elements = len(section["submenu"])
            elements = section["submenu"]
        
        rows_needed = (num_elements + max_columns - 1) // max_columns  # Calculate how many rows it occupies
        columns_used = min(num_elements, max_columns)
        
        section_details[section["id"]] = {
            "rows": rows_needed,
            "columns": columns_used
        }
        
        element_index = 0
        internal_grid = []

        if available_space < num_elements and current_row:
            grid.append(current_row)
            current_row = []
            available_space = max_columns

        for _ in range(rows_needed):
            if available_space < num_elements and current_row:
                if len(elements) > max_columns:
                    internal_grid.append(current_row)
                else:
                    grid.append(current_row)
                
                current_row = []
                available_space = max_columns
            
            row_elements = elements[element_index:element_index + max_columns]
            current_row.append((section["id"], section["label"], len(row_elements), row_elements))
            available_space -= len(row_elements)
            element_index += max_columns
            num_elements -= len(row_elements)
        
        if available_space == 0 and current_row:
            if len(elements) > max_columns:
                internal_grid.append(current_row)
            else:
                grid.append(current_row)
            current_row = []
            available_space = max_columns
        
        if len(elements) > max_columns and internal_grid:
            if current_row:
                internal_grid.append(current_row)
                current_row = []
                available_space = max_columns
            grid.append(internal_grid)
    
    if current_row:
        grid.append(current_row)
    
    return grid, section_details



element_per_row = 3
# rows = []
# grid_elements = []
# space_left_in_row = element_per_row
# items = []
# is_new_section = True
# for section_info in menu_pages:
    # section_name = section_info["label"]
    # section_container = st.container()
    # with section_container:
    #     st.markdown(f"## {section_name}")
        
    #     if not section_info.get("is_page", False):
    #         section_size = len(section_info.get("submenu", []))
    #         if section_size > space_left_in_row:
    #             rows.append(st.columns(element_per_row))
    #             grid_elements.append(items)
    #             space_left_in_row = element_per_row
    #             items = []
            
    #         for page_info in section_info.get("submenu", []):
    #             if page_info.get("is_page", False):
    #                 items.append(page_info)
    #                 space_left_in_row -= 1
    #                 if space_left_in_row == 0:
    #                     rows.append(st.columns(element_per_row, border=True))
    #                     grid_elements.append(items)
    #                     space_left_in_row = element_per_row
    #                     items = []
    #     else:
    #         if len(rows) == 0:
    #             rows.append(st.columns(element_per_row, border=True))
            
    #         items = [section_info]
    #         space_left_in_row -= 1
    #         rows[-1][element_per_row-space_left_in_row-1].markdown(f"## {section_name}")

    #         if space_left_in_row == 0:
    #             rows.append(st.columns(element_per_row, border=True))
    #             grid_elements.append(items)
    #             space_left_in_row = element_per_row
    #             items = []

    # if items:
    #     grid_elements.append(items)

organized_sections, sections_layout = distribute_sections(menu_pages, max_columns=element_per_row)

# for cols, elements in zip(rows, grid_elements):
for i, internal_content in enumerate(organized_sections):
    # print(f"Fila {i+1}:", [(s["id"], num) for s, num, elements in row])
    # Extraer la distribucion de la fila
    internal_rows = [internal_content]
    container = st.empty()
    multiple_rows = False
    if isinstance(internal_content[0], list):
        multiple_rows = True
        container = container.container(border=True)
        internal_rows = internal_content
        with container:
            st.write(f"## Seccion {internal_rows[0][0][1]}")
    
    for row in internal_rows:
        cols_distribution = []
        if multiple_rows:
            # Aqui unicamente salen las
            with container:
                for page_col in row:
                    cols = st.columns([1/element_per_row for _ in range(element_per_row)])
                    s_id, s_name, num_columns, pages_info = page_col
                    for i_col, page_info in enumerate(pages_info):
                        if page_info.get("is_page", False):
                            col = cols[i_col]
                            with col:
                                st.subheader(page_info["label"])
                                is_actual_page = st_which_page() == page_info["id"]
                                if st.button(page_info['label'], disabled=is_actual_page):
                                    st_switch_page(page_info["id"])
                        else:
                            col = st.columns(num_columns)[0]
                            with col:
                                st.markdown(f"## {page_info['label']}")
                                is_actual_page = st_which_page() == page_info["id"]
                                if st.button(page_info['label'], disabled=is_actual_page):
                                    st_switch_page(page_info["id"])
        else:
            cols_distribution = [row[i][2]/element_per_row for i in range(element_per_row) if i < len(row)]
            if len(cols_distribution) < element_per_row:
                cols_distribution.append((element_per_row-len(cols_distribution))/element_per_row)
            
            cols = st.columns(cols_distribution)
            i_col = 0
            for section_layout in row:
                s_id, s_name, num_columns, pages_info = section_layout
                for page_info in pages_info:
                    if page_info.get("is_page", False):
                        col = cols[i_col]
                        with col:
                            with st.container(border=True):
                                st.write(f"## Seccion {s_name}")
                                st.subheader(page_info["label"])
                                is_actual_page = st_which_page() == page_info["id"]
                                if st.button(page_info['label'], disabled=is_actual_page):
                                    st_switch_page(page_info["id"])
                    else:
                        col = st.columns(num_columns)[0]
                        with col:
                            with st.container(border=True):
                                st.write(f"## Seccion {s_name}")
                                st.markdown(f"## {page_info['label']}")
                                is_actual_page = st_which_page() == page_info["id"]
                                if st.button(page_info['label'], disabled=is_actual_page):
                                    st_switch_page(page_info["id"])

                i_col += num_columns

