from datetime import datetime
from logging import getLogger
from typing import List, Optional, TypeVar, cast, final

import pandas as pd
from requests import HTTPError

from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    add_assignees_to_annotation_task_annotation_tasks__annotation_task_uid__assignees_post as add_assignees_to_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    add_x_uids_to_annotation_task_annotation_tasks__annotation_task_uid__x_uids_post as add_x_uids_to_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    create_annotation_task_datasets__dataset_uid__annotation_tasks_post as create_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    delete_annotation_task_annotation_tasks__annotation_task_uid__delete as delete_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    fetch_annotation_task_dataframes_annotation_tasks__annotation_task_uid__dataframes_get as fetch_annotation_task_dataframes,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    get_annotation_task_annotation_tasks__annotation_task_uid__get as get_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    update_annotation_task_annotation_tasks__annotation_task_uid__put as update_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.datasets import (
    fetch_dataset_by_uid_datasets__dataset_uid__get as fetch_dataset_by_uid,
)
from snorkelai.sdk.client_v3.tdm.api.users import (
    get_list_workspaced_users_workspaced_users_get as get_users,
)
from snorkelai.sdk.client_v3.tdm.models import (
    AddAssigneesToAnnotationTaskParams,
    CreateAnnotationTaskParams,
    DataPointSelectionParams,
    DataPointStatus,
    UpdateAnnotationTaskParams,
)
from snorkelai.sdk.client_v3.tdm.models import (
    AnnotationForm as AnnotationFormModel,
)
from snorkelai.sdk.client_v3.tdm.types import UNSET
from snorkelai.sdk.client_v3.utils import _unwrap_unset, _wrap_in_unset
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.types.load import DATAPOINT_UID_COL

logger = getLogger(__name__)

T = TypeVar("T")


class LabelSchemaGroup:
    """A group of related label schemas to be shown together in the annotation form."""

    def __init__(
        self, name: str, description: Optional[str], label_schema_uids: List[int]
    ):
        """
        Parameters
        ----------
        name
            The name of the label schema group
        description
            A description of the label schema group, by default None
        label_schema_uids
            List of label schema UIDs in this group
        """
        self.name = name
        self.description = description
        self.label_schema_uids = label_schema_uids


class AnnotationForm:
    """Represents the annotation form with grouped and individual label schemas for a specific annotation task."""

    def __init__(
        self,
        grouped_label_schemas: Optional[List[LabelSchemaGroup]] = None,
        individual_label_schemas: Optional[List[int]] = None,
    ):
        """
        Parameters
        ----------
        grouped_label_schemas
            Groups of related label schemas that should be shown together, by default None
        individual_label_schemas
            Individual label_schema_uids not in any group, by default None
        """
        self.grouped_label_schemas = (
            grouped_label_schemas if grouped_label_schemas is not None else []
        )
        self.individual_label_schemas = (
            individual_label_schemas if individual_label_schemas is not None else []
        )


