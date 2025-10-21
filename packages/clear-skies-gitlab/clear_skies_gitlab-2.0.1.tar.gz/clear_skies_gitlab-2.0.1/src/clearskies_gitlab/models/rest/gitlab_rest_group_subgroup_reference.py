from clearskies_gitlab.models.rest import gitlab_rest_group_subgroup


class GitlabRestGroupSubgroupReference:
    def get_model_class(self):
        return gitlab_rest_group_subgroup.GitlabRestGroupSubgroup
