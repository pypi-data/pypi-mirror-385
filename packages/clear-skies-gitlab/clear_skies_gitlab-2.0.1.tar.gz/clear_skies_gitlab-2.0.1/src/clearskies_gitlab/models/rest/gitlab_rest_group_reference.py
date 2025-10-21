from clearskies_gitlab.models.rest import gitlab_rest_group


class GitlabRestGroupReference:
    def get_model_class(self):
        return gitlab_rest_group.GitlabRestGroup
