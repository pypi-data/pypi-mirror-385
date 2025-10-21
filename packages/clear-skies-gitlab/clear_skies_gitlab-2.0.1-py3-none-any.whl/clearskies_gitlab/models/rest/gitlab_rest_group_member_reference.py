from clearskies_gitlab.models.rest import gitlab_rest_group_member


class GitlabRestGroupMemberReference:
    def get_model_class(self):
        return gitlab_rest_group_member.GitlabRestGroupMember
