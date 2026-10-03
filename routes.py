from fastapi import (
    APIRouter,
    HTTPException
)

from ai_core.gemini_generator import (
    GeminiDocumentGenerator
)

from api.schemas import (
    DocumentRequest,
    DocumentResponse
)


router = APIRouter(
    tags=["Legal Documents"]
)


generator = GeminiDocumentGenerator()


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    request: DocumentRequest
):

    try:

        generated_text = (
            generator.generate_document(
                document_type=request.document_type,
                parties=request.parties,
                terms=request.terms,
                effective_date=request.effective_date,
            )
        )

        return DocumentResponse(
            success=True,
            document_type=request.document_type,
            content=generated_text,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=f"Document generation failed: {error}"
        ) from error