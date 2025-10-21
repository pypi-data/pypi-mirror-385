"""
Multi-Agent Coordination Patterns

This module provides production-ready multi-agent coordination patterns
that can be used directly via factory functions.

Patterns provide zero-config defaults with progressive configuration support.

Usage:
    from kaizen.agents.coordination import create_supervisor_worker_pattern

    # Zero-config usage
    pattern = create_supervisor_worker_pattern()
    tasks = pattern.delegate("Process 100 documents")
    results = pattern.aggregate_results(tasks[0]["request_id"])

    # Progressive configuration
    pattern = create_supervisor_worker_pattern(
        num_workers=5,
        model="gpt-4"
    )

Creating Custom Patterns:
    See examples/guides/creating-custom-multi-agent-patterns/ for tutorials on:
    - Extending BaseMultiAgentPattern
    - Creating custom coordination logic
    - Implementing pattern factories
"""

from kaizen.agents.coordination.base_pattern import BaseMultiAgentPattern
from kaizen.agents.coordination.consensus_pattern import (
    AggregatorAgent,
    ConsensusAggregationSignature,
    ConsensusPattern,
    ProposalCreationSignature,
    ProposerAgent,
    VoterAgent,
    VotingSignature,
    create_consensus_pattern,
)
from kaizen.agents.coordination.debate_pattern import (
    ArgumentConstructionSignature,
    DebatePattern,
    JudgeAgent,
    JudgmentSignature,
    OpponentAgent,
    ProponentAgent,
    RebuttalSignature,
    create_debate_pattern,
)
from kaizen.agents.coordination.handoff_pattern import (
    HandoffAgent,
    HandoffPattern,
    TaskEvaluationSignature,
    TaskExecutionSignature,
    create_handoff_pattern,
)
from kaizen.agents.coordination.sequential_pipeline import (
    PipelineStageAgent,
    SequentialPipelinePattern,
    StageProcessingSignature,
    create_sequential_pipeline,
)
from kaizen.agents.coordination.supervisor_worker import (
    CoordinatorAgent,
    ProgressMonitoringSignature,
    ResultAggregationSignature,
    SupervisorAgent,
    SupervisorWorkerPattern,
    TaskDelegationSignature,
    TaskExecutionSignature,
    WorkerAgent,
    create_supervisor_worker_pattern,
)

__all__ = [
    "BaseMultiAgentPattern",
    "SupervisorWorkerPattern",
    "SupervisorAgent",
    "WorkerAgent",
    "CoordinatorAgent",
    "create_supervisor_worker_pattern",
    "TaskDelegationSignature",
    "TaskExecutionSignature",
    "ResultAggregationSignature",
    "ProgressMonitoringSignature",
    "ConsensusPattern",
    "ProposerAgent",
    "VoterAgent",
    "AggregatorAgent",
    "create_consensus_pattern",
    "ProposalCreationSignature",
    "VotingSignature",
    "ConsensusAggregationSignature",
    "DebatePattern",
    "ProponentAgent",
    "OpponentAgent",
    "JudgeAgent",
    "create_debate_pattern",
    "ArgumentConstructionSignature",
    "RebuttalSignature",
    "JudgmentSignature",
    "SequentialPipelinePattern",
    "PipelineStageAgent",
    "create_sequential_pipeline",
    "StageProcessingSignature",
    "HandoffPattern",
    "HandoffAgent",
    "create_handoff_pattern",
    "TaskEvaluationSignature",
    "TaskExecutionSignature",
]
