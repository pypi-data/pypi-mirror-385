from textwrap import dedent
from typing import Literal, Type

from pydantic import BaseModel, Field

from kfinance.client.batch_request_handling import Task, process_tasks_in_thread_pool_executor
from kfinance.client.models.date_and_period_models import PeriodType
from kfinance.client.permission_models import Permission
from kfinance.domains.segments.segment_models import SegmentsResp, SegmentType
from kfinance.integrations.tool_calling.tool_calling_models import (
    KfinanceTool,
    ToolArgsWithIdentifiers,
    ToolRespWithErrors,
    ValidQuarter,
)


class GetSegmentsFromIdentifiersArgs(ToolArgsWithIdentifiers):
    # no description because the description for enum fields comes from the enum docstring.
    segment_type: SegmentType
    period_type: PeriodType | None = Field(default=None, description="The period type")
    start_year: int | None = Field(default=None, description="The starting year for the data range")
    end_year: int | None = Field(default=None, description="The ending year for the data range")
    start_quarter: ValidQuarter | None = Field(default=None, description="Starting quarter")
    end_quarter: ValidQuarter | None = Field(default=None, description="Ending quarter")


class GetSegmentsFromIdentifiersResp(ToolRespWithErrors):
    results: dict[str, SegmentsResp]


class GetSegmentsFromIdentifiers(KfinanceTool):
    name: str = "get_segments_from_identifiers"
    description: str = dedent("""
        Get the templated segments associated with a list of identifiers.

        - The tool accepts arguments in calendar years, and all outputs will be presented in terms of calendar years. Please note that these calendar years may not align with the company's fiscal year.
    """).strip()
    args_schema: Type[BaseModel] = GetSegmentsFromIdentifiersArgs
    accepted_permissions: set[Permission] | None = {Permission.SegmentsPermission}

    def _run(
        self,
        identifiers: list[str],
        segment_type: SegmentType,
        period_type: PeriodType | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        start_quarter: Literal[1, 2, 3, 4] | None = None,
        end_quarter: Literal[1, 2, 3, 4] | None = None,
    ) -> GetSegmentsFromIdentifiersResp:
        """Sample Response:

        {
            'results': {
                'SPGI': {
                    'segments': {
                        '2021': {
                            'Commodity Insights': {'CAPEX': -2000000.0, 'D&A': 12000000.0},
                            'Unallocated Assets Held for Sale': {'Total Assets': 321000000.0}
                        }
                    }
                }
            },
            'errors': ['No identification triple found for the provided identifier: NON-EXISTENT of type: ticker']
        }


        """

        api_client = self.kfinance_client.kfinance_api_client
        id_triple_resp = api_client.unified_fetch_id_triples(identifiers=identifiers)

        tasks = [
            Task(
                func=api_client.fetch_segments,
                kwargs=dict(
                    company_id=id_triple.company_id,
                    segment_type=segment_type,
                    period_type=period_type,
                    start_year=start_year,
                    end_year=end_year,
                    start_quarter=start_quarter,
                    end_quarter=end_quarter,
                ),
                result_key=identifier,
            )
            for identifier, id_triple in id_triple_resp.identifiers_to_id_triples.items()
        ]

        segments_responses: dict[str, SegmentsResp] = process_tasks_in_thread_pool_executor(
            api_client=api_client, tasks=tasks
        )

        # If no date and multiple companies, only return the most recent value.
        # By default, we return 5 years of data, which can be too much when
        # returning data for many companies.
        if (
            start_year is None
            and end_year is None
            and start_quarter is None
            and end_quarter is None
            and len(segments_responses) > 1
        ):
            for segments_response in segments_responses.values():
                if segments_response.segments:
                    most_recent_year = max(segments_response.segments.keys())
                    most_recent_year_data = segments_response.segments[most_recent_year]
                    segments_response.segments = {most_recent_year: most_recent_year_data}

        return GetSegmentsFromIdentifiersResp(
            results=segments_responses, errors=list(id_triple_resp.errors.values())
        )
