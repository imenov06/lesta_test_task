from fastapi import APIRouter, Request, UploadFile, File, status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from config import data_storage
from tf_idf.helper import save_data_in_storage

router = APIRouter(
    prefix="/frontend",
    tags=['страница загрузки файлов']
)
templates = Jinja2Templates(directory="templates")


@router.get("/upload")
def get_upload_page(
        request: Request,
):
    return templates.TemplateResponse(name="index.html", context={"request": request})


@router.post("/upload")
def upload_files(request: Request, files: list[UploadFile] = File(...)) -> RedirectResponse:
    save_data_in_storage(files)
    redirect_url = request.url_for('get_tables_result')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/tables_tf_idf")
def get_tables_result(
        request: Request,
):
    tables_data = data_storage.copy().get("data_for_tf_idf_tables")
    count_tables = len(tables_data)
    return templates.TemplateResponse(name="table.html",
                                      context={
                                          "request": request,
                                          "count_tables": count_tables,
                                          "tables_data": tables_data,
                                      })