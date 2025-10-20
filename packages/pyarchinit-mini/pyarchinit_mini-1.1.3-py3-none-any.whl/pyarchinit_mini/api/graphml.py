"""
GraphML Converter API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, FileResponse
from typing import Optional
import tempfile
import os

from pyarchinit_mini.graphml_converter import (
    convert_dot_to_graphml,
    convert_dot_content_to_graphml,
    get_template_path
)

router = APIRouter()


@router.post("/convert",
             summary="Convert DOT file to GraphML",
             description="Upload a Graphviz DOT file and convert it to yEd-compatible GraphML format")
async def convert_dot_file(
    file: UploadFile = File(..., description="DOT file to convert"),
    title: str = Form("", description="Diagram title/header"),
    reverse_epochs: bool = Form(False, description="Whether to reverse epoch ordering")
):
    """
    Convert uploaded DOT file to GraphML format.

    Args:
        file: DOT file upload
        title: Optional diagram title
        reverse_epochs: Whether to reverse epoch ordering (default: False)

    Returns:
        GraphML file content

    Example:
        curl -X POST "http://localhost:8000/api/graphml/convert" \
             -F "file=@harris_matrix.dot" \
             -F "title=Pompei - Regio VI" \
             -F "reverse_epochs=false"
    """
    if not file.filename.endswith('.dot'):
        raise HTTPException(status_code=400, detail="File must have .dot extension")

    try:
        # Read uploaded file content
        content = await file.read()
        dot_content = content.decode('utf-8')

        # Convert to GraphML
        graphml_content = convert_dot_content_to_graphml(
            dot_content,
            title=title,
            reverse_epochs=reverse_epochs
        )

        if graphml_content is None:
            raise HTTPException(status_code=500, detail="Conversion failed")

        # Return GraphML content
        filename = file.filename.replace('.dot', '.graphml')
        return Response(
            content=graphml_content,
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@router.post("/convert-content",
             summary="Convert DOT content to GraphML",
             description="Convert DOT content string to GraphML format")
async def convert_dot_content(
    dot_content: str = Form(..., description="DOT file content as string"),
    title: str = Form("", description="Diagram title/header"),
    reverse_epochs: bool = Form(False, description="Whether to reverse epoch ordering")
):
    """
    Convert DOT content string to GraphML format.

    Args:
        dot_content: DOT file content as string
        title: Optional diagram title
        reverse_epochs: Whether to reverse epoch ordering (default: False)

    Returns:
        GraphML content as string

    Example:
        curl -X POST "http://localhost:8000/api/graphml/convert-content" \
             -F "dot_content=digraph { \"US 100\" -> \"US 101\"; }" \
             -F "title=Test Site"
    """
    try:
        graphml_content = convert_dot_content_to_graphml(
            dot_content,
            title=title,
            reverse_epochs=reverse_epochs
        )

        if graphml_content is None:
            raise HTTPException(status_code=500, detail="Conversion failed")

        return Response(
            content=graphml_content,
            media_type="application/xml"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@router.get("/template",
            summary="Download yEd GraphML template",
            description="Download the EM_palette.graphml template used for Harris Matrix diagrams")
async def download_template():
    """
    Download the yEd GraphML template file.

    Returns:
        EM_palette.graphml template file

    Example:
        curl -X GET "http://localhost:8000/api/graphml/template" -o EM_palette.graphml
    """
    template_path = get_template_path()

    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Template file not found")

    return FileResponse(
        path=template_path,
        media_type="application/xml",
        filename="EM_palette.graphml"
    )


@router.get("/health",
            summary="Health check",
            description="Check if the GraphML converter service is running")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Service status
    """
    return {
        "status": "ok",
        "service": "graphml-converter",
        "version": "1.0.0"
    }
