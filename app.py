from __future__ import annotations

import html
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv

from utils.document_formatter import (
    format_docx,
    format_pdf,
    format_txt
)

from utils.text_utils import (
    settings,
    split_terms
)


load_dotenv()


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .hero {
        padding: 1.5rem;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            #111827,
            #1f2937
        );
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        margin-bottom: 0.3rem;
    }

    .preview {
        background: #111827;
        color: #f9fafb;
        border-radius: 14px;
        padding: 1.5rem;
        min-height: 420px;
        max-height: 620px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.6;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">

        <h1>⚖️ LegalEase</h1>

        <p>
            AI-powered legal document drafting,
            editing and export.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


st.warning(
    "LegalEase creates drafting assistance, not legal advice. "
    "Review important documents with a qualified legal "
    "professional before signing or relying on them."
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


if "generated_type" not in st.session_state:

    st.session_state.generated_type = ""


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header(
        "Document Details"
    )

    document_type = st.selectbox(
        "Document type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Lease Agreement",
            "Freelance Work Contract",
            "Employment Offer Letter",
            "Service Agreement",
            "Custom Agreement",
        ]
    )

    parties = st.text_area(
        "Parties involved",

        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),

        height=110
    )

    terms = st.text_area(
        "Terms & conditions",

        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Provider will deliver work by the "
            "agreed deadline; "
            "Either party may terminate with 15 days notice"
        ),

        height=170,

        help=(
            "Separate multiple terms using semicolons."
        )
    )

    effective_date = st.date_input(
        "Effective date",
        value=date.today()
    )

    generate_button = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True
    )

    st.divider()

    st.caption(
        f"Backend: {settings.backend_url}"
    )

    st.caption(
        f"AI Model: {settings.gemini_model}"
    )

    if settings.mock_ai:

        st.info(
            "MOCK_AI=true. "
            "The application is running without Gemini."
        )


# --------------------------------------------------
# GENERATE DOCUMENT
# --------------------------------------------------

if generate_button:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter at least one term."
        )

    else:

        payload = {

            "document_type":
                document_type,

            "parties":
                parties,

            "terms":
                terms,

            "effective_date":
                effective_date.isoformat()
        }

        try:

            with st.spinner(
                "Generating your legal draft..."
            ):

                response = requests.post(
                    (
                        f"{settings.backend_url.rstrip('/')}"
                        "/generate"
                    ),

                    json=payload,

                    timeout=120
                )

            if response.ok:

                data = response.json()

                st.session_state.document = (
                    data["content"]
                )

                st.session_state.generated_type = (
                    document_type
                )

                st.success(
                    "Document generated successfully!"
                )

            else:

                try:

                    error_message = (
                        response.json()
                        .get(
                            "detail",
                            response.text
                        )
                    )

                except Exception:

                    error_message = response.text

                st.error(
                    f"Backend error: {error_message}"
                )

        except requests.RequestException as error:

            st.error(
                "Could not connect to the FastAPI backend."
            )

            st.info(
                "Start FastAPI using:\n\n"
                "`uvicorn main:app --reload --port 8000`"
            )

            st.exception(error)


# --------------------------------------------------
# DOCUMENT PREVIEW
# --------------------------------------------------

st.subheader(
    "Document Preview & Editor"
)


if st.session_state.document:

    preview_column, editor_column = (
        st.columns([1.5, 1])
    )

    # ----------------------------------------------
    # PREVIEW
    # ----------------------------------------------

    with preview_column:

        safe_document = html.escape(
            st.session_state.document
        )

        st.markdown(
            (
                '<div class="preview">'
                f"{safe_document}"
                "</div>"
            ),
            unsafe_allow_html=True
        )

    # ----------------------------------------------
    # EDITOR
    # ----------------------------------------------

    with editor_column:

        edited_document = st.text_area(
            "Edit generated document",

            value=st.session_state.document,

            height=500
        )

        if st.button(
            "💾 Apply Edits",
            use_container_width=True
        ):

            st.session_state.document = (
                edited_document
            )

            st.success(
                "Edits applied."
            )

            st.rerun()

        # ------------------------------------------
        # DOWNLOAD BUTTONS
        # ------------------------------------------

        current_document = (
            edited_document
        )

        current_type = (
            st.session_state.generated_type
        )

        st.download_button(
            "⬇️ Download TXT",

            data=format_txt(
                current_document
            ),

            file_name="legalease_document.txt",

            mime="text/plain",

            use_container_width=True
        )

        st.download_button(
            "⬇️ Download DOCX",

            data=format_docx(
                current_document,
                current_type
            ),

            file_name="legalease_document.docx",

            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),

            use_container_width=True
        )

        st.download_button(
            "⬇️ Download PDF",

            data=format_pdf(
                current_document,
                current_type
            ),

            file_name="legalease_document.pdf",

            mime="application/pdf",

            use_container_width=True
        )

    # ------------------------------------------------
    # ORIGINAL TERMS
    # ------------------------------------------------

    st.divider()

    st.subheader(
        "Terms entered by user"
    )

    for term in split_terms(terms):

        st.markdown(
            f"- {term}"
        )

else:

    st.info(
        "Enter the document details in the sidebar "
        "and click Generate Document."
    )