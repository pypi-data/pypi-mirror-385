from portion.base import CommandBase
from portion.core import Logger
from portion.core import ProjectManager
from portion.core import TemplateManager


class NewCommand(CommandBase):
    def __init__(self,
                 template_name: str,
                 project_name: str,
                 logger: Logger) -> None:
        super().__init__(logger=logger)
        self.project_name = project_name
        self.template_name = template_name

        self.project_manager = ProjectManager()
        self.template_manager = TemplateManager()

    def execute(self) -> None:

        if self.project_manager.is_project_exist(self.project_name):
            self.logger.error("The project is already exist")
            return None

        if not self.template_manager.is_template_exists(self.template_name):
            self.logger.error("The template is not exist")
            return None

        self.project_manager.create_project(self.project_name)

        self.template_manager.copy_template(self.template_name,
                                            self.project_name)

        self.logger.info(
            f"{self.project_name} project has been created successfully")
