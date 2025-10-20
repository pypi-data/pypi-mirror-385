import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any

import json5
from pydantic import BaseModel, Field
from util_common.path import sort_paths

from batch_store import BatchStore
from workspace_services.batch import Batch, batch_service
from workspace_services.settings import workspace_settings
from workspace_services.tag_models.classification_tag import ClassificationTag
from workspace_services.tag_models.detection_tag import DetectionTag
from workspace_services.task import TaskType, task_service


class WorkspaceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Workspace(BaseModel):
    id: str
    description: str = Field(default="")
    task_description: str = Field(default="")
    task_id: str = Field(default="page_classification")
    task_type: TaskType
    page_filter: str = Field(default="")
    tag_config: dict[str, Any] = Field(default_factory=dict)
    batches: list[str] = Field(default_factory=list)
    status: WorkspaceStatus = Field(default=WorkspaceStatus.ACTIVE)


class WorkspaceService:
    def __init__(self):
        self.workspace_root = workspace_settings.workspace_root
        self.task_root = workspace_settings.task_root
        self.batch_root = workspace_settings.batch_root
        self._workspaces: dict[str, Workspace] = dict()

    @property
    def workspaces(self) -> dict[str, Workspace]:
        if not self._workspaces:
            self._load_workspaces()
        return self._workspaces

    def _read_workspace_settings(self, workspace_id: str) -> dict[str, Any]:
        # TODO: 优化读取 workspace 配置
        workspace_settings_path = self.workspace_root / f"{workspace_id}.jsonc"
        if not workspace_settings_path.exists():
            raise ValueError(f"Workspace config {workspace_settings_path} not found")
        try:
            workspace_settings = json5.loads(workspace_settings_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to load workspace settings {workspace_settings_path}: {e}")
        if not isinstance(workspace_settings, dict):
            raise ValueError(f"Invalid workspace settings: {workspace_settings_path}")
        return workspace_settings

    def _get_workspace(self, workspace_id: str) -> Workspace:
        workspace_settings = self._read_workspace_settings(workspace_id)

        # 处理 task_id 字段：如果 task_id 不存在，则使用默认值 'page_classification'
        task_id = workspace_settings.get('task_id') or 'page_classification'
        task = task_service.get_task(task_id)

        return Workspace(
            id=workspace_id,
            description=workspace_settings.get('description', ''),
            task_description=task.description,
            task_id=task_id,
            task_type=task.task_type,
            page_filter=workspace_settings.get('page_filter', ''),
            tag_config=task.tag_config,
            batches=workspace_settings.get('batches', []),
            status=WorkspaceStatus.ACTIVE,
        )

    def _load_workspaces(self) -> dict[str, Workspace]:
        """
        加载所有 workspace 配置, 并缓存到 self.workspaces 中。
        用户刷新 /ui/workspaces 页面时, 重新加载所有 workspace 配置。
        """
        workspaces: dict[str, Workspace] = dict()
        for settings_path in sort_paths(self.workspace_root.glob('*.jsonc')):
            workspace_id = settings_path.stem
            try:
                workspaces[workspace_id] = self._get_workspace(workspace_id)
            except Exception as e:
                logging.warning(f"Failed to load workspace {workspace_id}: {e}")
        self._workspaces = workspaces
        return workspaces

    def get_workspace(self, workspace_id: str) -> Workspace:
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        return workspace

    def get_workspace_batches(self, workspace_id: str) -> list[Batch]:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace {workspace_id} not found")
        workspace = self.get_workspace(workspace_id)
        batches: list[Batch] = []
        for batch_id in sort_paths(workspace.batches):
            batches.append(batch_service.get_batch(str(batch_id)))
        return batches

    def get_workspace_reviewed_batches(self, workspace_id: str) -> list[str]:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace {workspace_id} not found")
        workspace = self.get_workspace(workspace_id)
        reviewed_batches: list[str] = []
        for batch_id in workspace.batches:
            tagging_status_path = BatchStore(batch_id).batch_dir / 'tagging_status.json'
            if not tagging_status_path.exists():
                print(f"Warning: Tagging status file not found for {batch_id}")
                continue
            tagging_status = json.loads(tagging_status_path.read_text())
            tagging_status = [
                x
                for x in tagging_status['tagging_status']
                if x['workspace_id'] == workspace.id and x['task_id'] == workspace.task_id
            ]
            if len(tagging_status) == 1 and tagging_status[0]['human_reviewed'] is True:
                reviewed_batches.append(batch_id)
        return reviewed_batches

    @staticmethod
    def get_tag_file_name(workspace: Workspace) -> str:
        if workspace and workspace.tag_config and workspace.tag_config.get("tag_name"):
            tag_name = workspace.tag_config["tag_name"]
        else:
            raise ValueError(f"Tag name not found for workspace {workspace.id}")
        return f"tag-{tag_name}.json"

    def get_tag_path(self, workspace: Workspace, page_dir: Path) -> Path:
        """
        tag 文件路径: 对应的 page 目录下, 文件名: tag-<tag_name>.json
        """
        if not page_dir.exists():
            raise ValueError(f"Page directory {page_dir} not found")
        return page_dir / self.get_tag_file_name(workspace)

    def tag_exists(self, workspace_id: str, page_dir: Path) -> bool:
        workspace = self.get_workspace(workspace_id)
        tag_path = self.get_tag_path(workspace, page_dir)
        return tag_path.is_file()

    def get_tag(self, workspace_id: str, page_dir: Path) -> dict:
        def update_abandon_status(tag_data: dict) -> dict:
            if workspace.page_filter:
                page_filter_tag_path = page_dir / f'tag-{workspace.page_filter}.json'
                if page_filter_tag_path.is_file():
                    try:
                        page_filter_tag = ClassificationTag(
                            **json.loads(page_filter_tag_path.read_text(encoding="utf-8"))
                        )
                        tag_data['abandon'] = page_filter_tag.classification == 0
                    except Exception as e:
                        logging.warning(f"Invalid page filter tag data: {e}")
            return tag_data

        workspace = self.get_workspace(workspace_id)
        task_type = workspace.task_type
        tag_path = self.get_tag_path(workspace, page_dir)
        if not tag_path.exists():
            tag_data = {}
        else:
            tag_data = json.loads(tag_path.read_text(encoding="utf-8"))
        if task_type == TaskType.CLASSIFICATION:
            try:
                tag_data = ClassificationTag(**tag_data).model_dump()
            except Exception as e:
                logging.warning(f"Invalid tag data: {e}")
                tag_data = {}
        elif task_type == TaskType.DETECTION:
            try:
                tag_data = DetectionTag(**tag_data).model_dump()
            except Exception as e:
                logging.warning(f"Invalid tag data: {e}")
                tag_data = {}
        else:
            raise ValueError(f"Invalid task type: {task_type}")

        if tag_data and not tag_data.get('abandon'):
            tag_data = update_abandon_status(tag_data)
        return tag_data

    def save_tag(self, workspace_id: str, page_dir: Path, tag_data: dict) -> bool:
        workspace = self.get_workspace(workspace_id)
        task_type = workspace.task_type
        if task_type == TaskType.CLASSIFICATION:
            try:
                tag: BaseModel = ClassificationTag(**tag_data)
            except Exception as e:
                raise ValueError(f"Invalid tag data: {e}")
        elif task_type == TaskType.DETECTION:
            try:
                tag = DetectionTag(**tag_data)
            except Exception as e:
                raise ValueError(f"Invalid tag data: {e}")
        else:
            raise ValueError(f"Invalid task type: {task_type}")
        tag_path = self.get_tag_path(workspace, page_dir)
        tag_path.write_text(
            json.dumps(tag.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return True


workspace_service = WorkspaceService()
