from src.SharedKernel.base.Container import Component
from src.SharedKernel.base.Logger import ILogger
from .services.Vision import Vision
from .services.LLMService import LLMService
from .services.AgentService import AgentService


@Component
class AIFacade:
    def __init__(self, 
        logger: ILogger,
        vision: Vision,
        llm: LLMService,
        agent: AgentService,
    ) -> None:
        logger.info("Hello AI Engine")
        self._vision = vision
        self._llm = llm
        self._agent = agent

    @property
    def VISION(self):
        return self._vision

    @property
    def LLM(self):
        return self._llm

    @property
    def AGENT(self):
        return self._agent