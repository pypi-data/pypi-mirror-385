import sys

if sys.version_info < (3, 10):
    raise RuntimeError("The `ui_controller` module requires Python 3.10+.")

from typing import Annotated, List

try:
    from fastapi import HTTPException
    from fastapi.responses import HTMLResponse
    from fastui import AnyComponent, FastUI, prebuilt_html
    from fastui import components as c
    from fastui.events import GoToEvent, PageEvent
    from fastui.forms import fastui_form
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "The `ui_controller` module requires FastUI dependency. Install it with: pip install gukebox[ui]."
    ) from e
from pydantic import BaseModel, Field

from discstore.adapters.inbound.api_controller import APIController
from discstore.domain.entities.disc import Disc, DiscMetadata, DiscOption
from discstore.domain.use_cases.add_disc import AddDisc
from discstore.domain.use_cases.edit_disc import EditDisc
from discstore.domain.use_cases.list_discs import ListDiscs
from discstore.domain.use_cases.remove_disc import RemoveDisc


class DiscTable(DiscMetadata, DiscOption):
    tag: str = Field(title="Tag ID")
    uri: str = Field(title="URI / Path")


class DiscForm(BaseModel):
    tag: str = Field(title="Tag ID")
    uri: str = Field(title="URI / Path")


class UIController(APIController):
    def __init__(self, add_disc: AddDisc, list_discs: ListDiscs, remove_disc: RemoveDisc, edit_disc: EditDisc):
        super().__init__(add_disc, list_discs, remove_disc, edit_disc)
        self.register_routes()

    def register_routes(self):
        super().register_routes()

        @self.app.get("/api/ui/", response_model=FastUI, response_model_exclude_none=True)
        def list_discs() -> List[AnyComponent]:
            discs = self.list_discs.execute()
            discs_list = [
                DiscTable(tag=tag, uri=disc.uri, **disc.metadata.model_dump(), **disc.option.model_dump())
                for tag, disc in discs.items()
            ]
            return [
                c.Page(
                    components=[
                        c.Heading(text="DiscStore for Jukebox", level=1),
                        c.Button(text="➕ Add a new disc", on_click=PageEvent(name="modal-add-disc")),
                        c.Modal(
                            title="➕ Add a new disc",
                            body=[
                                c.ModelForm(model=DiscForm, submit_url="/modal-add-or-edit-disc", method="POST"),
                            ],
                            footer=None,
                            open_trigger=PageEvent(name="modal-add-disc"),
                        ),
                        c.Toast(
                            title="Toast",
                            body=[c.Paragraph(text="🎉 Disc added")],
                            open_trigger=PageEvent(name="toast-add-disc-success"),
                            position="top-center",
                        ),
                        c.Table(data=discs_list, no_data_message="No disc found"),  # type: ignore
                    ]
                ),
            ]  # type: ignore

        @self.app.post("/modal-add-or-edit-disc", response_model=FastUI, response_model_exclude_none=True)
        async def modal_add_or_edit_disc(disc: Annotated[DiscForm, fastui_form(DiscForm)]) -> list[AnyComponent]:
            try:
                self.add_disc.execute(disc.tag, Disc(uri=disc.uri, metadata=DiscMetadata()))
                return [
                    c.FireEvent(event=PageEvent(name="modal-add-disc", clear=True)),
                    c.FireEvent(event=PageEvent(name="toast-add-disc-success")),
                    GoToEvent(url="/api/ui"),  # type: ignore
                ]
            except ValueError:
                self.edit_disc.execute(disc.tag, Disc(uri=disc.uri, metadata=DiscMetadata()))
                return [
                    c.FireEvent(event=PageEvent(name="modal-add-disc", clear=True)),
                    c.FireEvent(event=PageEvent(name="toast-add-disc-success")),
                ]
            except Exception as err:
                raise HTTPException(status_code=500, detail=f"Server error: {str(err)}")

        @self.app.get("/{path:path}")
        def html_landing() -> HTMLResponse:
            return HTMLResponse(prebuilt_html(title="DiscStore for Jukebox", api_root_url="api/ui"))


c.Page.model_rebuild()
