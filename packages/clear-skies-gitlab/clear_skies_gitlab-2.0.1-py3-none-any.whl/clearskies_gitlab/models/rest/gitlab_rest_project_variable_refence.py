from clearskies_gitlab.models.rest import gitlab_rest_project_variable


class GitlabRestProjectVariableReference:
    def get_model_class(self):
        return gitlab_rest_project_variable.GitlabRestProjectVariable
