# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class StepType(str, Enum):
    RESEARCH = "research"
    PROCESSING = "processing"


class Step(BaseModel):
    need_search: bool = Field(..., description="Must be explicitly set for each step")
    title: str
    description: str = Field(..., description="Specify exactly what data to collect")
    step_type: StepType = Field(..., description="Indicates the nature of the step")
    execution_res: Optional[str] = Field(
        default=None, description="The Step execution result"
    )


class Plan(BaseModel):
    locale: str = Field(
        ..., description="e.g. 'en-US' or 'zh-CN', based on the user's language"
    )
    has_enough_context: bool
    thought: str
    title: str
    steps: List[Step] = Field(
        default_factory=list,
        description="Research & Processing steps to get more context",
    )

    def to_markdown(self) -> str:
        markdown = f"{self.thought}\n\n-----\n\n### {self.title}\n\n"
        for step in self.steps:
            markdown += f"#### {step.title}\n\n{step.description}\n\n"
        return markdown

    def to_plan_status(self) -> dict:
        status = {
            "title": self.title,
            "steps": [],
        }
        if self.has_enough_context:
            # All steps are successful if enough context
            for step in self.steps:
                status["steps"].append(
                    {
                        "title": step.title,
                        "description": step.description,
                        "status": "success",
                    }
                )
        else:
            found_running = False  # Flag to mark if we've found the first empty step
            for step in self.steps:
                if step.execution_res:
                    # Step has been executed successfully
                    step_status = "success"
                else:
                    if not found_running:
                        # First empty step is set to running
                        step_status = "running"
                        found_running = True
                    else:
                        step_status = "waiting"
                status["steps"].append(
                    {
                        "title": step.title,
                        "description": step.description,
                        "status": step_status,
                    }
                )
        return status

    def to_plan_status_markdown(self) -> str:
        markdown = f"#### {self.title}\n"
        for step in self.steps:
            if step.execution_res:

                markdown += (
                    f"- [x] {step.title}\n"
                    + '  <div style="font-size: 0.9em; color: grey;">'
                    + "</br>\n".join([f"  {i}" for i in step.description.split("\n")])
                    + "  </div>"
                    + "\n\n"
                )
            else:
                markdown += f"- [ ] {step.title}\n\n"
        return markdown

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "has_enough_context": False,
                    "thought": (
                        "To understand the current market trends in AI, we need to gather comprehensive information."
                    ),
                    "title": "AI Market Research Plan",
                    "steps": [
                        {
                            "need_search": True,
                            "title": "Current AI Market Analysis",
                            "description": (
                                "Collect data on market size, growth rates, major players, and investment trends in AI sector."
                            ),
                            "step_type": "research",
                        }
                    ],
                }
            ]
        }
