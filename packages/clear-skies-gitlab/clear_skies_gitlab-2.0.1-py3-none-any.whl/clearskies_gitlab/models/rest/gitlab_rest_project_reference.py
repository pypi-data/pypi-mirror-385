from clearskies_gitlab.models.rest import gitlab_rest_project


class GitlabRestProjectReference:
    def get_model_class(self):
        return gitlab_rest_project.GitlabRestProject
