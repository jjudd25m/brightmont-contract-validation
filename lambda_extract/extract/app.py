from llama_cloud_services import LlamaExtract # pip install llama_cloud_services
from llama_cloud import ExtractConfig, ExtractMode, PublicModelName
from typing import Any
import pdfplumber

"""
@dataclass(frozen=True)
class ExtractionStep:
    schema: Any
    page_range: str
"""


class LLMExtractor:
    def __init__(self,
                 api_key: str,
                 extraction_plans,
                 post_processing_plan,
    ):
        self.extractor = LlamaExtract(api_key=api_key)
        self.extract_config = ExtractConfig(
            extraction_mode=ExtractMode.PREMIUM,
            # extraction_mode=ExtractMode.PREMIUM, # Must use for checkbox
            # extract_model=PublicModelName.OPENAI_GPT_41,
            extract_model=PublicModelName.OPENAI_GPT_5,
            high_res_ocr=True,
            # preset="forms",
            # outlined_table_extraction=True,
            # output_tables_as_HTML=True,
            # confidence_scores=True,
            high_resolution_mode=True,
            page_range="1-1",
            # cite_sources=True,
            use_reasoning=True,
            # confidence_scores=True,
        )
        self.extraction_plans = extraction_plans
        self.post_processing_plan = post_processing_plan

    # def _resolve_schema(self, title):
        # return titles[title]

    def _get_title(self, local_file_name: str) -> str:
        with pdfplumber.open(local_file_name) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        # lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        # return lines[0] if lines else ""
        return text.splitlines()[0]

    def _resolve_plan(self, title):
        return self.extraction_plans[title]

    def extract(self, local_file_name: str) -> Any:
        title = self._get_title(local_file_name)
        plan = self._resolve_plan(title)


        agreement: dict = {}
        for step in plan:
            config = self.extract_config.copy(update={"page_range": step.page_range})
            res = self.extractor.extract(step.schema, config, local_file_name)
            agreement |= res.data

        post_processing_plan_fn = self.post_processing_plan.get(title)
        print(f"Title: {title}")
        print(self.post_processing_plan)
        print(f"Post processing plan fn: {post_processing_plan_fn}")
        if post_processing_plan_fn:
            agreement = post_processing_plan_fn(agreement)

        print(agreement)
        return agreement
