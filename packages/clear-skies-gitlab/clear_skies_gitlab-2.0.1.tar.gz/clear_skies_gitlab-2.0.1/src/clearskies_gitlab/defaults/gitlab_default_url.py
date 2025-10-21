import clearskies


class GitlabDefaultUrl(clearskies.di.AdditionalConfigAutoImport):
    def provide_gitlab_url(self, environment: clearskies.Environment):
        gitlab_url = environment.get("GITLAB_URL", True)
        return gitlab_url if gitlab_url else "https://gitlab.com/api/v4/"