@final
class AnnotationTask(Base):
    """
    Represents an annotation task within a Snorkel dataset for managing annotation workflows.

    An annotation task defines a set of datapoints that need to be annotated, along with
    the annotation form, user assignments, and task configuration. This class provides
    methods for creating, retrieving, updating, and managing annotation tasks.

    AnnotationTask objects should not be instantiated directly - use the ``create()`` or
    ``get()`` class methods instead.
    """

    def __init__(
        self,
        name: str,
        annotation_task_uid: int,
        dataset_uid: int,
        created_by_user_uid: int,
        created_at: datetime,
        description: Optional[str] = None,
        annotation_form: Optional[AnnotationForm] = None,
        x_uids: Optional[List[str]] = None,
    ):
        """Create an AnnotationTask object in-memory with necessary properties.
        This constructor should not be called directly, and should instead be accessed
        through the ``create()`` and ``get()`` methods.

        Parameters
        ----------
        name
            The name of the annotation task
        annotation_task_uid
            The unique identifier for the annotation task
        dataset_uid
            The UID of the dataset that the annotation task belongs to
        created_by_user_uid
            The UID of the user who created the annotation task
        created_at
            The timestamp when the annotation task was created
        description
            A description of the annotation task, by default None
        annotation_form
            The annotation form associated with the task, by default None
        x_uids
            List of datapoint UIDs in this annotation task, by default None
        """
        self._name = name
        self._annotation_task_uid = annotation_task_uid
        self._dataset_uid = dataset_uid
        self._created_by_user_uid = created_by_user_uid
        self._created_at = created_at
        self._description = description
        self._annotation_form = (
            annotation_form if annotation_form is not None else AnnotationForm()
        )
        self._x_uids = x_uids or []

    # ----------------------------------
    # ANNOTATION TASK PROPERTIES
    # ----------------------------------

    @property
    def uid(self) -> int:
        """Return the UID of the annotation task"""
        return self._annotation_task_uid

    @property
    def name(self) -> str:
        """Return the name of the annotation task"""
        return self._name

    @property
    def dataset_uid(self) -> int:
        """Return the UID of the dataset that the annotation task belongs to"""
        return self._dataset_uid

    @property
    def description(self) -> Optional[str]:
        """Return the description of the annotation task"""
        return self._description

    @property
    def created_by_user_uid(self) -> int:
        """Return the UID of the user who created the annotation task"""
        return self._created_by_user_uid

    @property
    def created_at(self) -> datetime:
        """Return the creation timestamp of the annotation task"""
        return self._created_at

    @property
    def annotation_form(self) -> AnnotationForm:
        """Return the annotation form of the annotation task"""
        return self._annotation_form

    @property
    def x_uids(self) -> List[str]:
        """Return the list of datapoint UIDs in this annotation task"""
        return self._x_uids

    # ----------------------------------
    # CRUD OPERATIONS
    # ----------------------------------
    @classmethod
    def create(
        cls,
        dataset_uid: int,
        name: str,
        description: Optional[str] = None,
    ) -> "AnnotationTask":
        """Create an annotation task.

        .. note::

            This method only accepts `dataset_uid`, `name`, and `description` as parameters.
            Other properties (such as annotation form, datapoint UIDs, and questions) can be set later through
            other methods.


        Parameters
        ----------
        dataset_uid
            The UID of the dataset for the annotation task
        name
            The name of the annotation task
        description
            A description of the annotation task, by default None

        Returns
        -------
        AnnotationTask
            The created annotation task object
        """
        annotation_task_params = CreateAnnotationTaskParams(
            # Since as mentioned above, we are not passing annotation_form intentionally, we can just assume empty ones.
            annotation_form=AnnotationFormModel(),
            description=_wrap_in_unset(description),
            name=name,
        )

        try:
            created_annotation_task = create_annotation_task(
                dataset_uid=dataset_uid,
                body=annotation_task_params,
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        return cls.get(created_annotation_task.annotation_task_uid)

    @classmethod
    def get(cls, annotation_task_uid: int) -> "AnnotationTask":
        """Get an annotation task by UID.

        Parameters
        ----------
        annotation_task_uid
            The UID of the annotation task to retrieve

        Returns
        -------
        AnnotationTask
            The annotation task object
        """
        try:
            annotation_task = get_annotation_task(annotation_task_uid)
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        # Convert the API model's AnnotationForm to our SDK's AnnotationForm
        annotation_form = None
        if annotation_task.annotation_form:
            grouped_label_schemas = []
            if (
                annotation_task.annotation_form.grouped_label_schemas
                and annotation_task.annotation_form.grouped_label_schemas is not UNSET
            ):
                for group in annotation_task.annotation_form.grouped_label_schemas:
                    group_description: Optional[str] = _unwrap_unset(
                        group.description, None
                    )
                    label_schema_uids: List[int] = _unwrap_unset(
                        group.label_schema_uids, cast(List[int], [])
                    )
                    grouped_label_schemas.append(
                        LabelSchemaGroup(
                            name=group.name,
                            description=group_description,
                            label_schema_uids=label_schema_uids,
                        )
                    )

            individual_label_schemas = (
                annotation_task.annotation_form.individual_label_schemas
                if (
                    annotation_task.annotation_form.individual_label_schemas
                    and annotation_task.annotation_form.individual_label_schemas
                    is not UNSET
                )
                else []
            )

            annotation_form = AnnotationForm(
                grouped_label_schemas=grouped_label_schemas,
                individual_label_schemas=individual_label_schemas,
            )

        # Extract values and handle UNSET types properly
        task_description: Optional[str] = _unwrap_unset(
            annotation_task.description, None
        )
        x_uids: List[str] = _unwrap_unset(annotation_task.x_uids, cast(List[str], []))

        return AnnotationTask(
            name=annotation_task.name,
            annotation_task_uid=annotation_task.annotation_task_uid,
            dataset_uid=annotation_task.dataset_uid,
            created_by_user_uid=annotation_task.created_by_user_uid,
            created_at=annotation_task.created_at,
            description=task_description,
            annotation_form=annotation_form,
            x_uids=x_uids,
        )

    @classmethod
    def delete(cls, annotation_task_uid: int) -> None:
        """Delete an annotation task.

        Parameters
        ----------
        annotation_task_uid
            The UID of the annotation task to delete
        """
        try:
            delete_annotation_task(annotation_task_uid=annotation_task_uid)
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Update an annotation task.

        Parameters
        ----------
        name
            The new name for the annotation task, by default None
        description
            The new description for the annotation task, by default None
        """
        update_body = UpdateAnnotationTaskParams(
            annotation_task_uid=self.uid,
            name=_wrap_in_unset(name),
            description=_wrap_in_unset(description),
        )

        try:
            update_annotation_task(annotation_task_uid=self.uid, body=update_body)

            # Update the in-memory object properties after successful API call
            if name is not None:
                self._name = name
            if description is not None:
                self._description = description

        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    # ----------------------------------
    # DATA FRAME OPERATIONS
    # ----------------------------------
    def get_dataframe(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> pd.DataFrame:
        """Fetch the dataset columns for all the datapoints in an annotation task.

        Parameters
        ----------
        limit
            The max number of rows to return. If None, all rows will be returned.
        offset
            Rows will be returned starting at this index.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the annotation task data
        """
        try:
            response = fetch_annotation_task_dataframes(
                annotation_task_uid=self.uid,
                dataset_uid=self.dataset_uid,
                limit=_wrap_in_unset(limit),
                offset=offset,
                include_x_uids=True,
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        records = [item.to_dict() for item in response.data]
        df = pd.DataFrame(records)

        if not df.empty:
            df = df.rename(columns={"x_uid": DATAPOINT_UID_COL})
            df = df.set_index(DATAPOINT_UID_COL)

        return df

    def get_annotation_status(self, user_format: bool = True) -> pd.DataFrame:
        """Fetch the task columns (assignees, status) for all the datapoints in an annotation task.

        Parameters
        ----------
        user_format
            If True, assignee names are returned instead of uids

        Returns
        -------
        pd.DataFrame
            A DataFrame with columns: x_uid (this is the index), assignees (list of user UIDs or usernames), status (str)
            The DataFrame will have one row per datapoint in the annotation task

            Example:
                Data Point ID    Assignee(s)         Status
                ----------       ----------          ----------
                doc::1           [101, 102]          ASSIGNED
                doc::2           [103]               READY_FOR_REVIEW
                doc::3           [101, 104]          COMPLETED
                doc::4           []                  UNASSIGNED
        """
        x_uids = self.x_uids

        if len(x_uids) == 0:
            return pd.DataFrame(columns=["assignees", "status"]).rename_axis(
                DATAPOINT_UID_COL
            )

        try:
            response = fetch_annotation_task_dataframes(
                annotation_task_uid=self.uid,
                dataset_uid=self.dataset_uid,
                include_x_uids=True,
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        records = [item.to_dict() for item in response.data]
        full_df = pd.DataFrame(records)
        if full_df.empty:
            df = pd.DataFrame(
                [
                    {
                        DATAPOINT_UID_COL: x_uid,
                        "assignees": [],
                        "status": DataPointStatus.UNASSIGNED,
                    }
                    for x_uid in x_uids
                ]
            ).set_index(DATAPOINT_UID_COL)
            df.index.name = DATAPOINT_UID_COL
            return df

        # Extract only the columns we need
        status_data = []

        df_by_x_uid = {
            row[DATAPOINT_UID_COL]: row for row in full_df.to_dict(orient="records")
        }

        for x_uid in x_uids:
            row = df_by_x_uid.get(x_uid)

            # In case the x_uid is missing in the fetched dataframe, we assume unassigned status and no assignees
            if row is None:
                status_data.append(
                    {
                        DATAPOINT_UID_COL: x_uid,
                        "assignees": [],
                        "status": DataPointStatus.UNASSIGNED,
                    }
                )
                continue

            status_data.append(
                {
                    DATAPOINT_UID_COL: x_uid,
                    "assignees": (
                        row["__ASSIGNEES"]
                        if isinstance(row["__ASSIGNEES"], list)
                        else []
                    ),
                    "status": str(row["__STATUS"]),
                }
            )

        df = pd.DataFrame(status_data)
        df = df.set_index(DATAPOINT_UID_COL)

        if user_format:
            try:
                dataset_response = fetch_dataset_by_uid(self.dataset_uid)

                workspace_uid = dataset_response.workspace_uid
                if workspace_uid is UNSET:
                    raise ValueError("Dataset is missing a valid workspace UID")
                assert isinstance(workspace_uid, int)  # mypy

                users_response = get_users(
                    workspace_uid=workspace_uid, include_inactive=True
                )
                uid_to_username = {
                    user.user_uid: user.username for user in users_response
                }

                df["assignees"] = df["assignees"].apply(
                    lambda assignee_list: (
                        [
                            uid_to_username.get(uid, f"unknown_user_{uid}")
                            for uid in assignee_list
                        ]
                        if assignee_list
                        else []
                    )
                )
            except HTTPError as e:
                # If we can't fetch users, fall back to UIDs
                logger.warning(
                    "Could not fetch necessary info for mapping user names. Falling back to user UIDs.",
                    exc_info=True,
                )

        return df

    # ----------------------------------
    # ANNOTATION OPERATIONS
    # ----------------------------------

    # ----------------------------------
    # DATA POINT OPERATIONS
    # ----------------------------------
    def add_datapoints(self, x_uids: List[str]) -> None:
        """Add datapoints to the annotation task.
        NOTE: This will be implemented properly in ENG-39277. Currently needed for testing purposes in ENG-39376

        Parameters
        ----------
        x_uids
            List of datapoint UIDs to add to the annotation task
        """
        params = DataPointSelectionParams(
            include_x_uids=x_uids,
        )

        add_x_uids_to_annotation_task(
            annotation_task_uid=self.uid,
            body=params,
        )

    # ----------------------------------
    # USER OPERATIONS
    # ----------------------------------

    def add_assignees(self, user_uids: List[int], x_uids: List[str]) -> None:
        """Assign all of the listed users to the listed datapoints in the annotation task.

        Parameters
        ----------
        user_uids
            List of user UIDs to assign to the datapoints
        x_uids
            List of datapoint UIDs to assign the users to

        Raises
        ------
        ValueError
            If user_uids or x_uids are empty, or if user input is invalid

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.add_assignees(user_uids=[1, 2, 3], x_uids=["doc::1", "doc::2", "doc::3"])
        """
        if not user_uids:
            raise ValueError("user_uids cannot be empty")
        if not x_uids:
            raise ValueError("x_uids cannot be empty")

        try:
            params = AddAssigneesToAnnotationTaskParams(
                user_uids=user_uids,
                include_x_uids=x_uids,
            )

            add_assignees_to_annotation_task(
                annotation_task_uid=self.uid,
                body=params,
            )
            logger.info(
                f"Successfully added {len(user_uids)} assignees to {len(x_uids)} datapoints "
                f"in annotation task {self.name}"
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    # ----------------------------------
    # LABEL SCHEMA OPERATIONS
    # ----------------------------------
