from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer


class ClientsOverview(App[None]):
    """A TUI to show clients in a DataTable."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("n", "sort_by_last_name", "Sortieren nach `last_name_encr`"),
        Binding("s", "sort_by_school", "Sortieren nach `schule`"),
        Binding("i", "sort_by_client_id", "Sortieren nach `client_id`"),
        Binding("c", "sort_by_class_name", "Sortieren nach `class_name`"),
    ]

    def __init__(self, data: list[list[Any]]) -> None:
        super().__init__()
        self.ROWS = data
        self.current_sorts: set[str] = set()

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.fixed_columns = 1
        table.zebra_stripes = True
        for col in self.ROWS[0]:
            table.add_column(col, key=col)
        table.add_rows(self.ROWS[1:])

    def sort_reverse(self, sort_type: str) -> bool:
        """
        Determine if `sort_type` is ascending or descending.
        """
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    def action_sort_by_client_id(self) -> None:
        """Sort DataTable by client_id"""
        table = self.query_one(DataTable)
        table.sort(
            "client_id",
            reverse=self.sort_reverse("client_id"),
        )

    def action_sort_by_last_name(self) -> None:
        """Sort DataTable by last name"""
        table = self.query_one(DataTable)
        table.sort(
            "last_name_encr",
            reverse=self.sort_reverse("last_name_encr"),
        )

    def action_sort_by_school(self) -> None:
        """Sort DataTable by school and last name"""
        table = self.query_one(DataTable)
        table.sort(
            "school",
            "last_name_encr",
            reverse=self.sort_reverse("school"),
        )

    def action_sort_by_class_name(self) -> None:
        """Sort DataTable by class_name and last name"""
        table = self.query_one(DataTable)
        table.sort(
            "class_name",
            "last_name_encr",
            reverse=self.sort_reverse("class_name"),
        )
