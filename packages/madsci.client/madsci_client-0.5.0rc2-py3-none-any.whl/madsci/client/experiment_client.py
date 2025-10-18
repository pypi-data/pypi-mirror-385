"""Client for the MADSci Experiment Manager."""

from typing import Optional, Union

import requests
from madsci.common.context import get_current_madsci_context
from madsci.common.types.experiment_types import (
    Experiment,
    ExperimentalCampaign,
    ExperimentDesign,
    ExperimentRegistration,
    ExperimentStatus,
)
from pydantic import AnyUrl
from ulid import ULID


class ExperimentClient:
    """Client for the MADSci Experiment Manager."""

    experiment_server_url: AnyUrl

    def __init__(
        self,
        experiment_server_url: Optional[Union[str, AnyUrl]] = None,
    ) -> "ExperimentClient":
        """
        Create a new Experiment Client.

        Args:
            experiment_server_url: The URL of the experiment server. If not provided, will use the URL from the current MADSci context.
        """
        self.experiment_server_url = (
            AnyUrl(experiment_server_url)
            if experiment_server_url
            else get_current_madsci_context().experiment_server_url
        )
        if not self.experiment_server_url:
            raise ValueError(
                "No experiment server URL provided, please specify a URL or set the context."
            )

    def get_experiment(self, experiment_id: Union[str, ULID]) -> dict:
        """Get an experiment by ID."""
        response = requests.get(
            f"{self.experiment_server_url}experiment/{experiment_id}", timeout=10
        )
        if not response.ok:
            response.raise_for_status()
        return Experiment.model_validate(response.json())

    def get_experiments(self, number: int = 10) -> list[Experiment]:
        """Get a list of the latest experiments."""
        response = requests.get(
            f"{self.experiment_server_url}experiments",
            params={"number": number},
            timeout=10,
        )
        if not response.ok:
            response.raise_for_status()
        return [Experiment.model_validate(experiment) for experiment in response.json()]

    def start_experiment(
        self,
        experiment_design: ExperimentDesign,
        run_name: Optional[str] = None,
        run_description: Optional[str] = None,
    ) -> Experiment:
        """Start an experiment based on an ExperimentDesign."""
        response = requests.post(
            f"{self.experiment_server_url}experiment",
            json=ExperimentRegistration(
                experiment_design=experiment_design.model_dump(mode="json"),
                run_name=run_name,
                run_description=run_description,
            ).model_dump(mode="json"),
            timeout=10,
        )
        if not response.ok:
            response.raise_for_status()
        return Experiment.model_validate(response.json())

    def end_experiment(
        self, experiment_id: Union[str, ULID], status: Optional[ExperimentStatus] = None
    ) -> Experiment:
        """End an experiment by ID. Optionally, set the status."""
        response = requests.post(
            f"{self.experiment_server_url}experiment/{experiment_id}/end",
            params={"status": status},
            timeout=10,
        )
        if not response.ok:
            response.raise_for_status()
        return Experiment.model_validate(response.json())

    def continue_experiment(self, experiment_id: Union[str, ULID]) -> Experiment:
        """Continue an experiment by ID."""
        response = requests.post(
            f"{self.experiment_server_url}experiment/{experiment_id}/continue",
            timeout=10,
        )
        if not response.ok:
            response.raise_for_status()
        return Experiment.model_validate(response.json())

    def pause_experiment(self, experiment_id: Union[str, ULID]) -> Experiment:
        """Pause an experiment by ID."""
        response = requests.post(
            f"{self.experiment_server_url}experiment/{experiment_id}/pause", timeout=10
        )
        if not response.ok:
            response.raise_for_status()
        return Experiment.model_validate(response.json())

    def cancel_experiment(self, experiment_id: Union[str, ULID]) -> Experiment:
        """Cancel an experiment by ID."""
        response = requests.post(
            f"{self.experiment_server_url}experiment/{experiment_id}/cancel",
            timeout=10,
        )
        if not response.ok:
            response.raise_for_status()
        return Experiment.model_validate(response.json())

    def register_campaign(self, campaign: ExperimentalCampaign) -> ExperimentalCampaign:
        """Register a new experimental campaign."""
        response = requests.post(
            f"{self.experiment_server_url}campaign",
            json=campaign.model_dump(mode="json"),
            timeout=10,
        )
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def get_campaign(self, campaign_id: str) -> ExperimentalCampaign:
        """Get an experimental campaign by ID."""
        response = requests.get(
            f"{self.experiment_server_url}campaign/{campaign_id}", timeout=10
        )
        if not response.ok:
            response.raise_for_status()
        return response.json()
