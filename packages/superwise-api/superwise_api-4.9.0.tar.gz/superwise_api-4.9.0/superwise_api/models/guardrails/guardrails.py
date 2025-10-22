from typing import Annotated
from typing import List
from typing import Literal
from typing import Set
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from superwise_api.models.agent.agent import GuardModelLLM


class BaseGuard(BaseModel):
    model_config = ConfigDict(extra="allow")


class AllowedTopicsGuard(BaseGuard):
    topics: List[str]
    type: Literal["allowed_topics"] = Field(default="allowed_topics")
    model: GuardModelLLM


class RestrictedTopicsGuard(BaseGuard):
    topics: List[str]
    type: Literal["restricted_topics"] = Field(default="restricted_topics")
    model: GuardModelLLM


class ToxicityGuard(BaseGuard):
    type: Literal["toxicity"] = Field(default="toxicity")
    threshold: float = 0.5
    validation_method: Literal["sentence"] | Literal["full"] = "sentence"


class CorrectLanguageGuard(BaseGuard):
    type: Literal["correct_language"] = Field(default="correct_language")
    language_codes: List[str] = Field(default_factory=list)
    filter_mode: Literal["include"] | Literal["exclude"] = "include"


class StringCheckGuard(BaseGuard):
    type: Literal["string_check"] = Field(default="string_check")
    regex_pattern: Set[str] = Field(default_factory=set)


class CompetitorCheckGuard(BaseGuard):
    type: Literal["competitor_check"] = Field(default="competitor_check")
    competitor_names: Set[str] = Field(default_factory=set)


class PiiDetectionGuard(BaseGuard):
    type: Literal["pii_detection"] = Field(default="pii_detection")
    threshold: float = Field(default=0.5)
    categories: Set[str] = Field(default_factory=set)


class DetectJailbreakGuard(BaseGuard):
    type: Literal["detect_jailbreak"] = Field(default="detect_jailbreak")
    tags: Set[Literal["input"]] = Field(default_factory=set)
    threshold: float = Field(default=0.7)


Guard = Annotated[
    Union[
        ToxicityGuard,
        AllowedTopicsGuard,
        RestrictedTopicsGuard,
        CorrectLanguageGuard,
        StringCheckGuard,
        CompetitorCheckGuard,
        PiiDetectionGuard,
        DetectJailbreakGuard,
    ],
    Field(discriminator="type"),
]
Guards = List[Guard]


class GuardResponse(BaseModel):
    valid: bool
    message: str

    @classmethod
    def from_dict(cls, obj: dict):
        if obj is None:
            return None

        return GuardResponse.model_validate(obj)


GuardResponses = List[GuardResponse]
