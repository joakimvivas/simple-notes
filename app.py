import re
import flet as ft
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to add a note with error handling
def add_note(content, tags):
    try:
        supabase.table("notes").insert({
            "content": content,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Error adding note: {e}")
        return False

# Function to update a note with error handling
def update_note(note_id, new_content, new_tags):
    try:
        supabase.table("notes").update({
            "content": new_content,
            "tags": new_tags,
            "updated_at": datetime.now().isoformat()
        }).eq("id", note_id).execute()
        return True
    except Exception as e:
        print(f"Error updating note: {e}")
        return False

# Function to delete a note with error handling
def delete_note(note_id):
    try:
        supabase.table("notes").delete().eq("id", note_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting note: {e}")
        return False

# Function to convert Markdown links into clickable elements
def render_markdown_links(content):
    # Regular expression to detect Markdown links
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    parts = []
    last_end = 0

    for match in link_pattern.finditer(content):
        # Text before the link
        parts.append(ft.Text(content[last_end:match.start()]))
        # Link text (clickable)
        parts.append(ft.Text(
            match.group(1),
            color=ft.colors.BLUE,
            style=ft.TextStyle(underline=True),
            on_click=lambda e, url=match.group(2): open_url(url),
        ))
        last_end = match.end()

    # Text after the last link
    parts.append(ft.Text(content[last_end:]))
    return parts

# Function to open a URL
def open_url(url):
    import webbrowser
    webbrowser.open(url)

def main(page: ft.Page):
    page.title = "Notes Application"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START

    # App bar
    app_bar = ft.AppBar(
        title=ft.Text("Notes App", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE_700,
    )

    # Search bar
    search_box = ft.TextField(
        label="Search notes",
        width=300,
        border=ft.Border(left=1, top=1, right=1, bottom=1),
        border_color=ft.Colors.GREY_300,
    )
    search_button = ft.ElevatedButton(
        "Search",
        icon=ft.Icons.SEARCH,
        on_click=lambda e: update_notes_list(notes_list, search_box.value),
        bgcolor=ft.Colors.BLUE_500,
        color=ft.Colors.WHITE
    )
    search_box_container = ft.Container(
        content=ft.Row(
            controls=[search_box, search_button],
            spacing=10
        ),
        padding=10,
        margin=10
    )

    # Big TextField without border
    content_input = ft.TextField(
        label="Content (Markdown accepted)",
        multiline=True,
        border=ft.InputBorder.NONE,  # Remove the visible border
        expand=True                  # Fill all space in the container
    )

    # Card that encloses the TextField
    content_card = ft.Card(
        elevation=3,
        content=ft.Container(
            width=520,
            height=220,
            padding=10,  # Space around the TextField
            content=content_input
        ),
    )

    # Tags input and Add button
    tags_input = ft.TextField(
        label="Tags (comma separated)",
        width=200,
        border=ft.Border(left=1, top=1, right=1, bottom=1),
        border_color=ft.Colors.GREY_300,
    )

    add_button = ft.ElevatedButton(
        "Add Note",
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE_500,
        color=ft.Colors.WHITE
    )

    # Function to add a new note
    def add_new_note(content_widget, tags_widget, notes_column):
        content_val = content_widget.value
        tags_val = tags_widget.value
        tags_list = [tag.strip() for tag in tags_val.split(",")] if tags_val else []
        if add_note(content_val, tags_list):
            content_widget.value = ""
            tags_widget.value = ""
            update_notes_list(notes_column)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Failed to add note. Please try again."))
            page.snack_bar.open = True
            page.update()

    add_button.on_click = lambda e: add_new_note(content_input, tags_input, notes_list)

    # Two rows: first row with the content card, second row with tags and button
    create_note_form = ft.Column(
        controls=[
            ft.Row(
                controls=[content_card],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row(
                controls=[tags_input, add_button],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
        ],
        spacing=20
    )

    # Notes list
    notes_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    # Function to load more notes (pagination)
    load_more_button = ft.ElevatedButton(
        "Load More",
        on_click=lambda e: update_notes_list(notes_list, search_box.value, offset=len(notes_list.controls)),
        bgcolor=ft.Colors.BLUE_500,
        color=ft.Colors.WHITE
    )

    # Function to update the notes list with pagination
    def update_notes_list(notes_column, query="", offset=0, limit=10):
        notes_column.controls.clear()
        if query.strip() == "":
            response = supabase.table("notes").select("*").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            notes = response.data
        else:
            response = supabase.table("notes").select("*").order("created_at", desc=True).execute()
            notes = response.data
            query_lower = query.lower()
            notes = [
                note for note in notes
                if (query_lower in note.get("content", "").lower())
                or any(query_lower in tag.lower() for tag in (note.get("tags") or []))
            ]
        for note in notes:
            notes_column.controls.append(create_note_card(note))
        page.update()

    # Function to create a note card
    def create_note_card(note):
        def view_note_details(e):
            view_dialog = ft.AlertDialog(
                title=ft.Text("Note Details"),
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Markdown(note["content"]),
                            ft.Text(f"Tags: {', '.join(note['tags']) if note.get('tags') else 'No tags'}"),
                        ],
                        spacing=10,
                    ),
                    width=600,
                ),
                actions=[ft.TextButton("Close", on_click=lambda e: close_dialog(view_dialog))]
            )
            page.dialog = view_dialog
            page.add(view_dialog)
            view_dialog.open = True
            page.update()

        def edit_note(e):
            content_edit = ft.TextField(
                label="Edit Content (Markdown accepted)",
                multiline=True,
                width=400,
                height=300,
                value=note["content"],
                border=ft.Border(left=1, top=1, right=1, bottom=1),
                border_color=ft.Colors.GREY_300,
            )
            tags_edit = ft.TextField(
                label="Edit Tags (comma separated)",
                width=400,
                height=50,
                value=",".join(note.get("tags") or []),
                border=ft.Border(left=1, top=1, right=1, bottom=1),
                border_color=ft.Colors.GREY_300,
            )
            edit_dialog = ft.AlertDialog(
                title=ft.Text("Edit Note"),
                content=ft.Column(
                    controls=[
                        content_edit,
                        tags_edit,
                    ],
                    spacing=10,
                ),
                actions=[
                    ft.TextButton("Save", on_click=lambda e: save_edit(note["id"], content_edit.value, tags_edit.value, edit_dialog)),
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(edit_dialog)),
                ]
            )
            page.dialog = edit_dialog
            page.add(edit_dialog)
            edit_dialog.open = True
            page.update()

        def save_edit(note_id, new_content, new_tags_str, dialog):
            new_tags = [tag.strip() for tag in new_tags_str.split(",")] if new_tags_str else []
            if update_note(note_id, new_content, new_tags):
                close_dialog(dialog)
                update_notes_list(notes_list)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Failed to update note. Please try again."))
                page.snack_bar.open = True
                page.update()

        def delete_note_action(e):
            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Confirm Delete"),
                content=ft.Text("Are you sure you want to delete this note?"),
                actions=[
                    ft.TextButton("Yes", on_click=lambda e: confirm_delete(note["id"], confirm_dialog)),
                    ft.TextButton("No", on_click=lambda e: close_dialog(confirm_dialog)),
                ]
            )
            page.dialog = confirm_dialog
            page.add(confirm_dialog)
            confirm_dialog.open = True
            page.update()

        def confirm_delete(note_id, dialog):
            if delete_note(note_id):
                close_dialog(dialog)
                update_notes_list(notes_list)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Failed to delete note. Please try again."))
                page.snack_bar.open = True
                page.update()

        def close_dialog(dialog):
            dialog.open = False
            page.update()

        return ft.Card(
            elevation=3,
            content=ft.Container(
                padding=15,
                border_radius=10,
                bgcolor=ft.Colors.GREY_100,
                content=ft.Column(
                    controls=[
                        ft.Markdown(note["content"], width=400),
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY_OUTLINED,
                                    tooltip="View Note",
                                    on_click=view_note_details,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Edit Note",
                                    on_click=edit_note,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Delete Note",
                                    on_click=delete_note_action,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=5,
                        ),
                    ],
                    spacing=10,
                ),
            ),
        )

    # Main layout
    page.add(
        app_bar,
        ft.Row(
            controls=[search_box_container],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        create_note_form,
        ft.Container(
            content=notes_list,
            padding=10,
            expand=True
        ),
        ft.Row(
            controls=[load_more_button],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

    # Initially load notes
    update_notes_list(notes_list)

ft.app(target=main)